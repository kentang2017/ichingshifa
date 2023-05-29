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

st.set_page_config(layout="wide",page_title="堅六爻")
pan,update,text = st.tabs([' 排盤 ', ' 日誌 ', ' 占訣 '])
with st.sidebar:
    pp_date=st.date_input("日期",pdlm.now(tz='Asia/Shanghai').date())
    pp_time=st.time_input("時間",pdlm.now(tz='Asia/Shanghai').time())
    p = str(pp_date).split("-")
    pp = str(pp_time).split(":")
    y = int(p[0])
    m = int(p[1])
    d = int(p[2])
    h = int(pp[0])
    min = int(pp[1])

with update:
    st.header('日誌')
    st.markdown(get_file_content_as_string("update.md"))
  
with text:
    st.header('占訣')
    st.markdown(get_file_content_as_string("text.md"))

with pan:
    st.header('堅六爻')
    pan = ichingshifa.Iching().display_pan(y,m,d,h,min)
    output2 = st.empty()
    with st_capture(output2.code):
        print(pan)

