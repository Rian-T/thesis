### 469be73 2026-08-13 17:42:33 +0200
Mesure décisive du levier DATE : atteignabilité des cibles par le pool, à M croissant

Si « dans le pool » monte avec M (256/1024/4096), le pool est le goulot et l'élargir est
le levier ; s'il plafonne, le résidu est arithmétique et aucun pool ne le résoudra. Job
918459 sur le base v2.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 7b55509 2026-08-13 17:39:41 +0200
Bras contrastif large : GLiNER entraîné, chaîne V5 lancée pour l'A/B contrastif vs MLM

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 2f652ea 2026-08-13 15:28:45 +0200
Vitesse v2 : 0.99 -> 0.45 s/doc (×2,2) malgré +39 % de texte lu ; 0.30 s en bf16

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### c9f3321 2026-08-13 15:28:06 +0200
Levier DATE chiffré : 57 % du hors-span est déjà DANS le document, l'arithmétique n'en vaut que 25 %

3 971 cibles DATE : 73,7 % dans le span, 14,9 % ailleurs dans le doc, 6,7 % à un décalage
régulier, 4,7 % non dérivables. Le chantier prioritaire n'est donc pas l'arithmétique de
dates mais l'atteignabilité (pool / liage de rôle) : le span annoté n'est souvent pas la
bonne évidence.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 8a9a921 2026-08-13 15:26:45 +0200
Saturation mesurée : seuil 0.5 devenu optimal, +0.055 derrière une décision parfaite, DATE bloquée par 8-10 % de cibles hors pool

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 80cc229 2026-08-13 15:18:36 +0200
Publication des deux variantes : ecrf-v2 (150 M, 0.809) et ecrf-large (395 M, 0.815)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 76ffc8a 2026-08-13 15:12:07 +0200
Le code publié figeait l'encodeur à 768 : la variante large ne se chargeait pas

Attrapé par le contrôle de chargement en isolation avant publication (le même qui avait
rattrapé le tokenizer manquant en juillet) : ecrf-v2 chargeait, ecrf-large levait un
size mismatch sur les 9 poids indexés par d. from_pretrained lit maintenant la dimension
sur assign.pt — le même fichier sert les deux tailles.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 701b495 2026-08-13 15:06:21 +0200
build_upload : trois variantes paramétrées (ecrf / ecrf-v2 / ecrf-large)

Le README, le model_name et le DÉFAUT max_chars du code publié suivent la variante — une
variante entraînée à 24k ne doit pas hériter du défaut 45k. Substitution par marqueurs
@@…@@ et non str.format() : le README contient des accolades littérales (blocs de code).
Tableau comparatif des trois variantes ajouté au README, avec la décomposition honnête
du gain (contexte +0.023 / taille +0.006).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 65e7afb 2026-08-13 15:01:08 +0200
Carré complet sur le TEST : base v2 0.809, large 0.815 — le gain vient du contexte (+0.023), pas de la taille (+0.006)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 74c3abd 2026-08-13 13:36:14 +0200
Base v2 val 0.824 (large 0.829) : l'écart taille se réduit à contexte égal ; MedEmbed-large terminé, bras contrastif lancé

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 708a7a2 2026-08-13 13:35:54 +0200
Bras contrastif large : GLiNER2 v3e sur MedEmbed-large (A/B contrastif vs MLM à 395M)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 2f60407 2026-08-13 10:03:15 +0200
Base v2 (assign re-entraîné à cap 45000) lancé : isole taille vs training long-contexte

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### d8ead7c 2026-08-13 07:06:13 +0200
TEST assign-large : macro 0.815 (+0.020 vs base, +0.029 vs le modèle publié en juillet)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### d37a47b 2026-08-13 06:06:06 +0200
assign-large : val macro 0.829 (+0.022 vs base à cap égal) ; éval test en cours

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### f82c65b 2026-08-13 01:45:21 +0200
V5-LARGE terminé ; têtes assign large lancées (3ep, cap 45000 au training)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 24d74d5 2026-08-13 01:05:46 +0200
MedEmbed-large : smoke PASS, run réel lancé (882137) ; max_steps yaml ignoré depuis toujours (v9 = 3 epochs tronqués walltime)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### cfdf5e5 2026-08-13 00:47:59 +0200
Cap 45 000 confirmé sur le TEST : macro 0.795 (+0.009), DATE +0.041 ; défaut publié mis à jour + push Hub

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### f472a0c 2026-08-13 00:10:25 +0200
Le dossier ModernCamemBERT-bio-large hors onto/ était purgé : pointer la copie fraîche (onto/)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### dc90e0e 2026-08-12 23:56:32 +0200
Sweep cap VALIDATION : 24k→45k = +0.014 macro (DATE +0.041), l'extrapolation RoPE tient

cap 24000 macro 0.7929 / 32000 0.8059 / 45000 0.8066 (100 docs val, seed 0). La
troncature à 24k (39 % des docs) coûtait plus que l'extrapolation au-delà des 8192
positions ne dégrade. Décision prise sur la VAL : cap 45000 (docs entiers) ; éval TEST
de confirmation lancée (job 880410). Audit paires transducteur (fodoca) : NUM 68,5 %
copie / 3,2 % conversion d'unité ; DATE 13,6 % calculées (irréductibles parseur).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 103aa27 2026-08-12 23:54:00 +0200
Lignée eCRF-large : têtes assign à dimension d'encodeur dynamique + lanceur V5-LARGE

train_assign --init paramétrable (défaut V5FROMV3B inchangé), d lu sur
encoder.config.hidden_size ; load_head infère d des poids du checkpoint (768/1024,
rétrocompatible). V5-LARGE (job 880314) part de rntc/gliner2-fr-biomed-v3e-large
restauré du Hub — le disque avait été purgé, tout était sauvegardé sur HF.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 2b4c80a 2026-08-12 23:48:49 +0200
Inférence eCRF ×2,5 (×3,5 avec bf16) : décodage batché compacté, sorties identiques 810/810

Un seul décodage glouton pour les 81 champs, avec compaction des lignes actives (sans
elle le batché était PLUS LENT : tout le lot tournait jusqu'à la séquence la plus
longue). bf16 opt-in sur le seul encodeur (4/810 valeurs changent). Mesuré sur H100,
10 docs test : 1,02 s -> 0,41 s/doc, 0,29 s en bf16. CPU quasi inchangé (l'encodeur
domine). Libellés de champs encodés une fois (cache).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### a5fc65e 2026-08-12 23:46:20 +0200
MedEmbed-large stage 1 : config + sbatch, et reconstruction des paires purgées

