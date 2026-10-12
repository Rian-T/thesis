'''
complement rules for extracting entities from text
based on regular expressions
'''

import re
import unicodedata
import logging
from datetime import timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

rules = []


def normalize_span_for_field(field_label, span_text, doc=None):
    """Apply normalization rules to a single span for one form field.

    ``field_label`` should be the human-readable field label (rules match on it).
    Returns a normalized string value, or None if no rule applies.
    """
    if span_text is None:
        return None
    text = str(span_text).strip()
    if not text:
        return None
    label = str(field_label or "").strip()
    for rule in rules:
        value = rule(label, text, doc)
        if value is not None and str(value).strip() != "":
            return str(value)
    return None


def register(rule):
    ''' register a normalization rule '''
    rules.append(rule)
    return rule


MONTHS = [
    'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
]
DAYS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']


def _strip_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )


MONTH_TO_NUM = {_strip_accents(m): i + 1 for i, m in enumerate(MONTHS)}
_MONTH_SPELLINGS = []
for m in MONTHS:
    plain = _strip_accents(m)
    _MONTH_SPELLINGS.append(re.escape(m))
    if plain != m:
        _MONTH_SPELLINGS.append(re.escape(plain))
MONTHS_ALT = '|'.join(_MONTH_SPELLINGS)

MONTHS_RE = re.compile(r'\b(' + MONTHS_ALT + r')\b', re.IGNORECASE)
DAYS_RE = re.compile(r'\b(' + '|'.join(DAYS) + r')\b', re.IGNORECASE)

# Full: 24/07/2026 or 24 Juillet 2026
_DATE_NUMERIC_FULL = re.compile(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})')
_DATE_TEXT_FULL = re.compile(
    rf'(\d{{1,2}})(?:er)?\s+({MONTHS_ALT})\s+(\d{{4}})',
    re.IGNORECASE,
)
# Partial: 07/2026 or Juillet 2026
_DATE_NUMERIC_PARTIAL = re.compile(r'(\d{1,2})[/\-.](\d{4})')
_DATE_TEXT_PARTIAL = re.compile(
    rf'({MONTHS_ALT})\s+(\d{{4}})',
    re.IGNORECASE,
)

_DATE_TEXT_PARTIAL2 = re.compile(
    rf'(\d{{1,2}})\s+({MONTHS_ALT})',
    re.IGNORECASE,
)
_DATE_ISO = re.compile(r'(\d{4})-(\d{2})(?:-(\d{2}))?')


def parse_french_date(value, doc = None):
    '''Parse a French date expression into ISO form.

    Accepts:
      - '24/07/2026', '24-07-2026', '24.07.2026' → '2026-07-24'
      - '07/2026' → '2026-07'
      - '24 Juillet 2026', '24 juillet 2026' → '2026-07-24'
      - 'Juillet 2026' → '2026-07'
      - already-ISO '2026-07-24' / '2026-07' (passed through)

    Returns None if the value cannot be parsed.
    '''
    if not isinstance(value, str) or not value.strip():
        return None

    if m := _DATE_ISO.search(value):
        year, month, day = m.group(1), m.group(2), m.group(3)
        if day:
            return f'{year}-{month}-{day}'
        return f'{year}-{month}-01'

    if m := _DATE_NUMERIC_FULL.search(value):
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31:
            return f'{year:04d}-{month:02d}-{day:02d}'
        return None

    if m := _DATE_TEXT_FULL.search(value):
        day = int(m.group(1))
        month = MONTH_TO_NUM[_strip_accents(m.group(2).lower())]
        year = int(m.group(3))
        if 1 <= day <= 31:
            return f'{year:04d}-{month:02d}-{day:02d}'
        return None

    if m := _DATE_NUMERIC_PARTIAL.search(value):
        month, year = int(m.group(1)), int(m.group(2))
        if 1 <= month <= 12:
            return f'{year:04d}-{month:02d}-01'
        return None

    if m := _DATE_TEXT_PARTIAL2.search(value):
        day = int(m.group(1))
        month = MONTH_TO_NUM[_strip_accents(m.group(2).lower())]
        if 1 <= day <= 31:
            return f'XXXX-{month:02d}-{day:02d}'
        return None

    if m := _DATE_TEXT_PARTIAL.search(value):
        month = MONTH_TO_NUM[_strip_accents(m.group(1).lower())]
        year = int(m.group(2))
        return f'{year:04d}-{month:02d}-01'

    if m := re.search(r'((?:19|20)\d{2})', value):
        return f'{m.group(1)}-01-01'

    if m := re.search(r'(J+?\d+(C\d+)?\w*)', value): 
        # future dates
        date = m.group(1)
        if doc and 'creation_date' in doc['metadata']:
            creation_date = doc['metadata']['creation_date']
            m = re.search(r'J(\d+)', date)
            days = int(m.group(1))
            # add days to creation date
            future_date = date.fromisoformat(creation_date) + timedelta(days=days)
            return future_date.isoformat()
        else:
            return date
    return None

