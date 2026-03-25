# Sample Tag Assignment Quantification Rules
# Consolidated to process all samples efficiently in a single job on one node

localrules: quantify_all_tags

rule quantify_all_tags:
    """
    Quantify VDJ and GEX sample assignments for all samples at once
    Runs locally on head node with minimal resource overhead
    Generates VDJ-T, VDJ-B, and GEX quantification for all samples in a single job
    """
    input:
        vdj_tcr=expand("results/vdj_demultiplex/{sample}/demultiplexed_vdj_tcr_annotations.csv", sample=SAMPLES),
        vdj_bcr=expand("results/vdj_demultiplex/{sample}/demultiplexed_vdj_bcr_annotations.csv", sample=SAMPLES),
        gex_inputs=expand("cellranger_outputs_2/{sample}/outs/multiplexing_analysis/tag_calls_summary.csv", sample=SAMPLES),
        cluster_quants=expand("results/cluster_quantification/{sample}/cluster_quantification.csv", sample=SAMPLES),
        configs=expand("metadata/sample_configs/{sample}_config.csv", sample=SAMPLES)
    output:
        vdj_t_quants=expand("results/tag_quantification/{sample}/vdj_t_quantification.csv", sample=SAMPLES),
        vdj_b_quants=expand("results/tag_quantification/{sample}/vdj_b_quantification.csv", sample=SAMPLES),
        gex_quants=expand("results/tag_quantification/{sample}/gex_quantification.csv", sample=SAMPLES)
    params:
        vdj_quant_script="scripts/quantify_vdj_demultiplex.py",
        gex_quant_script="scripts/merge_gex_quantifications.py",
        samples=SAMPLES,
        pipeline_dir=os.getcwd()
    shell:
        """
        python << 'SCRIPT'
import os
import subprocess
import sys

pipeline_dir = "{params.pipeline_dir}"
samples = {params.samples!r}
vdj_script = "{params.vdj_quant_script}"
gex_script = "{params.gex_quant_script}"

for sample in samples:
    print(f"\\n=== Processing {{sample}} ===")
    
    # Create output directory
    output_dir = f"{{pipeline_dir}}/results/tag_quantification/{{sample}}"
    os.makedirs(output_dir, exist_ok=True)
    
    # VDJ Quantification
    vdj_tcr_file = f"{{pipeline_dir}}/results/vdj_demultiplex/{{sample}}/demultiplexed_vdj_tcr_annotations.csv"
    vdj_bcr_file = f"{{pipeline_dir}}/results/vdj_demultiplex/{{sample}}/demultiplexed_vdj_bcr_annotations.csv"
    vdj_t_output = f"{{output_dir}}/vdj_t_quantification.csv"
    vdj_b_output = f"{{output_dir}}/vdj_b_quantification.csv"
    
    cmd = [sys.executable, vdj_script, vdj_tcr_file, vdj_bcr_file, vdj_t_output, vdj_b_output]
    print(f"VDJ Quantification for {{sample}}...")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"Error in VDJ quantification for {{sample}}")
        sys.exit(1)
    
    # GEX Quantification
    tag_calls = f"{{pipeline_dir}}/cellranger_outputs_2/{{sample}}/outs/multiplexing_analysis/tag_calls_summary.csv"
    cluster_quant = f"{{pipeline_dir}}/results/cluster_quantification/{{sample}}/cluster_quantification.csv"
    config_file = f"{{pipeline_dir}}/metadata/sample_configs/{{sample}}_config.csv"
    gex_output = f"{{output_dir}}/gex_quantification.csv"
    
    cmd = [sys.executable, gex_script, tag_calls, cluster_quant, config_file, gex_output]
    print(f"GEX Quantification for {{sample}}...")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"Error in GEX quantification for {{sample}}")
        sys.exit(1)

print("\\nAll tag quantifications completed successfully")
SCRIPT
        """
