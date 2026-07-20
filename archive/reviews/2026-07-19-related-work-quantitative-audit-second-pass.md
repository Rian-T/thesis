# Audit quantitatif de l'état de l'art — seconde passe

Date : 19 juillet 2026  
Périmètre : les trois chapitres actifs de l'état de l'art et les graphiques externes qui leur sont associés.  
Nature : passe contradictoire centrée sur les dénominateurs, variantes de modèle, régimes d'évaluation, seuils de performance et localisateurs de tableaux. Aucun fichier TeX, BibTeX, Python ou PDF de la thèse n'a été modifié.

## Verdict exécutif

Cette seconde passe ne révèle **aucune nouvelle valeur brute fausse** dans le texte courant. Elle trouve toutefois **deux chiffres exacts présentés sans la condition qui leur donne leur portée**, ainsi qu'une erreur de traçabilité dans le code d'un graphique :

1. le « huit tâches sur dix » de BioMistral vaut pour l'évaluation **3-shot in-context**, tandis que le papier donne sept sur dix après supervised fine-tuning ;
2. les 1,13 heures de MosaicBERT correspondent au temps nécessaire pour atteindre **79,6 de moyenne GLUE-dev**, pas à une durée universelle de préentraînement d'un BERT-base ;
3. le script du graphique LLaMA attribue ses valeurs à la Table 4, alors qu'elles viennent de la **Table 3**. La légende TeX est déjà correcte et les valeurs tracées le sont aussi.

Les deux premières formulations sont faciles à sécuriser en ajoutant quelques mots. Elles ne demandent ni changement de structure ni remise en cause de l'argument. Le troisième point est une correction de commentaire Python, sans effet sur le manuscrit rendu.

## Instantané contrôlé

Les numéros de ligne de ce rapport correspondent aux fichiers suivants :

- `sources/related_works/language_modeling.tex` : `d1f2c8175a98517937abdb6acf72bc02f87a0085540407ef9e6deb9dda29dbb8` ;
- `sources/related_works/corpus_annotation.tex` : `92293b698692ff151170be13bba8a58580a6a2c10d9c01a29d03f1df341ae194` ;
- `sources/related_works/clinical_ie.tex` : `595576abf15f2f5fab2ba830aa7cfb2a47d2f563dbfcfebab372e1fc0764418c`.

Les constats déjà consignés dans les audits précédents ont été exclus des nouveaux résultats. Les points encore présents concernant les statistiques vivantes, les longueurs cliniques, la CIM/CCAM/ATC ou la portée juridique ne sont donc pas recomptés ici.

## Nouveaux constats

### Q2-LM-1 — Les huit victoires de BioMistral dépendent du régime 3-shot

