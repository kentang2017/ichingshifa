import pickle, random

(sixtyfourgua, sixtyfourgua_description) = (pickle.load( open( "data/sixtyfourgua.pkl", "rb" )), pickle.load( open( "data/sixtyfourgua_description.pkl", "rb")))#64卦、4096種卦爻組合資料庫，爻由底(左)至上(右)起

def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None

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

def bookgua_details():
    guayao = bookgua()
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
            explaination2 = "主要看【"+getgua+"】卦彖辭。",  yao_results[7][2:]
        elif dong_yao == 1: 
            explaination2 = b_gua_n_g_gua, "主要看【"+top[:2]+"】",  top
        elif dong_yao == 2:
            explaination2 = b_gua_n_g_gua, "主要看【"+top[:2]+"】，其次看【"+second[:2]+"】。", top, second
        elif dong_yao == 3:
            if bian_yao.find("1") == 0:
                explaination2 = b_gua_n_g_gua, "【"+getgua+"】卦為貞(我方)，【"+g_gua+"】卦為悔(他方)。主悔【"+g_gua+"】卦，請參考兩卦彖辭", g_gua_result[7][2:],  yao_results[7][2:]
            elif bian_yao.find("1") > 0:
                explaination2 = b_gua_n_g_gua, "【"+getgua+"】卦為貞(我方)，【"+g_gua+"】卦為悔(他方)。主貞【"+getgua+"】卦，請參考兩卦彖辭", yao_results[7][2:], g_gua_result[7][2:]
        elif dong_yao == 4:
            explaination2 = b_gua_n_g_gua, "主要看【"+g_gua+"】的"+g_gua_result.get(second_jing_yao)[:2]+"，其次看"+g_gua_result.get(top_jing_yao)[:2]+"。", g_gua_result.get(second_jing_yao), g_gua_result.get(top_jing_yao)
        elif dong_yao == 5:    
            explaination2 = b_gua_n_g_gua, "主要看【"+g_gua+"】的"+g_gua_result.get(top_jing_yao)[:2]+"。", g_gua_result.get(top_jing_yao)
        elif dong_yao == 6:
            explaination2 = b_gua_n_g_gua, "主要看【"+g_gua+"】卦的彖辭。", g_gua_result[7][2:]
    except (TypeError, UnboundLocalError):
        pass
    return  guayao, getgua, yao_results, explaination, explaination2