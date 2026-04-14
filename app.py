import os, urllib
import streamlit as st
import pendulum as pdlm
from contextlib import contextmanager, redirect_stdout
from sxtwl import fromSolar
from io import StringIO
import streamlit.components.v1 as components
from ichingshifa import ichingshifa

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

def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/kentang2017/ichingshifa/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

def get_file_content_as_string1(path):
    url = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

st.set_page_config(layout="wide", page_title="堅六爻-周易排盤", page_icon="☯️")

# Custom CSS for improved UI
st.markdown("""
<style>
/* Larger monospace font in code blocks for better readability */
.stCode code, .stCode pre {
    font-size: 15px !important;
    line-height: 1.6 !important;
}
/* Sidebar section header styling */
.sidebar-section {
    font-size: 14px;
    font-weight: bold;
    color: #FF4B4B;
    margin-top: 8px;
    margin-bottom: 4px;
}
/* Mode badge */
.mode-badge-auto {
    background-color: #1f6aa5;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: bold;
}
.mode-badge-manual {
    background-color: #7a3b8c;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

pan_tab, booktext, oexample, update, links = st.tabs([' 🧮排盤 ', ' 🚀占訣 ', ' 📜古占例 ', '🆕日誌', ' 🔗連結 '])

with st.sidebar:
    st.markdown("#### 📅 起卦時間")
    pp_date = st.date_input("日期", pdlm.now(tz='Asia/Shanghai').date())

    # 設置時間初始值
    if 'pp_time' not in st.session_state:
        st.session_state.pp_time = pdlm.now(tz='Asia/Shanghai').time()

    time_col, now_col = st.columns([3, 1])
    with time_col:
        pp_time = st.time_input("時間", value=st.session_state.pp_time)
        st.session_state.pp_time = pp_time
    with now_col:
        st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
        if st.button("現在", help="設定為當前時間"):
            st.session_state.pp_time = pdlm.now(tz='Asia/Shanghai').time()
            st.rerun()

    p = str(pp_date).split("-")
    pp = str(pp_time).split(":")
    y = int(p[0])
    m = int(p[1])
    d = int(p[2])
    h = int(pp[0])
    min = int(pp[1])

    st.divider()
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

with links:
    st.header('連接')
    st.markdown(get_file_content_as_string1("update.md"), unsafe_allow_html=True)

with update:
    st.header('日誌')
    st.markdown(get_file_content_as_string("update.md"))

with booktext:
    st.header('占訣')
    st.markdown(get_file_content_as_string("text.md"))

with oexample:
    st.header('古占例')
    st.markdown(get_file_content_as_string("example.md"))

with pan_tab:
    header_col, mode_col = st.columns([4, 1])
    with header_col:
        st.header('☯️ 堅六爻　周易排盤')
    with mode_col:
        st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
        if manual:
            st.markdown('<span class="mode-badge-manual">✍️ 手動盤</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="mode-badge-auto">🤖 自動盤</span>', unsafe_allow_html=True)

    output2 = st.empty()
    with st.spinner("起卦中，請稍候…"):
        with st_capture(output2.code):
            if not manual:
                # Automatic mode
                result = ichingshifa.Iching().display_pan(y, m, d, h, min)
                print(result)
            elif manual:
                # Manual mode: use the 'combine' from sidebar selectboxes
                try:
                    result = ichingshifa.Iching().display_pan_m(y, m, d, h, min, combine)
                    print(result)
                except (ValueError, UnboundLocalError):
                    print("")  # Or handle error as needed, e.g., fallback to automatic
