"""
Dictionnaire des clés d'annotation rntc/lymphome-synth-v4 → labels FR naturels.

Le dataset annote un parcours lymphome multi-documents avec ~89 champs (eCRF/registre).
Les clés brutes (ex. `history_ann_arbor_score_at_diagnosis`) sont du snake_case anglais ;
pour l'extraction open-vocab (GLiNER2 extract_json) et pour la lisibilité, on les mappe
vers un label FR naturel + une description courte (ce que le modèle/juge « voit »).

Schéma de LABELS : { key: {"label": <nom FR court>, "desc": <description>, "section": <groupe>} }
Les 5 champs `evaluation_*` (méta-qualité de la note) et les champs structurellement vides
(hasenclever, tmtv, tmts) sont EXCLUS des cibles d'extraction (voir DROP).

SECTIONS (pour grouper les sous-schémas d'extraction, docs longs) :
  demographie · diagnostic · biomarqueurs · scores · antecedents
  ligne1 · ligne2 · autres_lignes · imagerie · suivi
"""

# Champs non-extractibles (méta-éval ou toujours vides dans le gold)
DROP = {
    "evaluation_language_quality", "evaluation_medical_consistency",
    "evaluation_completeness_of_the_note", "evaluation_note_synthesis",
    "evaluation_general_appreciation",
    "history_hasenclever_score_at_diagnosis", "imaging_tmtv", "imaging_tmts",
}

