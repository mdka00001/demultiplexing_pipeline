"""
Snakemake pipeline for running Cellranger Multi
"""

import pandas as pd
import os

configfile: "config.yaml"

SAMPLES = pd.read_csv(config["sample_sheet"], sep="\t")["sample_id"].tolist()
PIPELINE_DIR = os.path.dirname(os.path.abspath(workflow.snakefile))

# Include modular rule files
include: "rules/cellranger.smk"
include: "rules/qc.smk"
include: "rules/gmmdemux.smk"
include: "rules/cellcount.smk"

rule all:
    input:
        expand("cellranger_outputs_2/{sample}/finished.log", sample=SAMPLES),
        "results/merged_qc_metrics.csv",
        "results/total_cells_per_sample.csv",
        expand("results/gmm_demux_output/{sample}/finished.log", sample=SAMPLES)