@register
def date(field, value, doc = None):
    ''' normalize a date value '''
    if 'date' in field.lower() or 'année' in field.lower():
        v = parse_french_date(value)
        if not v:
            log.warning(f"<date> Field {field} value {value} failed to parse date")
        return v
    return None


@register
def score(field, value, doc = None):
    ''' normalize a score value '''
    if 'score' in field.lower() or re.search(r'\d\s+\d', field):
        if m := re.search(r'(\d)', value, re.IGNORECASE):
            return m.group(1)
        elif 'arbor' not in field.lower():
            log.warning(f"<score> Field {field} value {value} failed to parse score")
    return None


@register
def ann_arbor(field, value, doc = None):
    ''' normalize a score value '''
    if 'arbor' in field.lower():
        if m := re.search(r'\b(IV|III|II|I)\d?[abcdeABCDE]{0,2}', value):
            return str({'IV': 4, 'III': 3, 'II': 2, 'I': 1}[m.group(1)])
        else:
            log.warning(f"<ann_arbor> Field {field} value {value} failed to parse ann arbor")
    return None


@register
def age(field, value, doc = None):
    ''' normalize an age value '''
    if 'age' in field.lower():
        if m := re.search(r'(\d+)\s+ans', value):
            return m.group(1)
        else:
            log.warning(f"<age> Field {field} value {value} failed to parse age")
    return None


@register
def size(field, value, doc = None):
    ''' normalize a size value '''
    if 'taille' in field.lower():
        if m := re.search(r'(\d+(?:[.,]\d+)?(?:\s*x\s*\d+(?:[.,]\d+)?){0,2}\s+(?:cm|mm|m))', value):
            return m.group(1)
        else:
            log.warning(f"<size> Field {field} value {value} failed to parse size")
    return None


@register
def weight(field, value, doc = None):
    ''' normalize a weight value '''
    if 'poids' in field.lower():
        if m := re.search(r'(\d+(?:[.,]\d+)?\s+(?:kg|g))', value):
            return m.group(1)
        else:
            log.warning(f"<weight> Field {field} value {value} failed to parse weight")
    return None


@register
def gender(field, value, doc = None):
    ''' normalize a gender value '''
    if 'sexe' in field.lower():
        if 'Madame' in value or 'Mme ' in value or 'Mademoiselle' in value or 'patiente' in value.lower() or 'Mlle ' in value:
            return 'femme'
        elif 'femme' in value.lower() or 'féminin' in value.lower():
            return 'femme'
        elif 'Monsieur' in value or 'M. ' in value or 'patient' in value.lower() or 'homme' in value.lower() or 'masculin' in value.lower():
            return 'homme'
        elif 'Mr ' in value:
            return 'homme'
        elif m := re.search(r'sexe\s*:\s+([hfm])', value, re.IGNORECASE):
            v = m.group(1).lower()
            if v == 'h' or v == 'm':
                return 'homme'
            elif v == 'f':
                return 'femme'
            else:
                log.warning(f"<gender> Field {field} value {value} failed to parse gender")
        else:
            log.warning(f"<gender> Field {field} value {value} failed to parse gender")
    return None


@register
def diagnosis(field, value, doc = None):
    ''' normalize a diagnosis value '''
    if 'diagnose' in field.lower():
        if m := re.search(r'\b(LBDGC|LH|LF|MCL|EVB|MALT)\b', value):
            return m.group(1)
        elif re.search(r'DLBCL', value):
            return 'LBDGC'
        elif re.search(r'lymphome.+à\s+grandes\s+cellules', value, re.IGNORECASE):
            return 'LBDGC'
        elif re.search(r'lymphome.+folliculaire', value, re.IGNORECASE):
            return 'LF'
        elif re.search(r'lymphome.+Hodgkin', value, re.IGNORECASE):
            return 'LH'
        else:
            log.warning(f"<diagnosis> Field {field} value {value} failed to parse diagnosis")
    return None


