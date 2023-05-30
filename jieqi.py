# -*- coding: utf-8 -*-
"""
Created on Tue May  9 20:32:01 2023

@author: kentang
"""

import re
from math import pi
from ephem import Sun, Date, Ecliptic, Equatorial

jieqi_name = re.findall('..', '春分清明穀雨立夏小滿芒種夏至小暑大暑立秋處暑白露秋分寒露霜降立冬小雪大雪冬至小寒大寒立春雨水驚蟄')

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

def gong_wangzhuai():
    wangzhuai = list("旺相胎沒死囚休廢")
    wangzhuai_num = [3,4,9,2,7,6,1,8]
    wangzhuai_jieqi = {('春分','清明','穀雨'):'春分',
                        ('立夏','小滿','芒種'):'立夏',
                        ('夏至','小暑','大暑'):'夏至',
                        ('立秋','處暑','白露'):'立秋',
                        ('秋分','寒露','霜降'):'秋分',
                        ('立冬','小雪','大雪'):'立冬',
                        ('冬至','小寒','大寒'):'冬至',
                        ('立春','雨水','驚蟄'):'立春'}
    return dict(zip(new_list(wangzhuai_num, dict(zip(jieqi_name[0::3],wangzhuai_num )).get(multi_key_dict_get(wangzhuai_jieqi, "霜降"))), wangzhuai))

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

def jq(year, month, day, hour):
    ct =  Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
    p = Date(round((ct - 7 ), 3)).tuple()
    pp = Date(round((ct - 21 ), 3)).tuple()
    bf = fjqs(p[0], p[1], p[2], p[3])
    bbf = fjqs(pp[0], pp[1], pp[2], pp[3])
    if ct < bf[1]:
        return bbf[0]
    else:
        return jieqi_name[jieqi_name.index(bf[0])-1]

