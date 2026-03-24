"""
Snakemake pipeline for running Cellranger Multi
"""

import pandas as pd
import os
import shutil

configfile: "config.yaml"

SAMPLES = pd.read_csv(config["sample_sheet"], sep="\t")["sample_id"].tolist()
PIPELINE_DIR = os.path.dirname(os.path.abspath(workflow.snakefile))

rule all:
    input:
        expand("cellranger_outputs_2/{sample}/finished.log", sample=SAMPLES),
        "results/merged_qc_metrics.csv"

rule cellranger_multi:
    params:
        sample_id="{sample}",
        # We need the absolute path to the CSV because we 'cd' in the shell
        csv=lambda w: os.path.abspath(os.path.join(PIPELINE_DIR, config["cellranger_multi_configs"][w.sample])),
        localcores=config.get("cellranger_cores", 10),
        localmem=config.get("cellranger_mem", 180)
    output:
        # Snakemake will only look for this file to verify success
        done="cellranger_outputs_2/{sample}/finished.log"
    shell:
        """
        mkdir -p cellranger_outputs_2
        
        # Use a subshell ( (cmds) ) so the 'cd' doesn't affect the rest of the script
        (
            cd cellranger_outputs_2
            
            # Clean up if a previous run failed and left a directory
            if [ -d "{params.sample_id}" ]; then
                rm -rf "{params.sample_id}"
            fi
            
            cellranger multi \
                --id={params.sample_id} \
                --csv={params.csv} \
                --localcores={params.localcores} \
                --localmem={params.localmem}
        )
        
        # After the subshell finishes successfully, create the flag
        touch {output.done}
        """

rule merge_qc_metrics:
    input:
        expand("cellranger_outputs_2/{sample}/outs/qc_sample_metrics.csv", sample=SAMPLES)
    output:
        "results/merged_qc_metrics.csv"
    params:
        script=os.path.join(PIPELINE_DIR, "scripts/merge_qc_metrics.py"),
        output_dir=os.path.abspath("results")
    shell:
        """
        mkdir -p {params.output_dir}
        
        # Copy individual QC metrics to a temporary directory with unique names
        tmpdir=$(mktemp -d)
        
        # Create an array to store sample names for proper naming
        declare -a samples=({SAMPLES})
        i=0
        for file in {input}; do
            sample=${{samples[$i]}}
            cp "$file" "$tmpdir/${{sample}}_qc_metrics.csv"
            i=$((i + 1))
        done
        
        # Run the merge script in the temporary directory
        cd "$tmpdir"
        python {params.script}
        
        # Move the merged file to the output location with absolute path
        mv combined_samples.csv {params.output_dir}/merged_qc_metrics.csv
        
        # Clean up
        rm -rf "$tmpdir"
        """