@register
def polarity(field, value, doc = None):
    ''' normalize a polarity value '''
    if 'positif' in field.lower() or 'négatif' in field.lower():
        if 'positif' in value.lower() or 'positive' in value.lower() or '+' in value.lower():
            return 'positif'
        elif 'négatif' in value.lower() or 'négative' in value.lower() or '-' in value.lower():
            return 'négatif'
        elif re.search(r'(non|pas)\s+(exprimée?s?|présente?s?|détectée?s?|réalisée?s?|retrouvée?s?)|absente?s?', value, re.IGNORECASE):
            return 'négatif'
        elif re.search(r"pas\sd'expression|(sans|aucune)\s+expression", value, re.IGNORECASE):
            return 'négatif'
        elif (re.search(r'\b(exprimée?s?|détectée?s?|présente?s?|réalisée?s?|exprime(nt)?)\b', value, re.IGNORECASE)
              or re.search(r'exprime.*fortement', value, re.IGNORECASE)):
            return 'positif'
        elif re.search(r"expression\s+(\d+)", value, re.IGNORECASE):
            return 'positif'
        else:
            log.warning(f"<polarity> Field {field} value {value} failed to parse polarity")
    return None


@register
def COO(field, value, doc = None):
    ''' normalize a COO value '''
    if 'Test COO' in field:
        if re.search(r'non\s+(réalisé|classé|réalisable|applicable|effectué)', value, re.IGNORECASE):
            return 'indéterminé'
        elif 'NGC' in value or re.search(r'non(\s+|-)germinatif', value, re.IGNORECASE):
            return 'NGC'
        elif 'GC' in value or 'germinatif' in value.lower():
            return 'GC'
        else:
            log.warning(f"<COO> Field {field} value {value} failed to parse COO test")
    return None


@register
def treatment(field, value, doc = None):
    ''' normalize a treatment value '''
    if 'Traitement' in field and 'ligne' in field.lower():
        if m := re.search(r'\b(CHOP|mini-?CHOP|R-?CHOP|R-?miniCHOP|G-?CHOP|R-?CHVP|RDHAOX|R-?GEMOX|R-?ICE|R-?HOLOXAN|ABVD|Beacopp|R-?EPOCH)', value, re.IGNORECASE):
            return m.group(1)
        else:
            log.warning(f"<treatment> Field {field} value {value} failed to parse treatment")
    return None


@register
def professional_status(field, value, doc = None):
    ''' normalize a professional status value '''
    if 'Situation professionnelle' in field:
        if re.search(r'\b(actif|active)\b', value):
            return 'actif'
        elif re.search(r'\b(retraitée?|en retraite|à la retraite|ancien)\b', value):
            return 'retraité'
        elif re.search(r'\b(en activité|en activité partielle|à temps partiel)\b', value):
            return 'en activité'
        elif re.search(r'\b(étudiante?)\b', value):
            return 'étudiant'
        elif re.search(r'\b(sans emploi|au foyer|au chômage|sans activité|chômeur)\b', value):
            return 'sans emploi'
        elif not re.search(r'\b(chômage|chômeur|retraité|ancien)\b', value):
            return 'actif'
        else:
            log.warning(f"<professional_status> Field {field} value {value} failed to parse professional status")
    return None


@register
def SUVmax(field, value, doc = None):
    ''' normalize a SUVmax value '''
    if 'SUVmax' in field:
        if m := re.search(r'(\d+(?:[.,]\d+)?)', value):
            return m.group(1)
        else:
            log.warning(f"<SUVmax> Field {field} value {value} failed to parse SUVmax")
    return None


@register
def statut_vital(field, value, doc = None):
    ''' normalize a statut vital value '''
    if 'Statut vital' in field:
        if re.search(r'\b(décès|décédé|décédée|mort)\b', value):
            return 'décédé'
        else:
            return 'vivant'
    return None


CYCLES = {
    'un': 1,
    'deux': 2,
    'trois': 3,
    'quatre': 4,
    'cinq': 5,
    'six': 6,
    'sept': 7,
    'huit': 8,
    'neuf': 9,
    'dix': 10,
}


