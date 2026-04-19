import os
import sys
import json
import urllib.request
import datetime

# Ensure the src directory is on the Python path so that the ichingshifa
# package can be imported when the app is launched from the project root
# (e.g. ``streamlit run app.py``).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import streamlit as st
import pendulum as pdlm
from contextlib import contextmanager, redirect_stdout
from io import StringIO

from ichingshifa import ichingshifa
from ichingshifa.cerebras_client import (
    CerebrasClient,
    DEFAULT_MODEL,
    CEREBRAS_MODEL_OPTIONS,
    CEREBRAS_MODEL_DESCRIPTIONS,
)

# ---------------------------------------------------------------------------
# 常量配置
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_PROMPTS_FILE = os.path.join(BASE_DIR, "system_prompts.json")
DEFAULT_MAX_TOKENS = 200000
DEFAULT_TEMPERATURE = 0.7

# 五行對應顏色
WUXING_COLORS = {
    "木": "#4a9e4a",  # 青/綠
    "火": "#c94040",  # 紅
    "土": "#c9a840",  # 黃
    "金": "#e0e0e0",  # 白
    "水": "#4a7ec9",  # 藍
}

# 爻的名稱（由下至上）
YAO_NAMES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

# ---------------------------------------------------------------------------
# 工具函數
# ---------------------------------------------------------------------------


@contextmanager
def st_capture(output_func):
    """捕獲 stdout 輸出到 Streamlit 元素。"""
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write

        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret

        stdout.write = new_write
        yield


def read_local_file(path):
    """讀取專案根目錄下的文字檔案。"""
    full = os.path.join(BASE_DIR, path)
    with open(full, "r", encoding="utf-8") as f:
        return f.read()


def get_remote_file(url):
    """從遠端 URL 獲取文字內容。"""
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")


# ---------------------------------------------------------------------------
# 系統提示管理
# ---------------------------------------------------------------------------


def load_system_prompts():
    """載入系統提示，若不存在則建立預設值。"""
    default_content = (
        "你是一位精通周易六爻的大師，熟悉《增刪卜易》、《卜筮正宗》、《黃金策》及歷史占例。"
        "請根據提供的六爻排盤數據，進行以下操作：\n\n"
        "1. 解釋卦象的關鍵要素（本卦、之卦、世應、六親、動爻、伏神等）。\n"
        "2. 結合六爻理論，分析卦象的吉凶和潛在影響。\n"
        "3. 根據用神、原神、忌神、仇神的旺衰及動靜，詳細評估事情的發展趨勢。\n"
        "4. 提供實用的建議或應對策略。\n\n"
        "請以清晰的結構（分段、標題）呈現，語言專業且易懂，適當引用經典理論或歷史占例。"
    )
    try:
        with open(SYSTEM_PROMPTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        default_data = {
            "prompts": [{"name": "六爻大師", "content": default_content}],
            "selected": "六爻大師",
        }
        with open(SYSTEM_PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        return default_data


def save_system_prompts(prompts_data):
    """持久化系統提示到 JSON 檔案。"""
    try:
        with open(SYSTEM_PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(prompts_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"儲存提示時發生錯誤：{e}")
        return False


# ---------------------------------------------------------------------------
# SVG 卦圖生成
# ---------------------------------------------------------------------------


def generate_yao_svg(yao_type, y_pos, width=120, is_dong=False):
    """生成單個爻的 SVG 元素。

    yao_type: "7"=少陽, "8"=少陰, "9"=老陽(動), "6"=老陰(動)
    """
    elements = []
    line_color = "#d4af77"
    stroke_w = 4

    if yao_type in ("7", "9"):
        # 陽爻：一條實線
        elements.append(
            f'<rect x="10" y="{y_pos}" width="{width - 20}" height="{stroke_w}" '
            f'fill="{line_color}" rx="2"/>'
        )
        if yao_type == "9":
            # 老陽動爻標記 O
            elements.append(
                f'<circle cx="{width // 2}" cy="{y_pos + 2}" r="8" '
                f'fill="none" stroke="#9c2f2f" stroke-width="2"/>'
            )
            elements.append(
                f'<text x="{width // 2}" y="{y_pos + 6}" '
                f'text-anchor="middle" fill="#9c2f2f" font-size="10" '
                f'font-weight="bold">O</text>'
            )
    else:
        # 陰爻：斷開的兩段
        gap = 12
        half = (width - 20 - gap) // 2
        elements.append(
            f'<rect x="10" y="{y_pos}" width="{half}" height="{stroke_w}" '
            f'fill="{line_color}" rx="2"/>'
        )
        elements.append(
            f'<rect x="{10 + half + gap}" y="{y_pos}" width="{half}" height="{stroke_w}" '
            f'fill="{line_color}" rx="2"/>'
        )
        if yao_type == "6":
            # 老陰動爻標記 X
            cx = width // 2
            elements.append(
                f'<text x="{cx}" y="{y_pos + 6}" '
                f'text-anchor="middle" fill="#9c2f2f" font-size="12" '
                f'font-weight="bold">✕</text>'
            )

    return "\n".join(elements)


def generate_hexagram_svg(gua_code, title="", width=140, height=180):
    """生成完整六爻卦圖的 SVG。

    gua_code: 6 位字串，如 "789876"，由初爻到上爻。
    """
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
    ]

    if title:
        svg_parts.append(
            f'<text x="{width // 2}" y="20" text-anchor="middle" '
            f'fill="#d4af77" font-size="16" font-family="Noto Serif SC, serif" '
            f'font-weight="bold">{title}</text>'
        )

    # 由上爻到初爻繪製（視覺上上到下）
    yao_list = list(gua_code)
    start_y = 40 if title else 20
    spacing = 22

    for idx in range(5, -1, -1):
        y = start_y + (5 - idx) * spacing
        svg_parts.append(generate_yao_svg(yao_list[idx], y, width))

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ---------------------------------------------------------------------------
# 結構化數據提取（從 ichingshifa 核心庫）
# ---------------------------------------------------------------------------


def extract_pan_data(year, month, day, hour, minute, manual=False, combine=None):
    """從 ichingshifa 提取結構化排盤數據。

    返回一個 dict 包含所有排盤資訊。
    """
    ic = ichingshifa.Iching()

    try:
        if manual and combine:
            result = ic.qigua_manual(year, month, day, hour, minute, combine)
        else:
            result = ic.qigua_time_minute(year, month, day, hour, minute)
    except Exception as e:
        return {"error": str(e)}

    gz = ic.gangzhi(year, month, day, hour, minute)

    # 基礎資訊
    data = {
        "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute,
        "gangzhi": gz,
        "lunar": ic.lunar_date_d(year, month, day),
        "result": result,
    }

    # 大衍筮法結果
    oo = result.get("大衍筮法")
    data["ogua"] = oo[0]  # 原始六爻編碼
    data["bengua_name"] = oo[1]  # 本卦名
    data["zhigua_name"] = oo[2]  # 之卦名
    data["yao_desc"] = oo[3]  # 爻辭
    data["explanation"] = oo[4]  # 斷語

    # 變卦編碼
    data["zhigua_code"] = data["ogua"].replace("9", "8").replace("6", "7")

    # 本卦資訊
    bengua = result.get("本卦", {})
    data["bengua"] = bengua
    data["bengua_gua"] = bengua.get("卦", "")
    data["bengua_liuqin"] = bengua.get("六親用神", [])
    data["bengua_najia"] = bengua.get("納甲", [])
    data["bengua_wuxing"] = bengua.get("五行", [])
    data["bengua_shiying"] = bengua.get("世應爻", [])
    data["bengua_xingxiu"] = bengua.get("星宿", [])

    # 之卦資訊
    zhigua = result.get("之卦", {})
    data["zhigua"] = zhigua
    data["zhigua_gua"] = zhigua.get("卦", "")
    data["zhigua_liuqin"] = zhigua.get("六親用神", [])
    data["zhigua_najia"] = zhigua.get("納甲", [])
    data["zhigua_wuxing"] = zhigua.get("五行", [])
    data["zhigua_shiying"] = zhigua.get("世應爻", [])
    data["zhigua_xingxiu"] = zhigua.get("星宿", [])

    # 六神
    data["liushen"] = ic.find_six_mons(gz[2][0]) if len(gz) > 2 else []

    # 動爻判定
    dong = []
    for idx, y in enumerate(data["ogua"]):
        if y in ("6", "9"):
            dong.append(idx)
    data["dong_yao"] = dong

    # 伏神
    data["fushen_ben"] = bengua.get("伏神")
    data["fushen_zhi"] = zhigua.get("伏神")

    # 身爻
    data["shenyao"] = bengua.get("身爻", "")

    return data


# ---------------------------------------------------------------------------
# 頁面配置
# ---------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="堅六爻 — 周易排盤", page_icon="☯️")

# ---------------------------------------------------------------------------
# 古典易經風格 CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
/* ===== Google Fonts ===== */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Ma+Shan+Zheng&display=swap');

/* ===== 全局樣式 ===== */
.stApp {
    background-color: #0a0a0a !important;
    font-family: 'Noto Serif SC', 'SimSun', serif !important;
}

/* 極淡水墨竹簡背景 */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600"><defs><linearGradient id="g" x1="0%25" y1="0%25" x2="100%25" y2="100%25"><stop offset="0%25" style="stop-color:%23d4af77;stop-opacity:0.03"/><stop offset="100%25" style="stop-color:%23d4af77;stop-opacity:0.01"/></linearGradient></defs><rect fill="url(%23g)" width="400" height="600"/><line x1="50" y1="0" x2="50" y2="600" stroke="%23d4af77" stroke-opacity="0.04" stroke-width="1"/><line x1="100" y1="0" x2="100" y2="600" stroke="%23d4af77" stroke-opacity="0.04" stroke-width="1"/><line x1="150" y1="0" x2="150" y2="600" stroke="%23d4af77" stroke-opacity="0.04" stroke-width="1"/><line x1="200" y1="0" x2="200" y2="600" stroke="%23d4af77" stroke-opacity="0.04" stroke-width="1"/><line x1="250" y1="0" x2="250" y2="600" stroke="%23d4af77" stroke-opacity="0.04" stroke-width="1"/><line x1="300" y1="0" x2="300" y2="600" stroke="%23d4af77" stroke-opacity="0.04" stroke-width="1"/><line x1="350" y1="0" x2="350" y2="600" stroke="%23d4af77" stroke-opacity="0.04" stroke-width="1"/></svg>');
    background-size: 400px 600px;
    pointer-events: none;
    z-index: 0;
}

.main .block-container {
    max-width: 1200px;
    padding-top: 1rem;
}

/* ===== 文字樣式 ===== */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Ma Shan Zheng', 'Noto Serif SC', serif !important;
    color: #d4af77 !important;
}

