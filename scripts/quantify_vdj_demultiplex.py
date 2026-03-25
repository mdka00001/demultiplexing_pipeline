import pandas as pd
import os
from pathlib import Path

def quantify_vdj_demultiplex(vdj_tcr_file, vdj_bcr_file, output_tcr_file, output_bcr_file):
    """
    Quantify VDJ sample assignments from demultiplexed VDJ files
    
    Shows both Cellranger annotations (sample column) and GMM-demux annotations (sample_id column)
    side by side for comparison. Creates separate quantification files for TCR and BCR.
    
    Args:
        vdj_tcr_file: Path to demultiplexed_vdj_tcr_annotations.csv
        vdj_bcr_file: Path to demultiplexed_vdj_bcr_annotations.csv
        output_tcr_file: Output path for TCR quantification
        output_bcr_file: Output path for BCR quantification
    """
    
    if not os.path.exists(vdj_tcr_file):
        print(f"Error: VDJ TCR file '{vdj_tcr_file}' not found")
        return
    
    if not os.path.exists(vdj_bcr_file):
        print(f"Error: VDJ BCR file '{vdj_bcr_file}' not found")
        return
    
    print(f"Loading VDJ TCR annotations from {vdj_tcr_file}")
    tcr_df = pd.read_csv(vdj_tcr_file)
    print(f"TCR data shape: {tcr_df.shape}")
    print(f"TCR columns: {list(tcr_df.columns)[:10]}...")
    
    print(f"\nLoading VDJ BCR annotations from {vdj_bcr_file}")
    bcr_df = pd.read_csv(vdj_bcr_file)
    print(f"BCR data shape: {bcr_df.shape}")
    print(f"BCR columns: {list(bcr_df.columns)[:10]}...")
    
    # Process TCR
    print(f"\n=== PROCESSING TCR ===")
    _process_vdj_data(tcr_df, 'TCR', output_tcr_file)
    
    # Process BCR
    print(f"\n=== PROCESSING BCR ===")
    _process_vdj_data(bcr_df, 'BCR', output_bcr_file)


def _process_vdj_data(df, vdj_type, output_file):
    """
    Helper function to process TCR or BCR data
    Quantifies both cellranger (sample) and GMM-demux (sample_id) annotations
    """
    
    print(f"Quantifying {vdj_type} sample assignments...")
    
    # Check if required columns exist
    has_cellranger = 'sample' in df.columns
    has_gmm = 'sample_id' in df.columns
    
    print(f"Cellranger annotations present: {has_cellranger}")
    print(f"GMM-demux annotations present: {has_gmm}")
    
    output_rows = []
    
    if has_cellranger:
        # Quantify cellranger annotations
        cr_counts = df.groupby('sample')['barcode'].nunique().reset_index()
        cr_counts.columns = ['sample_name', 'CR_num_cells']
        cr_total = cr_counts['CR_num_cells'].sum()
        cr_counts['CR_pct_cells'] = (cr_counts['CR_num_cells'] / cr_total * 100).round(1)
        print(f"\nCellranger {vdj_type} Quantification:")
        print(cr_counts)
    
    if has_gmm:
        # Quantify GMM-demux annotations
        gmm_counts = df.groupby('sample_id')['barcode'].nunique().reset_index()
        gmm_counts.columns = ['sample_name', 'GMM_num_cells']
        gmm_total = gmm_counts['GMM_num_cells'].sum()
        gmm_counts['GMM_pct_cells'] = (gmm_counts['GMM_num_cells'] / gmm_total * 100).round(1)
        print(f"\nGMM-demux {vdj_type} Quantification:")
        print(gmm_counts)
    
    # Merge both quantifications side by side
    if has_cellranger and has_gmm:
        # Merge on sample_name
        merged = pd.merge(
            cr_counts,
            gmm_counts,
            left_on='sample_name',
            right_on='sample_name',
            how='outer'
        )
        merged = merged[['sample_name', 'CR_num_cells', 'CR_pct_cells', 'GMM_num_cells', 'GMM_pct_cells']].fillna(0)
        merged['CR_num_cells'] = merged['CR_num_cells'].astype(int)
        merged['GMM_num_cells'] = merged['GMM_num_cells'].astype(int)
        merged = merged.sort_values('sample_name').reset_index(drop=True)
        
        print(f"\nMerged {vdj_type} Quantification (Cellranger vs GMM-demux):")
        print(merged)
        
        merged.to_csv(output_file, index=False)
    elif has_cellranger:
        # Only cellranger data available
        cr_counts = cr_counts.sort_values('sample_name').reset_index(drop=True)
        cr_counts.to_csv(output_file, index=False)
    elif has_gmm:
        # Only GMM-demux data available
        gmm_counts = gmm_counts.sort_values('sample_name').reset_index(drop=True)
        gmm_counts.to_csv(output_file, index=False)
    
    print(f"\n{vdj_type} quantification saved to: {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: python quantify_vdj_demultiplex.py <vdj_tcr_file> <vdj_bcr_file> <output_tcr_file> <output_bcr_file>")
        sys.exit(1)
    
    vdj_tcr_file = sys.argv[1]
    vdj_bcr_file = sys.argv[2]
    output_tcr_file = sys.argv[3]
    output_bcr_file = sys.argv[4]
    
    quantify_vdj_demultiplex(vdj_tcr_file, vdj_bcr_file, output_tcr_file, output_bcr_file)