@register
def cycles(field, value, doc = None):
    if 'Nombre de cycles' in field:
        if m := re.search(r'(\d+|un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix)\s*(cycle|cure)s?', value, re.IGNORECASE):
            v = m.group(1).lower()
            return CYCLES.get(v, v)
        else:
            log.warning(f"<cycles> Field {field} value {value} failed to parse cycles")
    return None


@register
def marital_status(field, value, doc = None):
    ''' normalize a marital status value '''
    if 'Statut marital' in field:
        if re.search(r'\b(veuf|veuve)\b', value, re.IGNORECASE):
            return 'veuf'
        elif re.search(r'\b(mariée?|marié|conjoint|époux|épouse|femme)\b', value, re.IGNORECASE):
            return 'marié'
        elif re.search(r'\b(divorcée?)\b', value, re.IGNORECASE):
            return 'divorcé'
        elif re.search(r'\b(célibataire|célibataire|célibataire)\b', value, re.IGNORECASE):
            return 'célibataire'
        elif re.search(r'\b(en couple|pacsé|pacsée|compagnon|compagne)\b', value, re.IGNORECASE):
            return 'en vie avec un partenaire'
        else:
            log.warning(f"<marital_status> Field {field} value {value} failed to parse marital status")
    return None


@register
def TEP_scan(field, value, doc = None):
    ''' normalize a TEP scan value '''
    if 'TEP scan' in field and 'date' not in field.lower():
        if re.search(r'\b(TEP|TEP-CT|TAP|IRM|PET-CT|TDM)', value):
            if re.search(r'\b(réalisé|effectué|passé|conduit|demandé|demande)\b', value, re.IGNORECASE):
                return 'yes'
            elif parse_french_date(value):
                return 'yes'
            else:
                return 'no'
        else:
            log.warning(f"<TEP_scan> Field {field} value {value} failed to parse TEP scan")
    return None


@register
def raw_value(field, value, doc = None):
    ''' normalize a raw value '''
    if 'RAW' in field:
        if m := re.search(r'(\d+(?:[.,]\d+)?)\s*%', value):
            return m.group(1)
        else:
            log.warning(f"<raw_value> Field {field} value {value} failed to parse raw value")
    return None


@register
def LDH_level(field, value, doc = None):
    ''' normalize a LDH level value '''
    if 'Niveau de LDH' in field:
        if m := re.search(r'(\d+(\s+\d{3})?(?:[.,]\d+)?\s*(?:mg/dL|g/L|U/L|UI/L|UI/mL|IU/L|U/l|u/l|ng/mL|N))', value):
            return m.group(1)
        if m := re.search(r'LDH.*?(normal|(?:fortement|très)?\s*élevé)', value, re.IGNORECASE):
            return 'normal' if m.group(1).lower() == 'normal' else m.group(1)
        else:
            log.warning(f"<LDH_level> Field {field} value {value} failed to parse LDH level")
    return None


@register
def TMTV_score(field, value, doc = None):
    if 'TMTV' in field:
        if m := re.search(r'(\d+(?:[.,]\d+)?)\s*cm³', value):
            return m.group(1)
        else:
            log.warning(f"<TMTV_score> Field {field} value {value} failed to parse TMTV score")
    return None


@register
def Dmax_size(field, value, doc = None):
    if 'Dmax' in field:
        if m := re.search(r'(\d+(?:[.,]\d+)?(?:\s*x\s*\d+(?:[.,]\d+)?){0,2}\s*(?:cm|mm))', value):
            return m.group(1)
        else:
            log.warning(f"<Dmax_size> Field {field} value {value} failed to parse Dmax size")
    return None


@register
def tabac_consumption(field, value, doc = None):
    if 'tabagique' in field.lower():
        if re.search(r'\b(pas\s+de\s+tabac|ne\s+fume\s+pas)\b', value, re.IGNORECASE):
            return 'No'
        elif re.search(r'\b(tabagique|fumeur|fumeuse|tabagisme|occasionnel|modéré|important|\d+\s+paquets)\b', value, re.IGNORECASE):
            return 'Yes'
        else:
            log.warning(f"<tabac_consumption> Field {field} value {value} failed to parse tabac consumption")
    return None


