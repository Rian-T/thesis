"""Espace de labels dérivé des données — aucun vocabulaire écrit à la main.

Un schéma d'extraction déclare, pour chaque champ, un espace de sortie. Plutôt que de
le réécrire à la main (listes de synonymes, règles de négation, alias par langue), on le
*lit dans les données d'entraînement* :

  - CLOSED : les valeurs observées forment un petit ensemble stable -> les classes SONT
             ces valeurs, telles qu'elles apparaissent (aucune traduction inventée) ;
  - NUMBER : les valeurs parsent en nombre ;
  - DATE   : les valeurs parsent en date ISO ;
  - TEXT   : le reste.

Ce module ne traite que les *valeurs d'annotation*, qui sont déjà typées par le schéma
de génération. Extraire une valeur depuis du *texte libre* est un autre travail (parsing
de span) et vit ailleurs. Rien ici n'est spécifique à une langue ni à un domaine.
"""
import json
import re
import unicodedata
from collections import Counter, defaultdict

ISO_DATE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
NUMBER = re.compile(r"^[-+]?\d+(?:[.,]\d+)?$")


def normkey(s):
    """Clé de comparaison universelle : casse, accents et ponctuation neutralisés."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^0-9a-z]+", " ", s.lower()).strip()


def as_number(v):
    m = NUMBER.match(str(v).strip())
    return float(m.group().replace(",", ".")) if m else None


def as_date(v):
    v = str(v).strip()
    return v if ISO_DATE.match(v) else None


def collect_values(records, fields):
    """records : itérable de dicts d'annotation -> {champ: Counter(valeurs brutes)}."""
    out = defaultdict(Counter)
    for ann in records:
        for f in fields:
            v = ann.get(f)
            if v is None:
                continue
            for it in ([v] if isinstance(v, dict) else v):
                if isinstance(it, dict) and it.get("value") not in (None, ""):
                    out[f][str(it["value"]).strip()] += 1
    return out


def derive(values_by_field, coverage=0.90, max_classes=40, min_count=2, min_n=30, parse_rate=0.8):
    """-> {champ: {type, classes, coverage, n, n_distinct}}.

    Deux décisions distinctes, pour ne pas laisser un seuil de couverture amputer un
    vocabulaire :
      1. les *classes* d'un champ = toutes ses valeurs vues au moins `min_count` fois
         (plafonnées à `max_classes`, par fréquence décroissante) ;
      2. le champ est *fermé* si ces classes couvrent au moins `coverage` de sa masse.
    Un champ trop peu observé est marqué UNKNOWN plutôt que tranché à l'aveugle.
    """
    space = {}
    for f, cnt in values_by_field.items():
        n = sum(cnt.values())
        if n == 0:
            continue
        # variantes de surface partageant une clé normalisée = une seule classe,
        # représentée par sa forme la plus fréquente (sinon l'index les écraserait)
        merged = defaultdict(Counter)
        for v, c in cnt.items():
            merged[normkey(v)][v] += c
        agg = Counter({forms.most_common(1)[0][0]: sum(forms.values()) for forms in merged.values()})
        classes = [v for v, c in agg.most_common(max_classes) if c >= min_count]
        cov = sum(agg[v] for v in classes) / n
        vals = list(cnt.elements())
        if n < min_n:
            typ = "UNKNOWN"
        elif classes and cov >= coverage:
            typ = "CLOSED"
        elif sum(as_date(v) is not None for v in vals) / n >= parse_rate:
            typ = "DATE"
        elif sum(as_number(v) is not None for v in vals) / n >= parse_rate:
            typ = "NUMBER"
        else:
            typ = "TEXT"
        space[f] = {"type": typ, "classes": classes if typ == "CLOSED" else [],
                    "coverage": cov, "n": n, "n_distinct": len(cnt)}
    return space


def canon_index(space):
    """{champ: {clé normalisée -> classe canonique}} pour un appariement exact."""
    return {f: {normkey(c): c for c in s["classes"]} for f, s in space.items() if s["classes"]}


def to_canon(space, index, field, raw):
    """Valeur d'annotation -> valeur canonique, ou None si hors espace (jamais devinée)."""
    s = space.get(field)
    if s is None or raw is None or str(raw).strip() == "":
        return None
    if s["type"] == "CLOSED":
        return index.get(field, {}).get(normkey(raw))
    if s["type"] == "DATE":
        return as_date(raw)
    if s["type"] == "NUMBER":
        return as_number(raw)
    return str(raw).strip()


# --------------------------------------------------------------------------- I/O
def load_annotations(prod_path, keep_ids=None):
    """prod jsonl -> {doc_id: annotation}. keep_ids restreint au split d'entraînement."""
    out = {}
    for line in open(prod_path, encoding="utf-8"):
        r = json.loads(line)
        rid = f"lym_{r['sample_index']}"
        if keep_ids is None or rid in keep_ids:
            out[rid] = r.get("annotation") or {}
    return out


def build(prod_path, fields, train_ids, **kw):
    """Dérive l'espace de labels sur le SEUL split d'entraînement. -> (space, index)."""
    anns = load_annotations(prod_path, train_ids)
    space = derive(collect_values(anns.values(), fields), **kw)
    return space, canon_index(space)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import taxonomy as T

    LB = "/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/lymphome"
    PROD = "/lustre/fswork/projects/rech/rua/uvb79kr/biomed-fr-v4/lymphome_v4/outputs/prod_20260527_121452.jsonl"
    train_ids = {json.loads(l)["id"] for l in open(f"{LB}/lymphome_train_v2.jsonl", encoding="utf-8")}
    test_ids = {json.loads(l)["id"] for l in open(f"{LB}/lymphome_test_v2.jsonl", encoding="utf-8")}
    space, index = build(PROD, T.FIELDS, train_ids)

    print(f"espace dérivé sur {len(train_ids)} docs d'entraînement, {len(space)} champs")
    print(Counter(s["type"] for s in space.values()))
    print("\ntype dérivé  x  famille écrite à la main :")
    conf = Counter((space[f]["type"], T.FIELD_SPEC[f]["family"]) for f in space if f in T.FIELD_SPEC)
    for (a, b), c in sorted(conf.items()):
        print(f"   {a:7s} / {b:5s} : {c}")

    print("\ncouverture des valeurs de TEST par l'espace dérivé sur le TRAIN :")
    anns = load_annotations(PROD, test_ids)
    vt = collect_values(anns.values(), T.FIELDS)
    for typ in ("CLOSED", "NUMBER", "DATE"):
        ok = tot = 0
        for f, cnt in vt.items():
            if space.get(f, {}).get("type") != typ:
                continue
            for v, c in cnt.items():
                tot += c; ok += c * (to_canon(space, index, f, v) is not None)
        print(f"   {typ:7s} {ok}/{tot} = {100 * ok / max(tot, 1):.1f}%")

    print("\nexemples de champs CLOSED (classes telles qu'observées) :")
    for f in list(space)[:6]:
        if space[f]["type"] == "CLOSED":
            print(f"   {f[:48]:48s} {space[f]['classes']}")
