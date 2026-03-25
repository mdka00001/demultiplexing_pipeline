"""
Snakemake pipeline for running Cellranger Multi
"""

import pandas as pd
import os

configfile: "config.yaml"

SAMPLES = pd.read_csv(config["sample_sheet"], sep="\t")["sample_id"].tolist()
PIPELINE_DIR = os.path.dirname(os.path.abspath(workflow.snakefile))

# Wildcard constraint to ensure sample names don't include slashes
wildcard_constraints:
    sample="[^/]+"

# Include modular rule files
include: "rules/cellranger.smk"
include: "rules/qc.smk"
include: "rules/gmmdemux.smk"
include: "rules/cellcount.smk"
include: "rules/cluster_quantification.smk"
include: "rules/vdj_demultiplex.smk"
include: "rules/tag_quantification.smk"
include: "rules/plotting.smk"

rule all:
    input:
        expand("cellranger_outputs_2/{sample}/finished.log", sample=SAMPLES),
        "results/merged_qc_metrics.csv",
        "results/total_cells_per_sample.csv",
        expand("results/gmm_demux_output/{sample}/finished.log", sample=SAMPLES),
        expand("results/cluster_quantification/{sample}/cluster_quantification.csv", sample=SAMPLES),
        expand("results/vdj_demultiplex/{sample}/demultiplexed_vdj_tcr_annotations.csv", sample=SAMPLES),
        expand("results/vdj_demultiplex/{sample}/demultiplexed_vdj_bcr_annotations.csv", sample=SAMPLES),
        expand("results/tag_quantification/{sample}/vdj_t_quantification.csv", sample=SAMPLES),
        expand("results/tag_quantification/{sample}/vdj_b_quantification.csv", sample=SAMPLES),
        expand("results/tag_quantification/{sample}/gex_quantification.csv", sample=SAMPLES),
        "results/figures/sample_tag_qc/gex_tag_qc.pdf",
        "results/figures/sample_tag_qc/vdj_t_tag_qc.pdf",
        "results/figures/sample_tag_qc/vdj_b_tag_qc.pdf",
        "results/figures/sample_tag_qc/vdj_t_venn_diagram.pdf",
        "results/figures/sample_tag_qc/vdj_b_venn_diagram.pdf"
