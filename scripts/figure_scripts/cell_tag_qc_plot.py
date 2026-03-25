"""
Generate QC comparison plots for cell tag assignments
Creates PDF files comparing Cellranger vs GMM-demux cell counts for GEX, TCR, and BCR data
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import os
import glob

# Set global styles
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 11


def create_qc_plots(data_type, quantification_dir, output_dir, samples):
    """
    Create QC comparison plots for a specific data type
    
    Args:
        data_type: 'GEX', 'TCR', or 'BCR'
        quantification_dir: Path to tag_quantification directory containing sample subdirectories
        output_dir: Path to output figures directory
        samples: List of sample names
    """
    
    # Determine filename mapping
    if data_type == 'GEX':
        filename = 'gex_quantification.csv'
        pdf_name = 'gex_tag_qc.pdf'
        ylabel = 'Num Cells (GEX)'
    elif data_type == 'TCR':
        filename = 'vdj_t_quantification.csv'
        pdf_name = 'vdj_t_tag_qc.pdf'
        ylabel = 'Num Cells (TCR)'
    elif data_type == 'BCR':
        filename = 'vdj_b_quantification.csv'
        pdf_name = 'vdj_b_tag_qc.pdf'
        ylabel = 'Num Cells (BCR)'
    else:
        raise ValueError(f"Unknown data_type: {data_type}")
    
    print(f"\nProcessing {data_type} data...")
    
    # Load data for all samples
    datasets = []
    sample_labels = []
    
    for sample in samples:
        csv_path = os.path.join(quantification_dir, sample, filename)
        
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found, skipping {sample}")
            continue
        
        try:
            df = pd.read_csv(csv_path)
            datasets.append(df)
            sample_labels.append(sample)
            print(f"  Loaded {sample}: {len(df)} entries")
        except Exception as e:
            print(f"Error loading {csv_path}: {e}")
            continue
    
    if not datasets:
        print(f"No data found for {data_type}, skipping PDF generation")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create PDF with multiple pages if needed (4x2 grid = 8 plots per page)
    pdf_path = os.path.join(output_dir, pdf_name)
    
    with PdfPages(pdf_path) as pdf:
        # Process in groups of 8 for A4 pages (4 rows x 2 columns)
        plots_per_page = 8
        
        for page_start in range(0, len(datasets), plots_per_page):
            page_end = min(page_start + plots_per_page, len(datasets))
            page_datasets = datasets[page_start:page_end]
            page_labels = sample_labels[page_start:page_end]
            
            # Create figure for this page
            n_plots = len(page_datasets)
            n_rows = (n_plots + 1) // 2  # Round up division
            n_cols = 2 if n_plots > 1 else 1
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(8.27, 11.69))
            
            # Handle single plot case
            if n_plots == 1:
                axes = [axes]
            else:
                axes = axes.flatten()
            
            # Plot each sample
            for ax_idx, (ax, df, sample_label) in enumerate(zip(axes, page_datasets, page_labels)):
                # Check which columns are present
                has_cr = 'CR_num_cells' in df.columns
                has_gmm = 'GMM_num_cells' in df.columns
                
                if not has_cr and not has_gmm:
                    ax.text(0.5, 0.5, 'No data available', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(sample_label, fontweight='bold')
                    continue
                
                # Prepare data
                # Handle both 'sample_name' (VDJ) and 'sample_id' (GEX) column names
                sample_col = 'sample_name' if 'sample_name' in df.columns else 'sample_id'
                
                x = np.arange(len(df[sample_col]))
                width = 0.35
                
                # Plot bars
                if has_cr:
                    ax.bar(x - width/2, df['CR_num_cells'], width, 
                          label='Cellranger', color='#1f77b4', alpha=0.8)
                
                if has_gmm:
                    ax.bar(x + width/2, df['GMM_num_cells'], width, 
                          label='GMM-demux', color='#ff7f0e', alpha=0.8)
                
                # Formatting
                ax.set_title(sample_label, fontweight='bold', fontsize=12)
                ax.set_ylabel(ylabel, fontsize=10)
                ax.set_xticks(x)
                ax.set_xticklabels(df[sample_col], rotation=45, ha='right', fontsize=9)
                ax.grid(axis='y', alpha=0.3, linestyle='--')
                ax.set_axisbelow(True)
                
                # Legend on first plot only
                if ax_idx == 0:
                    ax.legend(loc='upper right', fontsize=9)
            
            # Hide unused subplots
            for ax_idx in range(n_plots, len(axes)):
                axes[ax_idx].axis('off')
            
            # Layout
            plt.suptitle(f'{data_type} Tag Assignment QC (Page {page_start // plots_per_page + 1})', 
                        fontsize=14, fontweight='bold', y=0.98)
            plt.tight_layout(rect=[0, 0, 1, 0.97])
            
            # Save page
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
    
    print(f"PDF created: {pdf_path}")


def main():
    """
    Generate all three QC comparison PDFs
    """
    
    # Configuration
    pipeline_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    quantification_dir = os.path.join(pipeline_dir, 'results', 'tag_quantification')
    output_dir = os.path.join(pipeline_dir, 'results', 'figures', 'sample_tag_qc')
    
    print(f"Pipeline directory: {pipeline_dir}")
    print(f"Quantification directory: {quantification_dir}")
    print(f"Output directory: {output_dir}")
    
    # Get list of samples
    if os.path.exists(quantification_dir):
        samples = sorted([d for d in os.listdir(quantification_dir) 
                         if os.path.isdir(os.path.join(quantification_dir, d))])
        print(f"\nFound samples: {samples}")
    else:
        print(f"Error: Quantification directory not found: {quantification_dir}")
        return
    
    if not samples:
        print("No samples found in quantification directory")
        return
    
    # Generate PDFs for each data type
    for data_type in ['GEX', 'TCR', 'BCR']:
        try:
            create_qc_plots(data_type, quantification_dir, output_dir, samples)
        except Exception as e:
            print(f"Error processing {data_type}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✓ All QC plots generated successfully in {output_dir}")


if __name__ == "__main__":
    main()
