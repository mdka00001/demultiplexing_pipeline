import pandas as pd
import os
import re

def load_sample_config(config_file):
    """
    Load the sample configuration file and extract hashtag_ids to sample_id mapping.
    
    Args:
        config_file: Path to sample config CSV (e.g., sample_1_config.csv)
    
    Returns:
        Dictionary mapping hashtag_id (e.g., 'C1') to sample_id (e.g., 'SLE_8')
    """
    config = {}
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
                    hashtag_id = parts[2]  # e.g., 'C1', 'C2', 'C3'
                    config[hashtag_id] = sample_id
    
    return config


def create_cluster_to_hashtag_mapping():
    """
    Create mapping from GMM cluster_id to hashtag names.
    Based on typical GMM-demux output where cluster IDs correspond to HTO tags.
    """
    return {
        0: 'negative',
        1: 'Hash-tag1',
        2: 'Hash-tag2',
        3: 'Hash-tag3',
        4: 'MSM',
        5: 'Unclear'
    }


def demultiplex_vdj(gmm_file, vdj_file, output_file, config_file, vdj_type='T'):
    """
    Merge VDJ contig annotations with GMM-demux assignments and assign to sample_ids.
    
    Args:
        gmm_file: Path to GMM_simplified.csv from GMM-demux
        vdj_file: Path to VDJ contig annotations (all_contig_annotations.csv)
        output_file: Output path for demultiplexed VDJ file
        config_file: Path to sample config file (e.g., sample_1_config.csv)
        vdj_type: 'T' for TCR or 'B' for BCR
    """
    
    # Check if files exist
    if not os.path.exists(gmm_file):
        print(f"Error: GMM file '{gmm_file}' not found")
        return
    
    if not os.path.exists(vdj_file):
        print(f"Error: VDJ file '{vdj_file}' not found")
        return
    
    if not os.path.exists(config_file):
        print(f"Error: Config file '{config_file}' not found")
        return
    
    # Load the GMM-Demux assignments (barcode is in the index)
    print(f"Loading GMM-demux results from {gmm_file}")
    gmm_df = pd.read_csv(gmm_file, index_col=0)
    gmm_df = gmm_df.reset_index()
    gmm_df = gmm_df.rename(columns={'index': 'barcode'})
    print(f"GMM columns: {list(gmm_df.columns)}")
    print(f"GMM shape: {gmm_df.shape}")
    
    # Load the Cell Ranger VDJ contig annotations
    print(f"Loading VDJ contig annotations from {vdj_file}")
    vdj_df = pd.read_csv(vdj_file)
    print(f"VDJ columns: {list(vdj_df.columns)}")
    print(f"VDJ shape: {vdj_df.shape}")
    
    # Extract barcode column from VDJ file
    if 'barcode' in vdj_df.columns:
        barcode_col = 'barcode'
    elif 'cell_id' in vdj_df.columns:
        barcode_col = 'cell_id'
    else:
        barcode_col = vdj_df.columns[0]
    
    print(f"Using '{barcode_col}' as barcode column in VDJ file")
    
    # Load sample configuration to map hashtag_ids to sample_ids
    print(f"\nLoading sample configuration from {config_file}")
    hashtag_to_sample = load_sample_config(config_file)
    print(f"Hashtag to Sample mapping: {hashtag_to_sample}")
    
    # Create cluster_id to hashtag mapping
    cluster_to_hashtag = create_cluster_to_hashtag_mapping()
    print(f"Cluster to Hashtag mapping: {cluster_to_hashtag}")
    
    # Create cluster_id to sample_id mapping
    # We need to infer the mapping from cluster IDs to hashtags to samples
    # Assuming: C1 → cluster 1, C2 → cluster 2, C3 → cluster 3, etc.
    cluster_to_sample = {}
    for hashtag_id, sample_id in hashtag_to_sample.items():
        # Extract number from hashtag_id (e.g., 'C1' -> 1)
        match = re.search(r'(\d+)', hashtag_id)
        if match:
            cluster_num = int(match.group(1))
            cluster_to_sample[cluster_num] = sample_id
    
    print(f"Cluster ID to Sample ID mapping: {cluster_to_sample}")
    
    # Merge VDJ with GMM assignments on barcode
    merged_vdj = pd.merge(
        vdj_df, 
        gmm_df[['barcode', 'Cluster_id']], 
        left_on=barcode_col, 
        right_on='barcode',
        how='left'
    )
    
    # Map cluster_id to sample_id
    merged_vdj['sample_id'] = merged_vdj['Cluster_id'].map(cluster_to_sample)
    
    print(f"\nMerged dataframe shape: {merged_vdj.shape}")
    
    # Save the demultiplexed VDJ file
    merged_vdj.to_csv(output_file, index=False)
    
    print(f"\nSuccessfully demultiplexed VDJ-{vdj_type} annotations")
    print(f"Output saved to: {output_file}")
    print(f"\nDemultiplexed VDJ-{vdj_type} summary:")
    print(f"Total contigs: {len(merged_vdj)}")
    print(f"Contigs with cluster assignment: {merged_vdj['Cluster_id'].notna().sum()}")
    print(f"Contigs with sample assignment: {merged_vdj['sample_id'].notna().sum()}")
    print(f"Unique clusters: {merged_vdj['Cluster_id'].nunique()}")
    print(f"Unique samples: {merged_vdj['sample_id'].nunique()}")
    print(f"\nCluster distribution:")
    print(merged_vdj['Cluster_id'].value_counts().sort_index())
    print(f"\nSample distribution:")
    print(merged_vdj['sample_id'].value_counts())

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 6:
        print("Usage: python vdj_demultiplex.py <gmm_file> <vdj_file> <output_file> <config_file> <vdj_type>")
        print("  vdj_type: 'T' for TCR or 'B' for BCR")
        print("  config_file: Path to sample config CSV (e.g., metadata/sample_configs/sample_1_config.csv)")
        sys.exit(1)
    
    gmm_file = sys.argv[1]
    vdj_file = sys.argv[2]
    output_file = sys.argv[3]
    config_file = sys.argv[4]
    vdj_type = sys.argv[5]
    
    demultiplex_vdj(gmm_file, vdj_file, output_file, config_file, vdj_type)
