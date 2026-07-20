# Audit exhaustif de `bibcheck_whitelist.txt`

Date de l'audit : 19 juillet 2026  
Périmètre : les 72 clés de `tools/bibcheck_whitelist.txt`, leur notice dans `thesis.bib`, leur justification dans la whitelist et leur usage dans `sources/**/*.tex`.

## Conclusion

La whitelist n'est pas une preuve de validité bibliographique : `verify_bib.py` retourne immédiatement `SKIPPED` pour toute clé qui s'y trouve. C'est pourquoi `make checkbib` pouvait afficher zéro erreur tout en laissant passer les erreurs de BioOntoBERT et de TxT360.

Sur les 72 notices :

- **42 sont bibliographiquement valides ou défendables** ;
- **22 désignent une source réelle, mais leur notice ou leur justification doit être complétée/corrigée** ;
- **6 comportent une erreur bibliographique nette** ;
- **2 ne sont pas de vraies références bibliographiques reproductibles**, mais des notices synthétiques construites pour porter des nombres.

Parmi les 47 clés whitelistées effectivement citées dans la thèse, quatre demandent une correction prioritaire :

1. `shashikumar2023bioontobert` : titre et auteurs faux ;
2. `tang2024txt360` : auteur collectif faux à la place des auteurs nommés ;
3. `aphp_eds_scale` : notice composite sans document source unique ;
4. `pubmed_eutils` : comptage dynamique sans requêtes permettant de le reproduire.

Les deux premières sont des erreurs de notice. Les deux dernières ne prouvent pas que les nombres cités sont faux, mais la bibliographie ne permet pas de les reproduire.

## Pourquoi `make checkbib` ne les détectait pas

Dans `tools/verify_bib.py`, chaque clé présente dans la whitelist reçoit directement le verdict `SKIPPED`; aucun DOI, titre, auteur, URL ou année n'est alors contrôlé. De plus, `make checkbib` n'examine que les clés citées, tandis que 25 des 72 clés whitelistées ne sont actuellement pas citées. Enfin, le mode normal est non bloquant ; seul `--strict` transforme les problèmes non exemptés en code de sortie non nul.

Le second passage automatique, effectué en ignorant temporairement la whitelist, a donné 7 `VERIFIED`, 47 `MISMATCH` et 18 `NOT_FOUND`. Ces nombres ne sont **pas** des verdicts bibliographiques : ils montrent surtout que le moteur actuel gère mal les livres, textes juridiques, pages institutionnelles et logiciels. Tous les cas ont donc été revus manuellement ci-dessous.

## Verdict ligne par ligne

Légende :

- **VALIDE** : notice exacte ou bibliographiquement défendable ;
- **À RÉPARER** : source réelle, mais métadonnées, lien ou justification incomplets ;
- **FAUX** : au moins un champ bibliographique important est erroné ;
- **SYNTHÉTIQUE** : la clé ne correspond pas à une publication identifiable et reproductible.

La colonne « action » concerne la whitelist, pas la présence de la source dans la thèse.