La purge SCRATCH a vidé medembed-data/ (parquet RDF stage-1 perdu) : rebuild_pairs.sbatch
regénère depuis les sources survivantes (RDF sur $WORK, textbooks rntc--*) avec
auto-contrôle ~775k. Le large part du ModernCamemBERT-bio-large public (le CPT maison
de v9 n'existe pas en large — caveat documenté dans la config).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### 7cd3e43 2026-08-12 23:25:06 +0200
Audit fodoca date_after sur le silver : 2,04 % de paires en violation, 20,3 % des docs touchés

Contraintes temporelles de fields.yml (fodoca, MIT, vendorées) transposées sur notre
schéma (1st_line→first_line). 641 violations strictes / 31 441 paires ; flags par
(doc, champ) écrits sur SCRATCH pour le nettoyage du train au prochain retrain.
death<last_news (39 %) = divergence sémantique probable, à exclure du filtre ;
tepscan_rechute<début_L1 (25 %) = vraies confusions d'annotateur.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### a68dfe9 2026-08-12 23:22:53 +0200
Budget tokens mesuré : le cap 24 000 sature déjà les 8 192 positions (schéma = 2 280 tokens)

120/410 docs test débordent déjà ; monter le cap = extrapolation RoPE, tranché par
un sweep val 24000/32000/45000 (eval_val_cap.py, job 879515). Plan de campagne dans
WORKPLAN_2026-08-12.md.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### ce289bf 2026-08-04 12:34:09 +0200
Terminologie « span », et la revendication de normalisation est nuancée

« empan » et « fragment » remplacés par « span » partout (README, docstrings,
commentaires) : c'est le terme employé dans le domaine, y compris en français.

CORRECTION DE FOND. Le README affirmait « la sortie est une valeur canonique ET NON
un span ». C'est faux pour une partie des champs : le test donne span="veuve" et
value="veuve", identiques. La normalisation peut laisser la valeur inchangée. La
formulation devient : selon le champ, la valeur coïncide avec le texte du span ou en
diffère.

Même correction dans la docstring de extract() : source="text" décrit désormais une
étape de normalisation « qui peut la laisser inchangée ou la réécrire », au lieu
d'affirmer une réécriture systématique.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 08ad6b6 2026-08-04 12:31:26 +0200
README et docstrings du modèle publié : ton factuel

Retiré les tournures rhétoriques et les emphases : « il ne surligne pas, il produit
la valeur », « sans détour », « la seule à comparer à un seuil », la question
rhétorique « y a-t-il un passage à aller vérifier ? », et le gras dispersé dans le
tableau de résultats et les limites.

Les faits sont inchangés. Les limites sont formulées en clair plutôt qu'en
proclamation : accord avec une annotation humaine non mesuré, 97,4 % des cibles CAT
déjà dans le vocabulaire d'entraînement, aucune évaluation sur un autre corpus, non
validé pour un usage clinique.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 67a6973 2026-08-04 12:15:33 +0200
extract() rend span, offsets et confiances (demande d'Eric), et le nommage est revu

Chaque champ rend désormais :

  {"value": "2017-04-15",              # None si le modèle s'abstient
   "span": "le 8 avril 2017",
   "start": 1247, "end": 1262,         # offsets caractère dans le texte
   "confidence": 0.83,                 # la seule à comparer à un seuil
   "normalization_confidence": 0.97,   # confiance dans la réécriture passage -> valeur
   "source": "text"}                   # ou "vocabulary"

NOMMAGE. Les premiers noms proposés étaient mauvais et le responsable l'a relevé :
- `route: "copy"` était FAUX. Le transducteur ne copie pas, il RÉÉCRIT (« le 8 avril
  2017 » -> 2017-04-15). Qui lit « copy » s'attend à retrouver la valeur telle quelle
  dans le texte. Remplacé par `source: "text" | "vocabulary"`, qui décrit une
  provenance et non une opération interne — et qui reste vrai si le transducteur
  change.
- `confidence_value` était ambigu à côté de `confidence` : rien ne disait laquelle
  sert à seuiller. `normalization_confidence` dit ce qu'elle mesure.

`confidence` garde son nom : c'est le seul nombre qu'on seuille, et le code existant
ne change donc pas de sémantique.

DEUX CHOIX à signaler. (1) `span`, les offsets et les deux confiances décrivent le
MEILLEUR CANDIDAT même quand le modèle s'abstient ; seul `value` suit la décision.
On peut donc ré-appliquer son propre seuil sans relancer le modèle — utile en
pré-remplissage relu par un humain, où l'on privilégie souvent le rappel.
(2) `normalization_confidence` est normalisée PAR CARACTÈRE, sinon une valeur longue
paraîtrait toujours moins sûre qu'une courte et les champs ne seraient pas
comparables.

TEST avec le VRAI paquet PyPI (gliner2 1.3.2, et non notre fork 1.2.3), sur GPU, via
un environnement éphémère `uv` — ce qui valide enfin la compatibilité de version que
je ne pouvais que déduire du code. Démo 14/81 champs, dossier réel de 17 717
caractères 52/81, et `text[start:end] == span` vérifié sur 14/14 puis 52/52.

OBSERVATION à creuser : sur les 66 champs remplis des deux documents, `source` vaut
"text" dans 100 % des cas. La route vocabulaire ne gagne jamais — le transducteur
produit la valeur canonique directement depuis le passage (« Patiente » -> femme,
« résidant à Nancy » -> urbain) et SUBSUME donc le vocabulaire au lieu de le
compléter. Sur deux documents ce n'est pas concluant, mais cela nuance le « +0.252
des options encodées » de ARCHITECTURE.md, mesuré sur une architecture antérieure.
À mesurer sur les 410 avant d'en tirer quoi que ce soit.

ENVIRONNEMENTS CASSÉS, sans rapport avec ce travail : `bge` et `reformulation` ont
un `torch/bin/` VIDE (torch_shm_manager manquant), `tabib` a perdu typing_extensions.
Les .so et .py de torch sont intacts : seuls des fichiers JAMAIS LUS ont disparu,
signature d'une purge automatique de SCRATCH. Correctif côté utilisateur :
`pip install --force-reinstall --no-deps torch==2.9.1`. Je n'ai pas copié le binaire
depuis vllm-019 (torch 2.10.0 contre 2.9.1) : déposer un binaire d'une autre version
dans un env de recherche partagé peut produire un comportement subtilement faux des
semaines plus tard.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 6c512e0 2026-07-30 14:28:44 +0200
README du modèle publié : usage et résultats seulement

Passé de 146 à 51 lignes. Gardé : ce que fait le modèle en deux phrases avec des
exemples concrets, l'installation, l'appel Python, la commande de démo, le tableau
de résultats, le lien vers le jeu d'évaluation, et un paragraphe de limites.

Retiré du README (et conservé dans ARCHITECTURE.md du dépôt) : le détail du
mécanisme, les onze ablations, le diagnostic du taux valeur-dans-span, la
justification du seuil, et le détail du vocabulaire dérivé.

Les limites restent explicites malgré la coupe : gold LLM sur synthétique du même
pipeline, 97,4 % des cibles CAT déjà dans le vocabulaire d'entraînement, aucune
validation hors corpus, non validé cliniquement.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 3760831 2026-07-30 14:12:56 +0200
Publication du modèle eCRF sur le Hub, exécutable avec le seul paquet `gliner2`

https://huggingface.co/rntc/mc-bio-gliner-lymphome-ecrf

`modeling_assign.py` est autonome : il ne dépend que de torch, transformers et
gliner2, et ne demande aucun code du dépôt de recherche. Il contient la tête A, le
transducteur, la construction du pool et l'inférence complète.

    from modeling_assign import ECRFExtractor
    m = ECRFExtractor.from_pretrained("rntc/mc-bio-gliner-lymphome-ecrf")
    m.extract(texte)   # -> {champ: valeur ou None}

COMPATIBILITÉ VÉRIFIÉE avant publication. La seule divergence de notre fork de
GLiNER2 avec fastino-ai/GLiNER2 est un patch de focal loss dans la LOSS
D'ENTRAÎNEMENT, derrière la variable GLINER_FOCAL, désactivé par défaut :
l'inférence est identique à l'upstream. Le code publié n'utilise que
compute_span_rep, count_embed, _encode_batch, processor et encoder.

DEUX BUGS DE PORTABILITÉ ATTRAPÉS AVANT ENVOI :
- le tokenizer manquait dans le paquet (`from_pretrained` fait
  AutoTokenizer.from_pretrained(dossier), donc le chargement aurait échoué chez
  TOUT LE MONDE alors qu'il marchait chez nous) ;
- config.json exposait un chemin absolu de notre cluster
  (/lustre/fsn1/.../medembed-v9/stage1/final). Il n'est pas utilisé au chargement,
  encoder_config et tokenizer étant fournis, mais il était affiché à l'utilisateur.
  Neutralisé en "modernbert-bio-fr-150m".

SMOKE EN ISOLATION avant publication : exécuté DEPUIS le dossier publié, sans le
dépôt de recherche dans sys.path. Import, chargement (81 champs, 52 vocabulaires),
extraction sur la démo, puis sur un vrai dossier de test (50 champs remplis, 43
présents dans le gold). Sorties correctes : « patiente » -> femme, « née le 15 mars
1953 » -> 1953-03-15, « lymphome B diffus à grandes cellules » -> LBDGC, « vit seule
dans un appartement à Nancy » -> urbain.

Le README publie les résultats ET les limites sans détour : gold silver-as-gold d'un
seul annotateur LLM sur documents synthétiques du même pipeline ; 97,4 % des cibles
CAT du test déjà dans le vocabulaire d'entraînement, donc très peu d'information sur
la généralisation aux valeurs nouvelles ; aucune validation hors corpus ; non validé
cliniquement.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### e002354 2026-07-30 00:39:53 +0200
ARCHITECTURE.md : document autosuffisant de l'architecture et de toutes les mesures

12 sections : la tâche et la contrainte de conception · le résultat (0.487 v3b nu ->
0.786, contre 0.582 pour un Qwen-9B finetuné) · l'architecture en ASCII avec le type
d'entrée exact des quatre voies · ce qui produit le résultat, chiffré · le mécanisme
tel qu'il est RÉELLEMENT démontré (la supervision par la valeur reforme l'encodeur,
pas la tête) · le routage dérivé confronté au schéma écrit à la main · les onze
pièces retirées avec qui les défendait · les cinq bugs, dont aucun n'était dans le
modèle · les corrections à des mesures antérieures de ce dépôt · l'ancre de section
et son échec au test de transférabilité · ce qui reste ouvert · les fichiers et les
six écueils à ne pas reproduire.

Contient aussi les réserves : le 0.503 -> 0.527 span-F1 vient d'un run antérieur à
la correction du prompt d'éval ; l'affectation dure n'est mesurée qu'à 1 epoch ; cinq
pièces n'ont jamais été ablatées ; 97,4 % des cibles CAT sont déjà dans le
vocabulaire du train, donc le test ne dit presque rien sur les valeurs nouvelles.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 630af8c 2026-07-29 15:26:37 +0200
BUG D'ÉVAL : on effaçait le schéma sur 29 % des documents au moment de mesurer

`doc_forward` appelait `collate_fn_train` À L'ÉVALUATION comme à l'entraînement.
Cette fonction applique l'échantillonneur d'entraînement de GLiNER2 AU PROMPT.
Mesuré sur ce modèle, 100 tirages du même document :

                          libellés remplacés par   descriptions   prompts
                          « entity 15 », « entity 5 »  supprimées  distincts/100
  collate_fn_train                 29 %                 42 %          59
  collate_fn_inference              0 %                  0 %           1

Or le libellé du champ est la SEULE chose qui porte le schéma dans ce design : les
options de vocabulaire et le conditionnement du transducteur passent par lui. On
l'effaçait sur près d'un tiers des documents de test, au moment même où on mesurait.

Trois conséquences.
1. Tous les chiffres rapportés sont des PLANCHERS, pas le vrai score.
2. `random` (stdlib) n'est pas semé — train_assign ne sème que torch et numpy — donc
   l'évaluation n'était pas reproductible d'un run à l'autre.
3. Les neuf ablations ont été comparées SOUS CE BRUIT. Les grands écarts tiennent
   (det_w 0.670 -> 0.776, transducteur +0.174, options encodées +0.252, taxonomy
   0.630 -> 0.895) : ils sont un ordre de grandeur au-dessus. Mais les verdicts à
   +0.005 (tête de sélection), +0.001 (décision apprise), 0.762 vs 0.767 (⊥
   atomique) et 0.784/0.783/0.780 (seuils) ne sont PAS établis — ils sont seulement
   non contredits. À re-tarifer.

Correctif : `doc_forward(..., train=False)` bascule sur `collate_fn_inference`.
Appliqué aux sept scripts d'évaluation ; la boucle d'entraînement garde train=True,
où la randomisation des libellés est une augmentation légitime (elle apprend au
modèle à lire les descriptions plutôt qu'à mémoriser les libellés).

Trouvé par une relecture critique, pas par moi. Ma première sonde regardait un
attribut inexistant du batch et concluait « aucune variation » — il fallait décoder
`input_ids` pour voir le prompt réel.

AUTRE RÉSULTAT : l'ancre GÉNÉRIQUE (60 caractères précédant le span, aucune
hypothèse de structure) ne donne RIEN — DATE 0.760 contre 0.759 pour la référence,
alors que l'en-tête donne 0.835. Le contexte gauche brut ne remplace pas l'en-tête.
Fenêtre à 150 en cours.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### dbe5015 2026-07-29 15:08:50 +0200
L'ancre de section vaut +0.076 sur DATE, et 82 % du gain est exploitable sans annotation

Trois bras, mêmes paires, même budget, transducteur seul :

  bras                              total    CAT    DATE    NUM    ORD
  1. span seul (référence)          0.8975  0.931  0.759  0.901  0.984
  2. en-tête CALCULÉ ⊕ span         0.9092  0.929  0.835  0.892  0.978
  3. en-tête ANNOTATEUR ⊕ span      0.9145  0.931  0.852  0.896  0.977

Le motif prédit AVANT la mesure est vérifié : DATE monte de +0.076 à +0.093 pendant
que CAT, NUM et ORD BAISSENT de 0.002 à 0.009. Si l'ancre n'apportait que du
contexte général, tout monterait ; elle n'aide que la famille dont 47 % des cibles
vivent dans l'en-tête de leur section, et elle gêne marginalement les autres, pour
qui c'est du bruit ajouté à un span court.

CONTRÔLE DE NON-FUITE : l'ancre calculée depuis la SEULE position du span capte 82 %
du gain de l'ancre de l'annotateur (+0.076 sur +0.093). `source_document` ne contient
donc presque rien que le texte ne donne, et le gain est exploitable à l'inférence.

RÉSERVE, et c'est le responsable du projet qui l'a soulevée : l'en-tête est trouvé
par une regex `^\s*=+[^\n]*=+\s*$`, c'est-à-dire le motif `=== ... ===` produit par
NOTRE générateur. C'est du savoir spécifique au dataset, et le cahier des charges
l'interdit. Une variante entièrement générique est lancée (`--ctxwin N` : les N
caractères précédant le span, aucune hypothèse de structure). Si elle capte
l'essentiel, la regex sort et l'idée « un span hérite du contexte qui le précède »
devient transférable ; sinon il faudra renoncer au gain ou l'assumer explicitement.

Ce contrôle aurait dû être fait AVANT de se réjouir du +0.076.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 3391a9a 2026-07-29 14:52:13 +0200
0.784 sur le test à 3 epochs : +0.297 sur v3b nu, +0.202 sur le Qwen-9B finetuné

  système, même barème, même test 410            macro
  v3b nu                                         0.487
  Qwen3.5-9B finetuné sur les mêmes 1 540 docs   0.582
  pipeline précédent                             0.603
  nous, 1 epoch                                  0.771
  nous, 3 epochs                                 0.784

Le critère posé par le responsable — « si on se prend la tête à ajouter des têtes,
c'est pour aller chercher du +0.2-0.3 » — est atteint : +0.297 sur v3b nu.

DÉTAIL QUI COMPTE : à 3 epochs le seuil brut à 0.5 redevient le MEILLEUR (0.784),
devant le seuil global balayé (0.783), le seuil par famille (0.782) et la règle
fermée F1/2 (0.780). Plus le modèle est bon, moins la calibration compte — sa
confiance se règle d'elle-même. La règle F1/2 gagnait sur les modèles faibles ; elle
devient inutile sur le bon. Une pièce de plus qui s'efface, et cette fois sans
qu'on ait à la retirer.

BUG ATTRAPÉ DANS L'EXPÉRIENCE D'ANCRE : `HDR = re.compile(r"^\\s*=+[^\\n]*=+\\s*$")`
— double échappement dans une chaîne brute, donc la regex cherchait un ANTISLASH
littéral suivi de « s » et ne matchait rien. Les trois bras rendaient des chiffres
BIT-À-BIT IDENTIQUES et l'expérience « tournait » parfaitement : 12 epochs, courbes
propres, convergence à 0.897. Repéré uniquement parce que ep0 loss=2.6202
test=0.3316 était identique au dixième près entre le bras 1 et le bras 2.

Corrigé, plus un garde-fou qui fait ÉCHOUER le run si moins de la moitié des paires
portent une ancre. Une expérience qui ne teste rien doit planter, pas rendre un
chiffre.

C'est le quatrième problème de la session qui n'est PAS dans le modèle : cap de
lecture, pondération de la loss, barème qui mesurait la copie, regex sur-échappée.
Zéro sur quatre pour les hypothèses architecturales.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 536ba8f 2026-07-29 14:39:56 +0200
DESIGN_V2 §11-14 : état final, neuf pièces retirées, ce qui reste ouvert

§11 clôt la question de la tête par le protocole écrit d'avance : partie de beta=0
avec toutes les corrections, elle plafonne à 0.615 en 4 epochs contre 0.776 en une
avec l'ancrage, et beta monte régulièrement — elle cherche le score de détection
sans y parvenir. Ni mal construite ni mal entraînée : le signal n'est pas là.

§12 l'état final (1 epoch test 0.771, 3 epochs val 0.798), §13 les neuf pièces
retirées avec qui les avait défendues — quatre étaient les miennes, dont la loss
auxiliaire que j'avais explicitement défendue contre le design.

§14 ce qui reste : la confiance qui ne sépare pas (borne 0.907 contre 0.771),
l'ancre de section (cible DATE dans son span 6,4 % du temps, dans l'en-tête de son
document source 47,0 %), et la validité externe.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 9673cec 2026-07-29 14:38:55 +0200
La tête ne peut PAS apprendre à pointer : partie de beta=0 elle plafonne à 0.615

