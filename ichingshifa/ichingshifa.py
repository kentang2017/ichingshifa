# -*- coding: utf-8 -*-#
import pickle, random
import datetime
import os

base = os.path.abspath(os.path.dirname(__file__))
path1 = os.path.join(base, 'sixtyfourgua.pkl')
path2 = os.path.join(base, 'sixtyfourgua_description.pkl')
sixtyfourgua = pickle.load(open(path1, "rb"))
sixtyfourgua_description = pickle.load(open(path2, "rb"))
eightgua = {1:"777", 2:"778", 3:"787", 4:"788", 5:"877", 6:"878", 7:"887", 8:"888"} #先天八卦
eightgua_element = {1: "天", 2:"澤", 3:"火", 4:"雷", 5:"風", 6:"水", 7:"山", 8:"地"}
#64卦、4096種卦爻組合資料庫，爻由底(左)至上(右)起
def rev(l):
    r = []
    for i in l:
        r.insert(0, i)
    return r

def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None

def mget_bookgua_details(guayao):
    getgua = multi_key_dict_get(sixtyfourgua, guayao)
    yao_results = sixtyfourgua_description.get(getgua)
    bian_yao = guayao.replace("6","1").replace("9","1").replace("7","0").replace("8","0")
    dong_yao = bian_yao.count("1")
    explaination = "動爻有【"+str(dong_yao )+"】根。"
    dong_yao_change = guayao.replace("6","7").replace("9","8")
    g_gua = multi_key_dict_get(sixtyfourgua, dong_yao_change)
    g_gua_result = sixtyfourgua_description.get(g_gua)
    b_gua_n_g_gua = "【"+getgua+"之"+g_gua+"】"
    top_bian_yao = bian_yao.rfind("1")+int(1)
    second_bian_yao = bian_yao.rfind("1",0, bian_yao.rfind("1"))+int(1)
    top_jing_yao = bian_yao.rfind("0") + int(1)
    second_jing_yao = bian_yao.rfind("0", 0, bian_yao.rfind("0"))+int(1)
    top = yao_results.get(top_bian_yao)
    second = yao_results.get(second_bian_yao)
    top_2 = yao_results.get(top_jing_yao)
    second_2 = yao_results.get(second_jing_yao)
    explaination2 = None
    try:
        if dong_yao == 0:
            explaination2 = explaination, "主要看【"+getgua+"】卦彖辭。",  yao_results[7][2:]
        elif dong_yao == 1: 
            explaination2 = explaination, b_gua_n_g_gua, "主要看【"+top[:2]+"】",  top
        elif dong_yao == 2:
            explaination2 = b_gua_n_g_gua, explaination, "主要看【"+top[:2]+"】，其次看【"+second[:2]+"】。", top, second
        elif dong_yao == 3:
            if bian_yao.find("1") == 0:
                explaination2 = b_gua_n_g_gua, explaination,  "【"+getgua+"】卦為貞(我方)，【"+g_gua+"】卦為悔(他方)。前十卦，主貞【"+getgua+"】卦，請參考兩卦彖辭", yao_results[7][2:], g_gua_result[7][2:]
            elif bian_yao.find("1") > 0:
                explaination2 = b_gua_n_g_gua, explaination,  "【"+getgua+"】卦為貞(我方)，【"+g_gua+"】卦為悔(他方)。後十卦，主悔【"+g_gua+"】卦，請參考兩卦彖辭", g_gua_result[7][2:],  yao_results[7][2:]
        elif dong_yao == 4:
            explaination2 = b_gua_n_g_gua, explaination, "主要看【"+g_gua+"】的"+g_gua_result.get(second_jing_yao)[:2]+"，其次看"+g_gua_result.get(top_jing_yao)[:2]+"。", g_gua_result.get(second_jing_yao), g_gua_result.get(top_jing_yao)
        elif dong_yao == 5:    
            explaination2 = b_gua_n_g_gua, explaination,  "主要看【"+g_gua+"】的"+g_gua_result.get(top_jing_yao)[:2]+"。", g_gua_result.get(top_jing_yao)
        elif dong_yao == 6:
            explaination2 = b_gua_n_g_gua, explaination, "主要看【"+g_gua+"】卦的彖辭。", g_gua_result[7][2:]
    except (TypeError, UnboundLocalError):
        pass
    return [guayao, getgua, g_gua, yao_results, explaination2]


