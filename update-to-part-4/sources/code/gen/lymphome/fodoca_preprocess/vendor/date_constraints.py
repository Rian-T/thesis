"""Transitive date_after constraint validation for annotation date fields."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Set, Tuple
import re

DateKey = Tuple[str, int]  # (field_name, rank)

POTENTIAL_FUTURE_DATE_REGEX = re.compile(r'prévu|programmé|envisagé|fixé|planifié|planification')


def parse_iso_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = s[:10]
    try:
        y, m, d = (int(x) for x in s.split("-"))
        return date(y, m, d)
    except (ValueError, TypeError):
        return None


def build_date_after_map(field_rows: List[dict]) -> Dict[str, str]:
    """Map field_name -> direct predecessor (date_after)."""
    out: Dict[str, str] = {}
    for row in field_rows:
        pred = row.get("date_after")
        if pred:
            out[row["name"]] = str(pred).strip()
    return out


def build_field_meta(field_rows: List[dict]) -> Dict[str, dict]:
    return {row["name"]: row for row in field_rows}


def transitive_predecessors(field: str, date_after_map: Dict[str, str]) -> List[str]:
    """All fields that must be strictly before `field` (direct + indirect)."""
    result: List[str] = []
    seen: Set[str] = set()
    stack: List[str] = []
    direct = date_after_map.get(field)
    if direct:
        stack.append(direct)
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        result.append(p)
        parent = date_after_map.get(p)
        if parent and parent not in seen:
            stack.append(parent)
    return result


def transitive_successors(field: str, date_after_map: Dict[str, str]) -> List[str]:
    """All fields that must be strictly after `field` (direct + indirect)."""
    children: Dict[str, List[str]] = {}
    for child, parent in date_after_map.items():
        children.setdefault(parent, []).append(child)
    result: List[str] = []
    seen: Set[str] = set()
    stack = list(children.get(field, []))
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        result.append(s)
        stack.extend(children.get(s, []))
    return result


def effective_rank_for_pair(
    field_name: str,
    other_name: str,
    rank: int,
    meta: Dict[str, dict],
) -> int:
    """Rank to use when reading `other_name` relative to `field_name` at `rank`."""
    other = meta.get(other_name) or {}
    if other.get("duplicate_field"):
        return rank
    return 0


def validate_date_constraints(
    values: Dict[DateKey, Any],
    field_rows: List[dict],
    document_creation_date: Any = None,
) -> List[dict]:
    """
    Validate all date_after constraints (transitively).

    values: (field_name, rank) -> ISO date string or empty.
    Returns list of violations dicts:
      field, rank, other_field, other_rank, relation ('after'|'before'), message
    """
    meta = build_field_meta(field_rows)
    date_after_map = build_date_after_map(field_rows)
    doc_date = parse_iso_date(document_creation_date)

    violations: List[dict] = []
    checked: Set[Tuple[str, int, str, int, str]] = set()

    def get_date(fn: str, rk: int) -> Optional[date]:
        raw = values.get((fn, rk))
        if isinstance(raw, (tuple, list)):
            raw = raw[0] if raw else None
        return parse_iso_date(raw)

    def label(fn: str) -> str:
        return (meta.get(fn) or {}).get("label") or fn

    constrained_fields = set(date_after_map.keys())
    for succ_root in date_after_map.values():
        constrained_fields.add(succ_root)
        constrained_fields |= set(transitive_successors(succ_root, date_after_map))

    for (field_name, rank), packed in list(values.items()):
        if isinstance(packed, (tuple, list)):
            raw = packed[0] if packed else None
            span = packed[1] if len(packed) > 1 else None
        else:
            raw = packed
            span = None
        if field_name not in constrained_fields and field_name not in date_after_map:
            # still validate fields that are predecessors in chain
            if field_name not in meta or meta[field_name].get("field_type") != "date":
                continue
        d_field = parse_iso_date(raw)
        if d_field is None:
            continue

        if doc_date and d_field > doc_date:
            violations.append(
                {
                    "field": field_name,
                    "rank": rank,
                    "relation": "after_document_creation",
                    "message": (
                        f"“{label(field_name)}” must not be after the document creation date "
                        f"({d_field.isoformat()} is after {doc_date.isoformat()})."
                    ),
                }
            )

        if span and POTENTIAL_FUTURE_DATE_REGEX.search(span):
            violations.append(
                {
                    "field": field_name,
                    "rank": rank,
                    "relation": "potential_future_date",
                    "message": f"“{label(field_name)}” denotes a potential future date ({raw}) [{span}].",
                }
            )

        for pred in transitive_predecessors(field_name, date_after_map):
            pr = effective_rank_for_pair(field_name, pred, rank, meta)
            key = (field_name, rank, pred, pr, "after")
            if key in checked:
                continue
            checked.add(key)
            d_pred = get_date(pred, pr)
            if d_pred is None:
                continue
            if d_field < d_pred:
                violations.append(
                    {
                        "field": field_name,
                        "rank": rank,
                        "other_field": pred,
                        "other_rank": pr,
                        "relation": "after",
                        "message": (
                            f"“{label(field_name)}” must be after “{label(pred)}” "
                            f"({d_field.isoformat()} is not after {d_pred.isoformat()})."
                        ),
                    }
                )

        for succ in transitive_successors(field_name, date_after_map):
            sr = effective_rank_for_pair(succ, field_name, rank, meta)
            key = (succ, sr, field_name, rank, "after")
            if key in checked:
                continue
            checked.add(key)
            d_succ = get_date(succ, sr)
            if d_succ is None:
                continue
            if d_succ < d_field:
                violations.append(
                    {
                        "field": succ,
                        "rank": sr,
                        "other_field": field_name,
                        "other_rank": rank,
                        "relation": "after",
                        "message": (
                            f"“{label(succ)}” must be after “{label(field_name)}” "
                            f"({d_succ.isoformat()} is not after {d_field.isoformat()})."
                        ),
                    }
                )

    # Deduplicate by message
    seen_msg: Set[str] = set()
    unique: List[dict] = []
    for v in violations:
        m = v["message"]
        if m in seen_msg:
            continue
        seen_msg.add(m)
        unique.append(v)
    return unique


def _merge_annotation_rows_into_patient_map(
    by_patient: Dict[str, Tuple[Dict[DateKey, Any], Dict[DateKey, int]]],
    rows,
) -> None:
    """Merge (patient, field_name, rank, field_value, document_id) rows into by_patient."""
    for patient, field_name, rank, field_value, document_id, span_value in rows:
        if patient not in by_patient:
            by_patient[patient] = ({}, {})
        values, sources = by_patient[patient]
        key = (field_name, int(rank or 0))
        if key not in values:
            values[key] = (field_value, span_value)
            sources[key] = int(document_id)


def all_patients_annotation_values(conn) -> Dict[str, Tuple[Dict[DateKey, Any], Dict[DateKey, int]]]:
    """
    One query over all patients; group annotations by patient in memory.
    Returns patient -> (values, document_id_per_key).
    """
    rows = conn.execute(
        """
        SELECT d.patient, a.field_name, a.rank, a.field_value, a.document_id, a.span_value
        FROM annotations a
        INNER JOIN documents d ON d.id = a.document_id
        WHERE a.field_value IS NOT NULL AND TRIM(a.field_value) != ''
          AND a.status IN ('validated', 'proposition')
        ORDER BY d.patient COLLATE NOCASE, a.document_id DESC
        """,
    ).fetchall()
    by_patient: Dict[str, Tuple[Dict[DateKey, Any], Dict[DateKey, int]]] = {}
    _merge_annotation_rows_into_patient_map(by_patient, rows)
    return by_patient


def patient_annotation_values(conn, patient: str) -> Tuple[Dict[DateKey, Any], Dict[DateKey, int]]:
    """
    Merge annotation values for all documents of a patient.
    Returns (values, document_id_per_key) for linking issues to a document.
    """
    rows = conn.execute(
        """
        SELECT d.patient, a.field_name, a.rank, a.field_value, a.document_id, a.span_value
        FROM annotations a
        INNER JOIN documents d ON d.id = a.document_id
        WHERE d.patient = ?
          AND a.field_value IS NOT NULL
          AND TRIM(a.field_value) != ''
          AND a.status IN ('validated', 'proposition')
        ORDER BY a.document_id DESC
        """,
        (patient,),
    ).fetchall()
    by_patient: Dict[str, Tuple[Dict[DateKey, Any], Dict[DateKey, int]]] = {}
    _merge_annotation_rows_into_patient_map(by_patient, rows)
    return by_patient.get(patient, ({}, {}))


def load_document_index(conn) -> Tuple[Dict[str, Tuple[int, str]], Dict[int, str]]:
    """First document per patient and id -> filename lookup."""
    doc_by_patient: Dict[str, Tuple[int, str]] = {}
    doc_filenames: Dict[int, str] = {}
    for patient, doc_id, filename in conn.execute(
        "SELECT patient, id, filename FROM documents ORDER BY patient COLLATE NOCASE, id",
    ).fetchall():
        doc_filenames[int(doc_id)] = filename
        if patient not in doc_by_patient:
            doc_by_patient[patient] = (int(doc_id), filename)
    return doc_by_patient, doc_filenames


def collect_date_constraint_issues(conn, field_rows: List[dict]) -> List[dict]:
    """Scan all patients for date_after violations (bulk query + groupby patient)."""
    by_patient = all_patients_annotation_values(conn)
    doc_by_patient, doc_filenames = load_document_index(conn)
    doc_creation_dates: Dict[int, Any] = {
        int(r[0]): r[1]
        for r in conn.execute(
            "SELECT id, creation_date FROM documents WHERE creation_date IS NOT NULL AND TRIM(creation_date) != ''"
        ).fetchall()
    }
    labels = {f["name"]: f.get("label", f["name"]) for f in field_rows}
    issues: List[dict] = []

    for patient in sorted(by_patient.keys(), key=lambda p: str(p).casefold()):
        values, sources = by_patient[patient]
        violations = validate_date_constraints(values, field_rows)

        # Also validate: date values must not be after their source document creation date.
        for (field_name, rank), (raw, _span) in list(values.items()):
            doc_id = sources.get((field_name, rank))
            if not doc_id:
                continue
            doc_raw = doc_creation_dates.get(int(doc_id))
            if not doc_raw:
                continue
            d_doc = parse_iso_date(doc_raw)
            d_val = parse_iso_date(raw)
            if d_doc and d_val and d_val > d_doc:
                violations.append(
                    {
                        "field": field_name,
                        "rank": int(rank or 0),
                        "relation": "after_document_creation",
                        "message": (
                            f"“{labels.get(field_name, field_name)}” must not be after the document creation date "
                            f"({d_val.isoformat()} is after {d_doc.isoformat()})."
                        ),
                    }
                )
        if not violations:
            continue
        fallback_id, fallback_name = doc_by_patient.get(patient, (None, ""))
        for v in violations:
            doc_id = document_id_for_violation(v, sources, fallback_id)
            filename = doc_filenames.get(doc_id, fallback_name) if doc_id else fallback_name
            issues.append(
                {
                    "type": "date_constraint",
                    "type_label": "Date violation",
                    "patient": patient,
                    "document_id": doc_id,
                    "filename": filename,
                    "message": v.get("message", ""),
                    "field": v.get("field"),
                    "field_label": labels.get(v.get("field"), v.get("field")),
                    "other_field": v.get("other_field"),
                    "rank": v.get("rank", 0),
                }
            )
    return issues


def document_id_for_violation(
    violation: dict,
    sources: Dict[DateKey, int],
    fallback_doc_id: Optional[int],
) -> Optional[int]:
    """Pick a document to open for this violation."""
    for fn, rk in (
        (violation.get("field"), violation.get("rank", 0)),
        (violation.get("other_field"), violation.get("other_rank", 0)),
    ):
        if fn is None:
            continue
        key = (fn, int(rk or 0))
        if key in sources:
            return sources[key]
    return fallback_doc_id


def merge_annotation_values(
    conn,
    doc_id: int,
    updates: List[dict],
) -> Dict[DateKey, Any]:
    """Current document annotation values with updates applied."""
    rows = conn.execute(
        "SELECT field_name, rank, field_value, span_value FROM annotations "
        "WHERE document_id = ? AND status IN ('validated', 'proposition')",
        (doc_id,),
    ).fetchall()
    values: Dict[DateKey, Any] = {(r[0], int(r[1] or 0)): (r[2], r[3]) for r in rows}
    # print(f"values before updates: {values}")
    for u in updates:
        name = u.get("name") if isinstance(u, dict) else u.name
        rank = int(u.get("rank", 0) if isinstance(u, dict) else (u.rank or 0))
        value = u.get("value") if isinstance(u, dict) else u.value
        span = u.get("span") if isinstance(u, dict) else u.span
        values[(name, rank)] = (value, span)
    # print(f"values after updates: {values}")
    return values
