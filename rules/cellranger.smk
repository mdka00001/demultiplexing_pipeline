"""
Cellranger Multi execution rule
"""

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