def bookgua(): #由底至上起爻
    shifa_results = []
    for i in range(6):
        stalks_first = 50-1 #一變 (分二、掛一、揲四、歸奇)
        dividers = sorted(random.sample(range(24, stalks_first), 1))
        first_division  = [a - b for a, b in zip(dividers + [stalks_first+10], [10] + dividers)]
        guayi = 1
        right = first_division[0] - guayi
        left_extract = first_division[1] % 4 
        if left_extract == 0:
            left_extract = 4
        right_extract = right % 4
        if right_extract == 0:
            right_extract = 4
        yibian  = left_extract + right_extract + guayi #二變 (分二、掛一、揲四、歸奇)
        stalks_second = stalks_first - yibian
        second_dividers = sorted(random.sample(range(12, stalks_second), 1))
        second_division  = [a - b for a, b in zip(second_dividers + [stalks_second+5], [5] + second_dividers)]
        right_second = second_division[0] - guayi
        left_extract_second = second_division[1] % 4 
        if left_extract_second == 0:
            left_extract_second = 4
        right_extract_second = right_second % 4 
        if right_extract_second == 0:
            right_extract_second = 4
        erbian = left_extract_second + right_extract_second + guayi #三變 (分二、掛一、揲四、歸奇)
        stalks_third = stalks_second - erbian
        third_dividers = sorted(random.sample(range(6, stalks_third), 1))
        third_division  = [a - b for a, b in zip(third_dividers + [stalks_third+3], [3] + third_dividers)]
        right_third = third_division[0] - guayi
        left_extract_third = third_division[1] % 4
        if left_extract_third  == 0:
            left_extract_third = 4
        right_extract_third = right_third % 4 
        if right_extract_third == 0:
            right_extract_third = 4
        sanbian = left_extract_third + right_extract_third + guayi
        yao = int((stalks_first - yibian - erbian - sanbian) / 4)
        shifa_results.append(yao)
    return "".join(str(e) for e in shifa_results[:6])

def datetime_bookgua(year, month, day, hour):
    upper_gua_remain = (year+month+day) % 8
    if upper_gua_remain is 0:
        upper_gua_remain = int(8)
    upper_gua = eightgua.get(upper_gua_remain)
    lower_gua_remain = (year+month+day+hour) % 8
    if lower_gua_remain is 0:
        lower_gua_remain = int(8)
    lower_gua = eightgua.get(lower_gua_remain)
    combine_gua1 =lower_gua+upper_gua
    combine_gua = list(combine_gua1)
    bian_yao = (year+month+day+hour) % 6
    if bian_yao is 0:
        bian_yao = int(6)
    if bian_yao is not 0:
        combine_gua[bian_yao -1] = combine_gua[bian_yao-1].replace("7","6").replace("8","9")
    bian_gua = "".join(combine_gua)
    ben_gua = multi_key_dict_get(sixtyfourgua, bian_gua)
    description = multi_key_dict_get(sixtyfourgua_description,  ben_gua)
    g_gua = multi_key_dict_get(sixtyfourgua, (bian_gua.replace("6", "7").replace("9", "8")))
    return ben_gua+"之"+g_gua, eightgua_element.get(upper_gua_remain)+eightgua_element.get(lower_gua_remain)+ben_gua , "變爻為"+description[bian_yao][:2], description[bian_yao][3:]
    
def bookgua_details():
    return mget_bookgua_details(bookgua())
    
def current_bookgua():
    now = datetime.datetime.now()
    return datetime_bookgua(int(now.year), int(now.month), int(now.day), int(now.hour))