- **Emplacement** : `sources/related_works/language_modeling.tex:1108-1112`.
- **Texte actuel** : BioMistral aurait battu Mistral 7B Instruct sur huit des dix tâches médicales.
- **Valeur brute** : exacte dans la Table 2 de l'article.
- **Condition omise** : la Table 2 est une évaluation **3-shot in-context**, répétée avec trois ensembles de démonstrations tirés aléatoirement ; aucun modèle n'y est fine-tuné sur les tâches. Dans la Table 3, après supervised fine-tuning, BioMistral bat Mistral 7B Instruct sur **sept tâches sur dix**.
- **Recalcul de la Table 2** : BioMistral est supérieur sur Clinical Knowledge, Medical Genetics, Anatomy, Professional Medicine, College Medicine, MedQA, MedQA 5 options et MedMCQA ; il est inférieur sur College Biology et PubMedQA, soit bien 8/10.
- **Source primaire** : [Labrak et al., 2024, Table 2 et §5.1](https://aclanthology.org/2024.findings-acl.348.pdf).
- **Verdict** : chiffre exact, portée insuffisamment qualifiée. Sans « 3-shot », la phrase peut être comprise comme une propriété générale du modèle, alors que le papier lui-même montre un autre décompte sous SFT.
- **Correction minimale proposée** :

  > BioMistral continued Mistral~7B on PubMed Central and reported that, in its 3-shot in-context evaluation, the adapted model beat Mistral~7B Instruct on eight of ten medical question-answering tasks.

### Q2-LM-2 — Les 1,13 heures de MosaicBERT sont liées à un score cible de 79,6

- **Emplacement** : `sources/related_works/language_modeling.tex:1150-1156`.
- **Texte actuel** : les modifications « let the authors train a BERT-base model in about 1.13 hours » sur huit A100, pour environ vingt dollars.
- **Valeurs brutes** : 1,13 h, huit A100 80 GB et environ 20 dollars sont toutes exactes.
- **Conditions omises** : le modèle est **MosaicBERT-Base**, qui possède 137 millions de paramètres, et le point de 1,13 h est défini par une moyenne **GLUE-dev de 79,6**. La Table 1 montre plusieurs durées selon le score atteint : MosaicBERT-Base atteint 83,2 en 4,6 h ; le BERT-Base de référence atteint ce même 83,2 en 11,5 h.
- **Source primaire** : [Portes et al., 2023, résumé, Table 1 et §3.1](https://arxiv.org/pdf/2312.17482).
- **Verdict** : la formulation actuelle transforme un point d'une courbe qualité-temps en durée absolue de « training ». Elle peut aussi être lue comme concernant le BERT-Base standard plutôt que MosaicBERT-Base.
- **Correction minimale proposée** :

  > Together these let MosaicBERT-Base reach a 79.6 average GLUE development score in about 1.13 hours on eight A100 80 GB GPUs, for roughly twenty dollars.

Cette version reprend exactement la revendication du papier sans ajouter les autres points de la courbe.

### Q2-PLOT-1 — Le commentaire source du graphique LLaMA pointe vers le mauvais tableau

- **Emplacement** : `plots/related_works/llama_vs_gpt3.py:4`.
- **Texte actuel du script** : « Table 4 (`tab:commonsense`) ».
- **Contrôle** : les lignes GPT-3 175B et LLaMA 13B utilisées par le script se trouvent dans la **Table 3**, intitulée « Zero-shot performance on Common Sense Reasoning tasks ». La Table 4 porte sur NaturalQuestions.
- **Source primaire** : [Touvron et al., 2023, Tables 3–4](https://arxiv.org/pdf/2302.13971).
- **Impact scientifique** : aucun. Les quatorze valeurs du script sont correctes, LLaMA 13B est supérieur sur cinq des sept tâches tracées, et la légende de `language_modeling.tex` pointe déjà vers la Table 3.
- **Correction minimale proposée** : remplacer uniquement `Table 4` par `Table 3` dans le commentaire du script.

## Contre-vérifications n'ayant pas produit de nouveau constat

### Meditron

La comparaison a été relue directement dans la Figure 3 du papier. Meditron-70B y dépasse bien le modèle nommé GPT-3.5 par les auteurs sur les quatre benchmarks affichés et dépasse les valeurs disponibles de Med-PaLM. Le papier précise que « GPT-3.5 » désigne ici `text-davinci-003`, que les résultats commerciaux sont repris de leurs articles respectifs et que Meditron utilise son meilleur régime avec self-consistency chain-of-thought. La phrase actuelle reste donc soutenue au niveau où elle est formulée. La prudence « in the reported evaluation » déjà évoquée dans l'audit de fidélité demeure possible, mais ce n'est pas un nouveau contresens quantitatif. Source : [Chen et al., 2023, Figure 3 et §6](https://arxiv.org/pdf/2311.16079).

### FlashAttention

Le « jusqu'à environ trois fois plus rapide » reste défendable. L'article rapporte 3× d'accélération end-to-end sur GPT-2 et, dans ses mesures du noyau d'attention sur A100, généralement 2–4× selon longueur, masque et dimension de tête. La valeur ne doit pas être lue comme constante pour tous les matériels — le papier donne aussi 15 % sur BERT-large — mais l'expression « up to » du texte évite précisément cette généralisation. Source : [Dao et al., 2022, résumé et annexe E.5](https://arxiv.org/pdf/2205.14135).

### LLaMA et Chinchilla

- Les quatorze valeurs du graphique LLaMA sont identiques à la Table 3 ; seule la docstring du script se trompe de numéro de table.
- Les points du graphique Chinchilla restent conformes à la Table 3, approche 1. Aucune permutation entre paramètres, tokens et FLOPs n'a été trouvée.

### E3C et DrBenchmark

La lecture des étiquettes publiées dans l'annexe de DrBenchmark confirme que la tâche clinique E3C utilise bien `O` et une seule classe `CLINENTITY`. Les totaux de vingt tâches et douze jeux de données restent également corrects. Source : [Labrak et al., 2024, Tables 1–2 et annexe B.4](https://aclanthology.org/2024.lrec-main.478.pdf).

## Priorité de correction proposée

1. Ajouter « in its 3-shot in-context evaluation » à BioMistral.
2. Remplacer « a BERT-base model » par « MosaicBERT-Base » et ajouter le seuil « 79.6 average GLUE development score ».
3. Corriger `Table 4` en `Table 3` dans la docstring du script LLaMA.

## Conclusion

La seconde passe renforce plutôt qu'elle n'affaiblit le verdict précédent : les valeurs numériques de l'état de l'art sont globalement fiables. Les prises restantes viennent surtout de l'effacement d'une condition expérimentale. BioMistral et MosaicBERT peuvent être rendus inattaquables avec une précision d'une demi-proposition chacun ; aucun recalcul de tableau ni changement de figure n'est nécessaire.