Test pré-enregistré « mal construite ou mal entraînée ». La tête reconstruite —
attention champ->pool, features d'ordre, support guidé par la cible, beta INITIALISÉ
À 0 donc sans démarrer sur la solution du détecteur — sur 4 epochs :

  epoch        0       1       2       3
  val macro  0.181   0.317   0.483   0.615
  beta       0.009   0.024   0.039   0.047

Elle plafonne à 0.615 après quatre epochs, contre 0.776 en UNE epoch avec l'ancrage.
Et beta grimpe régulièrement : elle CHERCHE à récupérer le score de détection sans y
parvenir. Ce n'est donc ni un défaut de construction ni un défaut d'entraînement —
le signal n'est pas là. Avec 1 540 documents, apprendre à pointer de zéro n'est pas
possible ; le score natif est irremplaçable.

Cela clôt définitivement la question, et par le protocole qui avait été écrit
d'avance plutôt que par abandon.

RUN 3 EPOCHS de la configuration gagnante (det_w=0, M=256, somme 8+4, alpha gelé) :

  epoch        0       1       2
  val macro  0.773   0.768   0.798
  DATE       0.652   0.662   0.694

+0.022 en entraînant plus longtemps. Meilleur chiffre de la session. Confirmation
test lancée.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 42c9cfe 2026-07-29 06:29:46 +0200
La tête d'affectation disparaît (0.777 sans elle) ; la décision apprise est réfutée

CTX=SONLY : aucun MLP sur la route COPIE, le score de copie EST S.

  tête complète (attention + ordre + MLP)   val 0.776
  ctx=sonly (aucun MLP de copie)            val 0.777

Supprimer entièrement la route COPIE paramétrée ne change rien. Sur les 2.17 M de la
tête, 0.40 M deviennent morts (f_proj, s_proj, o_proj, pos_proj, attention). Il ne
reste AUCUN paramètre pour choisir un span — seulement de quoi noter les options
hors-texte (vocab, summ, nul), convertir (sr_to_h) et deux scalaires.

Ce qui reste du design, en entier :
  softmax sur { S (le score natif) ∪ vocabulaire observé ∪ ⊥ }
  + transducteur caractère partagé par les 89 champs si une copie gagne
  + une seule loss, span latent, supervisée par la valeur
Deux mécanismes.

DÉCISION DE REMPLIR APPRISE : RÉFUTÉE.

  seuil p_v > 0.5                     test 0.763
  seuil p_v > 0.3                     test 0.773
  règle apprise (15 paramètres)       test 0.774
  décision PARFAITE (borne)           test 0.907

