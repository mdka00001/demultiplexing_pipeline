"""
Generate Venn diagrams comparing Cellranger vs GMM-demux barcode assignments
for demultiplexed VDJ (TCR and BCR) outputs
"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib_venn import venn2
import os
import numpy as np

# Set global styles
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 11


def create_venn_diagrams(vdj_type, vdj_dir, output_dir, samples):
    """
    Create Venn diagrams comparing CR vs GMM barcodes for each sample
    
    Args:
        vdj_type: 'TCR' or 'BCR'
        vdj_dir: Path to vdj_demultiplex directory containing sample subdirectories
        output_dir: Path to output figures directory
        samples: List of sample names
    """
    
    # Determine filename
    if vdj_type == 'TCR':
        filename = 'demultiplexed_vdj_tcr_annotations.csv'
        pdf_name = 'vdj_t_venn_diagram.pdf'
        title_prefix = 'TCR'
    elif vdj_type == 'BCR':
        filename = 'demultiplexed_vdj_bcr_annotations.csv'
        pdf_name = 'vdj_b_venn_diagram.pdf'
        title_prefix = 'BCR'
    else:
        raise ValueError(f"Unknown vdj_type: {vdj_type}")
    
    print(f"\nProcessing {vdj_type} Venn diagrams...")
    
    # Load data for all samples
    sample_data = {}
    
    for sample in samples:
        csv_path = os.path.join(vdj_dir, sample, filename)
        
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found, skipping {sample}")
            continue
        
        try:
            df = pd.read_csv(csv_path)
            
            # Extract barcodes for CR (sample column) and GMM (sample_id column)
            # Filter out NaN/empty values
            cr_barcodes = set(df[df['sample'].notna()]['barcode'].unique())
            gmm_barcodes = set(df[df['sample_id'].notna()]['barcode'].unique())
            
            sample_data[sample] = {
                'cr_barcodes': cr_barcodes,
                'gmm_barcodes': gmm_barcodes,
                'df': df
            }
            
            print(f"  Loaded {sample}:")
            print(f"    CR barcodes: {len(cr_barcodes)}")
            print(f"    GMM barcodes: {len(gmm_barcodes)}")
            
        except Exception as e:
            print(f"Error loading {csv_path}: {e}")
            continue
    
    if not sample_data:
        print(f"No data found for {vdj_type}, skipping Venn diagram generation")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create PDF with multiple pages if needed (4x2 grid = 8 plots per page)
    pdf_path = os.path.join(output_dir, pdf_name)
    
    with PdfPages(pdf_path) as pdf:
        # Process in groups of 8 for A4 pages (4 rows x 2 columns)
        plots_per_page = 8
        sample_list = sorted(sample_data.keys())
        
        for page_start in range(0, len(sample_list), plots_per_page):
            page_end = min(page_start + plots_per_page, len(sample_list))
            page_samples = sample_list[page_start:page_end]
            
            # Create figure for this page
            n_plots = len(page_samples)
            n_rows = (n_plots + 1) // 2  # Round up division
            n_cols = 2 if n_plots > 1 else 1
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(8.27, 11.69))
            
            # Handle single plot case
            if n_plots == 1:
                axes = [axes]
            else:
                axes = axes.flatten()
            
            # Plot each sample
            for ax_idx, (ax, sample_label) in enumerate(zip(axes, page_samples)):
                data = sample_data[sample_label]
                cr_barcodes = data['cr_barcodes']
                gmm_barcodes = data['gmm_barcodes']
                
                # Create Venn diagram
                if len(cr_barcodes) == 0 and len(gmm_barcodes) == 0:
                    ax.text(0.5, 0.5, 'No data available', 
                           ha='center', va='center', transform=ax.transAxes)
                else:
                    venn2([cr_barcodes, gmm_barcodes], 
                         set_labels=('Cellranger', 'GMM-demux'),
                         ax=ax,
                         set_colors=('#1f77b4', '#ff7f0e'),
                         alpha=0.6)
                
                ax.set_title(sample_label, fontweight='bold', fontsize=12)
            
            # Hide unused subplots
            for ax_idx in range(n_plots, len(axes)):
                axes[ax_idx].axis('off')
            
            # Layout
            plt.suptitle(f'{title_prefix} Barcode Assignment Comparison (Page {page_start // plots_per_page + 1})', 
                        fontsize=14, fontweight='bold', y=0.98)
            plt.tight_layout(rect=[0, 0, 1, 0.97])
            
            # Save page
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
    
    print(f"PDF created: {pdf_path}")


def main():
    """
    Generate Venn diagrams for both TCR and BCR
    """
    
    # Configuration
    pipeline_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    vdj_dir = os.path.join(pipeline_dir, 'results', 'vdj_demultiplex')
    output_dir = os.path.join(pipeline_dir, 'results', 'figures', 'sample_tag_qc')
    
    print(f"Pipeline directory: {pipeline_dir}")
    print(f"VDJ directory: {vdj_dir}")
    print(f"Output directory: {output_dir}")
    
    # Get list of samples
    if os.path.exists(vdj_dir):
        samples = sorted([d for d in os.listdir(vdj_dir) 
                         if os.path.isdir(os.path.join(vdj_dir, d))])
        print(f"\nFound samples: {samples}")
    else:
        print(f"Error: VDJ directory not found: {vdj_dir}")
        return
    
    if not samples:
        print("No samples found in VDJ directory")
        return
    
    # Generate Venn diagrams for each VDJ type
    for vdj_type in ['TCR', 'BCR']:
        try:
            create_venn_diagrams(vdj_type, vdj_dir, output_dir, samples)
        except Exception as e:
            print(f"Error processing {vdj_type}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✓ All Venn diagrams generated successfully in {output_dir}")


if __name__ == "__main__":
    main()
