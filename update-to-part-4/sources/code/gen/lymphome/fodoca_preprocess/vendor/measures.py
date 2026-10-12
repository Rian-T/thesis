"""Parse and normalize measure values (number + optional unit)."""

from __future__ import annotations

import re
from typing import Optional, Tuple

# Canonical unit -> factor relative to the group's base unit.
# Conversion: value_in_base = value * factor[unit]
#             value_in_target = value_in_base / factor[target]
_UNIT_GROUPS: dict[str, dict[str, float]] = {
    "length": {
        "m": 100.0,  # base: cm
        "cm": 1.0,
        "mm": 0.1,
    },
    "mass": {
        "kg": 1000.0,  # base: g
        "g": 1.0,
        "mg": 0.001,
    },
    "activity_concentration": {
        "ui/l": 1.0,
        "u/l": 1.0,
        "iu/l": 1.0,
    },
}

_UNIT_ALIASES: dict[str, str] = {
    "m": "m",
    "mètre": "m",
    "metre": "m",
    "metres": "m",
    "mètres": "m",
    "meter": "m",
    "meters": "m",
    "cm": "cm",
    "centimètre": "cm",
    "centimetre": "cm",
    "centimètres": "cm",
    "centimetres": "cm",
    "mm": "mm",
    "millimètre": "mm",
    "millimetre": "mm",
    "kg": "kg",
    "kilogramme": "kg",
    "kilogrammes": "kg",
    "kilo": "kg",
    "g": "g",
    "gramme": "g",
    "grammes": "g",
    "mg": "mg",
    "ui/l": "ui/l",
    "u/l": "u/l",
    "iu/l": "iu/l",
    "ui/L": "ui/l",
    "U/L": "u/l",
    "IU/L": "iu/l",
}

_UNIT_TO_GROUP: dict[str, str] = {}
for _group, _units in _UNIT_GROUPS.items():
    for _unit in _units:
        _UNIT_TO_GROUP[_unit] = _group

# Number + optional unit. Accepts "1,76 m", "176cm", "70", "± 1.5 kg".
_MEASURE_RE = re.compile(
    r"^\s*[+±\-]?\s*"
    r"(?P<number>\d+(?:[.,]\d+)?)"
    r"(?:\s*(?P<unit>[A-Za-zµ°%]+(?:\s*/\s*[A-Za-zµ°%]+)?))?"
    r"\s*$",
    re.UNICODE,
)


def canonicalize_unit(unit: Optional[str]) -> Optional[str]:
    if unit is None:
        return None
    raw = str(unit).strip()
    if not raw:
        return None
    compact = re.sub(r"\s+", "", raw)
    lower = compact.lower()
    if lower in _UNIT_ALIASES:
        return _UNIT_ALIASES[lower]
    if compact in _UNIT_ALIASES:
        return _UNIT_ALIASES[compact]
    # Try lower-case path for mixed aliases already listed
    for alias, canon in _UNIT_ALIASES.items():
        if alias.lower() == lower:
            return canon
    return lower


def parse_measure(value: str) -> Optional[Tuple[float, Optional[str]]]:
    """Return (number, canonical_unit_or_None) or None if unparseable."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    m = _MEASURE_RE.match(text)
    if not m:
        return None
    number_str = m.group("number").replace(",", ".")
    try:
        number = float(number_str)
    except ValueError:
        return None
    unit = canonicalize_unit(m.group("unit"))
    return number, unit


def convert_measure(
    number: float, from_unit: Optional[str], to_unit: Optional[str]
) -> Optional[float]:
    """Convert number between compatible units. None if conversion impossible."""
    src = canonicalize_unit(from_unit)
    dst = canonicalize_unit(to_unit)
    if dst is None:
        return None
    if src is None:
        # Bare number: already assumed to be in the target unit.
        return number
    if src == dst:
        return number
    group_src = _UNIT_TO_GROUP.get(src)
    group_dst = _UNIT_TO_GROUP.get(dst)
    if not group_src or group_src != group_dst:
        return None
    factors = _UNIT_GROUPS[group_src]
    if src not in factors or dst not in factors:
        return None
    return number * factors[src] / factors[dst]


def format_measure_number(number: float) -> str:
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    text = f"{number:.6f}".rstrip("0").rstrip(".")
    return text


def format_measure(number: float, unit: Optional[str]) -> str:
    num = format_measure_number(number)
    if not unit:
        return num
    return f"{num} {unit}"


def normalize_measure(value: str, default_unit: Optional[str] = None) -> str:
    """
    Normalize a measure string for storage.

    - If default_unit is set and the value has a compatible unit, convert to it.
    - If the value is a bare number and default_unit is set, append the unit.
    - If parsing/conversion fails, return the original trimmed string.
    """
    if value is None:
        return value
    original = str(value).strip()
    if not original:
        return original

    parsed = parse_measure(original)
    if parsed is None:
        return original

    number, unit = parsed
    target = canonicalize_unit(default_unit)
    display_unit = str(default_unit).strip() if default_unit and str(default_unit).strip() else target

    if target:
        converted = convert_measure(number, unit, target)
        if converted is None:
            # Incompatible or unknown unit: keep as-is (still format if we can).
            if unit:
                return format_measure(number, unit)
            return original
        return format_measure(converted, display_unit)

    if unit:
        return format_measure(number, unit)
    return format_measure_number(number)