+0.001 sur un simple seuil bien placé. Les poids montrent pourquoi : p1 (+0.695),
marge (+0.677), détection (+0.630) et p_null (-0.618) pèsent tous mais sont trop
corrélés pour ajouter à p1 seul. Je l'avais lancée en la présentant comme « le plus
gros gisement mesuré » — elle ne l'était pas.

MAIS la borne a bougé : 0.748 hier soir, 0.907 maintenant. La sélection s'est
tellement améliorée que la valeur en tête est très souvent la bonne. Il reste donc
+0.133 dans la décision, et ni un seuil ni une régression sur ces indices ne les
attrapent : le problème n'est pas la règle de décision, c'est que la CONFIANCE
elle-même ne sépare pas assez le juste du faux. C'est la frontière qui reste.

Huitième pièce qui ne rentre pas dans le design, et la mesure l'a écartée avant
qu'elle n'y entre.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### af14b99 2026-07-29 05:13:59 +0200
Le test de falsification pré-enregistré passe : rappel du pool DATE 0.61 -> 0.832

DESIGN_V2 §5 mesure n°2 : « le rappel du pool DATE doit passer de 0.52 vers ~0.9,
c'est la mesure la plus importante ». À M=256 et top-64 constants :

  ancien pipeline (top-12 par champ)        0.61
  modèle AVEC loss de détection             0.752
  modèle SANS loss de détection             0.832

Et 0.832 dépasse le plafond mesuré à froid (0.821, sur un pool 4x plus grand). Ce
n'est donc plus un meilleur classement : l'encodeur rend ATTEIGNABLES des valeurs
qui ne l'étaient pas. La revendication centrale — « un span d'en-tête que personne
n'a annoté reçoit de la masse » — est vérifiée au sens de la découverte, pas
seulement du réordonnancement.

Ce que j'ai écrit plus tôt (« vérifié au sens du classement, pas de la découverte »)
était vrai sur un modèle entraîné à 97,5 % sur la détection. Ça ne l'est plus.

CONTRÔLE D'ANCRAGE sur le meilleur modèle, et il est définitif :

  rappel@1              det_w=0.1   0.002    0.0
  détection brute         0.727     0.789   0.820
  détection, DATE         0.470     0.586   0.635
  P_A (la tête)          +0.005    +0.010  -0.000
  P_A sans son ancrage    0.234     0.215   0.187

La tête apporte EXACTEMENT ZÉRO au classement du meilleur modèle. Et supprimer la
loss de détection REND LA DÉTECTION MEILLEURE (+0.093 au rang 1, +0.165 sur DATE) —
parce que cette loss apprend à pointer là où l'annotateur a pointé, donc jamais sur
un en-tête, où vivent 55,7 % des cibles DATE.

Conséquence logique testée (job 377439) : `ctx=sonly`, aucun MLP sur la route COPIE,
le score de copie EST S. Si ça égale 0.771, la tête d'affectation disparaît du
design et il ne reste que deux mécanismes — un softmax sur (S ∪ vocabulaire ∪
abstention) et un transducteur partagé.

Éval test détaillée du modèle à det_w=0 : macro 0.763 au seuil 0.5, 0.771 au seuil
calibré. 52,8 % des spans DATE gagnants ne chevauchent aucun span gold. alpha reste
à 0.0000 pour la quatrième fois.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### dea25d6 2026-07-29 04:37:36 +0200
0.771 sur le test : +0.284 sur v3b nu, +0.189 sur un Qwen-9B finetuné

Confirmation test du retrait de la loss de détection (det_w=0) :

  règle de remplissage              val     TEST
  p > 0.5                          0.774   0.768
  global balayé (tau=0.4)          0.776   0.771
  par famille (4 ddl)              0.777   0.770
  F1/2, règle fermée, 0 ddl        0.772   0.769

Trajectoire complète, même barème, même test 410, UNE epoch :

  v3b nu                                     0.487
  Qwen3.5-9B finetuné sur les mêmes données  0.582
  v3b + têtes (pipeline précédent)           0.603
  + transducteur, abstention, seuil déduit   0.673
  + loss rééquilibrée (det_w 0.002)          0.739
  + loss de détection SUPPRIMÉE (det_w 0)    0.771

Ce qui produit le résultat, par ordre :
  retrait/rééquilibrage de la loss de détection   +0.098
  transducteur appris (ablation directe)          +0.174 (mesuré séparément)
  abstention comme option du softmax              +0.071
  seuil déduit de la métrique (F1/2)              +0.015

Ce qui ne produit rien et sort du design, chaque retrait adossé à une mesure :
  tête d'affectation comme sélecteur   +0.010 au rang 1, 0.215 sans son ancrage
  compétition entre champs (alpha)     0.000 après entraînement, trois fois
  pool large (1024 contre 256)         rien à budget de troncature fixe
  loss de détection auxiliaire         NUISIBLE (0.670 à det_w=0.1)
  hypothèse « ⊥ atomique »             0.767 contre 0.771, réfutée
  taxonomy.py (300 lignes)             battu 0.895 contre 0.630

La règle fermée F1/2 tient sur les trois checkpoints successifs, à 0.002 du meilleur
seuil balayé, avec zéro degré de liberté ajusté — pendant que le balayage par
famille surajuste à chaque fois.

Reste en vol : contrôle d'ancrage sur ce checkpoint (la tête tient-elle enfin debout
sans beta*S maintenant que l'encodeur n'est plus entraîné que par la valeur ?),
décision de remplir apprise, et run 3 epochs de la configuration gagnante.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 7cd8582 2026-07-29 04:26:06 +0200
La loss de détection auxiliaire est nuisible : la supprimer donne le meilleur score

Courbe monotone, un seul paramètre balayé, tout le reste identique :

  det_w      0.1     0.02    0.002    0.0
  val macro  0.670   0.673   0.749    0.776

J'avais écrit dans ce fichier qu'il fallait la garder « en auxiliaire à poids
faible » parce que l'annuler ferait dériver span_rep, et j'ai maintenu cette
réserve contre le design d'origine qui proposait de l'annuler. C'est faux. La
supprimer est le meilleur réglage mesuré.

Elle ne pesait pas un peu trop, elle CAPTURAIT l'encodeur : à det_w=0.1 la loss
valait 97,5 % de détection contre 2,5 % d'affectation. Et sa nature explique le
reste — elle entraîne à pointer LÀ OÙ L'ANNOTATEUR A POINTÉ, donc jamais sur un
en-tête de section, où vivent 55,7 % des cibles DATE. On apprenait activement au
modèle à ignorer la moitié d'une famille.

Noter la non-linéarité : diviser par 5 ne fait rien (+0.003), diviser par 50 fait
+0.079. Ce n'est pas un réglage fin, c'est un régime : au-dessus d'un seuil la
détection capture entièrement l'encodeur.

Une pièce de plus qui sort du design, et c'est la mesure qui la sort. Défaut du
script passé à 0.

Confirmation test, calibration, contrôle d'ancrage et run 3 epochs lancés sur ce
checkpoint.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 3f6bf1a 2026-07-29 04:19:31 +0200
DESIGN_V2 : la revendication d'ouverture est vraie, mais par l'encodeur (§10)

La phrase « on ne dit plus au modèle où chercher, il l'apprend » tient — la
supervision par la valeur fait monter le score de détection de +0.062 au rang 1 et
+0.116 sur DATE. Mais elle le fait en reformant l'ENCODEUR, pas via la tête
d'affectation, qui tombe à 0.215 sans son ancrage sur S. La tête est un tuyau.

§10 consigne : le résultat (0.487 v3b nu -> 0.739), ce qui le produit par ordre
d'importance (rééquilibrage +0.066, transducteur +0.174, décision de remplir,
abstention), ce qui ne produit rien et doit être retiré (sélecteur, alpha, pool
large, hypothèse ⊥ atomique), la règle qui explique les quatre têtes, la
démonstration que le value-F1 du capstone mesure la COPIE et non la valeur (28 %
de nos champs y passent ; « femme » contre « patiente » = 0.00), et les deux
corrections à des mesures de ce dépôt (19 champs à rôle et non 55 ; données x1,35
et non x10).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### eca15d6 2026-07-29 03:40:05 +0200
0.739 sur le test : le mécanisme marche, mais par l'ENCODEUR, pas par la tête

