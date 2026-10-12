#!/bin/bash
#SBATCH --job-name=laya10k
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:4
#SBATCH --constraint=h100
#SBATCH --time=20:00:00
#SBATCH --account=rua@h100
#SBATCH --output=/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/logs/laya10k_%j.out
#SBATCH --error=/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/logs/laya10k_%j.err

set -euo pipefail
module purge
module load vllm/0.5.4
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1
export VLLM_WORKER_MULTIPROC_METHOD=spawn VLLM_RPC_TIMEOUT=60000
export VLLM_ENGINE_ITERATION_TIMEOUT_S=600 PYTHONUNBUFFERED=1
export LD_LIBRARY_PATH=/lustre/fsn1/projects/rech/rua/uvb79kr/envs/reformulation/lib:${LD_LIBRARY_PATH:-}

ROOT=/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner
SCR=/lustre/fsn1/projects/rech/rua/uvb79kr/onto
cd "$ROOT/gen/laya_biomed"

python generate.py \
  --input "$SCR/medembed-outputs/gliner2-v3b/chunks_v3b.jsonl" \
  --output "$SCR/laya-biomed-v1/questions_10k.jsonl" \
  --limit 10000 --batch_size 128 --tensor_parallel_size 4
