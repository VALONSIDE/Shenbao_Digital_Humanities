"""
Module: Data Coding
Description: Merges raw Excel files and applies '3S Marketing Strategy' coding 
             (Scare, Science, Success) based on keyword dictionary matching.
"""

import pandas as pd
import os

# --- Configuration ---
INPUT_FILES = {
    "Beauty": "../data/raw_ads/申报_美容_数据.xlsx",
    "Health": "../data/raw_ads/申报_补脑_数据.xlsx",
    "Education": "../data/raw_ads/申报_函授_数据.xlsx"
}
OUTPUT_FILE = "../data/encoded_ads.csv"

# Dictionary for 'Dictionary-based Approach'
# Keys represent the marketing strategies, values are associated keywords (in Traditional/Simplified Chinese).
CODE_DICT = {
    "1_Fear_Appeal": [
        "苦", "痛", "病", "弱", "死", "亡", "笨", "愚", "黑", "老", "丑", "惨",
        "自杀", "枯黄", "憔悴", "失业", "落伍", "淘汰", "危险", "救命", "救星"
    ],
    "2_Scientific_Authority": [
        "医", "药", "科学", "化学", "物理", "博士", "专家", "发明", "化验",
        "德国", "美国", "西洋", "卫生", "原理", "研究", "证明", "确有", "功效"
    ],
    "3_Vision_Desire": [
        "美", "白", "嫩", "香", "滑", "摩登", "时髦",
        "聪明", "智慧", "神童", "天才", "强", "健", "壮",
        "升官", "发财", "名利", "富", "贵", "成功", "速成", "学位", "毕业"
    ]
}

def determine_strategy(text):
    """
    Classifies text into one of the 3 strategies based on keyword frequency.
    Returns: '0_Unclassified' if no keywords match.
    """
    if not isinstance(text, str):
        return "0_Unclassified"
    
    scores = {key: 0 for key in CODE_DICT}
    
    for category, keywords in CODE_DICT.items():
        for kw in keywords:
            if kw in text:
                scores[category] += 1
    
    # Select the category with the highest score
    max_score = max(scores.values())
    if max_score == 0:
        return "0_Unclassified"
    
    # Priority Rule: Fear > Vision > Science (if scores are equal)
    if scores["1_Fear_Appeal"] == max_score:
        return "1_Fear_Appeal"
    elif scores["3_Vision_Desire"] == max_score:
        return "3_Vision_Desire"
    else:
        return "2_Scientific_Authority"

def main():
    print("[*] Starting data integration and coding...")
    all_dfs = []
    
    for category, filepath in INPUT_FILES.items():
        if os.path.exists(filepath):
            df = pd.read_excel(filepath)
            df['Category'] = category
            all_dfs.append(df)
            print(f"    Loaded {category}: {len(df)} records")
            
    if not all_dfs:
        print("[!] No data found.")
        return

    # Merge and Deduplicate
    master_df = pd.concat(all_dfs, ignore_index=True)
    master_df.drop_duplicates(subset=['完整标题'], keep='first', inplace=True)
    
    # Apply Coding
    # Assuming '完整标题' is the column name for the full headline
    master_df['Strategy'] = master_df['完整标题'].apply(determine_strategy)
    
    # Save to CSV
    master_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"[+] Successfully saved encoded data to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()