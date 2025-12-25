"""
Module: Visualization (IEEE Standard)
Description: Generates stacked bar charts to analyze marketing strategies.
             (Fixed Version: Adapts to Chinese column headers in CSV)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
INPUT_FILE = os.path.join(SCRIPT_DIR, "..", "data", "encoded_ads.csv") 
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "..", "output", "IEEE_Chart_Strategies.pdf") 

# IEEE Standard Patterns
PATTERNS = ['///', '...', '   '] 

def draw_ieee_chart():
    print("[*] Generating IEEE standard chart...")
    
    # 1. Style Settings
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 12
    
    # 2. Load Data
    if not os.path.exists(INPUT_FILE):
        print(f"[!] Error: Data file not found at {INPUT_FILE}")
        return
    
    try:
        # Load with error handling
        df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig', on_bad_lines='skip', engine='python')
    except:
        df = pd.read_csv(INPUT_FILE, encoding='gbk', on_bad_lines='skip', engine='python')

    rename_map = {
        '关键词': 'Category',
        '预编码结果': 'Strategy'
    }
    df.rename(columns=rename_map, inplace=True)
    
    # Check if renaming succeeded
    if 'Category' not in df.columns or 'Strategy' not in df.columns:
        print(f"[!] Error: Could not find required columns even after renaming.")
        print(f"    Current columns: {df.columns.tolist()}")
        return
        
    # 3. Clean and Translate
    # Filter out unclassified rows
    df_clean = df[df['Strategy'] != '0_未分类'].copy()
    
    # Translation Dictionaries
    TRANS_MAP_CAT = {
        "美容": "Beauty",
        "补脑": "Health",
        "神经衰弱": "Health",  # Merge Neurasthenia into Health
        "函授": "Education"
    }
    
    TRANS_MAP_STRAT = {
        "1_恐吓": "Fear Appeal",
        "2_科学": "Scientific Authority",
        "3_愿景": "Vision/Desire"
    }
    
    # Apply Mapping
    df_clean['Category_En'] = df_clean['Category'].map(TRANS_MAP_CAT).fillna(df_clean['Category'])
    df_clean['Strategy_En'] = df_clean['Strategy'].map(TRANS_MAP_STRAT).fillna(df_clean['Strategy'])
    
    # 4. Process Data for Plotting
    pivot = pd.crosstab(df_clean['Category_En'], df_clean['Strategy_En'])
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    
    # Ensure column order
    desired_cols = ["Fear Appeal", "Scientific Authority", "Vision/Desire"]
    existing_cols = [c for c in desired_cols if c in pivot_pct.columns]
    pivot_pct = pivot_pct[existing_cols]

    # 5. Plotting
    print("  [*] Plotting...")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    pivot_pct.plot(
        kind='bar', 
        stacked=True, 
        ax=ax, 
        color='white',
        edgecolor='black',
        width=0.5,
        rot=0
    )
    
    # Apply Patterns
    for i, container in enumerate(ax.containers):
        pattern = PATTERNS[i % len(PATTERNS)]
        for bar in container:
            bar.set_hatch(pattern)
        
        # Add labels
        ax.bar_label(
            container, 
            labels=[f'{v.get_height():.1f}%' if v.get_height() > 3 else '' for v in container],
            label_type='center', 
            color='black',
            fontsize=10, 
            weight='bold',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1)
        )

    # Layout
    ax.set_xlabel("Advertising Category", fontsize=12, fontweight='bold')
    ax.set_ylabel("Percentage (%)", fontsize=12, fontweight='bold')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    
    # Legend
    handles, labels = ax.get_legend_handles_labels()
    # Clean labels just in case
    clean_labels = [l.split('_', 1)[1].replace('_', ' ') if '_' in l else l for l in labels]
    
    ax.legend(
        handles, clean_labels, 
        loc='lower center', 
        bbox_to_anchor=(0.5, 1.02), 
        ncol=3, 
        frameon=False
    )
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title("Marketing Strategy Distribution (1927-1937)", fontsize=14, pad=45)

    plt.tight_layout()
    plt.subplots_adjust(top=0.80)
    
    plt.savefig(OUTPUT_FILE, format='pdf', dpi=600)
    print(f"  [+] Saved PDF to: {OUTPUT_FILE}")

if __name__ == "__main__":
    draw_ieee_chart()