CONFIRMATION TEST du rééquilibrage (det_w 0.1 -> 0.002, rien d'autre) :

  règle de remplissage              val     TEST
  p > 0.5                          0.744   0.733
  global balayé (tau=0.38)         0.748   0.739
  par famille (4 ddl)              0.751   0.737   <- surajuste encore
  F1/2, règle fermée, 0 ddl        0.744   0.738

Trajectoire complète, même barème, même test 410 :

  v3b nu                                        0.487
  Qwen3.5-9B finetuné (mêmes données)           0.582
  v3b + têtes (pipeline précédent)              0.603
  + transducteur, abstention, seuil déduit      0.673
  + loss rééquilibrée                           0.739

+0.25 sur v3b nu. +0.157 sur un LLM 60x plus gros finetuné sur les mêmes données.
Le critère d'arrêt posé d'avance (0.688) est franchi par le SEUL rééquilibrage.

CE QUE LE CONTRÔLE D'ANCRAGE RÉVÈLE, et c'est la synthèse de la nuit :

  rappel@1              avant    rééquilibré
  détection brute       0.727      0.789
  détection, DATE       0.470      0.586
  P_A                   0.732      0.799   (+0.010)
  P_A privée de beta*S  0.234      0.215

La tête n'a TOUJOURS rien appris en propre (0.215 sans son ancrage). Mais la
DÉTECTION s'est améliorée de +0.062, et de +0.116 sur DATE — alors qu'on l'entraîne
50x moins.

Le paradoxe n'en est pas un : la loss d'affectation entraîne aussi l'encodeur, `S`
étant dans le graphe. Avec det_w=0.1 la loss de détection dominait et tirait
span_rep vers « pointer là où l'annotateur a pointé » — c'est-à-dire vers des spans
qui ne tombent JAMAIS sur les en-têtes. En la réduisant, c'est la supervision par la
VALEUR qui façonne l'encodeur.

Donc « superviser la valeur plutôt que le span » apprend bien au modèle où regarder,
mais il le fait en REFORMANT L'ENCODEUR, pas via une tête séparée. C'est pourquoi la
tête d'affectation est inutile : on n'a pas besoin d'un module qui réordonne, on a
besoin que le score de détection lui-même soit entraîné sur le bon objectif. La tête
n'était qu'un tuyau laissant passer S.

Cela réconcilie ce qui semblait contradictoire : le mécanisme central FONCTIONNE, la
tête censée le porter NE SERT À RIEN, et les deux sont vrais.

Hypothèse « ⊥ atomique » RÉFUTÉE : la règle « masse agrégée > masse(⊥) » donne 0.737,
sous le seuil global. La relecture prédisait <= 0.01, c'est vérifié.

La règle fermée F1/2 tient encore (0.738 contre 0.739), zéro degré de liberté ajusté.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 252b3f7 2026-07-29 03:29:28 +0200
La loss était pondérée à 97,5 % sur la détection : +0.079 en corrigeant un scalaire

Journaliser les deux termes séparément (fait sur remarque de relecture) donne
`affect~2.5` contre `det~952`. Avec det_w=0.1 la loss valait 0.1*952 + 2.5, soit
97,5 % de DÉTECTION et 2,5 % d'affectation. On entraînait l'encodeur à être un
détecteur, puis on s'étonnait que la tête d'affectation classe comme un détecteur.

Run de contrôle, det_w 0.1 -> 0.002, TOUT LE RESTE IDENTIQUE (M=256, somme 8+4,
alpha gelé, même epoch, même seed) :

                      det_w=0.1   det_w=0.002
  val macro             0.670        0.749     (+0.079)
  CAT                   0.728        0.798
  DATE                  0.469        0.594     (+0.125)
  NUM                   0.685        0.743
  ORD                   0.798        0.860
  masse route COPIE     0.696        0.792

Plus gros gain d'un changement unique depuis la correction du cap de lecture. Et
+0.125 sur DATE, la famille qu'on venait de déclarer bloquée par le plafond du pool.

Ce que ça oblige à réviser :
- « la tête d'affectation ne sert à rien » a été mesuré sur des modèles entraînés à
  2,5 % sur l'objectif d'affectation. Le contrôle d'ancrage est relancé sur ce
  checkpoint : si P_A tient debout sans beta*S, la conclusion de la nuit tombe.
- l'estimation « ce chemin est condamné à +0.1 » reposait sur les mêmes modèles.

Attention : 0.749 est de la VALIDATION, la référence 0.673 est du TEST. Sur le bras
précédent val 0.670 / test 0.660, donc l'écart val-test est d'environ +0.01. La
confirmation test tourne, et rien ne sera annoncé avant.

Lancé dans la foulée : confirmation test, contrôle d'ancrage au rang 1, calibration
du seuil sur ce checkpoint, balayage det_w (0.0 et 0.02) pour savoir si 0.002 est un
optimum ou si l'auxiliaire de détection ne sert à rien du tout.

Aussi : `learn_fill.py`, la décision de remplir APPRISE sur les 1 540 documents
d'entraînement (~38 000 décisions) au lieu des 100 de validation. Elle ne voit
jamais l'identité du champ, seulement des indices de confiance (masse, marge,
entropie, nombre de spans concordants, masse de l'abstention, confiance du
transducteur, type dérivé des données). ~15 paramètres, aucun par champ. Vise les
+0.074 que le seuil scalaire n'a pas récupérés sur les +0.089 disponibles.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 5534d6a 2026-07-29 02:59:27 +0200
Contrôle au rang 1 : la tête d'affectation recopie le détecteur (preuve par ablation)

Le contrôle précédent, au rang 64, était mesuré là où la détection est déjà à
0.98-0.99 : un test incapable de produire un résultat positif n'est pas un
contrôle négatif. Refait au rang 1, 4 et en MRR, avec en plus l'ablation de
l'ancrage.

  classement (moyenne)          @1      @4     MRR
  détection brute             0.727   0.822   0.775
  P_A                         0.732   0.831   0.780    (+0.005)
  P_A privée de beta*S        0.234   0.417   0.338    (-0.493)

Il y avait de la marge — la détection est à 0.727, et à 0.470 sur DATE. La tête en
prend 0.005. Et privée de son ancrage elle tombe à 0.234 : elle n'a rien appris en
propre, elle recopie le score de détection. Mon hypothèse que le contrôle changerait
de signe hors zone saturée était fausse.

Règle qui explique les quatre têtes du projet et qui est falsifiable : une tête
gagne quand elle ouvre un espace de sortie que le score de l'encodeur ne peut pas
exprimer (transducteur +0.174, classes hors texte +0.252, abstention +0.071) ; elle
ne gagne rien quand elle réordonne les mêmes objets à partir des mêmes
représentations (sélection +0.005).

REPLI « DONNÉES x10 » BLOQUÉ, vérifié : 2 774 graines PMC lymphome adulte
disponibles, 2 050 documents générés, une graine par document, aucune réutilisation.
La marge réelle est x1,35. Aller plus loin demande soit de réutiliser les graines en
ne variant que noms et dates (aucune information clinique nouvelle, fuite train/test
possible), soit d'élargir hors lymphome — ce qui change la tâche.

Critère d'arrêt inchangé et posé avant les résultats : 0.688.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### e75afdc 2026-07-29 02:38:33 +0200
Le liage par rôle concerne 19 champs, pas 55 — et c'est un problème de DATE

Ma définition des « champs indexés par un rôle » (leur cible coïncide avec celle
d'un autre champ du même document) était contaminée : sur 1 640 documents,

  valeur BANALE (« non », « négatif », présente dans >5 % des docs)  85,9 %
  valeur SPÉCIFIQUE au document (= vrai liage par rôle)              14,1 %

`first_line_radiation` <-> `first_line_transplant_therapy` (686x) ou
`history_bcl2_ihc` <-> `history_bcl6_ihc` (395x) ne partagent rien de sémantique :
ils partagent la chaîne « non ». Les vraies paires sont des DATE :

   865x  news_date_of_last_news      <-> news_date_of_last_visit
   220x  news_date_of_death          <-> news_date_of_last_news
   183x  imaging_dmax                <-> imaging_largest_tumor_size
   171x  first_line_date_of_response <-> imaging_date_of_tepscan_2nd_line

Trois conséquences.

1. Le « macro 0.556 sur les champs à rôle » ne mesurait PAS le liage par rôle. Il
   portait sur 55 champs dominés par des CAT à valeur banale. À refaire sur les 19.
2. Le liage par rôle et le problème DATE sont LE MÊME problème, pas deux chantiers.
3. Les deux recommandations de la relecture se contredisent donc : « abandonner
   DATE, retour sur investissement le plus faible » et « reconstruire la tête A,
   +0.05/+0.08 dont l'essentiel sur les champs à rôle » portent sur le même
   ensemble. L'espérance du run en cours est à réviser à la baisse : les features
   d'ordre et l'attention visent 19 champs DATE dont le plafond de pool est 0.748,
   le plus bas des quatre familles.

AUTRE DÉFAUT TROUVÉ, et il domine peut-être tous les autres. La journalisation
séparée des deux termes de la loss donne `affect~2.5` contre `det~952`. Avec
det_w=0.1, l'entraînement était à 97,5 % de la DÉTECTION. On passait le temps à
apprendre à l'encodeur à être un détecteur, puis on s'étonnait que la tête
d'affectation classe comme un détecteur. Deux runs le séparent : le rééquilibrage
seul (det_w 0.1 -> 0.002, tête inchangée) et la tête reconstruite.

CONTRÔLE DÉCISIF REFAIT. Il était mesuré au rappel@64, où la détection est déjà à
0.984-0.996 : un test qui ne PEUT PAS produire de résultat positif n'est pas un
contrôle négatif. `control_rank.py` le refait au rang 1, 4 et en MRR, et ajoute le
classement « P_A privée de son ancrage beta*S » — la seule façon de savoir si la
tête a appris quelque chose ou si elle recopie son initialisation.

TÊTE A RECONSTRUITE, quatre correctifs dont trois sont des RETRAITS de défauts :
beta initialisable à 0 (ne pas démarrer sur la solution suiveuse) ; support de la
marginale proposé depuis la cible (hard-EM : `sel = topk(P_A)` seul est une boucle
de rétroaction où le détecteur choisit qui apprend, donc se renforce) ; features
d'ordre (3 scalaires — « la date la plus tardive » était littéralement
inexprimable, le résumé sum-poolé détruit l'ordre) ; et un seul vrai ajout,
l'attention champ->pool, qui n'avait JAMAIS tourné (défaut ctx=none).

P_B réintégré à l'inférence : on entraînait `Σ P_A·P_B` et on décidait sur `Σ P_A`.

`load_head` rétrocompatible : `pos_proj` ajouté après coup aurait été chargé au
hasard sur les anciens checkpoints (strict=False), corrompant silencieusement des
modèles déjà mesurés. Il est mis à zéro, ce qui reproduit leur comportement réel.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 9c75c5f 2026-07-29 02:07:17 +0200
0.673 : la décision de remplir se DÉDUIT de la métrique — et le contrôle décisif est négatif

DEUX RÉSULTATS, l'un bon, l'autre qui oblige à réécrire la revendication centrale.

1. LE SEUIL DE REMPLISSAGE ÉTAIT FAUX, et le correctif ne coûte rien.

  règle                            val     TEST
  p > 0.5 (raisonnement additif)  0.664   0.658
  global balayé (tau=0.4)         0.674   0.673
  par famille, balayé (4 ddl)     0.675   0.670
  F1_val(famille)/2, règle fermée 0.670   0.673

`p > 0.5` venait d'une matrice de coût ADDITIVE (valeur fausse = 2, abstention = 1).
La métrique est un macro-F1 par famille, qui ne l'est pas : l'optimum pour la F1
est ~F1*/2 (Lipton et al. 2014), soit 0.25-0.40 ici. La règle fermée égale la
meilleure règle balayée SANS aucun degré de liberté ajusté — elle se déduit de la
métrique au lieu d'être calibrée. Et le balayage par famille (4 ddl sur 100
documents) fait déjà MOINS BIEN sur le test que le seuil global : surajustement de
la calibration, le piège où cette session est déjà tombée une fois.

