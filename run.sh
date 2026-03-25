#!/bin/bash

#SBATCH --job-name=cellranger_preprocess
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#SBATCH --partition=work

# Exit on any error and ensure job terminates
set -e
trap "exit" INT TERM

# --- 1. Environment Setup ---
export PATH=$PATH:/home/woody/mfn3/mfn3100h/cellranger_dir/cellranger-10.0.0/bin

# Correctly initialize Conda for script usage
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate sopa_env

# Create necessary directories
mkdir -p logs results error_logs .local_bin

# --- 2. Create the sbatch wrapper ---
# We capture the REAL path of tinyfat before we mess with the PATH
REAL_TINYFAT=$(which sbatch.tinyfat)

cat << EOF > .local_bin/sbatch
#!/bin/bash
# Pass all arguments exactly as received to the real tinyfat binary
exec $REAL_TINYFAT "\$@"
EOF

chmod +x .local_bin/sbatch

# Add our local wrapper to the start of the PATH
export PATH="$(pwd)/.local_bin:$PATH"

echo "Redirection active: $(which sbatch) -> $REAL_TINYFAT"

# --- 3. Execute Snakemake ---
# Note: Ensure profiles/slurm/config.yaml DOES NOT have 'submit-instruction'
snakemake \
  --snakefile Snakefile \
  --configfile config.yaml \
  --profile profiles/slurm \
  --executor slurm \
  --use-conda \
  --conda-frontend mamba \
  --slurm-logdir error_logs/ \
  --latency-wait 60

PIPELINE_EXIT_CODE=$?

# --- 4. Cleanup and Status ---
rm -rf .local_bin

if [ $PIPELINE_EXIT_CODE -eq 0 ]; then
  echo "$(date): Pipeline success" >> logs/pipeline_status.log
  echo "$(date): Job completed successfully. Terminating SLURM job." >> logs/pipeline_status.log
else
  echo "$(date): Pipeline failed (Exit: $PIPELINE_EXIT_CODE)" >> error_logs/pipeline_errors.log
  echo "$(date): Job failed. Terminating SLURM job." >> error_logs/pipeline_errors.log
fi

# Terminate the SLURM job immediately after pipeline completes
# This prevents the node from staying allocated after work is done
exit $PIPELINE_EXIT_CODE