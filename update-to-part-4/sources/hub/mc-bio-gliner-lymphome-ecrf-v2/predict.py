"""Remplir un eCRF depuis un dossier patient — exemple exécutable.

    pip install gliner2 torch huggingface_hub
    python predict.py --text dossier.txt
    python predict.py --demo                 # sur un extrait fourni

Ne dépend que de `modeling_assign.py`, fourni dans ce dépôt.
"""
import argparse
import json
from pathlib import Path

DEMO = """=== Compte-rendu de RCP — 2017-04-15 ===
Patiente de 62 ans, retraitée, vit seule dans un appartement à Nancy.
Diagnostic le 8 avril 2017 d'un lymphome B diffus à grandes cellules, stade IIIB.
Biopsie ganglionnaire axillaire. Phénotype non germinal. Aucun réarrangement des gènes MYC.
LDH à 450 UI/L. Décision : R-CHOP x8.

=== Compte-rendu de TEP-TDM — 2017-10-02 ===
SUVmax 12.4, plus grande lésion 68 mm. Réponse complète métabolique.

=== Courrier au médecin traitant — 2020-03-15 ===
Patiente en rémission complète. Dernière consultation ce jour, état général conservé.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="rntc/mc-bio-gliner-lymphome-ecrf")
    ap.add_argument("--text", help="fichier texte du dossier patient")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--device", default="cpu", help="cuda si disponible")
    ap.add_argument("--json", help="écrire le résultat en JSON")
    a = ap.parse_args()

    if not a.text and not a.demo:
        ap.error("donner --text FICHIER ou --demo")
    text = DEMO if a.demo else Path(a.text).read_text(encoding="utf-8")

    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from modeling_assign import ECRFExtractor

    print(f"chargement de {a.model} sur {a.device}…", flush=True)
    m = ECRFExtractor.from_pretrained(a.model, device=a.device)
    ecrf = m.extract(text)

    rempli = {k: v for k, v in ecrf.items() if v["value"] is not None}
    print(f"\n{len(rempli)} champs remplis sur {len(ecrf)}\n")
    section = None
    for k in sorted(rempli, key=lambda x: (m.schema[x]["section"], x)):
        r = rempli[k]
        sec = m.schema[k]["section"]
        if sec != section:
            print(f"  [{sec}]"); section = sec
        src = (f"{r['span']!r} @{r['start']}-{r['end']}" if r["source"] == "text"
               else "(inféré, aucun passage source)")
        print(f"    {m.schema[k]['label'][:36]:36s} {str(r['value'])[:20]:20s} "
              f"conf={r['confidence']:.2f} norm={r['normalization_confidence']:.2f}  {src}")

    if a.json:
        Path(a.json).write_text(json.dumps(ecrf, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n-> {a.json}")


if __name__ == "__main__":
    main()
