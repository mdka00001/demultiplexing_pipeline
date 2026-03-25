import pandas as pd
import os

def quantify_clusters(input_file, output_file, cluster_col='cluster_id'):
    """
    Read GMM_simplified.csv and quantify each cluster_id.
    Creates a summary dataframe with cluster counts.
    """
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return
    
    # Read the simplified GMM output
    df = pd.read_csv(input_file)
    
    print(f"Loaded {len(df)} barcodes from {input_file}")
    
    # Check if cluster_id column exists
    if cluster_col not in df.columns:
        print(f"Error: '{cluster_col}' column not found. Available columns: {list(df.columns)}")
        return
    
    # Quantify clusters - count occurrences of each cluster_id
    cluster_counts = df[cluster_col].value_counts().reset_index()
    cluster_counts.columns = [cluster_col, 'count']
    
    # Sort by cluster_id for consistent output
    cluster_counts = cluster_counts.sort_values(cluster_col).reset_index(drop=True)
    
    # Save to output file
    cluster_counts.to_csv(output_file, index=False)
    
    print(f"Cluster quantification summary:")
    print(cluster_counts.to_string())
    print(f"\nSuccessfully saved cluster quantification to '{output_file}'")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python cluster_quantification.py <input_file> <output_file> [cluster_col]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    cluster_col = sys.argv[3] if len(sys.argv) > 3 else 'Cluster_id'
    
    quantify_clusters(input_file, output_file, cluster_col)
