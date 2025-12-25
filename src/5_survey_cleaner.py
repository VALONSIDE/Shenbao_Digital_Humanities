"""
Module: Statistical Analysis Preparation
Description: Cleans raw survey data, maps Likert scales to integers, 
             and exports CSV ready for SmartPLS structural equation modeling.
             (Fixed Version: Corrected file paths and added robust column matching)
"""

import pandas as pd
import os

# ================= Configuration =================
# 1. Path Setup (Robust method)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "..", "data", "raw_survey.xlsx")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "..", "data", "smartpls_data.csv")

# 2. Likert Scale Mapping (Chinese to Integer)
LIKERT_MAP = {
    # 5-point scale
    "完全不符合": 1, "比较不符合": 2, "一般": 3, "比较符合": 4, "完全符合": 5,
    "完全不同意": 1, "不太同意": 2, "不同意": 2, "同意": 4, "完全同意": 5,
    # Fallback for numbers
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5
}

# 3. Demographic Mapping
GENDER_MAP = {"A.男": 1, "男": 1, "B.女": 2, "女": 2}
GRADE_MAP = {"A.大一": 1, "B.大二": 2, "C.大三": 3, "D.大四": 4, "E.研究生及以上": 5}

def clean_survey_data():
    print("[*] Starting survey data cleaning...")
    
    # Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"[!] Error: Input file not found at {INPUT_FILE}")
        print("    Please ensure 'raw_survey.xlsx' is in the 'data' folder.")
        return

    try:
        df = pd.read_excel(INPUT_FILE)
        print(f"    Loaded raw data: {len(df)} responses.")
    except Exception as e:
        print(f"[!] Critical Error reading Excel: {e}")
        return

    new_df = pd.DataFrame()
    
    # ================= Helper Function: Find Column =================
    def find_col(keyword, dataframe):
        """Fuzzy search for column names containing the keyword."""
        for col in dataframe.columns:
            if keyword in str(col):
                return col
        return None

    # ================= 1. Demographics =================
    print("    Processing demographics...")
    
    col_gender = find_col("您的性别", df)
    if col_gender:
        new_df['Gender'] = df[col_gender].map(GENDER_MAP).fillna(0)
        
    col_grade = find_col("您的年级", df)
    if col_grade:
        new_df['Grade'] = df[col_grade].map(GRADE_MAP).fillna(0)

    # ================= 2. Anxiety & History Variables =================
    # Mapping keywords to SmartPLS variable names
    # Ensure these keywords match your SurveyStar/Tencent Survey headers
    variable_map = [
        # Contemporary Anxiety - Appearance
        ("关注社交媒体", "Anx_Face_1"),
        ("外貌不够出众", "Anx_Face_2"),
        ("镜子里的自己", "Anx_Face_3"),
        
        # Contemporary Anxiety - Knowledge
        ("同学考证", "Anx_Know_1"),
        ("技能不够用", "Anx_Know_2"),
        ("担心毕业", "Anx_Know_3"),
        
        # Contemporary Anxiety - Health
        ("精神疲惫", "Anx_Health_1"),
        ("过度的脑力", "Anx_Health_2"),
        ("高强度的竞争", "Anx_Health_3"),
        
        # Historical Resonance - Appearance
        ("皮肤黑被丈夫", "Hist_Face_1"),
        ("容貌决定命运", "Hist_Face_2"),
        ("如果这款产品", "Hist_Face_3"),
        
        # Historical Resonance - Brain/Health
        ("愚笨可变聪明", "Hist_Brain_1"),
        ("优胜劣汰", "Hist_Brain_2"),
        ("购买尝试", "Hist_Brain_3"),
        
        # Historical Resonance - Knowledge
        ("自修英文", "Hist_Know_1"),
        ("知识改变命运", "Hist_Know_2"),
        ("速成", "Hist_Know_3"),
    ]

    print("    Processing latent variables...")
    for keyword, var_name in variable_map:
        col_name = find_col(keyword, df)
        if col_name:
            # Apply Likert mapping
            new_df[var_name] = df[col_name].apply(
                lambda x: LIKERT_MAP.get(str(x).strip(), x) if isinstance(x, str) else x
            )
            # Ensure numeric conversion (force errors to NaN then fill with mean or drop)
            new_df[var_name] = pd.to_numeric(new_df[var_name], errors='coerce')
        else:
            print(f"    [!] Warning: Column keyword '{keyword}' not found.")

    # ================= 3. Quality Control (Anti-Bot) =================
    # Check for the attention check question (Q6)
    col_check = find_col("不是机器人", df)
    if col_check:
        # User must select "比较符合" (mapped to 4)
        # Note: Depending on raw data, this might be string "比较符合" or mapped int 4
        # Let's check string in raw dataframe
        valid_indices = df[df[col_check].astype(str).str.contains("比较符合")].index
        
        dropped_count = len(df) - len(valid_indices)
        if dropped_count > 0:
            print(f"    [QC] Removed {dropped_count} failed attention checks.")
            new_df = new_df.loc[valid_indices].copy()
    
    # ================= 4. Export =================
    if len(new_df) > 0:
        new_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"[+] Success! SmartPLS ready data saved to: {OUTPUT_FILE}")
        print(f"    Final Valid Sample Size: {len(new_df)}")
    else:
        print("[!] Error: Resulting dataset is empty. Check mapping logic.")

if __name__ == "__main__":
    clean_survey_data()