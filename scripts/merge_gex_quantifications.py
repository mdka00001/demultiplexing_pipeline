import pandas as pd
import os

def merge_gex_quantifications(cellranger_tag_summary, cluster_quantification, config_file, output_file):
    """
    Merge Cellranger and GMM-demux GEX quantifications side by side for comparison
    
    Args:
        cellranger_tag_summary: Path to cellranger tag_calls_summary.csv
        cluster_quantification: Path to GMM-demux cluster_quantification.csv
        config_file: Path to sample config file
        output_file: Output path for merged quantification
    """
    
    # Check if files exist
    if not os.path.exists(cellranger_tag_summary):
        print(f"Error: Cellranger file '{cellranger_tag_summary}' not found")
        return
    
    if not os.path.exists(cluster_quantification):
        print(f"Error: Cluster quantification file '{cluster_quantification}' not found")
        return
    
    if not os.path.exists(config_file):
        print(f"Error: Config file '{config_file}' not found")
        return
    
    # ===== Load Cellranger data =====
    print(f"Loading cellranger tag calls summary from {cellranger_tag_summary}")
    cellranger_df = pd.read_csv(cellranger_tag_summary)
    
    # Extract individual tag counts
    cellranger_data = {}
    for category in ['C1', 'C2', 'C3']:
        matching_rows = cellranger_df[cellranger_df['Category'] == category]
        if len(matching_rows) > 0:
            cellranger_data[category] = {
                'CR_num_cells': int(matching_rows.iloc[0]['num_cells']),
                'CR_pct_cells': float(matching_rows.iloc[0]['pct_cells'])
            }
    
    # ===== Load sample config =====
    print(f"Loading sample configuration from {config_file}")
    hashtag_to_sample = {}
    with open(config_file, 'r') as f:
        in_samples_section = False
        for line in f:
            line = line.strip()
            if line == '[samples]':
                in_samples_section = True
                continue
            if line.startswith('[') and in_samples_section:
                break
            if in_samples_section and line and not line.startswith('sample_id'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    sample_id = parts[0]
                    hashtag_id = parts[2]
                    hashtag_to_sample[hashtag_id] = sample_id
    
    print(f"Hashtag to Sample mapping: {hashtag_to_sample}")
    
    # ===== Load GMM-demux data =====
    print(f"\nLoading GMM-demux cluster quantification from {cluster_quantification}")
    cluster_df = pd.read_csv(cluster_quantification)
    
    # Cluster to hashtag mapping
    import re
    cluster_to_hashtag = {
        0: 'negative',
        1: 'Hash-tag1',
        2: 'Hash-tag2',
        3: 'Hash-tag3',
        4: 'MSM',
        5: 'Unclear'
    }
    
    # Create cluster to sample mapping
    cluster_to_sample = {}
    for hashtag_id, sample_id in hashtag_to_sample.items():
        match = re.search(r'(\d+)', hashtag_id)
        if match:
            cluster_num = int(match.group(1))
            cluster_to_sample[cluster_num] = sample_id
    
    # Map clusters to samples and aggregate
    cluster_df['sample_id'] = cluster_df['Cluster_id'].map(cluster_to_sample)
    gmm_quantification = cluster_df.groupby('sample_id')['count'].sum().reset_index()
    gmm_quantification.columns = ['sample_id', 'GMM_num_cells']
    
    total_gmm_cells = gmm_quantification['GMM_num_cells'].sum()
    gmm_quantification['GMM_pct_cells'] = (gmm_quantification['GMM_num_cells'] / total_gmm_cells * 100).round(1)
    
    print(f"\nGMM-demux Quantification:")
    print(gmm_quantification)
    
    # ===== Create output dataframe =====
    # Create rows for each sample
    output_rows = []
    for sample_id in sorted(hashtag_to_sample.values()):
        row = {'sample_id': sample_id}
        
        # Add Cellranger data for this sample's hashtags (default to 0 if not found)
        cr_num_cells = 0
        cr_pct_cells = 0.0
        for hashtag_id, cr_sample in hashtag_to_sample.items():
            if cr_sample == sample_id:
                if hashtag_id in cellranger_data:
                    cr_num_cells = cellranger_data[hashtag_id]['CR_num_cells']
                    cr_pct_cells = cellranger_data[hashtag_id]['CR_pct_cells']
        
        row['CR_num_cells'] = cr_num_cells
        row['CR_pct_cells'] = cr_pct_cells
        
        # Add GMM-demux data for this sample (default to 0 if not found)
        gmm_num_cells = 0
        gmm_pct_cells = 0.0
        gmm_row = gmm_quantification[gmm_quantification['sample_id'] == sample_id]
        if len(gmm_row) > 0:
            gmm_num_cells = int(gmm_row.iloc[0]['GMM_num_cells'])
            gmm_pct_cells = gmm_row.iloc[0]['GMM_pct_cells']
        
        row['GMM_num_cells'] = gmm_num_cells
        row['GMM_pct_cells'] = gmm_pct_cells
        
        output_rows.append(row)
    
    output_df = pd.DataFrame(output_rows)
    output_df = output_df[['sample_id', 'CR_num_cells', 'CR_pct_cells', 'GMM_num_cells', 'GMM_pct_cells']]
    
    print(f"\nMerged GEX Quantification (Cellranger vs GMM-demux):")
    print(output_df)
    
    # Save to file
    output_df.to_csv(output_file, index=False)
    print(f"\nMerged quantification saved to: {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: python merge_gex_quantifications.py <cellranger_tag_summary> <cluster_quantification> <config_file> <output_file>")
        sys.exit(1)
    
    cellranger_tag_summary = sys.argv[1]
    cluster_quantification = sys.argv[2]
    config_file = sys.argv[3]
    output_file = sys.argv[4]
    
    merge_gex_quantifications(cellranger_tag_summary, cluster_quantification, config_file, output_file)
