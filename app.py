import os
import json
import urllib.request

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
# Helper utilities
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_PROMPTS_FILE = os.path.join(BASE_DIR, "system_prompts.json")
DEFAULT_MAX_TOKENS = 200000
DEFAULT_TEMPERATURE = 0.7


@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write

        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret

        stdout.write = new_write
        yield


def read_local_file(path):
    """Read a text file relative to the project root."""
    full = os.path.join(BASE_DIR, path)
    with open(full, "r", encoding="utf-8") as f:
        return f.read()


def get_remote_file(url):
    """Fetch a remote text file."""
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")


# ---------------------------------------------------------------------------
# System prompt persistence
# ---------------------------------------------------------------------------

def load_system_prompts():
    """Load system prompts from JSON file, creating defaults if needed."""
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
    """Persist system prompts to JSON file."""
    try:
        with open(SYSTEM_PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(prompts_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"儲存提示時發生錯誤：{e}")
        return False


# ---------------------------------------------------------------------------
# Page config & tabs
# ---------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="堅六爻-周易排盤")
tab_pan, tab_booktext, tab_example, tab_update, tab_links = st.tabs(
    [" 🧮排盤 ", " 🚀占訣 ", " 📜古占例 ", "🆕日誌", " 🔗連結 "]
)

# ---------------------------------------------------------------------------
# Sidebar – date/time, manual yao, and AI settings
# ---------------------------------------------------------------------------

with st.sidebar:
    pp_date = st.date_input("日期", pdlm.now(tz="Asia/Shanghai").date())

    if "pp_time" not in st.session_state:
        st.session_state.pp_time = pdlm.now(tz="Asia/Shanghai").time()

    pp_time = st.time_input("時間", value=st.session_state.pp_time)
    st.session_state.pp_time = pp_time
    p = str(pp_date).split("-")
    pp = str(pp_time).split(":")
    y = int(p[0])
    m = int(p[1])
    d = int(p[2])
    h = int(pp[0])
    mi = int(pp[1])
    st.write("")
    st.write("手動起爻︰(初爻由下而上)")

    with st.form("manual_form"):
        option_sixth = st.selectbox("上爻", ("老陰", "少陰", "少陽", "老陽"))
        option_fifth = st.selectbox("五爻", ("老陰", "少陰", "少陽", "老陽"))
        option_forth = st.selectbox("四爻", ("老陰", "少陰", "少陽", "老陽"))
        option_third = st.selectbox("三爻", ("老陰", "少陰", "少陽", "老陽"))
        option_second = st.selectbox("二爻", ("老陰", "少陰", "少陽", "老陽"))
        option_first = st.selectbox("初爻", ("老陰", "少陰", "少陽", "老陽"))
        yaodict = {"老陰": "6", "少陽": "7", "老陽": "9", "少陰": "8"}
        combine = "".join(
            yaodict.get(i)
            for i in [
                option_first,
                option_second,
                option_third,
                option_forth,
                option_fifth,
                option_sixth,
            ]
        )
        manual = st.form_submit_button("手動盤")

    # --- AI settings ---
    st.markdown("---")
    st.header("AI設置")

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
            help="選擇用於AI模型的系統提示，指導其分析六爻排盤結果",
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
            height=150,
            placeholder="範例：你是一位六爻大師，根據排盤數據提供詳細分析...",
            key="system_prompt_editor",
        )
        st.session_state.system_prompt = new_content

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 更新提示", key="update_prompt_button"):
                for pr in prompts_list:
                    if pr["name"] == selected_name:
                        pr["content"] = new_content
                        break
                if save_system_prompts(system_prompts_data):
                    st.toast(f"✅ 已更新系統提示 '{selected_name}'！")
        with col2:
            if st.button(
                "❌ 刪除提示",
                key="delete_prompt_button",
                disabled=len(prompts_list) <= 1,
            ):
                prompts_list = [
                    pr for pr in prompts_list if pr["name"] != selected_name
                ]
                system_prompts_data["prompts"] = prompts_list
                if selected_name == selected_prompt and prompts_list:
                    system_prompts_data["selected"] = prompts_list[0]["name"]
                if save_system_prompts(system_prompts_data):
                    st.toast(f"✅ 已刪除系統提示 '{selected_name}'！")
                    st.rerun()

    if "form_key_suffix" not in st.session_state:
        st.session_state.form_key_suffix = 0

    name_key = f"new_prompt_name_{st.session_state.form_key_suffix}"
    content_key = f"new_prompt_content_{st.session_state.form_key_suffix}"

    with st.expander("➕ 新增提示", expanded=False):
        new_prompt_name = st.text_input("新提示名稱", key=name_key)
        new_prompt_content = st.text_area(
            "新提示內容",
            height=100,
            placeholder="輸入AI分析指令...",
            key=content_key,
        )
        if st.button(
            "➕ 新增提示",
            key="add_prompt_button",
            disabled=not new_prompt_name or not new_prompt_content,
        ):
            if new_prompt_name in prompt_names:
                st.error(f"提示名稱 '{new_prompt_name}' 已存在。")
            else:
                prompts_list.append(
                    {"name": new_prompt_name, "content": new_prompt_content}
                )
                system_prompts_data["prompts"] = prompts_list
                if save_system_prompts(system_prompts_data):
                    st.session_state.form_key_suffix += 1
                    st.toast(f"✅ 已新增系統提示 '{new_prompt_name}'！")
                    st.rerun()

    if st.toggle("🔧 高級設置", key="advanced_settings_toggle"):
        st.session_state.ai_max_tokens = st.slider(
            "最大生成 Tokens",
            40000,
            DEFAULT_MAX_TOKENS,
            st.session_state.get("ai_max_tokens", DEFAULT_MAX_TOKENS),
            key="ai_max_tokens_slider",
            help="控制AI回應的最大長度",
        )
        st.session_state.ai_temperature = st.slider(
            "溫度 (專注 vs. 創意)",
            0.0,
            1.5,
            st.session_state.get("ai_temperature", DEFAULT_TEMPERATURE),
            step=0.05,
            key="ai_temperature_slider",
            help="較低值 (如 0.2) 更確定性；較高值 (如 0.8) 更隨機",
        )

