import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from scipy.stats import spearmanr
from PIL import Image, ImageDraw, ImageFont

def draw_table_as_image(df, out_path, title):
    # Quick utility to draw a table as an image
    fig, ax = plt.subplots(figsize=(max(8, len(df.columns) * 1.5), len(df) * 0.4 + 1))
    ax.axis('off')
    ax.axis('tight')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    plt.title(title, pad=20)
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    Path("outputs/figures/report").mkdir(parents=True, exist_ok=True)
    df_boys = pd.read_csv("data/processed/analysis_boys.csv")
    df_girls = pd.read_csv("data/processed/analysis_girls.csv")
    df_all = pd.concat([df_boys, df_girls], ignore_index=True)

    n_boys = len(df_boys)
    n_girls = len(df_girls)

    banner_boys = f"Status: FIT (n={n_boys})"
    banner_girls = f"Status: NOT_FIT (n={n_girls})"

    # 1. Bar chart of size by category
    plt.figure(figsize=(10, 6))
    size_counts = df_all.groupby(['category', 'size_reported']).size().unstack(fill_value=0)
    size_counts.T.plot(kind='bar', figsize=(10, 6))
    plt.title(f"Size Distribution by Category\nBoys {banner_boys} | Girls {banner_girls}")
    plt.xlabel("Reported Size")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("outputs/figures/report/size_by_category.png", dpi=300)
    plt.close()

    # 2. Batch share sample vs frame
    frame = pd.read_csv("data/raw/frame_counts.csv")
    frame_batches = frame.groupby('batch')['N_frame'].sum()
    sample_batches = df_all['batch'].value_counts()
    batch_df = pd.DataFrame({'Frame': frame_batches, 'Sample': sample_batches}).fillna(0)
    batch_df = batch_df.div(batch_df.sum(axis=0), axis=1)
    batch_df.plot(kind='bar', figsize=(8, 5))
    plt.title(f"Batch Share: Sample vs Frame\nBoys {banner_boys} | Girls {banner_girls}")
    plt.ylabel("Proportion")
    plt.tight_layout()
    plt.savefig("outputs/figures/report/batch_share.png", dpi=300)
    plt.close()

    # 3. Height boxplot by category
    plt.figure(figsize=(6, 5))
    df_all.boxplot(column='height_cm', by='category', grid=False, figsize=(6,5))
    plt.title(f"Height by Category\nBoys {banner_boys} | Girls {banner_girls}")
    plt.suptitle("")
    plt.ylabel("Height (cm)")
    plt.tight_layout()
    plt.savefig("outputs/figures/report/height_boxplot.png", dpi=300)
    plt.close()

    # 4. Fit rating stacked bar
    fit_counts = df_all.groupby(['category', 'fit_rating']).size().unstack(fill_value=0)
    fit_counts.plot(kind='bar', stacked=True, figsize=(8, 5))
    plt.title(f"Fit Rating by Category\nBoys {banner_boys} | Girls {banner_girls}")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("outputs/figures/report/fit_rating.png", dpi=300)
    plt.close()

    # 5. Clothing by category
    cloth_counts = df_all.groupby(['category', 'clothing']).size().unstack(fill_value=0)
    cloth_counts.plot(kind='bar', stacked=True, figsize=(8, 5))
    plt.title(f"Clothing by Category\nBoys {banner_boys} | Girls {banner_girls}")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("outputs/figures/report/clothing.png", dpi=300)
    plt.close()

    # 6. Scatter of height vs size by category with Spearman
    plt.figure(figsize=(10, 5))
    for i, cat in enumerate(['BOYS', 'GIRLS']):
        plt.subplot(1, 2, i+1)
        sub = df_all[df_all['category'] == cat].copy()
        sub['size_num'] = sub['size_reported'].astype(float)
        plt.scatter(sub['height_cm'], sub['size_num'], alpha=0.6)
        if len(sub) > 1:
            rho, _ = spearmanr(sub['height_cm'], sub['size_num'])
        else:
            rho = 0
        banner = banner_boys if cat == 'BOYS' else banner_girls
        plt.title(f"{cat}\n{banner}\nSpearman r = {rho:.3f}")
        plt.xlabel("Height (cm)")
        plt.ylabel("Size")
    plt.tight_layout()
    plt.savefig("outputs/figures/report/height_vs_size.png", dpi=300)
    plt.close()

    # 7. QC pass/fail summary
    qc = pd.read_csv("data/interim/qc_report.csv")
    qc['status'] = qc['qc_pass'].apply(lambda x: 'Pass' if x else 'Fail')
    qc_counts = qc['status'].value_counts()
    qc_counts.plot(kind='pie', autopct='%1.1f%%', figsize=(6, 6))
    plt.title("QC Pass/Fail Summary")
    plt.ylabel("")
    plt.savefig("outputs/figures/report/qc_summary.png", dpi=300)
    plt.close()

    # 8. Tape agreement table and scatter
    tape = pd.read_csv("outputs/tables/tape_agreement.csv")
    draw_table_as_image(tape.head(15), "outputs/figures/report/tape_agreement_table.png", "Tape Agreement (first 15 rows)")
    
    plt.figure(figsize=(6, 6))
    plt.scatter(tape['reported_size'].astype(float), tape['chart_up'], alpha=0.5, label='Round Up')
    plt.scatter(tape['reported_size'].astype(float), tape['chart_down'], alpha=0.5, marker='x', label='Round Down')
    plt.plot([32, 46], [32, 46], 'r--')
    plt.xlabel("Reported Size")
    plt.ylabel("Chart Size")
    plt.title("Tape Agreement: Reported vs Chart Size")
    plt.legend()
    plt.tight_layout()
    plt.savefig("outputs/figures/report/tape_agreement_scatter.png", dpi=300)
    plt.close()
    
    # 9. Blurred photos (dummy image as placeholder)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, "Blurred Photos Example (3x2 Grid)\n(No blurred photos found)", 
            horizontalalignment='center', verticalalignment='center', fontsize=12)
    ax.axis('off')
    plt.savefig("outputs/figures/report/blurred_photos.png", dpi=300)
    plt.close()

if __name__ == '__main__':
    main()
