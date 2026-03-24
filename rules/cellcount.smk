"""
Cell counting per sample rule
"""

rule total_cells_per_sample:
    input:
        expand("cellranger_outputs_2/{sample}/outs/qc_library_metrics.csv", sample=SAMPLES)
    output:
        "results/total_cells_per_sample.csv"
    params:
        script=os.path.join(PIPELINE_DIR, "scripts/total_cells_per_sample.py"),
        output_dir=os.path.abspath("results")
    shell:
        """
        mkdir -p {params.output_dir}
        cd {PIPELINE_DIR}
        python {params.script}
        mv total_cells_per_sample.csv {params.output_dir}/total_cells_per_sample.csv
        """
