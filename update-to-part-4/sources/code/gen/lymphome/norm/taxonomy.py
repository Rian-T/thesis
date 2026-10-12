"""
Taxonomie des 89 champs eCRF lymphome → familles de têtes de normalisation.

Familles :
  CAT  : catégoriel nominal (enum fini)      → tête classif (similarité type-cond.)
  ORD  : ordinal borné (score)               → tête ordinale (CORAL)
  NUM  : numérique continu (+ unité canon)    → tête régression
  DATE : date                                → normalisation ISO (parse déterministe + head offset)
  TXT  : texte libre                         → pas de tête (span brut)

Pour chaque champ CAT on donne les classes canoniques + synonymes (matching lowercase).
Pour NUM : unité canon + bornes physiologiques (garde-fou), + facteur si conversion.
Pour ORD : (lo, hi).

`normalize_target(field, raw)` -> valeur canon (str/float/int) ou None si non parsable.
C'est la §3.2 du DESIGN : cibles dérivées de annotation[field].value (Stage-3) — semi-normalisé.
"""
import re
import unicodedata

# ------------------------------------------------------------------ helpers
def _strip(s):
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()

def _num(s):
    """Premier nombre (gère virgule décimale FR)."""
    if s is None:
        return None
    m = re.search(r"[-+]?\d+(?:[.,]\d+)?", str(s))
    return float(m.group().replace(",", ".")) if m else None

_ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5}

def _roman_or_int(s):
    t = _strip(s)
    # stade Ann Arbor: chiffre romain en tête, éventuellement suffixé A/B (ex. "IIIB")
    m = re.search(r"stade\s+(iv|iii|ii|i|v)", t) or re.match(r"(iv|iii|ii|i|v)(?![a-z])", t) \
        or re.match(r"(iv|iii|ii|i|v)[ab]?\b", t)
    if m:
        return _ROMAN[m.group(1)]
    n = _num(t)
    return int(round(n)) if n is not None else None

_YESNO = {"oui": ["oui", "yes", "present", "positi", "vrai", "true", "connu", "actif tabag", "tabagisme"],
          "non": ["non", "no", "absent", "negati", "faux", "false", "jamais", "sans", "aucun", "nie"]}


# ------------------------------------------------------------------ FIELD_SPEC
# family, plus specifics. CAT: {"classes": {canon: [synonymes...]}}
# NUM: {"unit","bounds":(lo,hi),"conv":{pattern:factor}}   ORD:{"range":(lo,hi)}
Y = {"classes": {"oui": _YESNO["oui"], "non": _YESNO["non"]}}
FISH = {"classes": {"réarrangement": ["rearrang", "rearrangement", "remanie", "positi"],
                    "pas de réarrangement": ["pas de rearrang", "absence", "non rearrang", "negati", "normal"]}}
POSNEG = {"classes": {"positif": ["positi", "exprime", "surexprim"], "négatif": ["negati", "non exprime"]}}
RESP = {"classes": {"réponse complète": ["complete", "rc", "complet"],
                    "réponse partielle": ["partielle", "rp", "partiel"],
                    "progression": ["progress", "pd"],
                    "stable": ["stable", "sd"]}}
METHOD = {"classes": {"radiologique": ["radiolog", "tep", "scanner", "imagerie", "pet"],
                      "biologique": ["biolog", "sang", "ldh"],
                      "clinique": ["clinique", "examen"]}}
_TTT_LIST = ["R-miniCHOP", "R-CHOP", "G-CHOP", "R-CHVP", "RDHAOX", "R-GEMOX", "R-ICE",
             "R-DHAP", "R-DHAOX", "R-ESHAP", "R-Benda", "Pola-BR", "R-CEOP", "CEOP",
             "R-CVP", "R-Bendamustine", "Bendamustine", "CHOP", "ABVD", "Beacopp",
             "BEACOPP", "DHAP", "ICE", "GEMOX", "ESHAP", "IGEV", "MAT", "CAR-T",
             "Gazyva", "Obinutuzumab", "Ibrutinib", "autre"]
# ordre = du plus spécifique au moins spécifique (R-CHOP avant CHOP) pour le matching
TTT = {"classes": {c: [_strip(c)] for c in _TTT_LIST}, "fallback": "autre"}