| Clé | Citée | Verdict | Contrôle et action recommandée |
|---|:---:|---|---|
| `seqeval` | oui | VALIDE | Citation logicielle cohérente avec le dépôt officiel. Conserver seulement tant que le vérificateur ne valide pas les URL GitHub. |
| `neveol14quaero` | oui | À RÉPARER | Auteurs, année et pages exacts. Le titre publié emploie **“Ressource”** (avec deux *s*), alors que la notice a normalisé en “Resource”. Ajouter le PDF/URL de l'atelier. |
| `touchent2023camembertbio` | oui | VALIDE | Notice ACL exacte pour LREC-COLING **2024**. Retirer de la whitelist : le contrôle automatique la valide déjà. Le nom de clé et le commentaire “TALN 2023” sont périmés. |
| `cardon_presentation_2020` | oui | À RÉPARER | Auteurs, atelier et pages exacts, mais le titre est tronqué après “DEFT 2020”. Importer la notice complète et l'URL ACL `2020.jeptalnrecital-deft.1`. |
| `le_clercq_de_lannoy_strategies_2022` | oui | VALIDE | Notice conforme à ACL Anthology. Retirer de la whitelist après validation directe de l'URL ACL. |
| `miranda2022distemist` | oui | VALIDE | Notice conforme à CEUR-WS vol. 3180, p. 179–203. Ajouter l'URL `paper-11.pdf`, puis retirer l'exception. |
| `shashikumar2023bioontobert` | oui | **FAUX** | Le document officiel est **Sahil Sahil et P. Sreenivasa Kumar**, “Leveraging Biomedical Ontologies to Boost Performance of BERT-Based Models for Answering Medical MCQs”, ICBO 2023, CEUR vol. 3603, p. 94–105. Corriger immédiatement puis retirer de la whitelist. |
| `lindberg_unified_1993` | oui | À RÉPARER | Titre/auteurs/volume/pages exacts. Ajouter PMID 8412823 et DOI `10.1055/s-0038-1634945`; l'exception devient inutile. |
| `ec_directive_2001_83` | oui | VALIDE | Acte et CELEX 32001L0083 exacts. Exception légitime pour un texte juridique, mais ajouter l'URL EUR-Lex serait préférable. |
| `ema_qrd_template` | oui | À RÉPARER | Ressource EMA réelle, mais la notice ne donne ni URL précise ni version du modèle. Remplacer la simple mention de l'agence par l'URL du modèle QRD humain effectivement consulté. |
| `krallinger2017chemprot` | oui | VALIDE | Titre, premiers auteurs, volume et pages cohérents avec les actes BioCreative VI. Ajouter la liste officielle ou conserver `and others`, mais ajouter l'URL/record Zenodo. |
| `fox_health_online_2013` | oui | VALIDE | Titre, auteurs, année et URL Pew exacts. Exception web défendable. |
| `kittredge_sublanguages_1982` | oui | VALIDE | Notice exacte : article AJCL 8(2), p. 79–84, ACL `J82-2006`. **Le commentaire de whitelist est faux** : ce n'est pas un chapitre de l'ouvrage de Kittredge & Lehrberger. Ajouter l'URL ACL et retirer l'exception. |
| `sager_mlp_1987` | oui | VALIDE | Livre et auteurs confirmés (Addison-Wesley, 1987). Exception de livre défendable. |
| `grice_logic_1975` | oui | VALIDE | Chapitre, éditeurs, volume et pages cohérents. Exception de classique défendable. |
| `austin_words_1962` | oui | VALIDE | Édition originale OUP 1962 correctement décrite. Exception de livre défendable. |
| `wuster_einfuhrung_1979` | oui | VALIDE | Titre, auteur, éditeur et année cohérents. Exception de monographie défendable. |
| `tang2024txt360` | oui | **FAUX** | Le titre et l'année sont corrects, mais `{LLM360}` n'est pas l'auteur. La citation officielle courante donne 17 auteurs, de Liping Tang à Eric P. Xing. Corriger les auteurs depuis la carte officielle du dataset. |
| `gretton_kernel_2012` | oui | VALIDE | Notice JMLR 13(25):723–773 exacte. Retirer de la whitelist et faire reconnaître l'URL JMLR. |
| `mycin_book_1984` | oui | VALIDE | Titre, auteurs, éditeur et année exacts. Exception de livre défendable. |
| `qmr_status_1986` | oui | VALIDE | Notice exacte et PMID 3544509 déjà indiqué. Faire reconnaître les PMID plutôt que conserver l'exception. |
| `lighthill_1973` | oui | VALIDE | Rapport Lighthill/SRC réel et correctement daté. Ajouter un lien stable vers le rapport numérisé. |
| `nilsson_2010` | oui | VALIDE | Livre CUP exact. Exception de livre défendable. |
| `aphp_eds_scale` | oui | **SYNTHÉTIQUE** | Aucun auteur, URL ou document unique ; la note agrège le périmètre de l'EDS et deux études (PMID 41647696 et 41133988). Remplacer par les trois sources réelles ou au minimum deux notices PubMed plus la page institutionnelle AP-HP. |
| `gdpr_art9` | oui | VALIDE | Référence juridique exacte. Ajouter l'URL EUR-Lex ; conserver comme exception juridique si nécessaire. |
| `cnil_mr004` | oui | VALIDE | Numéro, date et objet de la délibération exacts. Ajouter l'URL CNIL/Légifrance. |
| `hdh_loi` | oui | VALIDE | Loi 2019-774, article 41, correctement identifiée. Ajouter l'URL Légifrance. |
| `ce_hdh` | oui | VALIDE | Ordonnance n° 444937 du 13 octobre 2020 correctement identifiée. Ajouter l'URL Conseil d'État. |
| `pubmed_eutils` | oui | **SYNTHÉTIQUE** | Les deux nombres et la date de requête sont inscrits à la main, sans URL ESearch, termes de requête ni réponse JSON archivée. Conserver les nombres seulement avec les requêtes exactes et un résultat archivé/scripté. |
| `goodfellow_deep_2016` | oui | VALIDE | Livre MIT Press exact ; l'URL est seulement placée dans `note`. Exception de livre défendable. |
| `russell_aima_2020` | non | VALIDE | AIMA, 4e édition, 2020, Pearson : exact. Ajouter `edition={4}` si la clé est réutilisée. |
| `manning_ir_2008` | oui | VALIDE | Livre CUP exact. Exception de livre défendable. |
| `snomed_ct` | oui | À RÉPARER | Page institutionnelle réelle, mais `year={2024}` ne correspond ni à la date d'accès 2026 ni à une version identifiée. Utiliser `urldate` et une version/release explicite, ou `n.d.`. |
| `who_icd10` | oui | À RÉPARER | Titre et organisme corrects ; `year={2019}` est arbitraire pour cette page vivante. Distinguer l'édition ICD-10 citée de la date d'accès au site. |
| `whocc_atc` | oui | À RÉPARER | Titre/organisme/URL corrects ; même incohérence entre année 2024 et accès 2026. Employer `urldate` ou l'édition ATC effectivement utilisée. |
| `nlm_mesh` | oui | À RÉPARER | Page MeSH officielle correcte ; `year={2024}` est périmé face à une consultation 2026. Citer l'édition MeSH ou traiter la page comme ressource sans date avec `urldate`. |
| `atih_pmsi` | oui | À RÉPARER | Page ATIH exacte ; l'année 2024 n'est pas justifiée par la page vivante consultée en 2026. Normaliser année/date d'accès. |
| `atih_cim10` | oui | VALIDE | La ressource est explicitement la CIM-10-FR 2025 et l'URL correspond à cette version. Exception institutionnelle défendable. |
| `atih_ccam` | oui | À RÉPARER | URL ATIH réelle mais générique, sans édition CCAM 2024 identifiable. Citer la version exacte utilisée ou retirer l'année de version. |
| `inca_rcp` | oui | À RÉPARER | La citation pointe seulement vers la page d'accueil `e-cancer.fr`; elle ne permet pas de retrouver le référentiel ou la définition exacte de RCP. Remplacer par un document/page INCa précis. |
| `gdpr_art4` | oui | VALIDE | Article 4(5), définition de la pseudonymisation, correctement identifié. Ajouter l'URL EUR-Lex. |
| `ansm2023thesaurus` | oui | À RÉPARER | Titre, organisme et année exacts pour le PDF ANSM du 15 septembre 2023, mais aucun URL/identifiant n'est conservé. Ajouter le PDF officiel. |
| `bdpm2024` | oui | À RÉPARER | Base officielle réelle, mais aucune URL et l'année 2024 ressemble à une date d'accès/version non explicitée. Ajouter la page BDPM et un `urldate`; préciser les organismes contributeurs si souhaité. |
| `finkel_nested_2009` | oui | VALIDE | Notice exacte, déjà dotée de l'URL ACL `D09-1015`. Retirer de la whitelist. |
| `APA:83` | non | **FAUX** | Le titre est **Publication Manual of the American Psychological Association**, pas “Publications Manual”. Ajouter la 3e édition et l'ISBN, ou supprimer la notice puisqu'elle n'est pas citée. |
| `HochSchm97` | non | À RÉPARER | Métadonnées exactes, mais le DOI est rangé dans `optdoi`, champ ignoré par BibTeX et par le vérificateur. Le déplacer vers `doi`, puis retirer l'exception. |
| `Sutton_2019` | non | VALIDE | Billet “The Bitter Lesson”, auteur, année et URL exacts. Exception web défendable. |
| `Tan2019EfficientNetRM` | non | VALIDE | Notice PMLR exacte. Retirer de la whitelist ; l'URL officielle suffit à la valider. |
| `aronoff2022morphology` | non | À RÉPARER | Livre réel et année correcte ; préciser qu'il s'agit de la 3e édition et normaliser l'éditeur Wiley-Blackwell/John Wiley & Sons. |
| `chowdhury2010introduction` | non | À RÉPARER | Livre réel ; préciser la 3e édition et, idéalement, l'ISBN/URL éditeur. |
| `elhage2021mathematical` | non | VALIDE | La notice reproduit la citation officielle du Transformer Circuits Thread. Exception web défendable. |
| `eval-harness` | non | VALIDE | DOI Zenodo `10.5281/zenodo.10256836` présent. La whitelist est injustifiée : corriger le résolveur DOI si nécessaire puis retirer l'exception. |
| `gumbel-orig` | non | VALIDE | Notice Numdam exacte pour **1935**. **Le commentaire de whitelist “Gumbel 1954” est faux.** Ajouter/faire reconnaître l'URL Numdam et retirer l'exception. |
| `harris1954distributional` | non | **FAUX** | La source est un article de *WORD* 10(2–3):146–162, DOI `10.1080/00437956.1954.11659520`, pas un `@misc` dont `publisher={Word}`. |
| `hu2022lora` | non | VALIDE | Notice ICLR/OpenReview exacte (à la casse des prénoms près). Retirer de la whitelist après contrôle direct de l'URL OpenReview. |
| `jain-etal-2023-contraclm` | non | VALIDE | Notice ACL 2023 exacte. Retirer de la whitelist. |
| `lda` | non | À RÉPARER | Article JMLR exact, mais `number={null}` est une valeur bibliographique erronée. Supprimer ce champ, ajouter l'URL JMLR, puis retirer l'exception. |
| `mle` | non | À RÉPARER | Article de Fisher, volume et pages exacts. Ajouter DOI `10.1098/rsta.1922.0009` et retirer l'exception. |
| `ramos2003using` | non | **FAUX** | Le PDF récupéré fait 4 pages et ne porte pas les métadonnées `volume={242}, pages={29--48}` de façon vérifiable ; les citations secondaires se contredisent (`29–48` ou `133–142`). Conserver auteur/titre/année et citer le PDF comme rapport/communication sans pagination inventée, ou supprimer la clé non citée. |
| `wals` | non | VALIDE | Citation recommandée cohérente pour WALS Online v2020.3, DOI `10.5281/zenodo.7385533`. Retirer de la whitelist : le DOI est explicite. |
| `weaver-1952-translation` | non | VALIDE | Notice ACL Anthology exacte. Retirer de la whitelist. |
| `zar2005spearman` | non | À RÉPARER | Chapitre réel, mais ajouter les éditeurs P. Armitage et T. Colton et le DOI `10.1002/0470011815.b2a15150`; `@inreference`/`@incollection` est plus précis que `@article`. |
| `clark-etal-2019-boolq` | non | VALIDE | Notice ACL et DOI `10.18653/v1/N19-1300` exacts. Retirer de la whitelist. |
| `francis79browncorpus` | non | VALIDE | Manuel du Brown Corpus réel ; exception de rapport ancien défendable, avec vérification/actualisation du lien ICAME. |
| `gini1912variabilita` | non | VALIDE | Monographie historique réelle et correctement datée. Exception de source pré-indexation défendable. |
| `lecun2022path` | non | **FAUX** | Le titre/auteur/date sont réels, mais `journal={Open Review}`, `volume={62}`, `number={1}`, `pages={1--62}` inventent une structure de revue. Citer comme position paper/`@misc` avec l'URL OpenReview, sans volume ni numéro. |
| `logit_lens` | non | VALIDE | Billet LessWrong réel, titre/auteur/année/URL cohérents. Exception web défendable. |
| `xFormers2022` | non | À RÉPARER | Source réelle, mais la citation officielle actuelle ajoute Luca Wehrstedt, Jeremy Reizenstein et Grigory Sizov, et fournit l'URL GitHub absente de la notice. Mettre la notice à jour ou figer un commit/version. |
| `synapse_medgpt_2025` | oui | VALIDE | Titre, média, date et URL confirmés sur Caducee.net. Exception presse défendable. |
| `nabla_agentique_2025` | oui | À RÉPARER | Titre/date/URL confirmés, mais l'article est signé **Célia Séramour**, pas par le média comme auteur. Le commentaire disant que la page est inaccessible/403 est périmé. |
| `alan_mo_2024` | oui | À RÉPARER | Même problème : titre/date/URL confirmés, article signé **Célia Séramour**. Le commentaire “headline only / 403” est périmé. |
| `truongkoyejo2026aims` | oui | VALIDE | Titre, auteurs et citation confirmés sur la page Stanford AIMS. Exception manuelle justifiée tant que le vérificateur produit le faux appariement DBLP documenté. |

