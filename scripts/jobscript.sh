#!/bin/bash
# Snakemake jobscript for SLURM
# This is the job submission template
#SBATCH --job-name=scRNAseq_vdj_preprocessing
#SBATCH --cpus-per-task={resources.cpus_per_task}
#SBATCH --mem={resources.mem_mb}
#SBATCH --time={resources.runtime}
#SBATCH --partition={resources.slurm_partition}
#SBATCH --output={log}.out
#SBATCH --error={log}.err

set -euo pipefail

{exec_job}
