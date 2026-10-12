#!/bin/bash
#SBATCH --job-name=ecrf-v3
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --constraint=h100
#SBATCH --account=rua@h100
#SBATCH --time=20:00:00
#SBATCH --output=/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/logs/ecrf_v3_%j.out
#SBATCH --error=/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/logs/ecrf_v3_%j.err

set -euo pipefail
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1

ROOT=/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner
PY=/lustre/fsn1/projects/rech/rua/uvb79kr/envs/v3-schema/bin/python
MODEL=/lustre/fsn1/projects/rech/rua/uvb79kr/onto/v3-schema-decision/model-v2
DATA=/lustre/fsn1/projects/rech/rua/uvb79kr/onto/v3-schema-decision/data
MODE=${MODE:-ce}
OUT=${OUT:?set OUT to an explicit output directory}

cd "$ROOT"
"$PY" v3_schema_decision/train_v3.py \
  --mode "$MODE" --model "$MODEL" --data "$DATA" --out "$OUT" ${EXTRA:-}
