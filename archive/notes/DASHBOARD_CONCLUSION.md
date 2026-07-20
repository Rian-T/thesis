# DASHBOARD — conclusion + petit fix (pour moi, aucune convention)

but global : (1) petit fix provenance cas cliniques ; (2) écrire les 3 chapitres de la conclusion.
process imposé par Rian : SUPERVISION (narratif, contexte, comment dire) = sous-agents **fable** ;
EXÉCUTION (concret : plots, intégration, compile) = sous-agents **opus** ; paragraphes durs = **fable** les écrit.
commencer par des **bullets** avant les paragraphes. TOUT sous-agent lit d'abord `guidelines/` en entier.

---

## TACHE 1 — petit fix provenance (MOI, minimal, PAS le coeur) ✅ fait ci-dessous

vérité (Rian) : les cas cliniques seeds des lymphomes synthétiques NE viennent PAS de PMC-Patients.
ils viennent des **2 M de cas cliniques** extraits par Biomed-Enriched (Partie 2, `\Cref{chap:quality}`) —
c'est le lien logique parfait P2→P3 (« la data cachée trouvée en partie 2 »).
- dataset publié : `rntc/open-clinical-cases-pubmed` (456 481 cas, splits en / fr_translated).
- annotation lymphome/non-lymphome par **Qwen3-Next-80B-A3B** (même modèle que l'extraction Biomed-Enriched ch2/ch3).
- ~400 000 docs haute qualité passés en inférence.
fichiers à toucher (minimal) : `sources/part_3/chapter9/article.tex` (lignes 83, 99-100, 153, 183, 194)
+ `sources/part_3/figures/fig04_wavefront.tex:22` (label "PMC-Patients").
→ remplacer par cas cliniques Biomed-Enriched + `\Cref{chap:quality}` ; retirer citation `zhao_pmcpatients_2023` si plus utilisée.
garder 2,050 records générés, 89 champs, etc.

---

## TACHE 2 — conclusion (3 chapitres). fichier : `sources/conclusion.tex`

épigraphe = Sutton, *Bitter Lesson* ("success tinged with bitterness") → colle au thème amer.

### Ch1 `What Holds Together` (sec:conclusion-holds-together) — actuellement bullets TODO
thème : montrer que TOUT se recoupe + **efficacité énergétique** (fil rouge anti-redondance).
argument (sans répéter les chapitres) :
- une seule route : corpus public → encodeur → CLM → texte ontologique → extraction.
- Biomed-Enriched a servi 2 fois : (a) entraîner des modèles avec 1/3 des tokens ; (b) surfacer les cas
  cliniques cachés → réutilisés pour générer les lymphomes synthétiques d'éval (data manquante). CONVERGENCE.
- cohorte lymphome en rechute = point de convergence.
- FIL ROUGE ÉNERGIE : plein d'approches réduisent l'énergie →
  * Biomed-Enriched : perf du corpus complet avec **1/3 des tokens** (recette clinique 2.5× moins).
  * CamemBERT-bio (CLM/continual pretraining) : **78 GPU-h, 0.80 kg CO2** vs DrBERT **2 560 GPU-h, 26.11 kg (32×)**,
    AliBERT **960 GPU-h, 8.16 kg (10×)**. France 34 g CO2/kWh.
  * MC-bio-gliner (GLiNER, 150M) ≈ perf d'un LLM génératif **27× plus gros** (0.634 vs Qwen3.5-4B 0.658).
- limite honnête : pas encore déployable ; mais texte public + données générées vont loin.
→ **PLOTS énergie à créer** (opus) : (a) barplot GPU-h/CO2 DrBERT vs AliBERT vs CamemBERT-bio ;
  (b) barplot params LLM vs MC-bio-gliner (27×) — attention peut-être déjà couvert par money_params fig18 ;
  décider : 1 plot énergie neuf suffit probablement (CO2 training). placer 1 seul plot, pas 2 côte à côte.
SUPERVISION = fable (narratif + bullets→prose). data ok ci-dessus.

### Ch2 `A New Problem` (sec:conclusion-evaluation) — TABIB déjà écrit, MANQUE transition
problème actuel : narrativement ça speedrun, ça tombe direct sur TABIB sans transition.
à AJOUTER AVANT TABIB (fable écrit, c'est un paragraphe dur) :
- 1re sous-partie légèrement **amère** (ton scientifique, pas larmoyant) : on a développé plein de méthodes
  efficientes/sobres, mais **ce n'est pas là que va le champ**. hôpitaux achètent des GPU, adoptent de gros
  modèles/agents. les petits modèles efficients ne sont pas la trajectoire réelle. → CHERCHER 1 source
  (acquisition GPU hôpitaux / adoption LLM cliniques) pour appuyer. sinon placeholder \citep{}.
- transition vers TABIB : les **décodeurs sont instables** (vs encodeurs) ; leur **sécurité/comportement est
  sous-évalué** par le QA factuel → d'où TABIB. belle transition, pas d'enchaînement brutal.
- garder TOUT le corps TABIB existant (7 protocoles, tables, figures publications/evalllm-2026/*.pdf).
SUPERVISION = fable. la 1re occurrence de TABIB doit suivre la transition, pas la précéder.

### Ch3 `Where Medical AI Is Going` (sec:conclusion-field-direction) — bullets TODO
paragraphe **ouverture / prospectif** (dernier mot de la thèse) :
- ça va encore plus loin : **LLM agentiques** déployés dans les hôpitaux → nouveaux problèmes.
- « LLMs often know when they are being evaluated » → le QA ne suffit plus.
- besoin d'**environnements d'évaluation** qui imitent l'hôpital, évaluent des tâches réelles au plus
  proche du déploiement. le champ n'est pas prêt ; c'est la direction.
- CHERCHER source : "LLMs know when being evaluated" / eval awareness / agentic clinical eval.
SUPERVISION = fable. ton = ouverture, pas bilan.

---

## PLAN D'EXÉCUTION
1. [x] tache 1 (moi) — PMC-Patients -> open clinical cases (Biomed-Enriched), plot fig06 rebuild ok.
2. fable (background) : [x] ch1 (reçu, sauvé scratchpad/ccl_ch1.tex) ; [ ] ch2 (af059b7ef98756eb0) ; [ ] ch3 (ab9f27f21201c77a4).
3. [x] plot énergie : plots/part_3/conclusion_energy.py -> output/conclusion_energy.pdf (32x visible, lime vs peach). fig:conclusion-energy.
4. [x] 3 chapitres intégrés dans conclusion.tex (ch1 prose+fig ; ch2 nouvelle intro avant TABIB, TABIB gardé ; ch3 ouverture agentique).
5. [x] compile clean (239 p, 0 undefined) + render-check ch1 p169-170 (fig 19.1 ok, 32x visible), ch2 p171, ch3 p179 — tous OK.
6. [x] checkbib : 5 refs VERIFIED. commits 90df3f6 (petit fix) + 2393938 (conclusion). NON PUSHÉ (attente signal Rian).

## PASSE DE PEAUFINAGE (en cours) — fable, retour edits old->new à vetter
- ch19 (a155d94504dde42da) ; ch20 intro (a3cdcac8ad4851c6f) ; ch21 (a6a691f9e040a5576).
- vetting : préserver TOUS les chiffres/refs ; refuser tout edit qui pad ou introduit du slop ; appliquer, compile, render-check, commit.
- TABIB body = marques « à polir » préexistantes (Rian) ; hors périmètre fable pour l'instant (dense/numérique). éventuellement passe prose-seule vettée après.

## VAGUE Ch21 AGENTIC (en cours) — tabib agentique dans §21.3
- source : /Users/rtouchen/tabib/ (docs PHILOSOPHY/PAPER_NIGHT/LIMITS lus). C'est un ENV d'éval agentique (≠ TABIB ch20 = perturbation de questions). Naming : "agentic extension of TABIB", PRÉLIMINAIRE.
- FINDING clé : même modèle, même savoir, même artefact forgé → 0% actes non-sûrs en chat vs ~25% (5/20) en agentique sous pression ; savoir constant (contrôle sans artefact = 0% partout) ; vérité poussée ne protège pas (~20% prescrivent contre le verdict lu) ; mécanisme = déférence sous pression à l'autorité forgée. Caveats : 1 modèle, 1 scénario, N=20, IC larges.
- postulat de départ = needham2025evalaware (déjà cité §21.2). garder AgentClinic/tau-bench.
- SCHÉMA fait + vérifié (standalone) : sources/part_3/figures/fig_agentic_env.tex (label fig:conclusion-agentic-env). grammaire ok (agent lavande, forged pêche, act lime, truth/EHR neutre, chokepoint note).
- §21.3 actuel dit "None of this infrastructure exists yet" → RÉVISER (on a un prototype).
- process : fable brainstorm (a998c816fd834d2af, relancé après 529) + fable écriture (à relancer, a échoué 529) ; sinon écriture directe. compile NORMAL = `latexmk` (lualatex). ⚠️ ne jamais utiliser `\style` comme commande texte (bug \role/\sub).
- reste : intégrer prose §21.3 + \input schéma ; compile + render-check ; commit.

## FINI (vagues préc.). reste (décisions Rian) :
- gretton_kernel_2012 MISMATCH checkbib = PRÉEXISTANT (ch16 MMD), pas moi.
- sicard2025ddi = désormais non-cité (retiré de ch2 par fable), entrée bib inoffensive.
- corps TABIB garde ses marques reviewrewrite « à polir » (texte du papier, sous review) — inchangé.
- push : attendre signal.

## RÉCONCILIATIONS chiffres (à appliquer)
- MC-bio-gliner publié = 0.640 value-F1 (après field competition), within 0.018 de Qwen3.5-4B 0.658 (PAS 0.634). money fig OURS=0.640. ch1 déjà corrigé.

## NOTES
- structure conclusion.tex : 3 `\chapter` sous `\illustratedpart[Conclusion]`.
- style : pas de em-dash, plain style, 1 phrase/caption, `\Cref{}`, `\section*{Conclusion}` etc.
- reviewrewrite/reviewread = macros de marques de review (togglable). les TODO sont dans `\begin{reviewrewrite}`.
