"""
Plotting rules for QC visualization
"""

localrules: generate_tag_qc_plots, generate_vdj_venn_diagrams


rule generate_tag_qc_plots:
    """
    Generate QC comparison plots for cell tag assignments (GEX, TCR, BCR)
    Creates PDF files comparing Cellranger vs GMM-demux cell counts
    """
    input:
        expand("results/tag_quantification/{sample}/gex_quantification.csv", sample=SAMPLES),
        expand("results/tag_quantification/{sample}/vdj_t_quantification.csv", sample=SAMPLES),
        expand("results/tag_quantification/{sample}/vdj_b_quantification.csv", sample=SAMPLES)
    output:
        gex_pdf="results/figures/sample_tag_qc/gex_tag_qc.pdf",
        tcr_pdf="results/figures/sample_tag_qc/vdj_t_tag_qc.pdf",
        bcr_pdf="results/figures/sample_tag_qc/vdj_b_tag_qc.pdf"
    log:
        "logs/plotting/generate_tag_qc_plots.log"
    shell:
        """
        /home/hpc/mfn3/mfn3100h/.conda/envs/sopa_env/bin/python scripts/figure_scripts/cell_tag_qc_plot.py > {log} 2>&1
        """


rule generate_vdj_venn_diagrams:
    """
    Generate Venn diagrams comparing Cellranger vs GMM-demux barcode assignments
    for demultiplexed VDJ (TCR and BCR) outputs
    """
    input:
        expand("results/vdj_demultiplex/{sample}/demultiplexed_vdj_tcr_annotations.csv", sample=SAMPLES),
        expand("results/vdj_demultiplex/{sample}/demultiplexed_vdj_bcr_annotations.csv", sample=SAMPLES)
    output:
        tcr_venn="results/figures/sample_tag_qc/vdj_t_venn_diagram.pdf",
        bcr_venn="results/figures/sample_tag_qc/vdj_b_venn_diagram.pdf"
    log:
        "logs/plotting/generate_vdj_venn_diagrams.log"
    shell:
        """
        /home/hpc/mfn3/mfn3100h/.conda/envs/sopa_env/bin/python scripts/figure_scripts/cell_tag_venn_plot.py > {log} 2>&1
        """
