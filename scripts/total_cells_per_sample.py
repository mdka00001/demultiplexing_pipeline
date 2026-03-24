import pandas as pd
import os
import glob

def total_cells_per_sample(output_filename="total_cells_per_sample.csv"):
    """
    Extract total cell counts from qc_library_metrics.csv files for each sample.
    Looks for the line: Library,Gene Expression,Physical library ID,<ID>,Cells,<count>
    """
    
    # Find all qc_library_metrics.csv files from cellranger outputs
    metrics_files = glob.glob("cellranger_outputs_2/*/outs/qc_library_metrics.csv")
    
    if not metrics_files:
        print("Error: No qc_library_metrics.csv files found in cellranger_outputs_2/*/outs/")
        return
    
    print(f"Found {len(metrics_files)} metrics files")
    
    sample_data = []
    
    for metrics_file in sorted(metrics_files):
        # Extract sample ID from path (e.g., "cellranger_outputs_2/sample_5/outs/...")
        sample_id = metrics_file.split("/")[1]
        
        # Read the CSV file
        df = pd.read_csv(metrics_file)
        
        # Find the line with Gene Expression and Cells metric
        # Filter: Library="Library", Library Type="Gene Expression", Metric Name="Cells"
        gex_cells = df[
            (df['Category'] == 'Library') & 
            (df['Library Type'] == 'Gene Expression') & 
            (df['Metric Name'] == 'Cells')
        ]
        
        if gex_cells.empty:
            print(f"Warning: Could not find GEX cell count for {sample_id}")
            continue
        
        # Get the cell count (should be only one row)
        cell_count = int(gex_cells['Metric Value'].values[0])
        
        sample_data.append({
            'Sample': sample_id,
            'n_cells': cell_count
        })
        
        print(f"Sample {sample_id}: {cell_count} cells")
    
    if not sample_data:
        print("Error: No cell count data extracted")
        return
    
    # Create dataframe and export
    result_df = pd.DataFrame(sample_data)
    result_df.to_csv(output_filename, index=False)
    print(f"\nSuccess! Total cells for {len(result_df)} samples saved to '{output_filename}'.")

if __name__ == "__main__":
    total_cells_per_sample()