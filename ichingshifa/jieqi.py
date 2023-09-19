# -*- coding: utf-8 -*-
"""
Created on Tue May  9 20:32:01 2023

@author: kentang
"""

import re
from math import pi
from ephem import Sun, Date, Ecliptic, Equatorial
import eacal
from sxtwl import fromSolar
from datetime import datetime

jieqi_name = re.findall('..', '春分清明穀雨立夏小滿芒種夏至小暑大暑立秋處暑白露秋分寒露霜降立冬小雪大雪冬至小寒大寒立春雨水驚蟄')
jqmc = ["冬至", "小寒", "大寒", "立春", "雨水", "驚蟄", "春分", "清明", "谷雨", "立夏",
     "小滿", "芒種", "夏至", "小暑", "大暑", "立秋", "處暑","白露", "秋分", "寒露", "霜降", 
     "立冬", "小雪", "大雪"]
jieqi_name = re.findall('..', '春分清明穀雨立夏小滿芒種夏至小暑大暑立秋處暑白露秋分寒露霜降立冬小雪大雪冬至小寒大寒立春雨水驚蟄')
c_t = eacal.EACal(zh_t=True)


def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None

def new_list(olist, o):
    a = olist.index(o)
    res1 = olist[a:] + olist[:a]
    return res1

def ecliptic_lon(jd_utc):
    return Ecliptic(Equatorial(Sun(jd_utc).ra,Sun(jd_utc).dec,epoch=jd_utc)).lon

def sta(jd_num):
    return int(ecliptic_lon(jd_num)*180.0/pi/15)
     
def solarterm_iter(jieqi):
    new_s_list = new_list(jieqi_name, jieqi)
    return new_s_list

def iteration(jd_num):
    s1_jd=sta(jd_num)
    s0_jd=s1_jd
    dt=1.0
    while True:
        jd_num+=dt
        s=sta(jd_num)
        if s0_jd!=s:
            s0_jd=s
            dt=-dt/2
        if abs(dt)<0.0000001 and s!=s1_jd:
            break
    return jd_num

def find_jq_date(year, month, day, hour, jie_qi):
    jd_format=Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
    e_1=ecliptic_lon(jd_format)
    n_1=int(e_1*180.0/pi/15)+1
    dzlist = []
    for i in range(24):
        if n_1>=24:
            n_1-=24
        jd_d=iteration(jd_format)
        d=Date(jd_d+1/3).tuple()
        bb_1 = {jieqi_name[n_1]: Date("{}/{}/{} {}:{}:00.00".format(str(d[0]).zfill(4), str(d[1]).zfill(2), str(d[2]).zfill(2), str(d[3]).zfill(2) , str(d[4]).zfill(2)))}
        n_1+=1
        dzlist.append(bb_1)
    return list(dzlist[list(map(lambda i:list(i.keys())[0], dzlist)).index(jie_qi)].values())[0]

def gong_wangzhuai(j_q):
    wangzhuai = list("旺相胎沒死囚休廢")
    #wangzhuai_num = [3,4,9,2,7,6,1,8]
    wangzhuai_num = list("震巽離坤兌乾坎艮")
    wangzhuai_jieqi = {('春分','清明','穀雨'):'春分',
                        ('立夏','小滿','芒種'):'立夏',
                        ('夏至','小暑','大暑'):'夏至',
                        ('立秋','處暑','白露'):'立秋',
                        ('秋分','寒露','霜降'):'秋分',
                        ('立冬','小雪','大雪'):'立冬',
                        ('冬至','小寒','大寒'):'冬至',
                        ('立春','雨水','驚蟄'):'立春'}
    r1 = dict(zip(new_list(wangzhuai_num, dict(zip(jieqi_name[0::3],wangzhuai_num )).get(multi_key_dict_get(wangzhuai_jieqi, j_q))), wangzhuai))
    r2 = {v: k for k, v in r1.items()}
    return r1, r2

def xzdistance(year, month, day, hour):
    return int(find_jq_date(year, month, day, hour, "夏至") -  Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2))))

def distancejq(year, month, day, hour, jq):
    return int( Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2))) - find_jq_date(year-1, month, day, hour, jq) )

def fjqs(year, month, day, hour):
    jd_format = Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
    n= int(ecliptic_lon(jd_format)*180.0/pi/15)+1
    c = []
    for i in range(1):
        if n>=24:
            n-=24
        d = Date(jd_format+1/3).tuple()
        c.append([jieqi_name[n], Date("{}/{}/{} {}:{}:00.00".format(str(d[0]).zfill(4), str(d[1]).zfill(2), str(d[2]).zfill(2), str(d[3]).zfill(2) , str(d[4]).zfill(2)))])
    return c[0]

def find_jq(year, month, day):
    dd = fromSolar(year, month, day) 
    while True:
        dd = dd.before(1)
        if dd.hasJieQi():
            return jqmc[dd.getJieQi()]
            break

def jq(year, month, day, hour, minute):
    solar_termlist = dict(zip([i[0] for i in c_t.get_annual_solar_terms(year)], [i[2] for i in c_t.get_annual_solar_terms(year)]))
    jq1 = find_jq(year, month, day)
    jq1_datetime = solar_termlist.get(jq1)
    jq2 = solarterm_iter(jq1)[1]
    jq2_datetime = solar_termlist.get(jq2)
    jq3 = solarterm_iter(jq1)[-1]
    jq3_datetime = solar_termlist.get(jq3)
    cdatetime = datetime(year, month, day, hour, minute, 0)
    a = cdatetime > jq1_datetime.replace(tzinfo=None)
    b = cdatetime > jq2_datetime.replace(tzinfo=None)
    if a == True:
        if b == False:
            return jq1
        if b == True:
            return jq2
    