0.603 -> 0.673 sans réentraîner ni toucher à l'architecture.

Diagnostic qui l'a fait trouver : une décision de remplissage PARFAITE vaudrait
+0.089 à sélection inchangée, et 25,4 % des cibles CAT (17,3 % des NUM) ont la
BONNE valeur en TÊTE de distribution pendant que le modèle s'abstient. Il savait,
la règle de décision le bâillonnait.

Le diagnostic révèle aussi que les familles ont des goulots OPPOSÉS, ce que le
macro-F1 masquait : CAT/NUM/ORD sont limitées par la DÉCISION (décision parfaite :
CAT 0.702->0.873, NUM 0.651->0.756, ORD 0.781->0.853) ; DATE ne gagne que +0.010
à décision parfaite, son problème est que la cible n'est produite par AUCUNE option.

2. LE CONTRÔLE DÉCISIF EST NÉGATIF. La tête d'affectation ne classe pas mieux que
le score de détection brut, sur le même pool :

  rappel@64        CAT     DATE     NUM     ORD
  par P_A         0.985   0.818   0.954   0.995
  par détection   0.984   0.791   0.953   0.996
  écart          +0.001  +0.027  +0.001  -0.001

et sur DATE l'écart n'est que de +0.004 à M=256, la configuration retenue.

Donc « on ne dit jamais au modèle OÙ regarder, il en déduit où tout seul » n'est
PAS démontré : la tête classe essentiellement comme le détecteur classait déjà.
Le gain vient d'ailleurs — du transducteur et de la décision de remplir. La
revendication à écrire est : superviser la valeur plutôt que le span permet
d'apprendre la CONVERSION et la DÉCISION de bout en bout sans règles écrites à la
main, mais à cette échelle de données cela n'apprend pas à mieux LOCALISER.

Conséquence : `ctx` (contexte inter-spans dans le score de copie, none/sum/attn)
est câblé en variante contrôlée. Le score de copie était STRICTEMENT PONCTUEL —
il ne dépendait que du couple (champ, span), jamais des autres spans. Ce qui a été
réfuté avec alpha n'est donc pas « les champs doivent interagir » mais la forme la
plus faible imaginable d'interaction. La question reste ouverte.

DÉFAUT DE PROTOCOLE assumé : le premier diagnostic tournait à topk=8 alors que
l'évaluation prédit à topk=32 — les deux ne décrivaient pas le même système et le
INATTEIGNABLE de DATE était gonflé par ma troncature. Relancé aligné.

Écart 0.660 -> 0.659 sur un même checkpoint : le décodage groupé change le
remplissage de lot et donc très légèrement les sorties. Dans le bruit, signalé.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 1967eb2 2026-07-29 01:05:16 +0200
Étape 2 mesurée sur le TEST : 0.660 contre 0.603, et le goulot n'était pas la couverture

Quatre configurations, 410 documents, barème inchangé (valeur fausse = fp ET fn,
tolérance 10 % sur NUM) pour rester comparable à la lignée précédente. UNE epoch.

  bras                     M     somme  alpha  test   DATE  rappel  rôles
  le plus simple          256    8+4      -    0.660  0.497  0.748  0.556
  alpha gelé             1024   32+8    gelé   0.651  0.488  0.816  0.537
  pool réduit             256   32+8    libre  0.651  0.486  0.760  0.542
  référence              1024   32+8    libre  0.645  0.479  0.817  0.529

CE QUI MARCHE. +0.057 sur le test en une epoch. Le rappel effectif passe de 0.61
(ancien ensemble de candidats, top-12 par champ) à 0.75-0.82 dans le top-64 de la
tête d'affectation. Aucun effondrement : p_copy reste entre 0.70 et 0.73, donc le
modèle emprunte bien la route COPIE au lieu de mémoriser du vocabulaire.

CE QUI EST RÉFUTÉ, et c'est la moitié du résultat.
- La compétition entre champs (normalisation sur l'axe des champs) ne sert à rien.
  Alpha, laissé libre, reste à 0 après une epoch complète, et le geler AMÉLIORE le
  score — y compris sur les champs indexés par un rôle, c'est-à-dire précisément le
  sous-ensemble qu'elle devait traiter. Elle sort du design.
- Le pool large ne sert à rien. Le pool étroit non plus n'est pas pénalisant.
- La somme marginale large ne sert à rien : 12 spans transduits valent mieux que 40.

LE RÉSULTAT CONTRE-INTUITIF. Le bras au plus MAUVAIS rappel de pool (0.748) obtient
le MEILLEUR F1 DATE (0.497) ; celui au meilleur rappel (0.817) obtient le pire
(0.479). Plus de couverture donne moins de performance. Le goulot n'est donc pas la
couverture mais la SÉLECTION, et élargir l'ensemble de candidats la rend plus dure.
Cela invalide la prémisse du diagnostic de pool mené plus tôt dans la session : la
montée en M jusqu'à 16384 mesurait consciencieusement la mauvaise quantité.

CE QUI N'EST VÉRIFIÉ QU'À MOITIÉ. Le rappel après entraînement (0.817) n'excède pas
le plafond du pool mesuré à froid (0.821). La tête a appris à CONCENTRER la réponse
dans un top-64 étroit, elle n'a pas ÉLARGI ce qui est atteignable. La formule « un
span d'en-tête jamais annoté reçoit de la masse grâce à la supervision par la
valeur » tient au sens du classement, pas au sens de la découverte. À formuler ainsi.

OÙ EST LE PROCHAIN GISEMENT, chiffré. DATE : la réponse est dans les 64 premières
options 81,6 % du temps, le F1 est à 48,8 %. L'écart de 0.33 est purement de
l'affectation. Et le liage par rôle reste le point faible (0.556 contre 0.660 global,
sur 55 champs des 81) — le problème est réel, c'est la solution proposée qui était
mauvaise.

Décodage groupé dans ValueModel.greedy_many : greedy_one décodait à batch 1, soit
des dizaines de milliers de pas de GRU séquentiels par document. Résultat identique.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### a7d4f98 2026-07-28 23:52:49 +0200
Somme marginale tronquée : M=1024 devient abordable (13 h -> 70 min par epoch)

Le terme transducteur est le poste dominant et croît linéairement en M. À M=1024
le diagnostic mettait ~10 s par document SANS gradient ; avec le backward on est
à ~30 s, soit ~13 h par epoch. Injouable, alors que M=1024 est justement le point
où le rappel du pool DATE atteint 0.82.

DESIGN_V2 §5 prévoyait la troncature de la somme marginale et elle n'était pas
implémentée. Elle l'est :
  - la tête A voit les M spans (produit matriciel, coût négligeable) ;
  - le transducteur ne voit que les `topk`=32 meilleurs selon P_A, PLUS `nsample`=8
    spans tirés uniformément.
Le coût du poste dominant devient indépendant de la taille du pool. Mesuré :
2,5 s/document, soit ~70 min par epoch sur 1 540 documents.

Les 8 tirages uniformes ne sont pas une décoration. Élaguer DUR une variable
latente biaise la marginale : un span jamais dans le top-32 ne recevrait jamais de
gradient et ne pourrait donc jamais y entrer — précisément le piège des en-têtes
dont on essaie de sortir. Le tirage uniforme restaure le support de la latente.
Approximation assumée : les spans hors sous-ensemble contribuent 0, et le biais
est d'autant plus faible que P_A est concentrée.

Le critère par rang est câblé dans build_pool et devient le défaut, sur la base de
la mesure (DATE 0.758 contre 0.613 à M=256 ; les deux convergent vers 0.82 à 1024).

