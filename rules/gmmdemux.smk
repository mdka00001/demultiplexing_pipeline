"""
Demultiplexing of filtered matrices using GMM-demux
"""

rule gmmdemux:
    input:
        matrix="cellranger_outputs_2/{sample}/outs/filtered_feature_bc_matrix",
        cell_counts="results/total_cells_per_sample.csv"
    output:
        directory("results/gmm_demux_output/{sample}"),
        done="results/gmm_demux_output/{sample}/finished.log"
    params:
        sample_id="{sample}",
        output_dir=lambda w: os.path.abspath(f"results/gmm_demux_output/{w.sample}"),
        hashtags=config.get("gmmdemux_hashtags", "Hash-tag1,Hash-tag2,Hash-tag3"),
    shell:
        """
        set -e
        mkdir -p {params.output_dir}
        
        # Extract total cell count for this sample from CSV
        total_cells=$(tail -n +2 {input.cell_counts} | grep "{params.sample_id}" | cut -d',' -f2)
        
        echo "Processing {params.sample_id} with $total_cells cells"
        
        # Run GMM-demux on each sample's filtered feature matrix with cell count and simplified output
        GMM-demux \
            {input.matrix} \
            {params.hashtags} \
            --output "{params.output_dir}" \
            --simplified "{params.output_dir}"

        touch {output.done}
        """

