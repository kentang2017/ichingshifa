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

st.set_page_config(layout="wide",page_title="堅六爻-周易排盤")
pan,booktext,oexample,update,links = st.tabs([' 🧮排盤 ',  ' 🚀占訣 ', ' 📜古占例 ', '🆕日誌', ' 🔗連結 '])

with st.sidebar:
    pp_date=st.date_input("日期",pdlm.now(tz='Asia/Shanghai').date())
    pp_time=st.time_input("時間",pdlm.now(tz='Asia/Shanghai').time())

    # 設置時間初始值
    if 'pp_time' not in st.session_state:
        st.session_state.pp_time = pdlm.now(tz='Asia/Shanghai').time()

# 使用儲存的時間初始值
    pp_time = st.time_input("時間", value=st.session_state.pp_time)
    st.session_state.pp_time = pp_time
    p = str(pp_date).split("-")
    pp = str(pp_time).split(":")
    y = int(p[0])
    m = int(p[1])
    d = int(p[2])
    h = int(pp[0])
    min = int(pp[1])
    st.write("")
    st.write("手動起爻︰(初爻由下而上)")
    option_sixth = st.selectbox(
         '上爻',
        ('老陰', '少陰', '少陽', '老陽'))
    option_fifth = st.selectbox(
        '五爻',
        ('老陰', '少陰', '少陽', '老陽'))
    option_forth = st.selectbox(
        '四爻',
        ('老陰', '少陰', '少陽', '老陽'))
    option_third = st.selectbox(
         '三爻',
        ('老陰', '少陰', '少陽', '老陽'))
    option_second = st.selectbox(
         '二爻',
        ('老陰', '少陰', '少陽', '老陽'))
    option_first = st.selectbox(
         '初爻',
        ('老陰', '少陰', '少陽', '老陽'))
    yaodict = {"老陰": "6", '少陽':"7", "老陽": "9", '少陰':"8" }
    combine = "".join([yaodict.get(i) for i in [option_first, option_second,option_third,option_forth,option_fifth,option_sixth]])
    manual = st.button('手動盤')
    #st.write(combine)

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

with pan:
    st.header('堅六爻')
    pan = ichingshifa.Iching().display_pan(y,m,d,h,min)
    pan_m = ichingshifa.Iching().display_pan_m(y,m,d,h,min,combine)
    output2 = st.empty()
    with st_capture(output2.code):
        if not manual:
            print(pan)
        if manual:
            try:
                print(pan_m)
            except (ValueError, UnboundLocalError):
                print(pan)


