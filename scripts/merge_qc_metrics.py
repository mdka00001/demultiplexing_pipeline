import pandas as pd
import glob
import os
import re

def combine_csv_files(output_filename="combined_samples.csv"):
    # 1. Get a list of all CSV files in the current directory
    # If your files are in a specific folder, change to 'path/to/folder/*.csv'
    extension = 'csv'
    all_filenames = [i for i in glob.glob(f'*.{extension}')]
    
    # Remove the output file from the list if it already exists to avoid recursion
    if output_filename in all_filenames:
        all_filenames.remove(output_filename)

    print(f"Found {len(all_filenames)} files: {all_filenames}")

    # 2. Read and combine, adding sample name from filename
    dfs = []
    for filename in all_filenames:
        df = pd.read_csv(filename)
        # Extract sample name from filename (e.g., "sample_5_qc_metrics.csv" -> "sample_5")
        match = re.match(r'(sample_\d+)_qc_metrics\.csv', filename)
        if match:
            sample_name = match.group(1)
            df.insert(0, 'Sample', sample_name)
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)

    # 3. Export to CSV
    combined_df.to_csv(output_filename, index=False)
    print(f"Successfully combined {len(all_filenames)} files into '{output_filename}'.")

if __name__ == "__main__":
    combine_csv_files()