# ---------------------------------------------------------------------------
# Tab: 連結
# ---------------------------------------------------------------------------

with tab_links:
    st.header("連接")
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
# Tab: 日誌
# ---------------------------------------------------------------------------

with tab_update:
    st.header("日誌")
    st.markdown(read_local_file("docs/update.md"))

# ---------------------------------------------------------------------------
# Tab: 占訣
# ---------------------------------------------------------------------------

with tab_booktext:
    st.header("占訣")
    st.markdown(read_local_file("docs/text.md"))

# ---------------------------------------------------------------------------
# Tab: 古占例
# ---------------------------------------------------------------------------

with tab_example:
    st.header("古占例")
    st.markdown(read_local_file("docs/example.md"))

# ---------------------------------------------------------------------------
# Tab: 排盤 (main chart + AI analysis)
# ---------------------------------------------------------------------------

with tab_pan:
    st.header("堅六爻")

    # Generate chart text
    pan_text = ""
    output2 = st.empty()
    with st_capture(output2.code):
        if not manual:
            pan_text = ichingshifa.Iching().display_pan(y, m, d, h, mi)
            print(pan_text)
        if manual:
            try:
                pan_text = ichingshifa.Iching().display_pan_m(y, m, d, h, mi, combine)
                print(pan_text)
            except (ValueError, UnboundLocalError) as exc:
                print(f"起卦錯誤：{exc}")

    # --- AI analysis button ---
    if st.button("🔍 使用AI分析排盤結果", key="analyze_with_ai"):
        with st.spinner("AI正在分析六爻排盤結果..."):
            cerebras_api_key = (
                st.secrets.get("CEREBRAS_API_KEY", "")
                or os.getenv("CEREBRAS_API_KEY", "")
            )
            if not cerebras_api_key:
                st.error(
                    "CEREBRAS_API_KEY 未設置，請在 .streamlit/secrets.toml 或環境變量中設置。"
                )
            else:
                try:
                    client = CerebrasClient(api_key=cerebras_api_key)
                    user_prompt = (
                        "以下是六爻排盤的計算結果，請根據這些數據提供詳細的分析和解釋：\n\n"
                        + pan_text
                    )
                    messages = [
                        {
                            "role": "system",
                            "content": st.session_state.get(
                                "system_prompt", ""
                            ),
                        },
                        {"role": "user", "content": user_prompt},
                    ]
                    api_params = {
                        "messages": messages,
                        "model": selected_model,
                        "max_tokens": st.session_state.get(
                            "ai_max_tokens", DEFAULT_MAX_TOKENS
                        ),
                        "temperature": st.session_state.get(
                            "ai_temperature", DEFAULT_TEMPERATURE
                        ),
                    }
                    response = client.get_chat_completion(**api_params)
                    raw_response = response.choices[0].message.content
                    with st.expander("AI分析結果", expanded=True):
                        st.markdown(raw_response)
                except Exception as e:
                    st.error(f"調用AI時發生錯誤：{e}")
