#!/bin/bash
#SBATCH --job-name=styleSOTA
#SBATCH --nodes=1 --ntasks-per-node=1 --cpus-per-task=16
#SBATCH --gres=gpu:1 --constraint=h100
#SBATCH --account=rua@h100
#SBATCH --time=02:00:00
#SBATCH --output=/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/logs/%x_%j.out
#SBATCH --error=/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/logs/%x_%j.err
set -euo pipefail
L=/lustre/fsn1/projects/rech/rua/uvb79kr
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
cd /lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner

# LE remplacant du "C2ST mots-fonction" (0.858 / 0.901), qui etait bricole ET fuite
# (standardisation calculee sur train+test avant la validation croisee, style_test.py:127).
#
# Ici : 4 metriques distributionnelles dans l espace MedEmbed, reference = PARHAF
# (VRAI texte hospitalier, pas E3C), et le C2ST sur embeddings n a PAS de fuite
# (aucun preprocessing avant cross_val_score).
$L/envs/tabib-C39hfyYp-py3.12/bin/python gen/stylometry/sota_dist_test.py
echo "=== done ==="