Smoke 12 documents à M=1024/rang : passe, p_null=0.374, p_copy=0.714 — la masse ne
fuit ni vers l'abstention ni hors de la route COPIE.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### d4d6042 2026-07-28 23:41:50 +0200
Étape 2 : tête d'affectation, loss à variable latente, et 4 correctifs de relecture

La chaîne complète tourne de bout en bout (smoke 6 documents) : pool partagé,
tête A, transducteur partagé, bloc VOCAB, inférence par somme sur les valeurs.
Sondes p_null=0.38 / p_copy=0.68 — la masse ne fuit ni vers l'abstention ni hors
de la route COPIE. Le macro du smoke n'est comparable à rien et n'est pas cité.

CRITÈRE D'ÉLAGAGE — tranché par la mesure, pas par principe.

  DATE, rappel du pool        max_f    rang
  actuel (top-12 par champ)    0.61      —
  M=128                        0.312     —
  M=256                        0.613    0.758
  M=1024                       0.824    0.821

Le rang domine à petit budget et converge à grand : les scores bruts de deux
champs ne sont pas à la même échelle, donc max_f laisse les champs bruyants
monopoliser le pool. À 256 spans le rang obtient ce que max_f demande ~700 spans
pour atteindre. Le terme transducteur de la loss croît linéairement en M, donc
ce choix vaut un facteur ~3 de calcul.

QUATRE CORRECTIFS, issus d'une relecture critique. Aucun n'ajoute de cas
particulier ; chacun corrige une asymétrie absente des données.

1. VOCAB gaté sur les champs CLOSED (déjà en place). Sans ce garde-fou, 13 % des
   cibles DATE de test sont littéralement dans le vocabulaire d'entraînement : le
   modèle prend la route VOCAB et le rappel du pool RESTERAIT PLAT PENDANT QUE LE
   MACRO-F1 MONTERAIT. On aurait conclu au mauvais endroit.
2. Température apprise sur log P_B. P_A(vocab) est atomique, P_A(copie)·P_B est un
   produit sur ~10 caractères : la route COPIE était pénalisée par un artefact de
   paramétrisation, pas par les données.
3. Inférence par somme sur les VALEURS. Une même date apparaît dans 3 à 8 spans ;
   l'argmax sur les options divisait sa masse et la faisait perdre contre une
   option VOCAB atomique — pénaliser la valeur la mieux attestée. Le seuil de
   remplissage n'est plus calibré : p_v > 0.5 tombe de la matrice de coût, et ⊥
   sort de l'argmax puisque c'est une décision, pas une classe.
4. span_rep branché sur l'état initial du décodeur de B, projection initialisée à
   ZÉRO donc démarrage à chaud inchangé. Sans elle B ne lit que des caractères :
   l'encodeur ne reçoit de la route COPIE qu'une responsabilité scalaire via A, et
   B ne peut jamais corriger une frontière de span.

Bug attrapé avant de coûter un run : build_pool était décoré @torch.no_grad, donc
H sortait détaché et l'encodeur n'aurait reçu aucun gradient de la tête A — on
n'aurait entraîné que les têtes. La sélection des M spans reste détachée (c'est un
topk), H et S restent dans le graphe.

Chiffres corrigés dans DESIGN_V2 : têtes A et B mesurées à 2.17 M et 2.00 M (et
non ~1.2 M / ~1.7 M estimés) ; le 89,5 % « depuis n'importe quel span » ne se
reconstitue pas (0.82 au mieux ici) et est marqué à ne plus citer tel quel.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### a92567a 2026-07-28 23:32:22 +0200
Étape 2, préalables : tête B intégrable (0.895) + diagnostic de pool

Tête B. L'étape 1 mettait le libellé du champ dans l'entrée caractère, ce qui
force à ré-encoder les M spans du document une fois PAR CHAMP dans la loss à
variable latente (~26 fois le même travail). Le libellé conditionne désormais
l'état initial du décodeur : les spans s'encodent une fois par document et sont
partagés. Mesuré à budget identique (mêmes paires, même split, 12 epochs) :

  entrée caractère (étape 1) : 0.869   CAT .914  DATE .733  NUM .832  ORD .969
  conditionnement décodeur   : 0.895   CAT .928  DATE .757  NUM .898  ORD .982

Meilleur sur les quatre familles : le déplacement est gratuit, et même profitable.
`init_state` accepte un apport optionnel, ajouté avant la tanh, pour brancher
plus tard span_rep sans casser la compatibilité du checkpoint.

Diagnostic de pool. Mesure préalable et falsifiable : ce qui n'est pas dans le
pool est perdu avant la première dérivée, donc on mesure avant d'écrire la tête.

  régime                     CAT    DATE    NUM     ORD    total
  actuel (top-12 par champ)  0.532  0.607   0.786   0.000  0.530
  pool-128 (max_f)           0.345  0.312   0.901   0.820  0.494
  pool-256 (max_f)           0.356  0.613   0.963   0.823  0.586

DATE est à 0.613, pas au ~0.9 espéré : à M=256 le pool fait match nul avec
l'existant sur la famille qui porte la thèse. NUM et ORD progressent nettement
(ORD passe de 0.000, taxonomy échouant totalement, à 0.823). CAT baisse, ce qui
est attendu et sans conséquence : les CAT passent par VOCAB, pas par COPIE.

55,1 % des spans DATE gagnants ne chevauchent AUCUN span gold — le pool trouve
bien des dates là où l'annotateur n'a jamais pointé.

Deux réserves de méthode, écrites plutôt que tues :
- la colonne « littéral » est mal nommée. Ce n'est pas une borne haute : la cible
  est canonique (2017-04-15, 62.0) alors que le texte est en surface (15/04/2017,
  62), d'où les 0.000 sur NUM. Elle ne borne rien, elle sous-estime.
- le 0.895 « depuis n'importe quel span » cité dans DESIGN_V2 ne se reconstitue
  pas ici. À revérifier avant d'être cité de nouveau.

Première version du diagnostic abandonnée : le régime « oracle » énumérait tous
les spans (~96 000/doc) et transduisait chacun pour chaque champ, soit 2,5 M de
décodages par document. Remplacé par un test de présence dans le document.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### e0a5eb3 2026-07-28 23:14:57 +0200
Split de validation échangeable dans le dataset publié (rntc/lymphome-synth-v5-eval)

La validation était « les 100 premiers par id numérique ». Ce sont les dossiers
générés en premier : 47,7 champs remplis par document contre 40,9 pour le test,
soit +16,5 %. Un seuil calibré sur ce régime plus dense ne se transfère pas — le
même défaut, mesuré à +28 % sur le sous-ensemble non-TXT, avait fait échouer la
calibration de seuil côté normalisation (val ↑0.530 / test ↓0.497).

Tirage aléatoire seed 0 : 39,3 champs/doc, soit −4,0 % du test.

test est inchangé (mêmes 410 dossiers, chiffres publiés comparables). train et
validation repartitionnent les mêmes 1640 dossiers, mais ce ne sont plus les
mêmes 100 qui sont mis de côté : tout seuil choisi avec l'ancienne validation
est à recalibrer. L'avertissement est écrit dans le README du dépôt, qui est
entre les mains d'un collaborateur.

Republié et vérifié depuis le Hub.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 6317029 2026-07-28 23:05:59 +0200
Harness d'éval autosuffisant pour rntc/lymphome-synth-v5-eval (livrable Eric)

evaluate.py  : scorer standalone (pandas seul), reproduit le protocole capstone —
               top-1 par (document, champ), compétition d'empans (IoU>0.5), seuil
               choisi sur la validation et reporté sur le test. span-F1 et value-F1.
predict.py   : inférence GLiNER2 turnkey, schéma lu depuis le dataset lui-même.
build_upload.py : construit et pousse le split exact train 1540 / validation 100 /
               test 410 (partition des 2050 dossiers, disjoints).

Vérifié : reproduit 0.644 value-F1 / 0.506 span-F1 pour V5FROMV3B et 0.658 pour V5MIX6.

RÉSERVE CONNUE (voir DESIGN_V2.md §7) : le split de validation publié est « les 100
premiers par sample_index », mesuré 28% plus dense en cibles que le test (DATE +40%).
Le seuil qu'il sélectionne est donc biaisé vers le remplissage. Un tirage aléatoire
corrigerait, mais le dataset est déjà entre les mains d'un collaborateur — décision
de republication à prendre.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### c857c72 2026-07-28 23:05:39 +0200
Expérience NÉGATIVE conservée : sélecteur enrichi posfeat (lignée découplée)

Ajoute 4 features positionnelles (start_frac, len_frac, rang, conf) au scoreur de
sélection de la baseline découplée (bi-encodeur gelé).

REJETÉ : overfit du régime gold-span (train) au régime pred-span (test), fait pire
que la version simple. Conservé pour la traçabilité, ne pas réactiver.

Cette lignée est de toute façon morte (val 0.86 gold-span contre 0.66 pour le
bi-encodeur gelé) et DESIGN_V2.md prévoit sa suppression.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 5ca474c 2026-07-28 23:05:24 +0200
Refonte du design normalisation : matrice d'affectation + transducteur appris

CONTEXTE. La session part de macro-F1 0.429 et se termine à 0.603, devant Qwen-9B
(0.582) sur la métrique stricte, en 150M single-pass.