FIELD_SPEC = {
    # ---- démographie
    "demography_birth_date": {"family": "DATE"},
    "demography_sexe": {"family": "CAT", "classes": {"homme": ["homme", "masculin", "h", "m", "patient", "il "],
                                                     "femme": ["femme", "feminin", "f", "patiente", "elle "]}},
    "demography_marital_status": {"family": "CAT", "classes": {
        "marié": ["marie", "mariee", "epoux", "epouse", "conjoint"],
        "en couple": ["couple", "partenaire", "concubin", "pacs"],
        "célibataire": ["celibataire"],
        "divorcé": ["divorce", "separe"],
        "veuf": ["veuf", "veuve"]}},
    "demography_living_environment": {"family": "CAT", "classes": {
        "rural": ["rural", "campagne", "village"],
        "urbain": ["urbain", "ville", "citadin"],
        "semi-urbain": ["semi", "peri", "banlieue"]}},
    "demography_professional_status": {"family": "CAT", "classes": {
        "actif": ["actif", "emploi", "travaille", "salarie", "activite"],
        "retraité": ["retrait"],
        "étudiant": ["etudiant"],
        "sans emploi": ["sans emploi", "chomage", "sans statut", "sans profession"],
        "invalidité": ["invalid", "handicap"]}},
    "demography_professional_category": {"family": "TXT"},
    # ---- diagnostic / histo
    "history_date_of_diagnosis_of_lymphoma": {"family": "DATE"},
    "history_age_at_diagnosis": {"family": "NUM", "unit": "ans", "bounds": (0, 120)},
    "history_disease_diagnosis": {"family": "CAT", "classes": {
        "LBDGC": ["lbdgc", "diffus a grandes cellules", "dlbcl", "grandes cellules b"],
        "LH": ["hodgkin", "lh "],
        "LF": ["folliculaire", "lf "],
        "T": ["lymphome t", " t ", "cellules t"],
        "autre-B": ["manteau", "marginale", "burkitt", "waldenstrom", "malt", "zone marginale"],
        "PCNSL": ["cerebral", "systeme nerveux", "pcnsl", "cns"],
        "autre": ["autre"]}},
    "history_disease_subtype": {"family": "TXT"},
    "history_tumor_origin": {"family": "CAT", "classes": {
        "ganglionnaire": ["ganglion", "nodal", "ganglionnaire"],
        "extra-ganglionnaire": ["extra", "non ganglion", "extraganglion"]}},
    "history_morphological_variant": {"family": "TXT"},
    "history_coo_test": {"family": "CAT", "classes": {
        "GC": ["gc", "germinal", "gcb"], "NGC": ["ngc", "non germinal", "abc", "non-gc"],
        "indéterminé": ["indetermine", "non conclu", "non determine"]}},
    "history_myc_fish": {"family": "CAT", **FISH},
    "history_bcl2_fish": {"family": "CAT", **FISH},
    "history_bcl6_fish": {"family": "CAT", **FISH},
    "history_myc_ihc": {"family": "CAT", **POSNEG},
    "history_myc_ihc_raw": {"family": "NUM", "unit": "%", "bounds": (0, 100)},
    "history_bcl2_ihc": {"family": "CAT", **POSNEG},
    "history_bcl2_ihc_raw": {"family": "NUM", "unit": "%", "bounds": (0, 100)},
    "history_bcl6_ihc": {"family": "CAT", **POSNEG},
    "history_bcl6_ihc_raw": {"family": "NUM", "unit": "%", "bounds": (0, 100)},
    "history_ngs_status": {"family": "CAT", "classes": {
        "réalisé": ["realise", "fait", "effectue", "disponible"],
        "non réalisé": ["non realise", "pas realise", "non fait", "non disponible", "absent"]}},
    "history_transformation_prior_indolent_lymphoid_malignancy": {"family": "CAT", **Y},
    "history_weight_au_diagnostic": {"family": "NUM", "unit": "kg", "bounds": (20, 250)},
    "history_height_au_diagnostic": {"family": "NUM", "unit": "cm", "bounds": (100, 220), "conv_m": True},
    "history_oms_score_au_diagnostic": {"family": "ORD", "range": (0, 5)},
    "history_symptom_b_at_diagnosis": {"family": "CAT", **Y},
    "history_ann_arbor_score_at_diagnosis": {"family": "ORD", "range": (1, 4), "roman": True},
    "history_extranodalinv_n_at_diagnosis": {"family": "NUM", "unit": "n", "bounds": (0, 20)},
    "history_ipi_extranodinv_at_diagnosis": {"family": "NUM", "unit": "n", "bounds": (0, 10)},
    "history_age_adjusted_ipi_au_diagnostic": {"family": "ORD", "range": (0, 3)},
    "history_ipi_score_at_diagnosis": {"family": "ORD", "range": (0, 5)},
    "history_flipi_score_at_diagnosis": {"family": "ORD", "range": (0, 5)},
    "history_gelf_score_at_diagnosis": {"family": "NUM", "unit": "n", "bounds": (0, 10)},
    "history_eortc_score_at_diagnosis": {"family": "NUM", "unit": "n", "bounds": (0, 10)},
    # LDH souvent en ratio ×LSN ("3.1") ou en U/L ("450") -> bornes larges pour capter les deux
    "history_ldh_blood_levels_at_diagnosis": {"family": "NUM", "unit": "UI/L|xLSN", "bounds": (0.3, 8000)},
    # ---- antécédents
    "antecedents_smoking_status": {"family": "CAT", **Y},
    "antecedents_alcohol_status": {"family": "CAT", **Y},
    "antecedents_cancer": {"family": "TXT"},
    "antecedents_other": {"family": "TXT"},
    "antecedents_immunosuppression_treatment": {"family": "CAT", **Y},
    "antecedents_surgery": {"family": "TXT"},
    # ---- 1re ligne
    "first_line_oms_score": {"family": "ORD", "range": (0, 5)},
    "first_line_treatment": {"family": "CAT", **TTT},
    "first_line_treatment_cycles_n": {"family": "NUM", "unit": "n", "bounds": (0, 12)},
    "first_line_radiation": {"family": "CAT", **Y},
    "first_line_start_date_of_treatment": {"family": "DATE"},
    "first_line_end_date_of_treatment": {"family": "DATE"},
    "first_line_transplant_therapy_after_treatment": {"family": "CAT", **Y},
    "first_line_date_of_transplant_therapy_after_treatment": {"family": "DATE"},
    "first_line_date_of_response_assessment_to_treatment": {"family": "DATE"},
    "first_line_response_assessment_to_treatment": {"family": "CAT", **RESP},
    "first_line_method_of_response_assessment_to_treatment": {"family": "CAT", **METHOD},
    "first_line_date_of_progression_or_relapse": {"family": "DATE"},
    "first_line_adverse_effects_presence": {"family": "CAT", **Y},
    "first_line_adverse_effects_description": {"family": "TXT"},
    "first_line_grade_ctcae_treatment": {"family": "ORD", "range": (0, 5)},
    # ---- 2e ligne
    "second_line_oms_score": {"family": "ORD", "range": (0, 5)},
    "second_line_treatment": {"family": "CAT", **TTT},
    "second_line_treatment_cycles_n": {"family": "NUM", "unit": "n", "bounds": (0, 12)},
    "second_line_radiation": {"family": "CAT", **Y},
    "second_line_start_date_of_treatment": {"family": "DATE"},
    "second_line_end_date_of_treatment": {"family": "DATE"},
    "second_line_transplant_therapy_after_treatment": {"family": "CAT", **Y},
    "second_line_date_of_transplant_therapy_after_treatment": {"family": "DATE"},
    "second_line_date_of_response_assessment_to_treatment": {"family": "DATE"},
    "second_line_response_assessment_to_treatment": {"family": "CAT", "classes": {
        **RESP["classes"], "NA": ["na", "non applicable", "non evalue"]}},
    "second_line_method_of_response_assessment_to_treatment": {"family": "CAT", **METHOD},
    "second_line_date_of_progression_or_relapse": {"family": "DATE"},
    # ---- autres lignes
    "other_lines_total_number_of_treatment_lines": {"family": "NUM", "unit": "n", "bounds": (0, 12)},
    "other_lines_oms_score_on_all_other_treatment_lines": {"family": "ORD", "range": (0, 5)},
    # ---- imagerie
    "imaging_tepscan_1st_rechute_realised": {"family": "CAT", **Y},
    "imaging_date_of_tepscan_1st_rechute": {"family": "DATE"},
    "imaging_tepscan_or_before_next_line_realised": {"family": "CAT", **Y},
    "imaging_date_of_tepscan_2nd_line_or_before_next_line": {"family": "DATE"},
    "imaging_tepscan_new_progression_realised": {"family": "CAT", **Y},
    "imaging_date_of_tepscan_new_progression": {"family": "DATE"},
    "imaging_suvmax": {"family": "NUM", "unit": "SUV", "bounds": (0, 80)},
    "imaging_dmax": {"family": "NUM", "unit": "mm", "bounds": (0, 500)},
    "imaging_score_deauville_or_lugano": {"family": "ORD", "range": (1, 5)},
    "imaging_extra_ganglionary_sites": {"family": "TXT"},
    "imaging_number_of_affected_organs": {"family": "NUM", "unit": "n", "bounds": (0, 20)},
    "imaging_largest_tumor_size": {"family": "NUM", "unit": "mm", "bounds": (0, 400)},
    # ---- dernières nouvelles
    "news_date_of_last_visit": {"family": "DATE"},
    "news_date_of_last_news": {"family": "DATE"},
    "news_vital_status_at_last_news": {"family": "CAT", "classes": {
        "vivant": ["vivant", "en vie", "vivante"], "décédé": ["decede", "deces", "mort", "decedee"]}},
    "news_date_of_death": {"family": "DATE"},
    "news_cause_of_death": {"family": "CAT", "classes": {
        "lié au lymphome": ["lie au lymphome", "lymphome", "progression", "maladie"],
        "non lié au lymphome": ["non lie", "autre cause", "intercurrent", "toxicite"]}},
}

