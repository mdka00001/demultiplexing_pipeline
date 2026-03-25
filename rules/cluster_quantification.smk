"""
Cluster quantification rule - counts cluster_id occurrences from GMM simplified output
"""

rule cluster_quantification:
    input:
        "results/gmm_demux_output/{sample}/GMM_simplified.csv"
    output:
        "results/cluster_quantification/{sample}/cluster_quantification.csv"
    params:
        script=os.path.join(PIPELINE_DIR, "scripts/cluster_quantification.py"),
        cluster_col = "Cluster_id"
    shell:
        """
        mkdir -p $(dirname {output})
        python {params.script} {input} {output} {params.cluster_col}
        """