@register
def alcohol_consumption(field, value, doc = None):
    if 'alcoolique' in field.lower():
        if re.search(r"\b(pas\s+d'alcool|ne\s+bois\s+pas|non\s+alcoolique)\b", value, re.IGNORECASE):
            return 'No'
        elif re.search(r'\b(alcoolique|occasionnel|modéré|important)\b', value, re.IGNORECASE):
            return 'Yes'
        else:
            log.warning(f"<alcohol_consumption> Field {field} value {value} failed to parse alcohol consumption")
    return None


@register
def immunosuppression(field, value, doc = None):
    if field == 'Traitement immunosupresseur':
        if re.search(r"\b(non\s+immunosupprimé|non\s+immunosupprimée|pas\s+de\s+traitement\s+immunosuppresseur|pas\s+d'immunosuppression)\b", value, re.IGNORECASE):
            return 'No'
        elif re.search(r'\b(immunosupprimé|immunosupprimée|immunosuppression|traitement\s+immunosuppresseur)\b', value, re.IGNORECASE):
            return 'Yes'
        else:
            log.warning(f"<immunosuppression> Field {field} value {value} failed to parse immunosuppression")
    return None


@register
def categorieprofessionnelle(field, value, doc = None):
    if field == 'Categorie professionnelle':
        value = re.sub(r'(à la retraite|en retraite|retraitée?|au foyer|au chômage)', '', value, re.IGNORECASE)
        value = re.sub(r'ancien(ne)?\s+', '', value, re.IGNORECASE)
        value = re.sub(r'(agé(e)?\s+)?de\s+\d+\s+ans', '', value, re.IGNORECASE)
        return value.strip()
    return None


@register
def response(field, value, doc = None):
    if 'Évaluation de la réponse' in field:
        if re.search(r'\b((rémission|réponse) complète)\b', value, re.IGNORECASE):
            return 'Réponse complète'
        elif re.search(r'\b((rémission|réponse) partielle)\b', value, re.IGNORECASE):
            return 'Réponse partielle'
        else:
            log.warning(f"<response> Field {field} value {value} failed to parse response")
    return None


@register
def response_method(field, value, doc = None):
    if 'Méthode d\'évaluation de la réponse' in field:
        if re.search(r'\b(IRM|TEP|PET-CT|TDM)\b', value, re.IGNORECASE):
            return 'Radiologique'
        else:
            log.warning(f"<response_method> Field {field} value {value} failed to parse response method")
    return None


@register
def deasase_subtype(field, value, doc = None):
    if 'Sous-type de maladie' in field:
        value = re.sub(r'diagnostic(\s+de|:)', '', value, re.IGNORECASE)
        return value.strip()
    return None


@register
def B_symptoms(field, value, doc = None):
    if 'Symptôme B au diagnostic' in field:
        if re.search(r'\b(non\s+présent|absent|((pas|absence)\s+de|aucuns?)\s+(signe|sympt[oô]me)s?)\b', value, re.IGNORECASE):
            return 'no'
        elif re.search(r'\b(présente?s?|présences?|signes?)\b', value, re.IGNORECASE):
            return 'yes'
        else:
            log.warning(f"<B_symptoms> Field {field} value {value} failed to parse B symptoms")
    return None


@register
def undesired_effects(field, value, doc = None):
    if "Survenue d'effets indésirables" in field:
        if re.search(r'\b(absence|(pas\s+de|aucune)\s+complication)', value, re.IGNORECASE):
            return 'no'
        elif re.search(r'\b(présente|présenté|présence|survenue|complication)', value, re.IGNORECASE):
            return 'yes'
        else:
            log.warning(f"<undesired_effects> Field {field} value {value} failed to parse undesired effects")
    return None


@register
def number_of_affected_organs(field, value, doc = None):
    if "Nombre d'organes atteints" in field:
        n = len(re.findall(r'(,|\bet\b)', value, re.IGNORECASE))
        if n:
            return str(n)
        else:
            log.warning(f"<number_of_affected_organs> Field {field} value {value} failed to parse number of affected organs")
    return None


@register
def cancer_antecedents(field, value, doc = None):
    if "Antécédents de cancer" in field:
        value = re.sub(r'antécédents?(\s+de|:)', '', value, re.IGNORECASE)
        return value.strip()
    return None