p, span, label, .stMarkdown {
    font-family: 'Noto Serif SC', serif !important;
    color: #f0e6d3 !important;
    line-height: 1.8 !important;
}

/* ===== 標題區域 ===== */
.app-title {
    text-align: center;
    padding: 1rem 0;
    border-bottom: 1px solid rgba(212, 175, 119, 0.2);
    margin-bottom: 1rem;
}

.app-title h1 {
    font-family: 'Ma Shan Zheng', serif !important;
    font-size: 2.5rem !important;
    color: #d4af77 !important;
    margin: 0 !important;
    letter-spacing: 8px;
    text-shadow: 0 0 20px rgba(212, 175, 119, 0.3);
}

.app-title p {
    color: rgba(240, 230, 211, 0.6) !important;
    font-size: 0.9rem !important;
    margin-top: 0.3rem !important;
}

/* ===== 側邊欄 ===== */
section[data-testid="stSidebar"] {
    background-color: #0f0f0f !important;
    border-right: 1px solid rgba(212, 175, 119, 0.15) !important;
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label {
    color: #f0e6d3 !important;
}

/* ===== Tab 樣式 ===== */
.stTabs [data-baseweb="tab-list"] {
    background-color: rgba(20, 20, 20, 0.8);
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(212, 175, 119, 0.15);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Noto Serif SC', serif !important;
    color: rgba(240, 230, 211, 0.6) !important;
    border-radius: 6px;
    padding: 8px 16px;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: rgba(212, 175, 119, 0.15) !important;
    color: #d4af77 !important;
    font-weight: 600;
}

.stTabs [data-baseweb="tab-highlight"] {
    background-color: #d4af77 !important;
}

/* ===== 卦圖容器 ===== */
.gua-card {
    background: linear-gradient(135deg, rgba(20, 18, 15, 0.95), rgba(30, 25, 20, 0.9));
    border: 1px solid rgba(212, 175, 119, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    position: relative;
    overflow: hidden;
}

.gua-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, #d4af77, transparent);
}

.gua-card h3 {
    font-family: 'Ma Shan Zheng', serif !important;
    color: #d4af77 !important;
    font-size: 1.5rem !important;
    margin-bottom: 1rem !important;
    letter-spacing: 3px;
}

/* ===== 爻卡片 ===== */
.yao-card {
    background: linear-gradient(135deg, rgba(20, 18, 15, 0.95), rgba(30, 25, 20, 0.9));
    border: 1px solid rgba(212, 175, 119, 0.15);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.3s ease;
}

.yao-card:hover {
    border-color: rgba(212, 175, 119, 0.4);
    box-shadow: 0 2px 15px rgba(212, 175, 119, 0.1);
    transform: translateX(4px);
}

.yao-card.dong-yao {
    border-left: 3px solid #9c2f2f;
    background: linear-gradient(135deg, rgba(156, 47, 47, 0.08), rgba(30, 25, 20, 0.9));
}

.yao-card .yao-name {
    font-family: 'Ma Shan Zheng', serif;
    font-size: 1.2rem;
    color: #d4af77;
    min-width: 50px;
}

.yao-card .yao-symbol {
    font-size: 1.5rem;
    min-width: 80px;
    text-align: center;
}

.yao-card .yao-info {
    flex: 1;
    font-size: 0.9rem;
    color: #f0e6d3;
    line-height: 1.6;
}

.yao-card .yao-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-right: 6px;
}

