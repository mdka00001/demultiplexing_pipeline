"""
QC metrics merging rule
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
