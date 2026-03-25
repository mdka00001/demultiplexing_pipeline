# VDJ Demultiplexing Rules
# Reassign VDJ cells based on GMM-demux outputs for TCR and BCR separately
# Consolidated into single rule to process all samples efficiently

localrules: demultiplex_all_vdj

rule demultiplex_all_vdj:
    """
    Process VDJ demultiplexing for all samples at once
    Runs locally on head node with minimal resource overhead
    Generates both TCR and BCR outputs for all samples in a single job
    """
    input:
        tcr_inputs=expand("cellranger_outputs_2/{sample}/outs/vdj_t/all_contig_annotations.csv", sample=SAMPLES),
        bcr_inputs=expand("cellranger_outputs_2/{sample}/outs/vdj_b/all_contig_annotations.csv", sample=SAMPLES),
        gmm_simplified=expand("results/gmm_demux_output/{sample}/GMM_simplified.csv", sample=SAMPLES),
        configs=expand("metadata/sample_configs/{sample}_config.csv", sample=SAMPLES)
    output:
        tcr_outputs=expand("results/vdj_demultiplex/{sample}/demultiplexed_vdj_tcr_annotations.csv", sample=SAMPLES),
        bcr_outputs=expand("results/vdj_demultiplex/{sample}/demultiplexed_vdj_bcr_annotations.csv", sample=SAMPLES)
    params:
        script="scripts/vdj_demultiplex.py",
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
script = "{params.script}"

for sample in samples:
    vdj_types = [('T', 'vdj_t'), ('B', 'vdj_b')]
    
    for vdj_type, vdj_dir in vdj_types:
        gmm_file = f"{{pipeline_dir}}/results/gmm_demux_output/{{sample}}/GMM_simplified.csv"
        vdj_file = f"{{pipeline_dir}}/cellranger_outputs_2/{{sample}}/outs/{{vdj_dir}}/all_contig_annotations.csv"
        output_file = f"{{pipeline_dir}}/results/vdj_demultiplex/{{sample}}/demultiplexed_vdj_{{vdj_type.lower()}}cr_annotations.csv"
        config_file = f"{{pipeline_dir}}/metadata/sample_configs/{{sample}}_config.csv"
        
        # Create output directory
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Run demultiplexing
        cmd = [sys.executable, script, gmm_file, vdj_file, output_file, config_file, vdj_type]
        print(f"Processing {{sample}} {{vdj_type}}...")
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"Error processing {{sample}} {{vdj_type}}")
            sys.exit(1)

print("All VDJ demultiplexing completed successfully")
SCRIPT
        """