## Erreurs dans les commentaires de whitelist

Même lorsque la notice est correcte, plusieurs commentaires donnent une fausse assurance ou décrivent une autre source :

- `shashikumar2023bioontobert` est annoncé “verified” alors que titre et auteurs sont faux ;
- `tang2024txt360` est annoncé vérifié sans contrôle de la liste d'auteurs officielle ;
- `kittredge_sublanguages_1982` est décrit comme un chapitre de livre, alors que la notice citée est l'article AJCL de 1982 ;
- `gumbel-orig` est décrit comme “Gumbel 1954”, alors que la notice et la source sont de 1935 ;
- `touchent2023camembertbio` est décrit comme “TALN 2023”, alors que la notice correcte est LREC-COLING 2024 ;
- `nabla_agentique_2025` et `alan_mo_2024` sont encore qualifiés de pages 403/non vérifiées, alors que leur contenu complet est maintenant accessible ;
- l'en-tête “real refs” est trop catégorique : la section contient notamment APA, Harris, Ramos et LeCun, qui demandent une correction.

## Sources primaires déterminantes

- BioOntoBERT : [PDF officiel CEUR](https://ceur-ws.org/Vol-3603/Paper9.pdf) et [sommaire CEUR vol. 3603](https://ceur-ws.org/Vol-3603/).
- TxT360 : [carte officielle et bloc BibTeX du dataset](https://huggingface.co/datasets/LLM360/TxT360/blob/main/README.md?code=true).
- DEFT 2020 : [ACL Anthology](https://aclanthology.org/2020.jeptalnrecital-deft.1/).
- DisTEMIST : [CEUR-WS vol. 3180](https://ceur-ws.org/Vol-3180/) et [PDF officiel](https://ceur-ws.org/Vol-3180/paper-11.pdf).
- QUAERO : [carte officielle du corpus et citation](https://huggingface.co/datasets/bigbio/quaero).
- UMLS 1993 : [notice PubMed](https://pubmed.ncbi.nlm.nih.gov/8412823/).
- Kittredge 1982 : [ACL Anthology J82-2006](https://aclanthology.org/J82-2006/).
- ANSM 2023 : [PDF officiel du thésaurus](https://ansm.sante.fr/uploads/2023/09/15/20230915-thesaurus-interactions-medicamenteuses-septembre-2023.pdf).
- Harris 1954 : [notice et DOI éditeur](https://www.tandfonline.com/doi/abs/10.1080/00437956.1954.11659520).
- LeCun 2022 : [PDF officiel OpenReview](https://openreview.net/pdf?id=BZ5a1r-kVsf).
- LDA : [notice officielle JMLR](https://www.jmlr.org/papers/v3/blei03a.html).
- WALS : [instructions de citation officielles](https://wals.info/) et [record v2020.3](https://meta.clld.org/contributions/7385533).
- xFormers : [bloc BibTeX officiel du dépôt](https://github.com/facebookresearch/xformers).
- Zar 2005 : [notice Wiley et DOI](https://onlinelibrary.wiley.com/doi/10.1002/0470011815.b2a15150).
- Articles de presse : [Alan/Mo](https://www.usine-digitale.fr/article/alan-prend-le-virage-de-l-intelligence-artificielle-avec-son-assistant-sante-mo.N2221794), [Nabla](https://www.usine-digitale.fr/article/nabla-leve-60-millions-d-euros-pour-mettre-les-compte-rendus-medicaux-a-l-ere-de-l-agentique.N2233930), [Synapse/MedGPT](https://www.caducee.net/actualite-medicale/16649/synapse-devoile-medgpt-l-assistant-ia-medical-100-francais.html).
- AI Measurement Science : [page et citation Stanford AIMS](https://aimslab.stanford.edu/textbook/).

## Recommandation de maintenance

La correction durable consiste à réduire la whitelist à de vraies exceptions et à renforcer le vérificateur :

1. corriger d'abord les quatre clés citées prioritaires ;
2. déplacer les DOI valides vers le champ `doi` et apprendre au script à reconnaître PMID, ACL Anthology, CEUR, JMLR, OpenReview, Zenodo et les URL officielles ;
3. retirer de la whitelist les articles déjà munis d'un identifiant ou d'une URL primaire ;
4. conserver une petite whitelist séparée pour livres, textes juridiques, pages institutionnelles et billets web, avec une source précise et une date de contrôle ;
5. faire échouer le contrôle si une clé whitelistée n'a ni justification, ni URL/identifiant, ou si sa justification n'a pas été revue récemment.

Cet audit n'a modifié ni `thesis.bib`, ni la whitelist, ni le texte de la thèse.