LA TROUVAILLE. MAX_CHARS=9000 sur des dossiers de 22 288 caractères en médiane :
100% des documents tronqués, 60,5% des spans gold jetés. Lire le dossier entier vaut
+0.100 de macro-F1. Le "la tête de sélection suit la détection à 96%" du journal
précédent était un artefact : à 9 000 caractères il n'y avait rien à re-classer.

CE QUI MARCHE. Laisser les têtes répondre "champ non documenté" (NullHeads) au lieu
d'un seuil sur le score de détection : +0.071, les trois classes d'erreur baissent
ensemble, réponses correctes +25%. Les têtes ne voyaient que 26 champs sur 81 et
n'avaient jamais rencontré un champ absent.

CE QUI EST RÉFUTÉ (chacun à coût faible). Aiguillage tête/parsing, biais sel_c,
conditionnement CAND_COUNT, calibration de seuil, reranker par attention (égalité
stricte 0.532=0.532), loss à marge sur cas durs (-0.017).

LE DESIGN V2 (DESIGN_V2.md). Les trois échecs ont une cause unique : l'interface
"top-12 candidats par champ", goulot non différentiable construit à partir du score
que la tête doit réviser. On garde la matrice champs x spans entière ; options d'un
champ = {tous les spans} u {vocabulaire observé} u {abstention} ; une seule loss à
variable latente supervisée par la VALEUR, pas par le span. Un span d'en-tête jamais
annoté reçoit de la masse dès que le transducteur sait en tirer la bonne valeur.

FAIT VÉRIFIÉ QUI MOTIVE TOUT. 55,7% des cibles DATE sont exactement une date d'en-tête
de section, et 0 span gold DATE sur 6 275 ne tombe sur un en-tête. La moitié des dates
est écrite au seul endroit que l'annotation n'annote jamais.

ÉTAPE 1 VALIDÉE. Transducteur appris (1,7M params, 5 min) contre taxonomy.py (300
lignes écrites à la main) : 0.869 vs 0.630, gagnant sur les 4 familles, handicapé
(pas de contexte) et jugé plus durement. CAT 0.914 vs 0.501. taxonomy.py peut partir.

CORRECTIONS DE MÉTHODE. Bug de métrique (chaîne elif : une valeur fausse n'était pas
comptée comme manquée, absolus gonflés de ~0.03). Split de validation non échangeable
avec le test (+28% de densité) -> tirage aléatoire, ramené à -2%. span_rep partagé
entre les 3 passes d'inférence. Baseline de l'ablation qui perdait son seuil.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### dc30e7e 2026-07-23 07:25:26 +0200
Journal complet têtes de normalisation : idée, succès, échecs, bugs, résultats

Documente : archi intégrée différentiable (GLiNER+têtes no-freeze), ce qui marche
(tête CAT +0.15 F1, candidats natifs), ce qui échoue (tête sélection num/date = suit
la détection à 96%, re-ranker non apprenable), les erreurs (cosine scorer, val fuitée,
métrique clémente, régression NUM) et bugs, les résultats (F1 0.50 vs Qwen 0.62,
oracle/enquête/diagnostic DATE). Recommandation : GLiNER + tête CAT only.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 005718c 2026-07-22 22:55:21 +0200
Fix re-ranker : candidats natifs only (pas d'injection gold score fixe) + tête sans biais conf

Enquête : tête = détection à 96% (suiveur, pas re-ranker). Oracle re-ranker (cible∈candidats)
ORD .77/NUM .69 vs actuel .61/.51 -> headroom +0.16/+0.19. Cause = 2 bugs training :
gold injecté à score 3.0 fixe + terme sel_c*logit(conf) -> la tête copie la détection.
Corrigés. DATE reste détection (oracle .28 à 89 champs). Finetune re-ranker lancé.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 3bd9e62 2026-07-22 19:15:11 +0200
Fix fuite schéma : train sur les 89 champs (absents=[] négatifs) = match éval réaliste

La val v3 (0.84) était fuitée : schéma = champs présents seulement (~17) -> fuite présence +
role-binding facilité. Test réaliste 89 champs = F1 0.50 < Qwen 0.62. build_dataset met
désormais TOUS les non-TXT dans le schéma. Finetune v4 relancé.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 4dc2f54 2026-07-22 18:41:40 +0200
Archi unifiée différentiable : candidats = VRAI score détection natif (count_embed) + F1

Fix majeur : candidat-recall via count_embed+einsum = CAT .68/ORD .96/NUM .88/DATE .76
(vs cosine .09-.23). Une forward : detection_scores natifs -> softmax/marginal-likelihood
(différentiable, détection+normalisation unifiées) -> têtes. predict_doc(thresh) pour
remplir-ou-non. Éval passe en F1 (precision/recall) sur 89 champs vs Qwen + DATE année-F1.
Finetune v3 unifié lancé (v5+v3b, 3ep).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 5278793 2026-07-22 18:23:48 +0200
Résultats intégré : bat Qwen-9B à métrique équitable (0.62 vs 0.58), single-pass 150M

Table finale test 410 (seuil 0.03) : CAT 0.64 écrase Qwen 0.36 ; DATE granularité-équitable
(année) 0.61-0.67 = parité Qwen ; ALL équitable v5 0.621 / v3b 0.626 vs Qwen 0.579.
Têtes rescuent net +2000 (mesuré). Détection = levier (miss 23%->9% via seuil).
Frontière : NUM + DATE role-binding -> fix = têtes sur vrais spans prédits cachés.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 4ec5c4e 2026-07-22 17:49:08 +0200
Amélioration têtes : entraînement sur candidats prédits (désambiguïsation) + analyse erreurs

Analyse test 410 : détection ratée 14-23%, DATE role-binding = tueur (1400-2100 mauvaises
occurrences), têtes rescuent net +1900 (surtout CAT). -> norm_loss_doc entraîne désormais
les têtes sur candidats PRÉDITS (top-k sim au type) ∪ gold ; val_acc idem (prédictif du test).
Finetune v2 (5ep) lancé. Éval : quantif granularité DATE (match année). + figure archi
(GLiNER + têtes normalisation, arch_norm.tex/pdf/png).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 850bc2c 2026-07-22 16:08:24 +0200
Éval intégrée single-pass + fix width-clamp (v3b max_width=8 vs v5=24)

eval_integrated : le modèle détecte (extract_entities) puis normalise (têtes),
vs span-brut / Qwen-9B. Fix : clamp largeur de span sur span_rep.shape[1] du modèle.
Alignement mot↔token confirmé (0.909). Finetunes v5+v3b en cours.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 56c58ae 2026-07-22 16:05:26 +0200
Modèle intégré GLiNER + têtes de normalisation (end-to-end, no-freeze)

Sous-classe/attache des têtes trainables à l'Extractor GLiNER (gliner2/* intact) :
- forward unique : détection native (_compute_sample_loss) + normalisation sur span_rep
  natif (compute_span_rep) des spans gold. Backprop dans tout le modèle, no-freeze.
- têtes : CAT classif (similarité option) + NUM/ORD/DATE sélection de span.
- e_f/options via encodeur GLiNER (grad flow) ; mapping char->mot via word_splitter natif.
Smoke GPU OK (loss norm descend, backward end-to-end). Finetune v5 + v3b lancés (ablation init).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 06fe422 2026-07-22 15:44:34 +0200
Baseline découplée finalisée (bat Qwen 0.746) + breakdown par champ + plan intégré

- eval_norm : ablation top-K (1/3/5/8) + breakdown par champ (edge cases).
- Diagnostic edge-cases : 3 modes (désambiguïsation dates, NUM comptage, champs rares).
- Négatif utile : sélecteur enrichi overfit (mismatch train gold-span/test pred-span) ->
  version simple retenue.
- INTEGRATED_PLAN.md : design validé du vrai modèle GLiNER+têtes end-to-end no-freeze
  (sous-classe Extractor, span_rep+schema_emb natifs, loss détection+normalisation).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 5dc87a0 2026-07-22 14:51:35 +0200
Têtes de normalisation eCRF : archi 2-modes (classif CAT + sélection NUM/ORD/DATE)

Résultat : GLiNER 150M gelé + têtes légères BAT Qwen-3.5-9B sur la normalisation
eCRF lymphome v5, bout-en-bout 0.746 vs 0.620 (4 familles), ~60x plus petit,
single-pass. CAT span-brut 0.33->0.75. Ablation top-k>top-1 (multi-span aide).

Pipeline: build_dataset -> encode_spans (frozen MedEmbed-v9) -> train_norm ->
eval_norm. Cibles = annotation.value normalisé (taxonomy.py, 89 champs, gate
CAT .999/ORD .995/NUM .974/DATE 1.0). Design: NORM_HEADS_DESIGN.md.
Résultats: RESULTS_NORM.md.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

### 7042412 2026-07-22 13:43:09 +0200
Checkpoint avant projet normalization-heads (têtes de normalisation eCRF)

État: gold lymphome v5 (TAPDL) uploadé, modèles v5 (V5FROMV3B/V5MIX6) entraînés
et évalués (capstone_ecrf). Spec des têtes de normalisation dans
gen/lymphome/NORM_HEADS_DESIGN.md. Filet de sécurité avant d'ajouter le code
gen/lymphome/norm/.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kxxr8q9hqmKsvV1uUifw6P

