from pydantic import BaseModel, Field


class Option(BaseModel):
    id: str = Field(description="Identifiant court, stable et indépendant de la position")
    description: str = Field(description="Description discriminante en français")
    probability: float = Field(ge=0.0, le=1.0)


class Decision(BaseModel):
    question_id: str
    type: str = Field(pattern="^(choice|score|noul)$")
    instruction: str
    options: list[Option] = Field(min_length=2, max_length=8)
    hard_gold: str
    evidence: list[str] = Field(min_length=1, max_length=4)


class DecisionAnnotation(BaseModel):
    decisions: list[Decision] = Field(min_length=4, max_length=6)


SYSTEM_PROMPT = """Tu construis des données d'entraînement pour un moteur de décisions biomédicales français.

À partir du texte fourni, produis exactement 5 décisions indépendantes et entièrement soutenues par le texte :
1. deux questions nominales `choice` avec 3 à 6 options plausibles ;
2. une question booléenne `noul` dont la réponse est vraie ;
3. une question booléenne `noul` dont la réponse est fausse ;
4. une question ordinale `score` si un ordre clinique naturel est justifié (sévérité, urgence, certitude, stade). Sinon, une troisième question `choice`.

Règles impératives :
- Pour `noul`, utilise exactement deux options : `false` puis `true`.
- Pour `score`, range les options du niveau le plus faible au plus élevé.
- `hard_gold` est l'identifiant de l'option la plus probable.
- Les probabilités doivent sommer à 1. Elles expriment l'ambiguïté réellement visible dans le texte, sans inventer d'incertitude gratuite.
- Chaque élément de `evidence` doit être une sous-chaîne littérale exacte du texte.
- Les distracteurs doivent être plausibles mais réfutables par le texte.
- Les identifiants d'options ne doivent jamais encoder leur position (`option_1`, `A`, etc. interdits).
- Les cinq questions doivent porter sur des faits différents.
- N'utilise aucune connaissance qui ne soit pas nécessaire pour interpréter le texte.

Réponds uniquement avec le JSON conforme au schéma fourni."""


def build_messages(text: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Texte biomédical :\n\n" + text},
    ]
