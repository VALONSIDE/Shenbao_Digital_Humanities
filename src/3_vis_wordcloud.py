"""
Module: Visualization (Word Cloud)
Description: Generates word clouds for different ad categories.
             Includes Traditional-to-Simplified Chinese conversion and EXTENSIVE stopword filtering.
             (Fixed Version: Handles CSV parsing errors)
"""

import pandas as pd
import jieba
from wordcloud import WordCloud
import re
import zhconv  # Library for Traditional -> Simplified Chinese conversion
import os

# --- Configuration ---
# 自动向上寻找 data 文件夹
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "encoded_ads.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Windows 字体路径
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"

# ================= SUPER STOPWORD LIST =================
STOPWORDS = {
    # 1. Basic Function Words
    '之', '的', '了', '在', '是', '有', '和', '大', '及', '与', '等', '或', '此', '亦', '即',
    '我们', '可以', '这个', '一个', '价', '元', '号', '路', '房', '药', '部', '处', '为', '以',
    '注意', '办法', '无不', '不论', '一切', '各种', '一种', '二种', '三种', '几种', '因为', '所以',
    '许多', '常常', '非常', '十分', '比较', '不过', '但是', '若是', '或者', '以及',
    
    # 2. Commercial Noise & Location/Time
    '上海', '上海市', '申报', '广告', '发行', '总', '分', '洋行', '公司', '启', '谨启', '启事',
    '电话', '地址', '经理', '售', '试服', '代售', '出售', '制造', '出品', '创制', '诸君',
    '一律', '同时', '赠品', '大赠品', '免费', '函索', '简章', '索寄', '样本', '大廉', '价目',
    '老牌', '名牌', '唯一', '第一', '无上', '最高', '最优', '特别', '特殊', '有名', '著名',
    '日', '月', '年', '星期', '礼拜', '十二月', '十一月', '一月', '二月', '三月', '四月', '五月',
    '廿日', '本日', '现在', '冬季', '冬令', '新春', '开幕', '举行', '本埠', '外埠',
    '周年', '纪念', '大减价', '廉价', '优待', '本校', '本院', '本社',
    
    # 3. Education Specific Noise
    '函授', '学校', '学社', '书局', '印书馆', '中华书局', '商务印书馆', '商务', '大东书局',
    '教育', '局', '馆', '所', '社', '科', '级', '员', '生', '师', '私立', '公立',
    '招生', '招收', '附设', '开设', '开学', '报名', '通告', '章程', '简章', '新生', '注册',
    '毕业', '肄业', '专修', '讲义', '学费', '教授', '同学', '大学',
    
    # 4. Beauty/Health Specific Noise
    '美容', '美容品', '美容院', '补脑', '脑汁', '补血', '神经衰弱', '衰弱', '神经',
    '艾罗', '艾罗补', '中法', '大药房', '药房', '五洲', '先施', '雅霜', '韦廉士', '安祺儿',
    '奇药', '妙品', '圣药', '灵药', '特效', '功效', '功能', '效力', '良药', '大补', '补剂',
    '应用', '秘诀', '秘密', '法', '剂', '丸', '水', '膏', '油', '露', '片', '几许',
    '强身', '健体', '卫生', '滋补', '服用', '精制', '改良', '发明', '保卫', '救星', '人丹'
}

def generate_wordcloud(category, texts):
    """
    Generates and saves a word cloud image.
    """
    print(f"[*] Processing WordCloud for: {category}")
    
    # 1. Convert Traditional to Simplified Chinese
    texts_simp = [zhconv.convert(str(t), 'zh-cn') for t in texts]
    
    # 2. Tokenization and Cleaning
    full_text = " ".join(texts_simp)
    full_text = re.sub(r"[^\u4e00-\u9fa5]", "", full_text) 
    
    words = jieba.lcut(full_text)
    
    clean_words = [w for w in words if len(w) > 1 and w not in STOPWORDS]
    
    if not clean_words:
        print(f"    [!] No valid words found for {category} after cleaning.")
        return

    # 3. Color Scheme
    if 'Beauty' in category or '美容' in str(category):
        c_map = 'magma'
    elif 'Education' in category or '函授' in str(category):
        c_map = 'cividis'
    else:
        c_map = 'viridis'

    # 4. Rendering
    wc = WordCloud(
        font_path=FONT_PATH,
        width=1600, height=1000,
        background_color='white',
        max_words=100,
        colormap=c_map,
        prefer_horizontal=0.9,
        random_state=42
    ).generate(" ".join(clean_words))
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_path = os.path.join(OUTPUT_DIR, f"wordcloud_{category}.png")
    wc.to_file(output_path)
    print(f"    [+] Saved: {output_path}")

def main():
    print(f"[*] Reading data from: {DATA_FILE}")
    if not os.path.exists(DATA_FILE):
        print(f"[!] Error: Data file not found. Please run '2_data_coding.py' first.")
        return

    # === 关键修改：增加容错参数 ===
    try:
        df = pd.read_csv(DATA_FILE, encoding='utf-8-sig', on_bad_lines='skip', engine='python')
    except UnicodeDecodeError:
        print("[!] UTF-8 failed, trying GBK...")
        df = pd.read_csv(DATA_FILE, encoding='gbk', on_bad_lines='skip', engine='python')
    except Exception as e:
        print(f"[!] Critical Read Error: {e}")
        return
    
    print(f"[*] Successfully loaded {len(df)} records.")

    # Detect column names (Handling potential Chinese/English headers)
    if 'Category' in df.columns:
        cat_col = 'Category'
        text_col = '完整标题' # Assuming standard output from step 2
    elif '关键词' in df.columns:
        cat_col = '关键词'
        text_col = '完整标题'
    else:
        print(f"[!] Error: Could not find Category column. Available columns: {df.columns}")
        return

    categories = df[cat_col].unique()
    
    for cat in categories:
        subset = df[df[cat_col] == cat]
        
        if text_col in subset.columns:
            titles = subset[text_col].tolist()
            generate_wordcloud(cat, titles)
        else:
            print(f"[!] Error: '{text_col}' column missing.")

    print("\n🎉 All Word Clouds Generated in 'output/' folder!")

if __name__ == "__main__":
    main()