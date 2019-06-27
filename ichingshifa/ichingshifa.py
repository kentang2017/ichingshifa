import random
import pickle

def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None

#64卦、4096種卦爻組合資料庫，爻由底(左)至上(右)起
sixtyfourgua = pickle.load( open( "data/sixtyfourgua.pkl", "rb" ) )
sixtyfourgua_description =  pickle.load( open( "data/sixtyfourgua_description.pkl", "rb" ) )
def bookgua(): #由底至上起爻
    shifa_results = []
    for i in range(6):
        n=2
        #掛一
        stalks_first = 50-1
        #一變 (分二、掛一、揲四、歸奇)
        dividers = sorted(random.sample(range(1, stalks_first), n - 1))
        first_division  = [a - b for a, b in zip(dividers + [stalks_first], [0] + dividers)]
        guayi = 1
        right = first_division[0] - guayi
        left_extract = first_division[1] % 4 
        if left_extract == 0:
            left_extract = 4
        right_extract = right % 4
        if right_extract == 0:
            right_extract = 4
        yibian  = left_extract + right_extract + guayi
        #二變 (分二、掛一、揲四、歸奇)
        
        stalks_second = stalks_first - yibian
        second_dividers = sorted(random.sample(range(1, stalks_second), n - 1))
        second_division  = [a - b for a, b in zip(second_dividers + [stalks_second], [0] + second_dividers)
        right_second = second_division[0] - guayi
        left_extract_second = second_division[1] % 4 
        if left_extract_second == 0:
            left_extract_second = 4
        right_extract_second = right_second % 4 
        if right_extract_second == 0:
            right_extract_second = 4
        erbian = left_extract_second + right_extract_second + guayi
        #三變 (分二、掛一、揲四、歸奇)
        stalks_third = stalks_second - erbian
        third_dividers = sorted(random.sample(range(1, stalks_third), n - 1))
        third_division  = [a - b for a, b in zip(third_dividers + [stalks_third], [0] + third_dividers)]
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
    return str(shifa_results[0]) + str(shifa_results[1]) + str(shifa_results[2]) + str(shifa_results[3]) + str(shifa_results[4]) + str(shifa_results[5])

def bookgua_details():
    guayao = bookgua()
    getgua = multi_key_dict_get(sixtyfourgua, guayao)
    yao_results = sixtyfourgua_description.get(getgua)
    bian_yao = guayao.replace("6","1").replace("9","1").replace("7","0").replace("8","0")
    dong_yao = bian_yao.count("1")
    explain = "動爻有【"+str(dong_yao )+"】根。"
    dong_yao_change = guayao.replace("6","7").replace("9","8")
    dong_yao_bian_gua = multi_key_dict_get(sixtyfourgua, dong_yao_change)
    g_gua_result = sixtyfourgua_description.get(dong_yao_bian_gua)
    g_gua = "【"+getgua+"之"+dong_yao_bian_gua+"】"
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
            explaination2 = "主要看【"+getgua+"】卦卦辭。",  yao_results[0]
        elif dong_yao == 1: 
            explaination2 = g_gua, "主要看【"+top[0]+top[1]+"】",  top
        elif dong_yao == 2:
            explaination2 = g_gua, "主要看【"+top[0]+top[1]+"】，其次看【"+second[0]+second[1]+"】。", top, second
        elif dong_yao == 3:
            if bian_yao.find("1") == 0:
                explaination2 = g_gua, "【"+getgua+"】卦為貞(我方)，【"+dong_yao_bian_gua+"】卦為悔(他方)。主悔【"+dong_yao_bian_gua+"】卦", g_gua_result[0],  yao_results[0]
            elif bian_yao.find("1") > 0:
                explaination2 = g_gua, "【"+getgua+"】卦為貞(我方)，【"+dong_yao_bian_gua+"】卦為悔(他方)。主貞【"+getgua+"】卦", yao_results[0], g_gua_result[0]
        elif dong_yao == 4:
            explaination2 = g_gua, "主要看【"+getgua+"】的"+second_2[0]+second_2[1]+"，其次看【"+getgua+"】的"+top_2[0]+top_2[1]+"。", second_2, top_2
        elif dong_yao == 5:    
            explaination2 = g_gua, "主要看【"+getgua+"】的"+top_2[0]+top_2[1]+"。",  top_2
        elif dong_yao == 6:
            explaination2 = g_gua, "主要看【"+dong_yao_bian_gua+"】卦的彖辭。", g_gua_result[6]
    except (TypeError, UnboundLocalError):
        pass
    return  guayao, getgua, yao_results, explain, explaination2