FIELDS = list(FIELD_SPEC.keys())
FAMILIES = ("CAT", "ORD", "NUM", "DATE", "TXT")
BY_FAMILY = {fam: [f for f, s in FIELD_SPEC.items() if s["family"] == fam] for fam in FAMILIES}


# ------------------------------------------------------------------ dates
def normalize_date(s):
    """Extrait YYYY-MM-DD ou YYYY-MM depuis un texte libre FR."""
    if not s:
        return None
    t = str(s)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", t)
    if m:
        return m.group(0)
    m = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", t)
    if m:
        d, mo, y = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    MOIS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
            "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}
    tt = _strip(t)
    m = re.search(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", tt)
    if m and m.group(2) in MOIS:
        return f"{m.group(3)}-{MOIS[m.group(2)]:02d}-{int(m.group(1)):02d}"
    m = re.search(r"([a-z]+)\s+(\d{4})", tt)
    if m and m.group(1) in MOIS:
        return f"{m.group(2)}-{MOIS[m.group(1)]:02d}"
    m = re.search(r"\b(\d{4})\b", t)
    if m:
        return m.group(1)
    return None


# ------------------------------------------------------------------ cat matching
def match_cat(field, raw):
    spec = FIELD_SPEC[field]
    t = " " + _strip(raw) + " "
    best = None
    for canon, syns in spec["classes"].items():
        for syn in syns:
            if syn and syn in t:
                # priorité au synonyme le plus long trouvé
                if best is None or len(syn) > best[1]:
                    best = (canon, len(syn))
    if best:
        return best[0]
    # fallback (ex. protocole de traitement hors vocab -> "autre") si valeur non vide
    if spec.get("fallback") and _strip(raw):
        return spec["fallback"]
    return None


# ------------------------------------------------------------------ API cible
def normalize_target(field, raw):
    """Valeur canon depuis une valeur brute (annotation.value ou span text)."""
    spec = FIELD_SPEC.get(field)
    if spec is None or raw is None or str(raw).strip() == "":
        return None
    fam = spec["family"]
    if fam == "TXT":
        return str(raw).strip()
    if fam == "DATE":
        return normalize_date(raw)
    if fam == "CAT":
        return match_cat(field, raw)
    if fam == "ORD":
        v = _roman_or_int(raw) if spec.get("roman") else (_num(raw) and int(round(_num(raw))))
        if v is None:
            return None
        lo, hi = spec["range"]
        return v if lo <= v <= hi else None
    if fam == "NUM":
        v = _num(raw)
        if v is None:
            return None
        if spec.get("conv_m") and v < 3:      # taille donnée en mètres -> cm
            v *= 100
        lo, hi = spec["bounds"]
        return round(v, 3) if lo <= v <= hi else None
    return None


if __name__ == "__main__":
    from collections import Counter
    c = Counter(s["family"] for s in FIELD_SPEC.values())
    print("N champs:", len(FIELD_SPEC), "| familles:", dict(c))
    # smoke sur quelques cibles
    tests = [("demography_sexe", "patiente"), ("history_weight_au_diagnostic", "Poids : 58 kg"),
             ("history_height_au_diagnostic", "1,75 m"), ("history_oms_score_au_diagnostic", "OMS 1"),
             ("history_ann_arbor_score_at_diagnosis", "IIIB"), ("history_myc_fish", "réarrangement de MYC"),
             ("first_line_treatment", "R-CHOP x8"), ("news_date_of_death", "décédé le 3 mars 2020"),
             ("first_line_response_assessment_to_treatment", "réponse complète"),
             ("imaging_suvmax", "SUVmax 18.7"), ("news_vital_status_at_last_news", "patient vivant")]
    for f, r in tests:
        print(f"  {f:45s} {r!r:35s} -> {normalize_target(f, r)!r}")