/* ===== 五行顏色標籤 ===== */
.wx-mu { background: rgba(74, 158, 74, 0.2); color: #4a9e4a; border: 1px solid rgba(74, 158, 74, 0.3); }
.wx-huo { background: rgba(201, 64, 64, 0.2); color: #c94040; border: 1px solid rgba(201, 64, 64, 0.3); }
.wx-tu { background: rgba(201, 168, 64, 0.2); color: #c9a840; border: 1px solid rgba(201, 168, 64, 0.3); }
.wx-jin { background: rgba(224, 224, 224, 0.2); color: #e0e0e0; border: 1px solid rgba(224, 224, 224, 0.3); }
.wx-shui { background: rgba(74, 126, 201, 0.2); color: #4a7ec9; border: 1px solid rgba(74, 126, 201, 0.3); }

/* ===== 世應標記 ===== */
.shi-badge { background: rgba(212, 175, 119, 0.2); color: #d4af77; border: 1px solid rgba(212, 175, 119, 0.4); padding: 2px 10px; border-radius: 4px; font-size: 0.85rem; }
.ying-badge { background: rgba(156, 47, 47, 0.2); color: #c94040; border: 1px solid rgba(156, 47, 47, 0.4); padding: 2px 10px; border-radius: 4px; font-size: 0.85rem; }

/* ===== 表格樣式 ===== */
.info-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid rgba(212, 175, 119, 0.2);
    border-radius: 8px;
    overflow: hidden;
}

.info-table th {
    background: rgba(212, 175, 119, 0.1);
    color: #d4af77;
    padding: 10px 12px;
    font-family: 'Noto Serif SC', serif;
    font-weight: 600;
    text-align: center;
    border-bottom: 1px solid rgba(212, 175, 119, 0.15);
}

.info-table td {
    padding: 8px 12px;
    text-align: center;
    color: #f0e6d3;
    font-family: 'Noto Serif SC', serif;
    border-bottom: 1px solid rgba(212, 175, 119, 0.08);
}

.info-table tr:hover td {
    background: rgba(212, 175, 119, 0.05);
}

/* ===== 排盤預覽區 ===== */
.pan-preview {
    background: rgba(15, 12, 10, 0.9);
    border: 1px solid rgba(212, 175, 119, 0.2);
    border-radius: 8px;
    padding: 1rem;
    font-family: 'Noto Serif SC', monospace;
    font-size: 13px;
    line-height: 1.8;
    color: #f0e6d3;
    white-space: pre-wrap;
    overflow-x: auto;
}

/* ===== 動爻動畫 ===== */
@keyframes dong-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.dong-indicator {
    animation: dong-pulse 2s ease-in-out infinite;
    color: #9c2f2f;
    font-weight: bold;
}

/* ===== Code block 樣式 ===== */
.stCode code, .stCode pre {
    font-size: 14px !important;
    line-height: 1.6 !important;
    font-family: 'Noto Serif SC', monospace !important;
    background-color: rgba(15, 12, 10, 0.95) !important;
}

/* ===== 按鈕樣式 ===== */
.stButton > button {
    font-family: 'Noto Serif SC', serif !important;
    border: 1px solid rgba(212, 175, 119, 0.3) !important;
    color: #d4af77 !important;
    background: linear-gradient(135deg, rgba(212, 175, 119, 0.1), rgba(212, 175, 119, 0.05)) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    border-color: #d4af77 !important;
    box-shadow: 0 0 15px rgba(212, 175, 119, 0.2) !important;
    background: linear-gradient(135deg, rgba(212, 175, 119, 0.2), rgba(212, 175, 119, 0.1)) !important;
}

/* ===== 主起卦按鈕 ===== */
.qigua-btn > button {
    background: linear-gradient(135deg, rgba(156, 47, 47, 0.3), rgba(212, 175, 119, 0.2)) !important;
    border: 2px solid #9c2f2f !important;
    color: #d4af77 !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    padding: 0.6rem 2rem !important;
}

.qigua-btn > button:hover {
    background: linear-gradient(135deg, rgba(156, 47, 47, 0.5), rgba(212, 175, 119, 0.3)) !important;
    box-shadow: 0 0 25px rgba(156, 47, 47, 0.3) !important;
}

/* ===== 歷史記錄樣式 ===== */
.history-item {
    background: rgba(20, 18, 15, 0.8);
    border: 1px solid rgba(212, 175, 119, 0.1);
    border-radius: 6px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.4rem;
    cursor: pointer;
    transition: all 0.2s;
}

.history-item:hover {
    border-color: rgba(212, 175, 119, 0.3);
    background: rgba(212, 175, 119, 0.05);
}

/* ===== Expander 樣式 ===== */
.streamlit-expanderHeader {
    font-family: 'Noto Serif SC', serif !important;
    color: #d4af77 !important;
}

/* ===== 聊天區域 ===== */
.chat-container {
    border-top: 1px solid rgba(212, 175, 119, 0.2);
    padding-top: 1rem;
    margin-top: 2rem;
}

/* ===== 行動裝置適配 ===== */
@media (max-width: 768px) {
    .app-title h1 {
        font-size: 1.8rem !important;
        letter-spacing: 4px;
    }
    .gua-card {
        padding: 1rem;
    }
    .yao-card {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

/* ===== 分隔線 ===== */
hr {
    border-color: rgba(212, 175, 119, 0.15) !important;
}

/* ===== 模式標籤 ===== */
.mode-badge-auto {
    background: linear-gradient(135deg, rgba(31, 106, 165, 0.3), rgba(31, 106, 165, 0.1));
    color: #6db3e8;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    border: 1px solid rgba(31, 106, 165, 0.3);
}

.mode-badge-manual {
    background: linear-gradient(135deg, rgba(122, 59, 140, 0.3), rgba(122, 59, 140, 0.1));
    color: #b87ed4;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    border: 1px solid rgba(122, 59, 140, 0.3);
}

/* ===== Selectbox/Input 樣式 ===== */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea textarea {
    font-family: 'Noto Serif SC', serif !important;
    background-color: rgba(20, 18, 15, 0.95) !important;
    border-color: rgba(212, 175, 119, 0.2) !important;
    color: #f0e6d3 !important;
}

/* ===== Divider ===== */
.sidebar-divider {
    border-top: 1px solid rgba(212, 175, 119, 0.15);
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 標題
# ---------------------------------------------------------------------------

st.markdown("""
<div class="app-title">
    <h1>☯ 堅六爻 · 周易排盤</h1>
    <p>大衍蓍草法 · 銅錢法 · 梅花易數 · 手動輸入</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 側邊欄 — 輸入區
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🔮 起卦設定")

    # 占卜問題（必填）
    divination_question = st.text_area(
        "📝 占卜問題（必填）",
        placeholder="請輸入您要占卜的問題，例如：今日運勢如何？",
        height=80,
        key="divination_question",
        help="詳細描述您的問題，以便 AI 提供更精準的解讀",
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # 起卦方法
    method = st.selectbox(
        "🎴 起卦方法",
        ["大衍蓍草法（自動）", "手動輸入"],
        key="method_select",
        help="大衍蓍草法：依照當前時間自動起卦\n手動輸入：自行選擇每一爻",
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # 時間設定
    st.markdown("#### 📅 起卦時間")
    pp_date = st.date_input("日期", pdlm.now(tz='Asia/Shanghai').date())

    if 'pp_time' not in st.session_state:
        st.session_state.pp_time = pdlm.now(tz='Asia/Shanghai').time()

    time_col, now_col = st.columns([3, 1])
    with time_col:
        pp_time = st.time_input("時間", value=st.session_state.pp_time)
        st.session_state.pp_time = pp_time
    with now_col:
        st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
        if st.button("現在", help="設定為當前北京時間"):
            st.session_state.pp_time = pdlm.now(tz='Asia/Shanghai').time()
            st.rerun()

    p = str(pp_date).split("-")
    pp = str(pp_time).split(":")
    y = int(p[0])
    m = int(p[1])
    d = int(p[2])
    h = int(pp[0])
    mi = int(pp[1])

    # 手動輸入爻
    manual = False
    combine = ""
    if method == "手動輸入":
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### ✍️ 手動起爻")
        st.caption("初爻由下而上")

        with st.form("manual_form"):
            option_sixth = st.selectbox('上爻', ('老陰', '少陰', '少陽', '老陽'))
            option_fifth = st.selectbox('五爻', ('老陰', '少陰', '少陽', '老陽'))
            option_forth = st.selectbox('四爻', ('老陰', '少陰', '少陽', '老陽'))
            option_third = st.selectbox('三爻', ('老陰', '少陰', '少陽', '老陽'))
            option_second = st.selectbox('二爻', ('老陰', '少陰', '少陽', '老陽'))
            option_first = st.selectbox('初爻', ('老陰', '少陰', '少陽', '老陽'))
            yaodict = {"老陰": "6", '少陽': "7", "老陽": "9", '少陰': "8"}
            combine = "".join([yaodict.get(i) for i in [option_first, option_second, option_third, option_forth, option_fifth, option_sixth]])
            manual = st.form_submit_button('🔮 手動起卦', use_container_width=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # 立即起卦按鈕
    st.markdown('<div class="qigua-btn">', unsafe_allow_html=True)
    auto_qigua = st.button("☯ 立即起卦", use_container_width=True, key="auto_qigua_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # --- AI 設定 ---
    with st.expander("🤖 AI 設定", expanded=False):
        selected_model = st.selectbox(
            "AI 模型",
            options=CEREBRAS_MODEL_OPTIONS,
            index=0,
            key="cerebras_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in CEREBRAS_MODEL_DESCRIPTIONS.items()),
        )

        system_prompts_data = load_system_prompts()
        prompts_list = system_prompts_data.get("prompts", [])
        prompt_names = [pr["name"] for pr in prompts_list]
        selected_prompt = system_prompts_data.get("selected")

        if prompt_names:
            selected_index = 0
            if selected_prompt in prompt_names:
                selected_index = prompt_names.index(selected_prompt)

            selected_name = st.selectbox(
                "選擇系統提示",
                options=prompt_names,
                index=selected_index,
                key="system_prompt_selector",
            )

            system_prompts_data["selected"] = selected_name

            selected_content = ""
            for pr in prompts_list:
                if pr["name"] == selected_name:
                    selected_content = pr["content"]
                    break

            if "system_prompt" not in st.session_state:
                st.session_state.system_prompt = selected_content
            elif selected_name != st.session_state.get("last_selected_prompt"):
                st.session_state.system_prompt = selected_content

            st.session_state.last_selected_prompt = selected_name

            new_content = st.text_area(
                "編輯系統提示",
                value=st.session_state.system_prompt,
                height=120,
                key="system_prompt_editor",
            )
            st.session_state.system_prompt = new_content

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 更新", key="update_prompt_button"):
                    for pr in prompts_list:
                        if pr["name"] == selected_name:
                            pr["content"] = new_content
                            break
                    if save_system_prompts(system_prompts_data):
                        st.toast(f"✅ 已更新 '{selected_name}'")
            with col2:
                if st.button(
                    "❌ 刪除",
                    key="delete_prompt_button",
                    disabled=len(prompts_list) <= 1,
                ):
                    prompts_list = [pr for pr in prompts_list if pr["name"] != selected_name]
                    system_prompts_data["prompts"] = prompts_list
                    if selected_name == selected_prompt and prompts_list:
                        system_prompts_data["selected"] = prompts_list[0]["name"]
                    if save_system_prompts(system_prompts_data):
                        st.toast(f"✅ 已刪除 '{selected_name}'")
                        st.rerun()

        if "form_key_suffix" not in st.session_state:
            st.session_state.form_key_suffix = 0

        name_key = f"new_prompt_name_{st.session_state.form_key_suffix}"
        content_key = f"new_prompt_content_{st.session_state.form_key_suffix}"

        with st.expander("➕ 新增提示", expanded=False):
            new_prompt_name = st.text_input("新提示名稱", key=name_key)
            new_prompt_content = st.text_area("新提示內容", height=80, key=content_key)
            if st.button(
                "➕ 新增",
                key="add_prompt_button",
                disabled=not new_prompt_name or not new_prompt_content,
            ):
                if new_prompt_name in prompt_names:
                    st.error(f"名稱 '{new_prompt_name}' 已存在。")
                else:
                    prompts_list.append({"name": new_prompt_name, "content": new_prompt_content})
                    system_prompts_data["prompts"] = prompts_list
                    if save_system_prompts(system_prompts_data):
                        st.session_state.form_key_suffix += 1
                        st.toast(f"✅ 已新增 '{new_prompt_name}'")
                        st.rerun()

        if st.toggle("🔧 高級設置", key="advanced_settings_toggle"):
            st.session_state.ai_max_tokens = st.slider(
                "最大 Tokens", 40000, DEFAULT_MAX_TOKENS,
                st.session_state.get("ai_max_tokens", DEFAULT_MAX_TOKENS),
                key="ai_max_tokens_slider",
            )
            st.session_state.ai_temperature = st.slider(
                "溫度", 0.0, 1.5,
                st.session_state.get("ai_temperature", DEFAULT_TEMPERATURE),
                step=0.05, key="ai_temperature_slider",
            )

    # --- 歷史記錄 ---
    if "history" not in st.session_state:
        st.session_state.history = []

    if st.session_state.history:
        with st.expander("📜 占卜歷史", expanded=False):
            for idx, h_item in enumerate(reversed(st.session_state.history)):
                st.markdown(
                    f'<div class="history-item">'
                    f'<b>{h_item["time"]}</b><br/>'
                    f'{h_item["question"][:30]}... → {h_item["bengua"]}之{h_item["zhigua"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# 主畫面 — 起卦邏輯
# ---------------------------------------------------------------------------

# 初始化 session state
if "pan_data" not in st.session_state:
    st.session_state.pan_data = None
if "pan_text" not in st.session_state:
    st.session_state.pan_text = ""

# 觸發起卦
should_qigua = auto_qigua or manual

if should_qigua:
    if not divination_question and not divination_question.strip():
        st.warning("⚠️ 請先在左側輸入您的占卜問題！")
    else:
        with st.spinner("☯ 起卦中，正在演算大衍蓍草法…"):
            ic = ichingshifa.Iching()
            try:
                if manual and combine:
                    pan_text = ic.display_pan_m(y, m, d, h, mi, combine)
                    pan_data = extract_pan_data(y, m, d, h, mi, manual=True, combine=combine)
                else:
                    pan_text = ic.display_pan(y, m, d, h, mi)
                    pan_data = extract_pan_data(y, m, d, h, mi)

                st.session_state.pan_text = pan_text
                st.session_state.pan_data = pan_data
                st.session_state.divination_q = divination_question

                # 加入歷史記錄
                if "error" not in pan_data:
                    st.session_state.history.append({
                        "time": f"{y}/{m}/{d} {h}:{mi:02d}",
                        "question": divination_question,
                        "bengua": pan_data.get("bengua_name", ""),
                        "zhigua": pan_data.get("zhigua_name", ""),
                    })
                    # 只保留最近 20 條
                    if len(st.session_state.history) > 20:
                        st.session_state.history = st.session_state.history[-20:]
            except Exception as e:
                st.error(f"起卦錯誤：{e}")


# ---------------------------------------------------------------------------
# 五個主 Tab
# ---------------------------------------------------------------------------

pan_data = st.session_state.get("pan_data")
pan_text = st.session_state.get("pan_text", "")

tab1, tab2, tab3, tab4, tab5, tab_texts, tab_example, tab_update, tab_links = st.tabs([
    "🔮 卦象總覽",
    "☯ 本卦·變卦",
    "📊 六爻詳解",
    "📋 納甲·六親·神煞",
    "🧠 斷卦參考",
    "📖 占訣",
    "📜 古占例",
    "🆕 日誌",
    "🔗 連結",
])


# =================== Tab 1: 卦象總覽 ===================
with tab1:
    if pan_data and "error" not in pan_data:
        # 模式標籤
        mode_html = (
            '<span class="mode-badge-manual">✍️ 手動盤</span>'
            if manual
            else '<span class="mode-badge-auto">🤖 自動盤</span>'
        )
        st.markdown(mode_html, unsafe_allow_html=True)

        # 總覽資訊
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            gz = pan_data["gangzhi"]
            lunar = pan_data["lunar"]
            st.markdown(f"""
            <div class="gua-card">
                <h3>📅 時間資訊</h3>
                <p>起卦：{pan_data['year']}年{pan_data['month']}月{pan_data['day']}日 {pan_data['hour']}:{pan_data['minute']:02d}</p>
                <p>干支：{gz[0]}年 {gz[1]}月 {gz[2]}日 {gz[3]}時</p>
                <p>農曆：{lunar.get('月')}月{lunar.get('日')}日</p>
            </div>
            """, unsafe_allow_html=True)

        with col_info2:
            # 占卜問題
            q = st.session_state.get("divination_q", "")
            st.markdown(f"""
            <div class="gua-card">
                <h3>❓ 占卜問題</h3>
                <p style="font-size: 1.1rem; color: #f0e6d3;">{q if q else '未設定問題'}</p>
                <p style="color: rgba(240,230,211,0.5); font-size: 0.85rem; margin-top: 0.5rem;">
                    求得【{pan_data['bengua_name']}】之【{pan_data['zhigua_name']}】
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # 大卦圖展示
        col_ben, col_arrow, col_zhi = st.columns([2, 1, 2])

        with col_ben:
            svg_ben = generate_hexagram_svg(
                pan_data["ogua"], title=pan_data["bengua_name"] + "卦"
            )
            st.markdown(
                f'<div class="gua-card"><h3>本卦</h3>{svg_ben}'
                f'<p style="margin-top:0.5rem; color: rgba(240,230,211,0.7);">'
                f'{pan_data.get("bengua_gua", "")}</p></div>',
                unsafe_allow_html=True,
            )

        with col_arrow:
            # 動爻資訊
            dong_info = ""
            if pan_data["dong_yao"]:
                dong_names = [YAO_NAMES[i] for i in pan_data["dong_yao"]]
                dong_info = "、".join(dong_names)
            else:
                dong_info = "無動爻"

            st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding-top: 3rem;">
                <div style="font-size: 2rem; color: #d4af77;">⟹</div>
                <div class="dong-indicator" style="margin-top: 1rem; font-size: 0.9rem;">
                    動爻：{dong_info}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_zhi:
            svg_zhi = generate_hexagram_svg(
                pan_data["zhigua_code"], title=pan_data["zhigua_name"] + "卦"
            )
            st.markdown(
                f'<div class="gua-card"><h3>變卦（之卦）</h3>{svg_zhi}'
                f'<p style="margin-top:0.5rem; color: rgba(240,230,211,0.7);">'
                f'{pan_data.get("zhigua_gua", "")}</p></div>',
                unsafe_allow_html=True,
            )

        # 完整排盤文字
        with st.expander("📋 查看完整排盤文字", expanded=False):
            st.code(pan_text, language=None)

    else:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; color: rgba(240,230,211,0.4);">
            <p style="font-size: 3rem;">☯</p>
            <p style="font-size: 1.2rem; font-family: 'Ma Shan Zheng', serif;">
                請在左側輸入占卜問題，然後點擊「立即起卦」
            </p>
            <p style="font-size: 0.9rem; margin-top: 1rem;">
                支持大衍蓍草法自動起卦與手動輸入六爻
            </p>
        </div>
        """, unsafe_allow_html=True)


# =================== Tab 2: 本卦·變卦 ===================
with tab2:
    if pan_data and "error" not in pan_data:
        col_b, col_z = st.columns(2)

        with col_b:
            st.markdown(f'<div class="gua-card"><h3>本卦 — {pan_data["bengua_name"]}</h3></div>', unsafe_allow_html=True)

            # 逐爻顯示（由上到下）
            for idx in range(5, -1, -1):
                yao_code = pan_data["ogua"][idx]
                liuqin = pan_data["bengua_liuqin"][idx] if idx < len(pan_data["bengua_liuqin"]) else ""
                najia = pan_data["bengua_najia"][idx] if idx < len(pan_data["bengua_najia"]) else ""
                wuxing = pan_data["bengua_wuxing"][idx] if idx < len(pan_data["bengua_wuxing"]) else ""
                shiying = pan_data["bengua_shiying"][idx] if idx < len(pan_data["bengua_shiying"]) else ""

                is_dong = yao_code in ("6", "9")
                dong_class = "dong-yao" if is_dong else ""

                yao_symbol = "▅▅▅▅▅" if yao_code in ("7", "9") else "▅▅　▅▅"
                dong_mark = ""
                if yao_code == "9":
                    dong_mark = '<span class="dong-indicator"> ○</span>'
                elif yao_code == "6":
                    dong_mark = '<span class="dong-indicator"> ✕</span>'

                wx_class = {
                    "木": "wx-mu", "火": "wx-huo", "土": "wx-tu",
                    "金": "wx-jin", "水": "wx-shui"
                }.get(wuxing, "")

                shi_html = ""
                if "世" in shiying:
                    shi_html = '<span class="shi-badge">世</span>'
                elif "應" in shiying:
                    shi_html = '<span class="ying-badge">應</span>'

                st.markdown(f"""
                <div class="yao-card {dong_class}">
                    <div class="yao-name">{YAO_NAMES[idx]}</div>
                    <div class="yao-symbol" style="color: #d4af77; font-family: monospace;">{yao_symbol}{dong_mark}</div>
                    <div class="yao-info">
                        <span class="yao-badge {wx_class}">{wuxing}</span>
                        {liuqin} {najia} {shi_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col_z:
            st.markdown(f'<div class="gua-card"><h3>變卦 — {pan_data["zhigua_name"]}</h3></div>', unsafe_allow_html=True)

            zhigua_code = pan_data["zhigua_code"]
            for idx in range(5, -1, -1):
                yao_code = zhigua_code[idx]
                liuqin = pan_data["zhigua_liuqin"][idx] if idx < len(pan_data["zhigua_liuqin"]) else ""
                najia = pan_data["zhigua_najia"][idx] if idx < len(pan_data["zhigua_najia"]) else ""
                wuxing = pan_data["zhigua_wuxing"][idx] if idx < len(pan_data["zhigua_wuxing"]) else ""
                shiying = pan_data["zhigua_shiying"][idx] if idx < len(pan_data["zhigua_shiying"]) else ""

                yao_symbol = "▅▅▅▅▅" if yao_code in ("7", "9") else "▅▅　▅▅"

                wx_class = {
                    "木": "wx-mu", "火": "wx-huo", "土": "wx-tu",
                    "金": "wx-jin", "水": "wx-shui"
                }.get(wuxing, "")

                shi_html = ""
                if "世" in shiying:
                    shi_html = '<span class="shi-badge">世</span>'
                elif "應" in shiying:
                    shi_html = '<span class="ying-badge">應</span>'

                st.markdown(f"""
                <div class="yao-card">
                    <div class="yao-name">{YAO_NAMES[idx]}</div>
                    <div class="yao-symbol" style="color: #d4af77; font-family: monospace;">{yao_symbol}</div>
                    <div class="yao-info">
                        <span class="yao-badge {wx_class}">{wuxing}</span>
                        {liuqin} {najia} {shi_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("請先起卦以查看本卦與變卦。")


# =================== Tab 3: 六爻詳解 ===================
with tab3:
    if pan_data and "error" not in pan_data:
        st.markdown('<div class="gua-card"><h3>六爻逐爻詳解</h3></div>', unsafe_allow_html=True)

        yao_desc = pan_data.get("yao_desc", {})

        for idx in range(5, -1, -1):
            yao_code = pan_data["ogua"][idx]
            liuqin = pan_data["bengua_liuqin"][idx] if idx < len(pan_data["bengua_liuqin"]) else ""
            najia = pan_data["bengua_najia"][idx] if idx < len(pan_data["bengua_najia"]) else ""
            wuxing = pan_data["bengua_wuxing"][idx] if idx < len(pan_data["bengua_wuxing"]) else ""
            shiying = pan_data["bengua_shiying"][idx] if idx < len(pan_data["bengua_shiying"]) else ""
            xingxiu = pan_data["bengua_xingxiu"][idx] if idx < len(pan_data["bengua_xingxiu"]) else ""
            liushen = pan_data["liushen"][idx] if idx < len(pan_data["liushen"]) else ""

            is_dong = yao_code in ("6", "9")
            dong_class = "dong-yao" if is_dong else ""

            # 陰陽判定
            yinyang = "陽" if yao_code in ("7", "9") else "陰"
            yao_type_name = {"6": "老陰（動）", "7": "少陽", "8": "少陰", "9": "老陽（動）"}.get(yao_code, "")

            wx_class = {
                "木": "wx-mu", "火": "wx-huo", "土": "wx-tu",
                "金": "wx-jin", "水": "wx-shui"
            }.get(wuxing, "")

            shi_html = ""
            if "世" in shiying:
                shi_html = '<span class="shi-badge">世</span>'
            elif "應" in shiying:
                shi_html = '<span class="ying-badge">應</span>'

            dong_html = ""
            if is_dong:
                changed = "少陽" if yao_code == "6" else "少陰"
                dong_html = f'<span class="dong-indicator">→ 變為{changed}</span>'

            # 爻辭
            yao_text = yao_desc.get(idx + 1, "") if yao_desc else ""

            yao_symbol = "▅▅▅▅▅" if yao_code in ("7", "9") else "▅▅　▅▅"

            # 六神名稱
            liushen_name = {"龍": "青龍", "雀": "朱雀", "陳": "勾陳", "蛇": "螣蛇", "虎": "白虎", "武": "玄武"}.get(liushen, liushen)

            st.markdown(f"""
            <div class="yao-card {dong_class}" style="flex-direction: column; align-items: stretch;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                    <span class="yao-name">{YAO_NAMES[idx]}</span>
                    <span style="color: #d4af77; font-family: monospace; font-size: 1.3rem;">{yao_symbol}</span>
                    <span style="color: rgba(240,230,211,0.6); font-size: 0.85rem;">{yao_type_name}</span>
                    {shi_html}
                    {dong_html}
                </div>
                <div style="display: flex; gap: 0.8rem; flex-wrap: wrap; margin-bottom: 0.5rem;">
                    <span class="yao-badge {wx_class}">五行：{wuxing}</span>
                    <span class="yao-badge" style="background: rgba(212,175,119,0.1); color: #d4af77; border: 1px solid rgba(212,175,119,0.2);">六親：{liuqin}</span>
                    <span class="yao-badge" style="background: rgba(212,175,119,0.1); color: #d4af77; border: 1px solid rgba(212,175,119,0.2);">納甲：{najia}</span>
                    <span class="yao-badge" style="background: rgba(120,100,80,0.15); color: rgba(240,230,211,0.7); border: 1px solid rgba(120,100,80,0.2);">六神：{liushen_name}</span>
                </div>
                <div style="color: rgba(240,230,211,0.6); font-size: 0.85rem; line-height: 1.6;">
                    {yao_text if yao_text else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 卦辭
        if yao_desc:
            st.markdown("<br/>", unsafe_allow_html=True)
            with st.expander("📖 卦辭 · 彖辭 · 象辭", expanded=True):
                gua_ci = yao_desc.get(0, "")
                tuan_ci = yao_desc.get(7, "")[2:] if yao_desc.get(7) else ""
                st.markdown(f"""
                <div class="gua-card">
                    <p><b style="color: #d4af77;">卦辭：</b>{gua_ci}</p>
                    <p><b style="color: #d4af77;">彖：</b>{tuan_ci}</p>
                </div>
                """, unsafe_allow_html=True)

                # 爻辭展示
                for i in range(1, 7):
                    yd = yao_desc.get(i, "")
                    if yd:
                        st.markdown(f"**{YAO_NAMES[i-1]}：** {yd}")
    else:
        st.info("請先起卦以查看六爻詳解。")


# =================== Tab 4: 納甲·六親·神煞 ===================
with tab4:
    if pan_data and "error" not in pan_data:
        st.markdown('<div class="gua-card"><h3>納甲·六親·神煞 詳表</h3></div>', unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)

        # 構建表格
        table_rows = ""
        for idx in range(5, -1, -1):
            yao_code = pan_data["ogua"][idx]
            liuqin = pan_data["bengua_liuqin"][idx] if idx < len(pan_data["bengua_liuqin"]) else ""
            najia = pan_data["bengua_najia"][idx] if idx < len(pan_data["bengua_najia"]) else ""
            wuxing = pan_data["bengua_wuxing"][idx] if idx < len(pan_data["bengua_wuxing"]) else ""
            shiying = pan_data["bengua_shiying"][idx] if idx < len(pan_data["bengua_shiying"]) else ""
            xingxiu = pan_data["bengua_xingxiu"][idx] if idx < len(pan_data["bengua_xingxiu"]) else ""
            liushen = pan_data["liushen"][idx] if idx < len(pan_data["liushen"]) else ""

            yinyang = "陽" if yao_code in ("7", "9") else "陰"
            is_dong = "動" if yao_code in ("6", "9") else "靜"

            wx_color = WUXING_COLORS.get(wuxing, "#f0e6d3")
            liushen_name = {"龍": "青龍", "雀": "朱雀", "陳": "勾陳", "蛇": "螣蛇", "虎": "白虎", "武": "玄武"}.get(liushen, liushen)

            # 世應
            sy_html = ""
            if "世" in shiying:
                sy_html = '<span style="color: #d4af77; font-weight: bold;">世</span>'
            elif "應" in shiying:
                sy_html = '<span style="color: #c94040; font-weight: bold;">應</span>'

            dong_color = "#9c2f2f" if is_dong == "動" else "rgba(240,230,211,0.5)"

            table_rows += f"""
            <tr>
                <td>{YAO_NAMES[idx]}</td>
                <td>{yinyang}</td>
                <td style="color: {wx_color}; font-weight: bold;">{wuxing}</td>
                <td>{liuqin}</td>
                <td>{najia}</td>
                <td>{liushen_name}</td>
                <td>{xingxiu}</td>
                <td>{sy_html}</td>
                <td style="color: {dong_color}; font-weight: bold;">{is_dong}</td>
            </tr>
            """

        st.markdown(f"""
        <table class="info-table">
            <thead>
                <tr>
                    <th>爻位</th>
                    <th>陰陽</th>
                    <th>五行</th>
                    <th>六親</th>
                    <th>納甲</th>
                    <th>六神</th>
                    <th>星宿</th>
                    <th>世應</th>
                    <th>動靜</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """, unsafe_allow_html=True)

        # 伏神資訊
        st.markdown("<br/>", unsafe_allow_html=True)
        fushen = pan_data.get("fushen_ben")
        if fushen:
            with st.expander("👁️ 伏神資訊", expanded=True):
                st.markdown(f"""
                <div class="gua-card">
                    <p><b style="color: #d4af77;">伏神爻：</b>{fushen.get('伏神爻', '')}</p>
                    <p><b style="color: #d4af77;">本卦伏神所在爻：</b>{fushen.get('本卦伏神所在爻', '')}</p>
                </div>
                """, unsafe_allow_html=True)

        # 變卦表格
        st.markdown("<br/>", unsafe_allow_html=True)
        with st.expander("📊 變卦（之卦）詳表", expanded=False):
            zhi_rows = ""
            zhigua_code = pan_data["zhigua_code"]
            for idx in range(5, -1, -1):
                yao_code = zhigua_code[idx]
                liuqin = pan_data["zhigua_liuqin"][idx] if idx < len(pan_data["zhigua_liuqin"]) else ""
                najia = pan_data["zhigua_najia"][idx] if idx < len(pan_data["zhigua_najia"]) else ""
                wuxing = pan_data["zhigua_wuxing"][idx] if idx < len(pan_data["zhigua_wuxing"]) else ""
                shiying = pan_data["zhigua_shiying"][idx] if idx < len(pan_data["zhigua_shiying"]) else ""
                xingxiu = pan_data["zhigua_xingxiu"][idx] if idx < len(pan_data["zhigua_xingxiu"]) else ""

                yinyang = "陽" if yao_code in ("7", "9") else "陰"
                wx_color = WUXING_COLORS.get(wuxing, "#f0e6d3")

                sy_html = ""
                if "世" in shiying:
                    sy_html = '<span style="color: #d4af77; font-weight: bold;">世</span>'
                elif "應" in shiying:
                    sy_html = '<span style="color: #c94040; font-weight: bold;">應</span>'

                zhi_rows += f"""
                <tr>
                    <td>{YAO_NAMES[idx]}</td>
                    <td>{yinyang}</td>
                    <td style="color: {wx_color}; font-weight: bold;">{wuxing}</td>
                    <td>{liuqin}</td>
                    <td>{najia}</td>
                    <td>{xingxiu}</td>
                    <td>{sy_html}</td>
                </tr>
                """

            st.markdown(f"""
            <table class="info-table">
                <thead><tr><th>爻位</th><th>陰陽</th><th>五行</th><th>六親</th><th>納甲</th><th>星宿</th><th>世應</th></tr></thead>
                <tbody>{zhi_rows}</tbody>
            </table>
            """, unsafe_allow_html=True)
    else:
        st.info("請先起卦以查看納甲·六親·神煞。")


# =================== Tab 5: 斷卦參考 ===================
with tab5:
    if pan_data and "error" not in pan_data:
        st.markdown('<div class="gua-card"><h3>🧠 斷卦參考</h3></div>', unsafe_allow_html=True)

        # 大衍筮法解讀
        explanation = pan_data.get("explanation")
        if explanation:
            with st.expander("📖 大衍筮法斷語", expanded=True):
                for item in explanation:
                    if item:
                        st.markdown(f"> {item}")

        st.markdown("<br/>", unsafe_allow_html=True)

        # AI 分析按鈕
        if st.button("🔍 使用 AI 分析排盤結果", key="analyze_with_ai", use_container_width=True):
            question = st.session_state.get("divination_q", "")
            if not pan_text:
                st.warning("排盤數據為空，請重新起卦。")
            else:
                with st.spinner("🤖 AI 正在分析六爻排盤結果..."):
                    cerebras_api_key = (
                        st.secrets.get("CEREBRAS_API_KEY", "")
                        or os.getenv("CEREBRAS_API_KEY", "")
                    )
                    if not cerebras_api_key:
                        st.error("CEREBRAS_API_KEY 未設置，請在 .streamlit/secrets.toml 或環境變量中設置。")
                    else:
                        try:
                            client = CerebrasClient(api_key=cerebras_api_key)

                            # 帶入占卜問題
                            question_context = f"\n\n占卜問題：{question}\n\n" if question else ""
                            user_prompt = (
                                f"以下是六爻排盤的計算結果，請根據這些數據提供詳細的分析和解釋：{question_context}"
                                + pan_text
                            )

                            messages = [
                                {
                                    "role": "system",
                                    "content": st.session_state.get("system_prompt", ""),
                                },
                                {"role": "user", "content": user_prompt},
                            ]
                            api_params = {
                                "messages": messages,
                                "model": selected_model,
                                "max_tokens": st.session_state.get("ai_max_tokens", DEFAULT_MAX_TOKENS),
                                "temperature": st.session_state.get("ai_temperature", DEFAULT_TEMPERATURE),
                            }
                            response = client.get_chat_completion(**api_params)
                            raw_response = response.choices[0].message.content

                            st.markdown(f"""
                            <div class="gua-card" style="text-align: left;">
                                <h3>🤖 AI 分析結果</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown(raw_response)
                        except Exception as e:
                            st.error(f"調用 AI 時發生錯誤：{e}")
    else:
        st.info("請先起卦以查看斷卦參考。")


# =================== Tab: 占訣 ===================
with tab_texts:
    st.markdown('<div class="gua-card"><h3>📖 占訣</h3></div>', unsafe_allow_html=True)
    st.markdown(read_local_file("docs/text.md"))


# =================== Tab: 古占例 ===================
with tab_example:
    st.markdown('<div class="gua-card"><h3>📜 古占例</h3></div>', unsafe_allow_html=True)
    st.markdown(read_local_file("docs/example.md"))


# =================== Tab: 日誌 ===================
with tab_update:
    st.markdown('<div class="gua-card"><h3>🆕 更新日誌</h3></div>', unsafe_allow_html=True)
    st.markdown(read_local_file("docs/update.md"))


# =================== Tab: 連結 ===================
with tab_links:
    st.markdown('<div class="gua-card"><h3>🔗 相關連結</h3></div>', unsafe_allow_html=True)
    try:
        st.markdown(
            get_remote_file(
                "https://raw.githubusercontent.com/kentang2017/kinliuren/master/update.md"
            ),
            unsafe_allow_html=True,
        )
    except Exception:
        st.info("無法載入遠端連結內容。")


# ---------------------------------------------------------------------------
# 底部固定 LLM 聊天區域
# ---------------------------------------------------------------------------

st.markdown('<div class="chat-container"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("### 💬 AI 對話助手")

# 初始化聊天記錄
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# 顯示聊天記錄
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天輸入
if chat_input := st.chat_input("請輸入您的問題，我會結合排盤結果為您解答..."):
    # 添加用戶訊息
    st.session_state.chat_messages.append({"role": "user", "content": chat_input})
    with st.chat_message("user"):
        st.markdown(chat_input)

    # 調用 AI
    cerebras_api_key = (
        st.secrets.get("CEREBRAS_API_KEY", "")
        or os.getenv("CEREBRAS_API_KEY", "")
    )

    if not cerebras_api_key:
        with st.chat_message("assistant"):
            st.error("CEREBRAS_API_KEY 未設置。")
    else:
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    client = CerebrasClient(api_key=cerebras_api_key)

                    # 構建上下文
                    context = ""
                    if pan_text:
                        context = f"\n\n當前排盤數據：\n{pan_text}"

                    question = st.session_state.get("divination_q", "")
                    if question:
                        context += f"\n\n占卜問題：{question}"

                    system_msg = st.session_state.get("system_prompt", "") + context

                    messages = [{"role": "system", "content": system_msg}]
                    # 加入聊天歷史（最近 10 條）
                    for msg in st.session_state.chat_messages[-10:]:
                        messages.append({"role": msg["role"], "content": msg["content"]})

                    api_params = {
                        "messages": messages,
                        "model": selected_model,
                        "max_tokens": st.session_state.get("ai_max_tokens", DEFAULT_MAX_TOKENS),
                        "temperature": st.session_state.get("ai_temperature", DEFAULT_TEMPERATURE),
                    }
                    response = client.get_chat_completion(**api_params)
                    assistant_msg = response.choices[0].message.content
                    st.markdown(assistant_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": assistant_msg})
                except Exception as e:
                    st.error(f"AI 回應錯誤：{e}")
