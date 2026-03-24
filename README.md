# Minimal Snakemake + SLURM Pipeline

A minimal snakemake pipeline for preprocessing Cellranger Multi outputs.

## Features

- **GEX processing**: Quality filtering and normalization
- **HTO demultiplexing**: Simple HTO assignment for cell hashing
- **VDJ processing**: B and T cell receptor clonotype filtering
- **QC report**: Summary statistics for all samples
- **SLURM integration**: Automatic job submission and resource management

## Setup

1. **Update config.yaml**: Add your cellranger output paths and sample configurations
2. **Update samples.tsv**: List your sample IDs
3. **Make run.sh executable**: `chmod +x run.sh`

## Running the Pipeline

```bash
# Submit to SLURM
sbatch run.sh

# Or run locally (testing)
bash run.sh
```

## Directory Structure

```
.
├── Snakefile          # Main pipeline rules
├── config.yaml        # Configuration (edit with your data)
├── samples.tsv        # Sample list
├── run.sh             # SLURM submission script
├── scripts/           # Python processing scripts
│   └── jobscript.sh
├── envs/              # Conda environments
│   └── scanpy.yaml
├── logs/              # Job logs and error files
└── results/           # Output directory (created on run)
```

## Customization

- Edit `config.yaml` for filtering parameters
- Modify script files for custom preprocessing logic
- Adjust SLURM parameters in `run.sh` and `jobscript.sh`

## Dependencies

- Snakemake
- Conda/Mamba
- SLURM (for HPC execution)
- Python packages: scanpy, pandas, numpy, muon