LABELS = {
    # ── Démographie ─────────────────────────────────────────────────────────────
    "demography_birth_date": {"label": "date de naissance", "desc": "la date de naissance du patient", "section": "demographie"},
    "demography_sexe": {"label": "sexe", "desc": "le sexe/genre du patient", "section": "demographie"},
    "demography_marital_status": {"label": "statut marital", "desc": "la situation familiale (marié, célibataire, veuf…)", "section": "demographie"},
    "demography_living_environment": {"label": "environnement de vie", "desc": "le cadre de vie (urbain, rural, domicile, institution)", "section": "demographie"},
    "demography_professional_status": {"label": "statut professionnel", "desc": "l'activité professionnelle (actif, retraité, sans emploi)", "section": "demographie"},
    "demography_professional_category": {"label": "catégorie professionnelle", "desc": "le métier ou la catégorie socioprofessionnelle", "section": "demographie"},

    # ── Diagnostic / histologie ─────────────────────────────────────────────────
    "history_date_of_diagnosis_of_lymphoma": {"label": "date du diagnostic", "desc": "la date du diagnostic du lymphome", "section": "diagnostic"},
    "history_age_at_diagnosis": {"label": "âge au diagnostic", "desc": "l'âge du patient au moment du diagnostic", "section": "diagnostic"},
    "history_disease_diagnosis": {"label": "diagnostic du lymphome", "desc": "le diagnostic de lymphome (lignée B, T, Hodgkin…)", "section": "diagnostic"},
    "history_disease_subtype": {"label": "sous-type de lymphome", "desc": "le sous-type histologique précis du lymphome", "section": "diagnostic"},
    "history_tumor_origin": {"label": "site d'origine tumorale", "desc": "le site/organe d'origine de la tumeur (ganglion, site extra-ganglionnaire)", "section": "diagnostic"},
    "history_morphological_variant": {"label": "variant morphologique", "desc": "la description morphologique/cytologique de la prolifération", "section": "diagnostic"},
    "history_transformation_prior_indolent_lymphoid_malignancy": {"label": "transformation d'un lymphome indolent", "desc": "transformation à partir d'une hémopathie lymphoïde indolente antérieure", "section": "diagnostic"},

    # ── Biomarqueurs (FISH / IHC / NGS / COO) ───────────────────────────────────
    "history_coo_test": {"label": "test cellule d'origine (COO)", "desc": "le résultat du test de cellule d'origine (GCB / ABC / non-GCB)", "section": "biomarqueurs"},
    "history_myc_fish": {"label": "FISH MYC", "desc": "le statut du réarrangement MYC en FISH", "section": "biomarqueurs"},
    "history_bcl2_fish": {"label": "FISH BCL2", "desc": "le statut du réarrangement BCL2 en FISH", "section": "biomarqueurs"},
    "history_bcl6_fish": {"label": "FISH BCL6", "desc": "le statut du réarrangement BCL6 en FISH", "section": "biomarqueurs"},
    "history_myc_ihc": {"label": "IHC MYC", "desc": "le pourcentage/statut d'expression de MYC en immunohistochimie", "section": "biomarqueurs"},
    "history_myc_ihc_raw": {"label": "IHC MYC (texte brut)", "desc": "la formulation brute du résultat IHC MYC", "section": "biomarqueurs"},
    "history_bcl2_ihc": {"label": "IHC BCL2", "desc": "le pourcentage/statut d'expression de BCL2 en immunohistochimie", "section": "biomarqueurs"},
    "history_bcl2_ihc_raw": {"label": "IHC BCL2 (texte brut)", "desc": "la formulation brute du résultat IHC BCL2", "section": "biomarqueurs"},
    "history_bcl6_ihc": {"label": "IHC BCL6", "desc": "le pourcentage/statut d'expression de BCL6 en immunohistochimie", "section": "biomarqueurs"},
    "history_bcl6_ihc_raw": {"label": "IHC BCL6 (texte brut)", "desc": "la formulation brute du résultat IHC BCL6", "section": "biomarqueurs"},
    "history_ngs_status": {"label": "statut NGS", "desc": "le résultat du séquençage haut débit (NGS) / mutations identifiées", "section": "biomarqueurs"},

    # ── Scores & biologie au diagnostic ─────────────────────────────────────────
    "history_weight_au_diagnostic": {"label": "poids au diagnostic", "desc": "le poids du patient au diagnostic (kg)", "section": "scores"},
    "history_height_au_diagnostic": {"label": "taille au diagnostic", "desc": "la taille du patient au diagnostic (m)", "section": "scores"},
    "history_oms_score_au_diagnostic": {"label": "score OMS au diagnostic", "desc": "l'indice de performance OMS/ECOG au diagnostic", "section": "scores"},
    "history_symptom_b_at_diagnosis": {"label": "signes B au diagnostic", "desc": "présence de signes B (fièvre, sueurs, amaigrissement) au diagnostic", "section": "scores"},
    "history_ann_arbor_score_at_diagnosis": {"label": "stade Ann Arbor", "desc": "le stade Ann Arbor au diagnostic (I à IV, A/B)", "section": "scores"},
    "history_extranodalinv_n_at_diagnosis": {"label": "nombre de sites extra-ganglionnaires", "desc": "le nombre de localisations extra-ganglionnaires au diagnostic", "section": "scores"},
    "history_ipi_extranodinv_at_diagnosis": {"label": "atteinte extra-ganglionnaire (IPI)", "desc": "l'item atteinte extra-ganglionnaire du score IPI", "section": "scores"},
    "history_age_adjusted_ipi_au_diagnostic": {"label": "IPI ajusté à l'âge (aaIPI)", "desc": "le score IPI ajusté à l'âge", "section": "scores"},
    "history_ipi_score_at_diagnosis": {"label": "score IPI", "desc": "le score pronostique international IPI au diagnostic", "section": "scores"},
    "history_flipi_score_at_diagnosis": {"label": "score FLIPI", "desc": "le score FLIPI (lymphome folliculaire) au diagnostic", "section": "scores"},
    "history_gelf_score_at_diagnosis": {"label": "critères GELF", "desc": "les critères GELF (forte masse tumorale) au diagnostic", "section": "scores"},
    "history_eortc_score_at_diagnosis": {"label": "score EORTC", "desc": "le score pronostique EORTC au diagnostic", "section": "scores"},
    "history_ldh_blood_levels_at_diagnosis": {"label": "taux de LDH au diagnostic", "desc": "le taux sanguin de LDH au diagnostic", "section": "scores"},

    # ── Antécédents ─────────────────────────────────────────────────────────────
    "antecedents_smoking_status": {"label": "statut tabagique", "desc": "la consommation de tabac (fumeur, ex-fumeur, non-fumeur)", "section": "antecedents"},
    "antecedents_alcohol_status": {"label": "statut alcool", "desc": "la consommation d'alcool", "section": "antecedents"},
    "antecedents_cancer": {"label": "antécédent de cancer", "desc": "un antécédent personnel de cancer", "section": "antecedents"},
    "antecedents_other": {"label": "autre antécédent médical", "desc": "tout autre antécédent médical pertinent", "section": "antecedents"},
    "antecedents_immunosuppression_treatment": {"label": "traitement immunosuppresseur", "desc": "un antécédent de traitement immunosuppresseur", "section": "antecedents"},
    "antecedents_surgery": {"label": "antécédent chirurgical", "desc": "un antécédent d'intervention chirurgicale", "section": "antecedents"},

    # ── 1re ligne de traitement ─────────────────────────────────────────────────
    "first_line_oms_score": {"label": "score OMS (1re ligne)", "desc": "l'indice OMS/ECOG au début de la 1re ligne", "section": "ligne1"},
    "first_line_treatment": {"label": "traitement de 1re ligne", "desc": "le protocole de traitement de 1re ligne (ex. R-CHOP)", "section": "ligne1"},
    "first_line_treatment_cycles_n": {"label": "nombre de cycles (1re ligne)", "desc": "le nombre de cycles de la 1re ligne", "section": "ligne1"},
    "first_line_radiation": {"label": "radiothérapie (1re ligne)", "desc": "une radiothérapie en 1re ligne", "section": "ligne1"},
    "first_line_start_date_of_treatment": {"label": "date de début (1re ligne)", "desc": "la date de début de la 1re ligne", "section": "ligne1"},
    "first_line_end_date_of_treatment": {"label": "date de fin (1re ligne)", "desc": "la date de fin de la 1re ligne", "section": "ligne1"},
    "first_line_transplant_therapy_after_treatment": {"label": "greffe après 1re ligne", "desc": "une greffe de cellules souches après la 1re ligne (auto/allo)", "section": "ligne1"},
    "first_line_date_of_transplant_therapy_after_treatment": {"label": "date de greffe (1re ligne)", "desc": "la date de la greffe après 1re ligne", "section": "ligne1"},
    "first_line_date_of_response_assessment_to_treatment": {"label": "date d'évaluation de réponse (1re ligne)", "desc": "la date de l'évaluation de la réponse à la 1re ligne", "section": "ligne1"},
    "first_line_response_assessment_to_treatment": {"label": "réponse au traitement (1re ligne)", "desc": "la réponse à la 1re ligne (RC, RP, progression…)", "section": "ligne1"},
    "first_line_method_of_response_assessment_to_treatment": {"label": "méthode d'évaluation de réponse (1re ligne)", "desc": "la méthode d'évaluation de la réponse (TEP, scanner…)", "section": "ligne1"},
    "first_line_date_of_progression_or_relapse": {"label": "date de progression/rechute (1re ligne)", "desc": "la date de progression ou rechute après 1re ligne", "section": "ligne1"},
    "first_line_adverse_effects_presence": {"label": "présence d'effets indésirables (1re ligne)", "desc": "la présence d'effets indésirables en 1re ligne", "section": "ligne1"},
    "first_line_adverse_effects_description": {"label": "description des effets indésirables (1re ligne)", "desc": "la description des effets indésirables de la 1re ligne", "section": "ligne1"},
    "first_line_grade_ctcae_treatment": {"label": "grade CTCAE (1re ligne)", "desc": "le grade CTCAE de toxicité en 1re ligne", "section": "ligne1"},

    # ── 2e ligne de traitement ──────────────────────────────────────────────────
    "second_line_oms_score": {"label": "score OMS (2e ligne)", "desc": "l'indice OMS/ECOG au début de la 2e ligne", "section": "ligne2"},
    "second_line_treatment": {"label": "traitement de 2e ligne", "desc": "le protocole de traitement de 2e ligne", "section": "ligne2"},
    "second_line_treatment_cycles_n": {"label": "nombre de cycles (2e ligne)", "desc": "le nombre de cycles de la 2e ligne", "section": "ligne2"},
    "second_line_radiation": {"label": "radiothérapie (2e ligne)", "desc": "une radiothérapie en 2e ligne", "section": "ligne2"},
    "second_line_start_date_of_treatment": {"label": "date de début (2e ligne)", "desc": "la date de début de la 2e ligne", "section": "ligne2"},
    "second_line_end_date_of_treatment": {"label": "date de fin (2e ligne)", "desc": "la date de fin de la 2e ligne", "section": "ligne2"},
    "second_line_transplant_therapy_after_treatment": {"label": "greffe après 2e ligne", "desc": "une greffe de cellules souches après la 2e ligne", "section": "ligne2"},
    "second_line_date_of_transplant_therapy_after_treatment": {"label": "date de greffe (2e ligne)", "desc": "la date de la greffe après 2e ligne", "section": "ligne2"},
    "second_line_date_of_response_assessment_to_treatment": {"label": "date d'évaluation de réponse (2e ligne)", "desc": "la date de l'évaluation de la réponse à la 2e ligne", "section": "ligne2"},
    "second_line_response_assessment_to_treatment": {"label": "réponse au traitement (2e ligne)", "desc": "la réponse à la 2e ligne", "section": "ligne2"},
    "second_line_method_of_response_assessment_to_treatment": {"label": "méthode d'évaluation de réponse (2e ligne)", "desc": "la méthode d'évaluation de la réponse en 2e ligne", "section": "ligne2"},
    "second_line_date_of_progression_or_relapse": {"label": "date de progression/rechute (2e ligne)", "desc": "la date de progression ou rechute après 2e ligne", "section": "ligne2"},

    # ── Autres lignes ───────────────────────────────────────────────────────────
    "other_lines_total_number_of_treatment_lines": {"label": "nombre total de lignes de traitement", "desc": "le nombre total de lignes de traitement reçues", "section": "autres_lignes"},
    "other_lines_oms_score_on_all_other_treatment_lines": {"label": "score OMS (autres lignes)", "desc": "l'indice OMS/ECOG aux lignes ultérieures", "section": "autres_lignes"},

    # ── Imagerie ────────────────────────────────────────────────────────────────
    "imaging_tepscan_1st_rechute_realised": {"label": "TEP à la 1re rechute", "desc": "réalisation d'un TEP-scan à la 1re rechute", "section": "imagerie"},
    "imaging_date_of_tepscan_1st_rechute": {"label": "date du TEP (1re rechute)", "desc": "la date du TEP-scan à la 1re rechute", "section": "imagerie"},
    "imaging_tepscan_or_before_next_line_realised": {"label": "TEP avant ligne suivante", "desc": "réalisation d'un TEP-scan avant la ligne suivante", "section": "imagerie"},
    "imaging_date_of_tepscan_2nd_line_or_before_next_line": {"label": "date du TEP (avant ligne suivante)", "desc": "la date du TEP-scan avant la ligne suivante", "section": "imagerie"},
    "imaging_tepscan_new_progression_realised": {"label": "TEP à nouvelle progression", "desc": "réalisation d'un TEP-scan à une nouvelle progression", "section": "imagerie"},
    "imaging_date_of_tepscan_new_progression": {"label": "date du TEP (nouvelle progression)", "desc": "la date du TEP-scan à une nouvelle progression", "section": "imagerie"},
    "imaging_suvmax": {"label": "SUVmax", "desc": "la valeur SUVmax au TEP-scan", "section": "imagerie"},
    "imaging_dmax": {"label": "Dmax", "desc": "la distance Dmax (dispersion tumorale) au TEP", "section": "imagerie"},
    "imaging_score_deauville_or_lugano": {"label": "score de Deauville/Lugano", "desc": "le score de Deauville ou Lugano au TEP", "section": "imagerie"},
    "imaging_extra_ganglionary_sites": {"label": "sites extra-ganglionnaires (imagerie)", "desc": "les localisations extra-ganglionnaires à l'imagerie", "section": "imagerie"},
    "imaging_number_of_affected_organs": {"label": "nombre d'organes atteints", "desc": "le nombre d'organes atteints à l'imagerie", "section": "imagerie"},
    "imaging_largest_tumor_size": {"label": "taille de la plus grosse lésion", "desc": "la taille de la plus grande masse tumorale", "section": "imagerie"},

    # ── Suivi / nouvelles ───────────────────────────────────────────────────────
    "news_date_of_last_visit": {"label": "date de dernière consultation", "desc": "la date de la dernière consultation", "section": "suivi"},
    "news_date_of_last_news": {"label": "date des dernières nouvelles", "desc": "la date des dernières nouvelles du patient", "section": "suivi"},
    "news_vital_status_at_last_news": {"label": "statut vital aux dernières nouvelles", "desc": "le statut vital (vivant/décédé) aux dernières nouvelles", "section": "suivi"},
    "news_date_of_death": {"label": "date de décès", "desc": "la date de décès du patient", "section": "suivi"},
    "news_cause_of_death": {"label": "cause du décès", "desc": "la cause du décès", "section": "suivi"},
}

# Sous-schémas par section (pour des appels extract_json tractables sur docs longs)
SECTIONS = {}
for _k, _v in LABELS.items():
    SECTIONS.setdefault(_v["section"], []).append(_k)

# label FR -> key (pour re-mapper la sortie du modèle vers la clé gold)
LABEL_TO_KEY = {v["label"]: k for k, v in LABELS.items()}


if __name__ == "__main__":
    import json
    print(f"{len(LABELS)} champs extractibles, {len(DROP)} exclus, {len(SECTIONS)} sections")
    for s, ks in SECTIONS.items():
        print(f"  {s:14s} : {len(ks)} champs")
    # dump JSON lisible pour le paper / repro
    out = {k: {"label": v["label"], "desc": v["desc"], "section": v["section"]}
           for k, v in LABELS.items()}
    print(json.dumps(out, ensure_ascii=False, indent=2)[:300])
