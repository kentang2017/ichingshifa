# -*- coding: utf-8 -*-#
import pickle, random, datetime, os,itertools,re
from ephem import Date
import numpy as np
from sxtwl import fromSolar
import cn2an
from cn2an import an2cn
from ichingshifa.jieqi import *


wuxing = "火水金火木金水土土木,水火火金金木土水木土,火火金金木木土土水水,火木水金木水土火金土,木火金水水木火土土金"
wuxing_relation_2 = dict(zip(list(map(lambda x: tuple(re.findall("..",x)), wuxing.split(","))), "尅我,我尅,比和,生我,我生".split(",")))
yingyang =  {tuple(list("甲丙戊庚壬")):"陽",tuple(list("乙丁己辛癸")):"陰" }
zhiying = dict(zip("寅巳申丑戌未子卯辰亥酉午","巳申寅戌未丑卯子辰亥酉午"))
ying_chong = dict(zip(list(map(lambda x: tuple(x), "寅巳申丑戌未子卯,午辰酉亥".split(","))),"刑,自刑".split(","))) 
yingke = {('寅巳', '巳申', '申寅', '丑戌', '戌未', '未丑', '子卯', '卯子', '辰辰', '亥亥', '酉酉', '午午'):"刑"}

class Iching():
    #64卦、4096種卦爻組合資料庫，爻由底(左)至上(右)起
    def __init__(self):
        base = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(base, 'data.pkl')
        self.data = pickle.load(open(path, "rb"))
        self.sixtyfourgua = self.data.get("數字排六十四卦")
        self.sixtyfourgua_description = self.data.get("易經卦爻詳解")
        self.eightgua = self.data.get("八卦數值")
        self.eightgua_element = self.data.get("八卦卦象")
        self.bagua_pure_code = self.data.get("八宮卦純卦")
        self.tiangan = self.data.get("干")
        self.dizhi = self.data.get("支")
        self.wuxin = self.data.get("五行")
        self.down = self.data.get("下卦數")
        self.up = self.data.get("上卦數")
        self.gua = self.data.get("八卦")
        self.shen = self.data.get("世身")
        self.sixtyfour_gua_index = self.data.get("六十四卦")
        self.shiying2 = self.data.get("世應排法")
        self.findshiying = dict(zip(list(self.data.get("八宮卦").values()), self.shiying2))
        self.liuqin = self.data.get("六親")
        self.liuqin_w = self.data.get("六親五行")
        self.mons = self.data.get("六獸")
        self.chin_list = self.data.get("二十八宿")
        self.gua_down_code = dict(zip(self.gua,self.down))
        self.gua_up_code = dict(zip(self.gua,self.up))
        self.ymc = [11,12,1,2,3,4,5,6,7,8,9,10]
        self.rmc = list(range(1,32))
        #旬
    def shun(self, gz):
        shun_value = dict(zip(self.Zhi, list(range(1,13)))).get(gz[1]) - dict(zip(self.Gan, list(range(1,11)))).get(gz[0])
        if shun_value < 0:
            shun_value = shun_value+12
        return {0:"戊", 10:"己", 8:"庚", 6:"辛", 4:"壬", 2:"癸"}.get(shun_value)
    
    def find_shier_luck(self, gan):
        return {**dict(zip(self.tiangan[0::2], list(map(lambda y: dict(zip(y, re.findall('..',"長生沐浴冠帶臨官帝旺衰　病　死　墓　絕　胎　養　") )),list(map(lambda i:self.new_list(self.dizhi, i),list("亥寅寅巳申"))))))), **dict(zip(self.tiangan[1::2], [dict(zip(y,  re.findall('..',"死　病　衰　帝旺臨官冠帶沐浴長生養　胎　絕　墓　"))) for y in list(map(lambda i:self.new_list(self.dizhi, i), list("亥寅寅巳申")))]))}.get(gan)

    #日空時空    
    def daykong_shikong(self, year, month, day, hour, minute):
        guxu = {'甲子':{'孤':'戌亥', '虛':'辰巳'}, '甲戌':{'孤':'申酉', '虛':'寅卯'},'甲申':{'孤':'午未', '虛':'子丑'},'甲午':{'孤':'辰巳', '虛':'戌亥'},'甲辰':{'孤':'寅卯', '虛':'申酉'},'甲寅':{'孤':'子丑', '虛':'午未'} }
        return {"日空":self.multi_key_dict_get(guxu, self.multi_key_dict_get(self.liujiashun_dict(), self.gangzhi(year, month, day, hour, minute)[2])).get("孤"), "時空":self.multi_key_dict_get(guxu, self.multi_key_dict_get(self.liujiashun_dict(), self.gangzhi(year, month, day, hour, minute)[3])).get("孤")}
    
    def liujiashun_dict(self):
        return dict(zip(list(map(lambda x: tuple(x), list(map(lambda x:self.new_list(self.jiazi(), x)[0:10] ,self.jiazi()[0::10])))), self.jiazi()[0::10]))
    
    def new_list(self, olist, o):
        zhihead_code = olist.index(o)
        res1 = []
        for i in range(len(olist)):
            res1.append( olist[zhihead_code % len(olist)])
            zhihead_code = zhihead_code + 1
        return res1

    def chin_iter(self, olist, chin):
        new_chin_list = self.new_list(olist, chin)
        return itertools.cycle(new_chin_list)
    
    def upper_lowergua_code(self, gua1, gua2):
        gua_dict = dict(zip(list("乾兌離震巽坎艮坤"),[126,132,138,144,150,156,162,168]))
        return gua_dict.get(gua1) + gua_dict.get(gua2)
    
    def four_gz_code(self, ygz, mgz,dgz, hgz):
        jiazi_code = dict(zip(self.jiazi(),[112,190,34,56,75,91,107,217,249,190,248,303,35,61,107,116,94,136,112,293,228,177,135,122,62,49,129,120,202,91,119,177,131,86,225,169,83,105,158,249,109,98,57,187,222,95,266,135,105,183,137,228,98,83,70,171,99,101,249,296]))
        return jiazi_code.get(ygz) + jiazi_code.get(mgz) + jiazi_code.get(dgz) + jiazi_code.get(hgz) 
    
    def count_yy(self, ygz, mgz, dgz,hgz):
        fourgz = [ygz[1],mgz[1],dgz[1],hgz[1]]
        zhi_count = {tuple(list("子,寅,辰,未,酉,亥")):"老", tuple(list("午,申,戌,丑,卯,巳")):"少"}
        countfour = [self.multi_key_dict_get(zhi_count, i) for i in fourgz]
        if countfour.count("老") > countfour.count("少"):
            result = 720
        if countfour.count("少") > countfour.count("老"):
            result = 360
        if countfour.count("少") == countfour.count("老"):
            result = 720
        return result

    def guaike(self, year, month, day, hour, minute,  gua1, gua2):
        gz = self.gangzhi(year, month, day, hour, minute)
        ygz = gz[0]
        mgz = gz[1]
        dgz = gz[2]
        hgz = gz[3]
        gua_code = dict(zip(list(range(0,11)),list("艮艮兌坎離震巽巽坤乾")))
        two_gua = self.upper_lowergua_code(gua1, gua2)
        fgz = self.four_gz_code( ygz, mgz,dgz, hgz)
        laoshao = self.count_yy( ygz, mgz, dgz,hgz)
        minus_year = self.multi_key_dict_get({tuple(list("甲乙戊己")):11, tuple(list("丙丁")):3, tuple(list("庚辛")): 4 , tuple(list("壬癸")): 9}, ygz[0])
        result = two_gua + fgz + laoshao - minus_year
        return [result, "".join([gua_code.get(int(i)) for i in list(str(result))])]

    def jiazi(self):
        tiangan = self.tiangan
        dizhi = self.dizhi
        jiazi = [tiangan[x % len(tiangan)] + dizhi[x % len(dizhi)] for x in range(60)]
        return jiazi
    
    def multi_key_dict_get(self, d, k):
        for keys, v in d.items():
            if k in keys:
                return v
        return None
    
    def Ganzhiwuxing(self, gangorzhi):
        ganzhiwuxing = dict(zip(list(map(lambda x: tuple(x),"甲寅乙卯震巽,丙巳丁午離,壬亥癸子坎,庚申辛酉乾兌,未丑戊己未辰戌艮坤".split(","))), list("木火水金土")))
        return self.multi_key_dict_get(ganzhiwuxing, gangorzhi)

    def find_wx_relation(self, zhi1, zhi2):
        return self.multi_key_dict_get(wuxing_relation_2, self.Ganzhiwuxing(zhi1) + self.Ganzhiwuxing(zhi2))
    
    def find_six_mons(self, daygangzhi):
        mons = [i[1] for i in self.data.get("六獸")]
        return self.new_list(mons, self.multi_key_dict_get(dict(zip([tuple(i) for i in '甲乙,丙丁,戊,己,庚辛,壬癸'.split(",")], mons)), daygangzhi[0]))

    def rev(self, l):
        r = []
        for i in l:
            r.insert(0, i)
        return r
    
    def show_sixtyfourguadescription(self, gua):
        sixtyfourguadescription = self.sixtyfourgua_description
        return sixtyfourguadescription.get(gua)
    
    #五虎遁，起正月
    def find_lunar_month(self, year):
        fivetigers = {
        tuple(list('甲己')):'丙寅',
        tuple(list('乙庚')):'戊寅',
        tuple(list('丙辛')):'庚寅',
        tuple(list('丁壬')):'壬寅',
        tuple(list('戊癸')):'甲寅'
        }
        if self.multi_key_dict_get(fivetigers, year[0]) == None:
            result = self.multi_key_dict_get(fivetigers, year[1])
        else:
            result = self.multi_key_dict_get(fivetigers, year[0])
        return dict(zip(range(1,13), self.new_list(self.jiazi(), result)[:12]))
    
    #五鼠遁，起子時
    def find_lunar_hour(self, day):
        fiverats = {
        tuple(list('甲己')):'甲子',
        tuple(list('乙庚')):'丙子',
        tuple(list('丙辛')):'戊子',
        tuple(list('丁壬')):'庚子',
        tuple(list('戊癸')):'壬子'
        }
        if self.multi_key_dict_get(fiverats, day[0]) == None:
            result = self.multi_key_dict_get(fiverats, day[1])
        else:
            result = self.multi_key_dict_get(fiverats, day[0])
        return dict(zip(list(self.dizhi), self.new_list(self.jiazi(), result)[:12]))
    #農曆
    def lunar_date_d(self, year, month, day):
        day = fromSolar(year, month, day)
        return {"年":day.getLunarYear(),  "月": day.getLunarMonth(), "日":day.getLunarDay()}
    #干支
    def gangzhi(self, year, month, day, hour, minute):
        if year == 0:
            return ["無效"]
        if year < 0:
            year = year + 1 
        if hour == 23:
            d = Date(round((Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day+1).zfill(2), str(0).zfill(2)))), 3))
        else:
            d = Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
        dd = list(d.tuple())
        cdate = fromSolar(dd[0], dd[1], dd[2])
        yTG,mTG,dTG,hTG = "{}{}".format(self.tiangan[cdate.getYearGZ().tg], self.dizhi[cdate.getYearGZ().dz]), "{}{}".format(self.tiangan[cdate.getMonthGZ().tg],self.dizhi[cdate.getMonthGZ().dz]), "{}{}".format(self.tiangan[cdate.getDayGZ().tg], self.dizhi[cdate.getDayGZ().dz]), "{}{}".format(self.tiangan[cdate.getHourGZ(dd[3]).tg], self.dizhi[cdate.getHourGZ(dd[3]).dz])
        if year < 1900:
            mTG1 = self.find_lunar_month(yTG).get(self.lunar_date_d(year, month, day).get("月"))
        else:
            mTG1 = mTG
        hTG1 = self.find_lunar_hour(dTG).get(hTG[1])
        gangzhi_minute = self.minutes_jiazi_d().get(str(hour)+":"+str(minute))
        return [yTG, mTG1, dTG, hTG1, gangzhi_minute]
   
    #分干支
    def minutes_jiazi_d(self):
        t = [f"{h}:{m}" for h in range(24) for m in range(60)]
        c = list(itertools.chain.from_iterable([[i]*24 for i in self.jiazi()]))
        #minutelist = dict(zip(t, cycle(repeat_list(2, jiazi()))))
        return dict(zip(t, c))

    def mget_bookgua_details(self, guayao):
        getgua = self.multi_key_dict_get(self.sixtyfourgua, guayao)
        yao_results = self.sixtyfourgua_description.get(getgua)
        bian_yao = guayao.replace("6","1").replace("9","1").replace("7","0").replace("8","0")
        dong_yao = bian_yao.count("1")
        explaination = "動爻有【"+str(dong_yao )+"】根。"
        dong_yao_change = guayao.replace("6","7").replace("9","8")
        g_gua = self.multi_key_dict_get(self.sixtyfourgua, dong_yao_change)
        g_gua_result = self.sixtyfourgua_description.get(g_gua)
        b_gua_n_g_gua = "【"+getgua+"之"+g_gua+"】"
        top_bian_yao = bian_yao.rfind("1")+int(1)
        second_bian_yao = bian_yao.rfind("1",0, bian_yao.rfind("1"))+int(1)
        top_jing_yao = bian_yao.rfind("0") + int(1)
        second_jing_yao = bian_yao.rfind("0", 0, bian_yao.rfind("0"))+int(1)
        top = yao_results.get(top_bian_yao)
        second = yao_results.get(second_bian_yao)
        #top_2 = yao_results.get(top_jing_yao)
        #second_2 = yao_results.get(second_jing_yao)
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
    
    def bookgua(self): #由底至上起爻
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

    def datetime_bookgua(self, y,m,d,h,minute):
        gangzhi = self.gangzhi(y,m,d,h,minute)
        ld = self.lunar_date_d(y,m,d)
        zhi_code = dict(zip(self.dizhi, range(1,13)))
        yz_code = zhi_code.get(gangzhi[0][1])
        hz_code = zhi_code.get(gangzhi[3][1])
        cm = ld.get("月")
        cd =  ld.get("日")
        eightgua = {1:"777", 2:"778", 3:"787", 4:"788", 5:"877", 6:"878", 7:"887", 8:"888"}
        upper_gua_remain = (yz_code +cm+cd+hz_code) % 8
        if upper_gua_remain == 0:
            upper_gua_remain = int(8)
        upper_gua = eightgua.get(upper_gua_remain)
        lower_gua_remain = (yz_code+cm+cd) % 8
        if lower_gua_remain == 0:
            lower_gua_remain = int(8)
        lower_gua = eightgua.get(lower_gua_remain)
        combine_gua1 =lower_gua+upper_gua
        combine_gua = list(combine_gua1)
        bian_yao = (yz_code+cm+cd+hz_code) % 6
        if bian_yao == 0:
            bian_yao = int(6)
        elif bian_yao != 0:
            combine_gua[bian_yao -1] = combine_gua[bian_yao-1].replace("7","9").replace("8","6")
        bian_gua = "".join(combine_gua)
        ben_gua = self.multi_key_dict_get(self.sixtyfourgua, bian_gua)
        description = self.multi_key_dict_get(self.sixtyfourgua_description,  ben_gua)
        g_gua = self.multi_key_dict_get(self.sixtyfourgua, (bian_gua.replace("6", "7").replace("9", "8")))
        return ben_gua+"之"+g_gua, self.eightgua_element.get(upper_gua_remain)+self.eightgua_element.get(lower_gua_remain)+ben_gua , "變爻為"+description[bian_yao][:2], description[bian_yao][3:]
        
    def bookgua_details(self):
        return self.mget_bookgua_details(self.bookgua())

    #現在時間起卦
    def current_bookgua(self):
        now = datetime.datetime.now()
        return self.datetime_bookgua(int(now.year), int(now.month), int(now.day), int(now.hour), int(now.minute))
    
    def dc_gua(self, gua):
        fivestars = self.data.get("五星")
        eightgua = self.data.get("數字排八卦")
        sixtyfourgua =  self.data.get("數字排六十四卦")
        su_yao = self.data.get("二十八宿配干支")
        shiying = self.multi_key_dict_get(self.data.get("八宮卦"), self.multi_key_dict_get(sixtyfourgua, gua))
        Shiying = list(self.findshiying.get(shiying))
        dgua = self.multi_key_dict_get(eightgua, gua[0:3])
        down_gua = self.gua_down_code.get(dgua)
        ugua = self.multi_key_dict_get(eightgua,gua[3:6])
        up_gua = self.gua_up_code.get(ugua)
        dt = [self.tiangan[int(g[0])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        dd = [self.dizhi[int(g[1])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        dw = [self.wuxin[int(g[2])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        ut = [self.tiangan[int(g[0])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        ud = [self.dizhi[int(g[1])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        uw = [self.wuxin[int(g[2])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        t = dt+ut
        d = dd+ud
        w = dw+uw
        find_gua_wuxing = self.multi_key_dict_get(self.data.get("八宮卦五行"), self.multi_key_dict_get(sixtyfourgua, gua))
        #liuqin = [i[0] for i in self.liuqin]
        lq = [self.multi_key_dict_get(self.liuqin_w,i+find_gua_wuxing) for i in dw+uw]
        gua_name = self.multi_key_dict_get(sixtyfourgua, gua)
        find_su = dict(zip(self.sixtyfour_gua_index, self.chin_iter(self.chin_list, "參"))).get(gua_name)
        sy = dict(zip(self.sixtyfour_gua_index, su_yao)).get(gua_name)
        ng = [t[i]+d[i] for i in range(0,6)]
        sy2 =  [c== sy for c in ng]
        sy3 = [str(i).replace("False", "").replace("True", find_su) for i in sy2]
        ss = dict(zip(self.sixtyfour_gua_index, self.chin_iter(fivestars, "鎮星"))).get(gua_name)
        position = sy3.index(find_su)
        if position == 0:
            g = self.new_list(self.chin_list, find_su)[0:6]
        elif position == 5:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:]
        elif position == 4:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][1:] + [list(reversed(self.new_list(self.chin_list, find_su)))[0]] 
        elif position == 3:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][2:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:2] 
        elif position == 2:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][3:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:3] 
        elif position == 1:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][4:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:4] 
        build_month_code = dict(zip(self.data.get("六十四卦"),self.data.get("月建"))).get(gua_name)
        build_month = self.new_list(self.jiazi(), build_month_code)[0:6]
        accumulate_code = dict(zip(self.data.get("六十四卦"),self.data.get("積算"))).get(gua_name)
        accumulate = self.new_list(self.jiazi(), accumulate_code)
        return {"卦":gua_name, 
                "五星":ss, 
                "世應卦":shiying+"卦",  
                "星宿":g, 
                "天干":t, 
                "地支":d, 
                "五行":w, 
                "世應":Shiying, 
                "六親用神":lq, 
                "納甲":ng, 
                "建月":build_month, 
                "積算":[list(i) for i in np.array_split(accumulate, 10)]}
    
    def decode_gua(self, gua, daygangzhi = None):
        if daygangzhi is None:
            now = datetime.datetime.now()
            daygangzhi = self.gangzhi(int(now.year), int(now.month), int(now.day), int(now.hour))[2]
        fivestars = self.data.get("五星")
        eightgua = self.data.get("數字排八卦")
        sixtyfourgua =  self.data.get("數字排六十四卦")
        su_yao = self.data.get("二十八宿配干支")
        shiying = self.multi_key_dict_get(self.data.get("八宮卦"), self.multi_key_dict_get(sixtyfourgua, gua))
        Shiying = list(self.findshiying.get(shiying))
        dgua = self.multi_key_dict_get(eightgua, gua[0:3])
        down_gua = self.gua_down_code.get(dgua)
        ugua = self.multi_key_dict_get(eightgua,gua[3:6])
        up_gua = self.gua_up_code.get(ugua)
        dt = [self.tiangan[int(g[0])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        dd = [self.dizhi[int(g[1])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        dw = [self.wuxin[int(g[2])] for g in [down_gua[i].split(',') for i in range(0,3)]]
        ut = [self.tiangan[int(g[0])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        ud = [self.dizhi[int(g[1])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        uw = [self.wuxin[int(g[2])] for g in [up_gua[i].split(',') for i in range(0,3)]]
        t = dt+ut
        d = dd+ud
        w = dw+uw
        find_gua_wuxing = self.multi_key_dict_get(self.data.get("八宮卦五行"), self.multi_key_dict_get(sixtyfourgua, gua))
        liuqin = [i[0] for i in self.liuqin]
        lq = [self.multi_key_dict_get(self.liuqin_w,i+find_gua_wuxing) for i in dw+uw]
        gua_name = self.multi_key_dict_get(sixtyfourgua, gua)
        find_su = dict(zip(self.sixtyfour_gua_index, self.chin_iter(self.chin_list, "參"))).get(gua_name)
        sy = dict(zip(self.sixtyfour_gua_index, su_yao)).get(gua_name)
        ng = [t[i]+d[i] for i in range(0,6)]
        sy2 =  [c== sy for c in ng]
        sy3 = [str(i).replace("False", "").replace("True", find_su) for i in sy2]
        ss = dict(zip(self.sixtyfour_gua_index, self.chin_iter(fivestars, "鎮星"))).get(gua_name)
        position = sy3.index(find_su)
        if position == 0:
            g = self.new_list(self.chin_list, find_su)[0:6]
        elif position == 5:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:]
        elif position == 4:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][1:] + [list(reversed(self.new_list(self.chin_list, find_su)))[0]] 
        elif position == 3:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][2:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:2] 
        elif position == 2:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][3:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:3] 
        elif position == 1:
            g = list(reversed(self.new_list(self.chin_list, find_su)))[-6:][4:] + list(reversed(self.new_list(self.chin_list, find_su)))[0:4] 
        build_month_code = dict(zip(self.data.get("六十四卦"),self.data.get("月建"))).get(gua_name)
        build_month = self.new_list(self.jiazi(), build_month_code)[0:6]
        accumulate_code = dict(zip(self.data.get("六十四卦"),self.data.get("積算"))).get(gua_name)
        accumulate = self.new_list(self.jiazi(), accumulate_code)
        aa = list(set(lq))
        fu =  str(str([value for value in liuqin if value not in aa]).replace("['","").replace("']",""))
        fu_gua = self.dc_gua(self.multi_key_dict_get(self.bagua_pure_code, gua_name))
        fu_gua_gang = fu_gua.get("天干")
        fu_gua_zhi = fu_gua.get("地支")
        fu_gua_wu = fu_gua.get("五行")
        fu_gua_lq = fu_gua.get("六親用神")
        shen = self.multi_key_dict_get(self.shen, d[Shiying.index("世")])
        try:
            fu_num = fu_gua_lq.index(fu)
            fuyao = [str(g ==fu) for g in fu_gua_lq].index('True')
            fuyao1 = fu_gua_lq[fu_num] + fu_gua_gang[fu_num] +  fu_gua_zhi[fu_num] + fu_gua_wu[fu_num]
            fu_yao = {"伏神所在爻": lq[fuyao], "伏神六親":fu, "伏神排爻數字":fu_num, "本卦伏神所在爻":lq[fu_num]+t[fu_num]+d[fu_num]+w[fu_num], "伏神爻":fuyao1}

        except (ValueError, IndexError ,AttributeError):
            fu_yao = ""
        
        return {"卦":gua_name, 
                "五星":ss, 
                "世應卦":shiying+"卦",  
                "星宿":g, 
                "天干":t, 
                "地支":d, 
                "五行":w, 
                "世應爻":Shiying, 
                "身爻":lq[shen]+t[shen]+d[shen]+w[shen],
                "六親用神":lq, 
                "伏神":fu_yao,
                "六獸":self.find_six_mons(daygangzhi),
                "納甲":ng, 
                "建月":build_month, 
                "積算":[list(i) for i in np.array_split(accumulate, 10)]}

    def decode_two_gua(self, bengua, ggua, daygangzhi = None):
        if daygangzhi is None:
            now = datetime.datetime.now()
            daygangzhi = self.gangzhi(int(now.year), int(now.month), int(now.day), int(now.hour))[2]
        a = self.decode_gua(bengua, daygangzhi)
        b = self.decode_gua(ggua, daygangzhi)
        try:
            fu_yao = a.get("伏神").get("伏神爻")
            fu_ben_yao = a.get("伏神").get('本卦伏神所在爻')
            g_yao = b.get("六親用神") + b.get("天干") + b.get("地支") + b.get("五行")
            if fu_yao == g_yao:
                fei = fu_ben_yao
            else:
                fei = ""
        except (ValueError, IndexError ,AttributeError):
            fei = ""
        return {"本卦":a, "之卦":b, "飛神":fei}

    def qigua_time(self, y, m, d, h, minute):
        gangzhi = self.gangzhi(y,m,d,h, minute)
        ld = self.lunar_date_d(y,m,d)
        zhi_code = dict(zip(self.dizhi, range(1,13)))
        yz_code = zhi_code.get(gangzhi[0][1])
        hz_code = zhi_code.get(gangzhi[3][1])
        cm = ld.get("月")
        cd =  ld.get("日")
        eightgua = self.data.get("八卦數值")
        lower_gua_remain = (yz_code +cm+cd+hz_code) % 8
        upper_gua_remain = (yz_code+cm+cd) % 8
        if upper_gua_remain == 0:
            upper_gua_remain = int(8)
        upper_gua = eightgua.get(upper_gua_remain)
        if lower_gua_remain == 0:
            lower_gua_remain = int(8)
        lower_gua = eightgua.get(lower_gua_remain)
        combine_gua1 =lower_gua+upper_gua
        combine_gua = list(combine_gua1)
        bian_yao = (yz_code+cm+cd+hz_code) % 6
        if bian_yao == 0:
            bian_yao = int(6)
        elif bian_yao != 0:
            combine_gua[bian_yao -1] = combine_gua[bian_yao-1].replace("7","9").replace("8","6")
        bian_gua = "".join(combine_gua)
        ggua = bian_gua.replace("6","7").replace("9","8")
        return {**{'日期':gangzhi[0]+"年"+gangzhi[1]+"月"+gangzhi[2]+"日"+gangzhi[3]+"時"}, **{"大衍筮法":self.mget_bookgua_details(bian_gua)}, **self.decode_two_gua(bian_gua, ggua, gangzhi[2])}

    def qigua_now(self):
        now = datetime.datetime.now()
        return self.qigua_time(int(now.year), int(now.month), int(now.day), int(now.hour), int(now.minute))

    def qigua_manual(self, y, m, d, h, minute, gua):
        gangzhi = self.gangzhi(y,m,d,h, minute)
        ggua = gua.replace("6","7").replace("9","8")
        return {**{'日期':gangzhi[0]+"年"+gangzhi[1]+"月"+gangzhi[2]+"日"+gangzhi[3]+"時"}, **{"大衍筮法":self.mget_bookgua_details(gua)}, **self.decode_two_gua(gua, ggua, gangzhi[2])}

#先天策軌數
    def innate_cegui(self, year, month, day, hour, minute):
        innate_gua = list("乾兌離震巽坎艮坤")
        innate_kinkun_num = {tuple([7,9]):216,tuple([6,8]):180}
        dongyao_position = {tuple([0,1,2]):"下卦",tuple([3,4,5]):"上卦"}
        gua = self.qigua_time(year, month, day, hour, minute).get("大衍筮法")[0]
        gua1 = list(str(gua.replace("9","7").replace("6","8")))
        gua_sum = sum([{"7":36, "8":24}.get(i) for i in gua1])
        gua2 = list(gua)
        lower = "".join(gua1[0:3])
        upper = "".join(gua1[3:6])
        lower_g = bidict(self.eightgua).inverse[lower]
        upper_g = bidict(self.eightgua).inverse[upper]
        try:
            dy = gua2.index("6")
        except ValueError:
            dy = gua2.index("9")
        dongyao = {0:1,1:2,2:3,3:4,4:5,5:6}.get(dy)    
        dy_p = multi_key_dict_get(dongyao_position, dy)
        if dy_p == "下卦":
            innate_num = (lower_g * 10 * gua_sum) + (dongyao * gua_sum) + gua_sum + (upper_g + lower_g + dongyao)
        if dy_p == "上卦":
            innate_num = (dongyao * 10 * gua_sum) + (upper_g * gua_sum) + gua_sum + (upper_g + lower_g + dongyao)
        num_to_wuxing =dict(zip(list(range(0,10)),list("空水火木金土水火木金土")))
        return  [list("元會運世")[i]+ [num_to_wuxing.get(int(i)) for i in list(str(innate_num))][i] for i in range(0,4)]

	
    def display_pan_m(self, year, month, day, hour, minute, mgua):
        gz = self.gangzhi(year, month, day, hour, minute)
        oo = self.qigua_manual(year, month, day, hour, minute, mgua).get('大衍筮法')
        ogua = self.qigua_manual(year, month, day, hour, minute, mgua).get('大衍筮法')[0]
        bengua = self.qigua_manual(year, month, day, hour, minute, mgua).get("本卦")
        ggua = self.qigua_manual(year, month, day, hour, minute, mgua).get("之卦")
        gb = ogua.replace("9","8").replace("6","7")
        wugua = ogua.replace("9","7").replace("6","8")[1:4]+gb[2:5]
        b1 = self.qigua_manual(year, month, day, hour, minute, mgua).get("本卦").get("星宿")
        b2 = self.qigua_manual(year, month, day, hour, minute, mgua).get("本卦").get('六親用神')
        b3 = self.qigua_manual(year, month, day, hour, minute, mgua).get("本卦").get('納甲')
        b4 = self.qigua_manual(year, month, day, hour, minute, mgua).get("本卦").get('五行')
        b5 = self.qigua_manual(year, month, day, hour, minute, mgua).get("本卦").get('世應爻')
        g1 = self.qigua_manual(year, month, day, hour, minute, mgua).get("之卦").get("星宿")
        g2 = self.qigua_manual(year, month, day, hour, minute, mgua).get("之卦").get('六親用神')
        g3 = self.qigua_manual(year, month, day, hour, minute, mgua).get("之卦").get('納甲')
        g4 = self.qigua_manual(year, month, day, hour, minute, mgua).get("之卦").get('五行')
        g5 = self.qigua_manual(year, month, day, hour, minute, mgua).get("之卦").get('世應爻')
        try:
            gua_no_yao = {  "父":"卦無【父母】，乃幟不備也。",
                            "妻":"卦無【妻財】，糧草缺絕也。",
                            "官":"卦無【官鬼】，如與鬼墓絕胎者，敵必遁去也。",
                            "子":"卦無【子孫】，動來救。",
                            "兄":"卦無【兄弟】，防奸細也。"}.get(list(set(list("官父妻兄子"))- set(b2))[0])
        except IndexError:
            gua_no_yao = ""
        guayaodict = {"6":"▅▅ ▅▅ X", "7":"▅▅▅▅▅  ", "8":"▅▅ ▅▅  ", "9":"▅▅▅▅▅ O"}
        #guayaodict = {"6":"▅▅　▅▅ X", "7":"▅▅▅▅▅  ", "8":"▅▅　▅▅  ", "9":"▅▅▅▅▅ O"}
        bg = [guayaodict.get(i) for i in list(ogua)]
        gb1 = [guayaodict.get(i) for i in list(gb)]
        wgb = [guayaodict.get(i) for i in list(wugua)]
        bg_yaolist = ["".join([b2[i],b3[i],b4[i],b5[i]]) for i in range(0,6)]
        #gg_yaolist = ["".join([b2[i],b3[i],b4[i],b5[i]]) for i in range(0,6)]
        smons = self.find_six_mons(gz[2][0])
        lunar_month = self.lunar_date_d(year, month, day).get("月")
        build_month = self.find_lunar_month(gz[0]).get(lunar_month)
        dong_yaos = [i.replace("7", "").replace("8", "").replace("6", "動").replace("9", "動") for i in list(ogua)]
        qin_elements = dict(zip(b2, [b2[i]+b4[i]+dong_yaos[i] for i in range(0,6)]))
        by = {
            0:["身","　","　","　","　","　"],
            1:["　","身","　","　","　","　"],
            2:["　","　","身","　","　","　"],
            3:["　","　","　","身","　","　"],
            4:["　","　","　","　","身","　"],
            5:["　","　","　","　","　","身"],
            }.get([b2[i]+b3[i] for i in range(0,6)].index(bengua.get('身爻')[0:3]))
        try:
            fugod1 = bengua.get("伏神").get("伏神排爻數字")
            fugod2 = ggua.get("伏神").get("伏神排爻數字")
            fyao1 = bengua.get("伏神").get("伏神爻")
            fyao2 = ggua.get("伏神").get("伏神爻")
            fu_location = {0:[fyao1,"　　　　","　　　　","　　　　","　　　　","　　　　"] ,1:["　　　　",fyao1,"　　　　","　　　　","　　　　","　　　　"], 2:["　　　　","　　　　",fyao1,"　　　　","　　　　","　　　　"], 3:["　　　　","　　　　","　　　　",fyao1,"　　　　","　　　　"], 4:["　　　　","　　　　","　　　　","　　　　",fyao1,"　　　　"], 5:["　　　　","　　　　","　　　　","　　　　","　　　　",fyao1]}
            fu_location1 = {0:[fyao2,"　　　　","　　　　","　　　　","　　　　","　　　　"] ,1:["　　　　",fyao2,"　　　　","　　　　","　　　　","　　　　"], 2:["　　　　","　　　　",fyao2,"　　　　","　　　　","　　　　"], 3:["　　　　","　　　　","　　　　",fyao2,"　　　　","　　　　"], 4:["　　　　","　　　　","　　　　","　　　　",fyao2,"　　　　"], 5:["　　　　","　　　　","　　　　","　　　　","　　　　",fyao2]}
            fufu = fu_location.get(fugod1)
            fufu2 = fu_location1.get(fugod2)
            flylocation = bengua.get("伏神").get('本卦伏神所在爻')
            flygodyao = bengua.get("伏神").get('本卦伏神所在爻')[2:]
            fugodyao = fyao1[2:]
            if flylocation[0] == "父":
                father_lay_dist = {"子":"父下伏子，眾將懾服，擒縱如意也。",
                                   "妻":"父下伏財，備器足餉，智無遺算，但左右防伏戎也。",
                                   "兄":"父下伏兄，貪財好色，狎侮私人也。",
                                   "官":"父下伏鬼，智短計拙，動見疏虞也。"}.get(fyao1[0])
            else:
                father_lay_dist = ""
            flyfu_relation = self.find_wx_relation(flygodyao[0],fugodyao[0])
            if flyfu_relation == "我尅":
                ff_relation = "我尅】，飛來克伏為害，為凶。"
            if flyfu_relation == "尅我":
                ff_relation = "尅我】，伏克飛神為出暴，出暴者，凶而快。"
            if flyfu_relation == "比和":
                ff_relation = "比和】。"
            if flyfu_relation == "生我":
                ff_relation = flyfu_relation + "】。"
            if flyfu_relation == "我生":
                ff_relation = flyfu_relation + "】。"
            flyfu_dist = "伏神爻【"+fyao1+"】，飛神【"+flygodyao+"】在【"+flylocation+"】，伏神【"+fugodyao+"】，飛伏關係為【"+ff_relation
        except AttributeError:
            fufu = ["　　　　","　　　　","　　　　","　　　　","　　　　","　　　　"]
            fufu2 = ["　　　　","　　　　","　　　　","　　　　","　　　　","　　　　"]
            flyfu_dist = ""
        daykong = self.daykong_shikong(year, month, day, hour, minute).get("日空")
        hourkong = self.daykong_shikong(year, month, day, hour, minute).get("時空")
        gettwelve = self.find_shier_luck(gz[2][0])
        twelvelucks =  "".join([self.find_shier_luck(gz[2][0]).get(i)+"　" for i in self.dizhi])
        twelvelucks_hour = self.find_shier_luck(gz[3][0])
        twelvelucks_hour1 = "".join([self.find_shier_luck(gz[3][0]).get(i)+"　" for i in self.dizhi])
        try:
            father_luck = self.multi_key_dict_get({("衰　","病　","死　","墓　","絕　"):"父母爻處衰絕，主隊軍師老髦也，守舊保守也。",
                 ("長生","沐浴","冠帶","臨官","帝旺"):"父母爻處旺相，主隊軍師少壯也，開明進取也。",
                 ("胎　","養　"):"父母爻處胎、養，主隊軍師不威重也，欠謀略。"},  twelvelucks_hour.get(b3[b2.index("父")][1]))
        except (ValueError,IndexError):
            father_luck = ""
        a = "起卦時間︰{}年{}月{}日{}時{}分\n".format(year, month, day, hour, minute)
        b = "農曆︰{}{}月{}日\n".format(cn2an.transform(str(year)+"年", "an2cn"), an2cn(self.lunar_date_d(year, month, day).get("月")), an2cn(self.lunar_date_d(year,month, day).get("日")))
        c = "干支︰{}年  {}月  {}日  {}時\n".format(gz[0], gz[1], gz[2], gz[3])
        j_q = jq(year, month, day, hour, minute)
        c0 = "節氣︰{} | 旺︰{} | 相︰{}\n".format(j_q, gong_wangzhuai(j_q)[1].get("旺"), gong_wangzhuai(j_q)[1].get("相"))
        c1 = "旬空︰　　　  　　　  {}    {}\n".format(daykong, hourkong)
        c2 = "月建︰　　　  {}\n\n".format(build_month)
        c3 = "　　　　"+ "".join([i+"　　" for i in self.dizhi]) +"\n"
        c4 = "　　　　"+"".join([self.Ganzhiwuxing(i)+"　　" for i in self.dizhi] )+"\n"
        c5 = "日支運︰"+ twelvelucks+"\n"
        c5_1 = "時支運︰"+ twelvelucks_hour1+"\n\n"
        d = "　　　　　　　       　 　{}卦　　　　　　　　　　 　　　　　              　  {}卦                \n".format(bengua.get("卦"), ggua.get("卦"))
        e = "六神　  伏神　　         本卦　　　　　　　　　　　       互卦               伏神　　   之卦\n"
        f = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}　\n".format(smons[5],fufu[5],b1[5],b2[5],b3[5],b4[5],twelvelucks_hour.get(b3[5][1]),b5[5].replace("六","　"), bg[5],by[5],wgb[5],fufu2[5],g1[5],g2[5],g3[5],g4[5],g5[5].replace("六","　"),gb1[5])
        g = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n".format(smons[4],fufu[4],b1[4],b2[4],b3[4],b4[4],twelvelucks_hour.get(b3[4][1]),b5[4].replace("五","　"), bg[4],by[4],wgb[4],fufu2[4],g1[4],g2[4],g3[4],g4[4],g5[4].replace("五","　"),gb1[4])
        h = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n".format(smons[3],fufu[3],b1[3],b2[3],b3[3],b4[3],twelvelucks_hour.get(b3[3][1]),b5[3].replace("四","　"), bg[3],by[3],wgb[3],fufu2[3],g1[3],g2[3],g3[3],g4[3],g5[3].replace("四","　"),gb1[3])
        i = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n".format(smons[2],fufu[2],b1[2],b2[2],b3[2],b4[2],twelvelucks_hour.get(b3[2][1]),b5[2].replace("三","　"), bg[2],by[2],wgb[2],fufu2[2],g1[2],g2[2],g3[2],g4[2],g5[2].replace("三","　"),gb1[2])
        j = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n".format(smons[1],fufu[1],b1[1],b2[1],b3[1],b4[1],twelvelucks_hour.get(b3[1][1]),b5[1].replace("二","　"), bg[1],by[1],wgb[1],fufu2[1],g1[1],g2[1],g3[1],g4[1],g5[1].replace("二","　"),gb1[1])
        k = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n\n\n".format(smons[0],fufu[0],b1[0],b2[0],b3[0],b4[0],twelvelucks_hour.get(b3[0][1]),b5[0].replace("初","　"), bg[0],by[0],wgb[0],fufu2[0],g1[0],g2[0],g3[0],g4[0],g5[0].replace("初","　"),gb1[0])
        l = "【大衍筮法】\n"
        try:
            m = "求得【{}之{}】，{}{}{}\n\n".format(oo[1], oo[2], oo[4][0], oo[4][2], oo[4][3])
        except IndexError:
            m = "求得【{}之{}】，{}{}\n\n".format(oo[1], oo[2], oo[4][0], oo[4][2])
        n = "【{}卦】\n卦辭︰{}\n彖︰{}\n{}\n{}\n{}\n{}\n{}\n{}\n\n".format(oo[1],oo[3].get(0), oo[3].get(7)[2:], oo[3].get(6), oo[3].get(5), oo[3].get(4), oo[3].get(3), oo[3].get(2), oo[3].get(1)  )
        eightgua = { '777':"乾金",  '778':"兌金",  '787':"離火",  '788':"震木",  '877':"巽木", '878':"坎水",  '887':"艮土",  '888':"坤土"}
        downgua = eightgua.get(ogua[0:3].replace("6","8").replace("9","7"))
        upgua = eightgua.get(ogua[3:6].replace("6","8").replace("9","7"))
        status = {("旺","相"):"，吉也",("胎","沒"):"，平也",("死","囚","休","廢"):"，凶也"} 
        downgua1 =  "【"+gong_wangzhuai(j_q)[0].get(downgua[0])+"】" + self.multi_key_dict_get(status, gong_wangzhuai(j_q)[0].get(downgua[0]) )
        upgua1 = "【"+gong_wangzhuai(j_q)[0].get(upgua[0])+"】" + self.multi_key_dict_get(status, gong_wangzhuai(j_q)[0].get(upgua[0]) )
        shi =  bg_yaolist[["世" in i  for i in bg_yaolist].index(True)]
        ying = bg_yaolist[["應" in i  for i in bg_yaolist].index(True)]
        hour_status = self.find_shier_luck(gz[3][0])
        shi_luck = hour_status.get(shi[2])
        ying_luck = hour_status.get(ying[2])
        if shi_luck == "帝旺" or shi_luck == "臨官" and ying_luck != "帝旺" or ying_luck != "臨官":
            s_vs_y_dist = "世旺應衰者，我強彼弱，宜攻也。"
        if ying_luck == "帝旺" or ying_luck == "臨官" and shi_luck != "帝旺" or shi_luck != "臨官" :
            s_vs_y_dist = "世衰應旺者，我弱彼強，宜守也。"
        if shi_luck == "帝旺" or shi_luck == "臨官" and ying_luck == "帝旺" or ying_luck == "臨官" :
            s_vs_y_dist = "世應皆旺，必不交鋒，戰亦勝負難決也。"
        else:
            s_vs_y_dist = "世應皆不旺，戰亦勝負難決也。"
        shi_yy = {"陽":"世陽而動者，宜出師。", "陰":"世陰而靜者，宜堅壁也。"}.get(self.multi_key_dict_get(yingyang, shi[1]))
        down_vs_up = self.multi_key_dict_get(wuxing_relation_2,  downgua[1]+upgua[1])
        shi_vs_ying = self.find_wx_relation(shi[2], ying[2])
        shi_vs_ying2 =  {"我尅":"世尅應爻，我軍必勝",
                        "尅我":"應尅世爻，我軍必敗",
                        "比和":"世應比和，勢軍力敵",
                        "我生":"世生應爻，我軍不利",
                        "生我":"應生世爻，彼軍不利",
                        }.get(shi_vs_ying)
        sy_monster = {"龍":"臨【青龍】，良將也。",
			   "虎":"臨【白虎】，猛將也。",
			   "陳":"臨【勾陳】，密遣擒賊也。",
			   "雀":"臨【朱雀】，號令嚴明也。",
			   "蛇":"臨【螣蛇】，變幻不測也。",
			   "武":"臨【玄武】，善用囊沙背水之術，或巧於偷營劫寨也。"}
        shi_monster = "世爻" + sy_monster.get(smons[b5.index("世")])
        ying_monster = "應爻" + sy_monster.get(smons[b5.index("應")])
        try:
            dongyao = re.findall(r'\d+', oo[4][1])[0]
        except IndexError:
            dongyao = "0"
        if shi[2] == daykong[0] or shi[2] == daykong[1] or shi[2] == hourkong[1] or shi[2] == hourkong[0]:
            sk_dist = "，世爻主隊遇旬空，不利"
        else:
            sk_dist = ""
        god_dist1 = {"兄":"，忌神持世，不利","父":"，仇神持世，不利","妻":"，用神持世，有利", "子":"，原神持世，費心", "官":"，泄神持世，有利"}  
        god_dist2 = {"兄":"，忌神持應，不利","父":"，仇神持應，不利","妻":"，用神持應，有利", "子":"，原神持應，費心", "官":"，泄神持應，有利"}  
        s_dist2 = god_dist1.get(shi[0])
        y_dist2 = god_dist2.get(ying[0])
        s_dist3 = {"父":"父母持世，大敗之兆",
        		  "妻":"妻財持世，如旺相，如獨發便嬴",
        		  "官":"官鬼持世。皆敗，乃彼我不得地，世旺克應，我勝；應旺克也，彼勝",
        		  "兄":"兄弟持世，主有奸人在軍中，世下伏鬼亦然",
        		  "子":"子孫持世，如旺相，或獨發便贏，若鬼兄財爻動便輸"}.get(shi[0])
        if ying[2] == daykong[0] or ying[2] == daykong[1] or ying[2] == hourkong[1] or ying[2] == hourkong[0]:
            yk_dist = "，應爻客隊遇旬空，不利"
        else:
            yk_dist = ""
        if "官" in shi == True:
            sguan = "，世見官鬼爻，皆敗"
        else:
            sguan = ""
        if "官" in ying == True:
            yguan = "，應見官鬼爻，皆敗"
        else:
            yguan = ""
        
        if dongyao == "0":
            if  flyfu_dist == "":
                o = "【斷主客勝負】\n1.客隊下卦為【{}】，主隊上卦為【{}】，主客關係為【{}】。內卦為我寨，處{}，外卦為彼營，處{}。{} \n2.主隊世爻，{}世爻為【{}】{}{}{}，{}；{}客隊應爻為【{}】{}{}{}，{}主客關係為【{}】，{}。\n3.日干下主隊世爻臨【{}】，客隊應爻臨【{}】，時干下{}{}".format(downgua,upgua, down_vs_up,downgua1,upgua1,father_luck,shi_yy,shi[0:4],sk_dist,sguan,s_dist2,s_dist3,shi_monster,ying[0:4],yk_dist,yguan,y_dist2,ying_monster,shi_vs_ying,shi_vs_ying2, gettwelve.get(shi[2]), gettwelve.get(ying[2]), s_vs_y_dist, gua_no_yao)
            if  flyfu_dist != "":
                o = "【斷主客勝負】\n1.客隊下卦為【{}】，主隊上卦為【{}】，主客關係為【{}】。內卦為我寨，處{}，外卦為彼營，處{}。{} \n2.主隊世爻，{}世爻為【{}】{}{}{}，{}；{}客隊應爻為【{}】{}{}{}，{}主客關係為【{}】，{}。\n3.日干下主隊世爻臨【{}】，客隊應爻臨【{}】，時干下{}{} \n5.{}{}".format(downgua,upgua, down_vs_up,downgua1,upgua1,father_luck,shi_yy,shi[0:4],sk_dist,sguan,s_dist2,s_dist3,shi_monster,ying[0:4],yk_dist,yguan,y_dist2,ying_monster,shi_vs_ying,shi_vs_ying2, gettwelve.get(shi[2]), gettwelve.get(ying[2]), s_vs_y_dist, gua_no_yao, flyfu_dist,father_lay_dist)
        if dongyao !="0":
            try:
                num = int(ogua.index("9")) 
                dong = bg_yaolist[int(ogua.index("9"))]
            except ValueError:
                num = int(ogua.index("6")) 
                dong = bg_yaolist[int(ogua.index("6"))]
            if self.multi_key_dict_get(yingke, gz[2][1]+dong[2]) is None and  self.multi_key_dict_get(yingke, gz[3][1]+dong[2]) is None:
                dd_dist = "動爻與日辰地支沒有刑克。"
            if self.multi_key_dict_get(yingke, gz[2][1]+dong[2]) =="刑" or self.multi_key_dict_get(yingke, gz[3][1]+dong[2]) =="刑":
                dd_dist = "動爻與日辰地支刑克。"
            dong_dist = {"父":"【父母】爻發動，乃大敗之兆。",
			"官":"【官鬼】爻發動，我軍不嬴。",
			"子":"【子孫】爻發動，我軍勝。",
			"妻":"【妻財】爻發動，我軍不利。",
			"兄":"【兄弟】爻發動，凶，我軍輸。"}.get(dong[0])
            
            dong2 = self.multi_key_dict_get({(0,1,2):"動爻在下卦，即客隊，", (3,4,5):"動爻在上卦，即主隊，"},num)
            if dong2[3] == "下":
                bian = eightgua.get(gb[0:3])
                vs = self.multi_key_dict_get(wuxing_relation_2,  bian[1]+upgua[1])
            if dong2[3] == "上":
                bian = eightgua.get(gb[3:6])
                vs = self.multi_key_dict_get(wuxing_relation_2,  downgua[1]+bian[1])
            try:
                vs2 = self.find_wx_relation(shi[2],dong[2])
                vs3 = self.find_wx_relation(ying[2],dong[2])
            except IndexError:
                vs2 = ""
                vs3 = ""
            if  flyfu_dist == "":
                o = "【斷主客勝負】\n1.客隊下卦為【{}】，主隊上卦為【{}】，主客關係為【{}】。內卦為我寨，處{}，外卦為彼營，處{}。{}\n2.主隊世爻，{}世爻為【{}】{}{}{}，{}；{}客隊應爻為【{}】{}{}{}，{}主客關係為【{}】，{}。 \n3.{}變為【{}】，主客關係為【{}】。 \n4.動爻【{}】，主隊世爻【{}】，關係為【{}】。 \n5.動爻【{}】，客隊應爻【{}】，關係為【{}】。\n6.{}。\n7.{} \n8.日干下主隊世爻臨【{}】，客隊應爻臨【{}】，時干下{}{}".format(downgua,upgua, down_vs_up,downgua1,upgua1,father_luck,shi_yy,shi[0:4],sk_dist,sguan,s_dist2,s_dist3,shi_monster,ying[0:4],yk_dist,yguan,y_dist2,ying_monster,shi_vs_ying,shi_vs_ying2,dong2, bian, vs, dong[:-1],shi[0:4], vs2, dong[:-1],ying[0:4], vs3, dd_dist,dong_dist, gettwelve.get(shi[2]), gettwelve.get(ying[2]), s_vs_y_dist, gua_no_yao)
            if  flyfu_dist != "":
                o = "【斷主客勝負】\n1.客隊下卦為【{}】，主隊上卦為【{}】，主客關係為【{}】。內卦為我寨，處{}，外卦為彼營，處{}。{}\n2.主隊世爻，{}世爻為【{}】{}{}{}，{}；{}客隊應爻為【{}】{}{}{}，{}主客關係為【{}】，{}。 \n3.{}變為【{}】，主客關係為【{}】。 \n4.動爻【{}】，主隊世爻【{}】，關係為【{}】。 \n5.動爻【{}】，客隊應爻【{}】，關係為【{}】。\n6.{}{}{} \n7.{} \n8.日干下主隊世爻臨【{}】，客隊應爻臨【{}】，時干下{}{}".format(downgua,upgua, down_vs_up,downgua1,upgua1,father_luck,shi_yy,shi[0:4],sk_dist,sguan,s_dist2,s_dist3,shi_monster,ying[0:4],yk_dist,yguan,y_dist2,ying_monster,shi_vs_ying,shi_vs_ying2,dong2, bian, vs, dong[:-1],shi[0:4], vs2, dong[:-1],ying[0:4], vs3,dd_dist,flyfu_dist,father_lay_dist, dong_dist,gettwelve.get(shi[2]), gettwelve.get(ying[2]), s_vs_y_dist, gua_no_yao)
        return a+b+c0+c+c1+c2+c3+c4+c5+c5_1+d+e+f+g+h+i+j+k+l+m+n+o
    
    def display_pan(self, year, month, day, hour, minute):
        gz = self.gangzhi(year, month, day, hour, minute)
        oo = self.qigua_time(year, month, day, hour, minute).get('大衍筮法')
        ogua = self.qigua_time(year, month, day, hour, minute).get('大衍筮法')[0]
        bengua = self.qigua_time(year, month, day, hour, minute).get("本卦")
        ggua = self.qigua_time(year, month, day, hour, minute).get("之卦")
        gb = ogua.replace("9","8").replace("6","7")
        wugua = ogua.replace("9","7").replace("6","8")[1:4]+gb[2:5]
        b1 = self.qigua_time(year, month, day, hour, minute).get("本卦").get("星宿")
        b2 = self.qigua_time(year, month, day, hour, minute).get("本卦").get('六親用神')
        b3 = self.qigua_time(year, month, day, hour, minute).get("本卦").get('納甲')
        b4 = self.qigua_time(year, month, day, hour, minute).get("本卦").get('五行')
        b5 = self.qigua_time(year, month, day, hour, minute).get("本卦").get('世應爻')
        g1 = self.qigua_time(year, month, day, hour, minute).get("之卦").get("星宿")
        g2 = self.qigua_time(year, month, day, hour, minute).get("之卦").get('六親用神')
        g3 = self.qigua_time(year, month, day, hour, minute).get("之卦").get('納甲')
        g4 = self.qigua_time(year, month, day, hour, minute).get("之卦").get('五行')
        g5 = self.qigua_time(year, month, day, hour, minute).get("之卦").get('世應爻')
        try:
            gua_no_yao = {  "父":"卦無【父母】，乃幟不備也。",
                            "妻":"卦無【妻財】，糧草缺絕也。",
                            "官":"卦無【官鬼】，如與鬼墓絕胎者，敵必遁去也。",
                            "子":"卦無【子孫】，動來救。",
                            "兄":"卦無【兄弟】，防奸細也。"}.get(list(set(list("官父妻兄子"))- set(b2))[0])
        except IndexError:
            gua_no_yao = ""
        guayaodict = {"6":"▅▅ ▅▅ X", "7":"▅▅▅▅▅  ", "8":"▅▅ ▅▅  ", "9":"▅▅▅▅▅ O"}
        #guayaodict = {"6":"▅▅　▅▅ X", "7":"▅▅▅▅▅  ", "8":"▅▅　▅▅  ", "9":"▅▅▅▅▅ O"}
        bg = [guayaodict.get(i) for i in list(ogua)]
        gb1 = [guayaodict.get(i) for i in list(gb)]
        wgb = [guayaodict.get(i) for i in list(wugua)]
        bg_yaolist = ["".join([b2[i],b3[i],b4[i],b5[i]]) for i in range(0,6)]
        #gg_yaolist = ["".join([b2[i],b3[i],b4[i],b5[i]]) for i in range(0,6)]
        smons = self.find_six_mons(gz[2][0])
        lunar_month = self.lunar_date_d(year, month, day).get("月")
        build_month = self.find_lunar_month(gz[0]).get(lunar_month)
        dong_yaos = [i.replace("7", "").replace("8", "").replace("6", "動").replace("9", "動") for i in list(ogua)]
        qin_elements = dict(zip(b2, [b2[i]+b4[i]+dong_yaos[i] for i in range(0,6)]))
        by = {
            0:["身","　","　","　","　","　"],
            1:["　","身","　","　","　","　"],
            2:["　","　","身","　","　","　"],
            3:["　","　","　","身","　","　"],
            4:["　","　","　","　","身","　"],
            5:["　","　","　","　","　","身"],
            }.get([b2[i]+b3[i] for i in range(0,6)].index(bengua.get('身爻')[0:3]))
        try:
            fugod1 = bengua.get("伏神").get("伏神排爻數字")
            fugod2 = ggua.get("伏神").get("伏神排爻數字")
            fyao1 = bengua.get("伏神").get("伏神爻")
            fyao2 = ggua.get("伏神").get("伏神爻")
            fu_location = {0:[fyao1,"　　　　","　　　　","　　　　","　　　　","　　　　"] ,1:["　　　　",fyao1,"　　　　","　　　　","　　　　","　　　　"], 2:["　　　　","　　　　",fyao1,"　　　　","　　　　","　　　　"], 3:["　　　　","　　　　","　　　　",fyao1,"　　　　","　　　　"], 4:["　　　　","　　　　","　　　　","　　　　",fyao1,"　　　　"], 5:["　　　　","　　　　","　　　　","　　　　","　　　　",fyao1]}
            fu_location1 = {0:[fyao2,"　　　　","　　　　","　　　　","　　　　","　　　　"] ,1:["　　　　",fyao2,"　　　　","　　　　","　　　　","　　　　"], 2:["　　　　","　　　　",fyao2,"　　　　","　　　　","　　　　"], 3:["　　　　","　　　　","　　　　",fyao2,"　　　　","　　　　"], 4:["　　　　","　　　　","　　　　","　　　　",fyao2,"　　　　"], 5:["　　　　","　　　　","　　　　","　　　　","　　　　",fyao2]}
            fufu = fu_location.get(fugod1)
            fufu2 = fu_location1.get(fugod2)
            flylocation = bengua.get("伏神").get('本卦伏神所在爻')
            flygodyao = bengua.get("伏神").get('本卦伏神所在爻')[2:]
            fugodyao = fyao1[2:]
            if flylocation[0] == "父":
                father_lay_dist = {"子":"父下伏子，眾將懾服，擒縱如意也。",
                                   "妻":"父下伏財，備器足餉，智無遺算，但左右防伏戎也。",
                                   "兄":"父下伏兄，貪財好色，狎侮私人也。",
                                   "官":"父下伏鬼，智短計拙，動見疏虞也。"}.get(fyao1[0])
            else:
                father_lay_dist = ""
            flyfu_relation = self.find_wx_relation(flygodyao[0],fugodyao[0])
            if flyfu_relation == "我尅":
                ff_relation = "我尅】，飛來克伏為害，為凶。"
            if flyfu_relation == "尅我":
                ff_relation = "尅我】，伏克飛神為出暴，出暴者，凶而快。"
            if flyfu_relation == "比和":
                ff_relation = "比和】。"
            if flyfu_relation == "生我":
                ff_relation = flyfu_relation + "】。"
            if flyfu_relation == "我生":
                ff_relation = flyfu_relation + "】。"
            flyfu_dist = "伏神爻【"+fyao1+"】，飛神【"+flygodyao+"】在【"+flylocation+"】，伏神【"+fugodyao+"】，飛伏關係為【"+ff_relation
        except AttributeError:
            fufu = ["　　　　","　　　　","　　　　","　　　　","　　　　","　　　　"]
            fufu2 = ["　　　　","　　　　","　　　　","　　　　","　　　　","　　　　"]
            flyfu_dist = ""
        daykong = self.daykong_shikong(year, month, day, hour, minute).get("日空")
        hourkong = self.daykong_shikong(year, month, day, hour, minute).get("時空")
        gettwelve = self.find_shier_luck(gz[2][0])
        twelvelucks =  "".join([self.find_shier_luck(gz[2][0]).get(i)+"　" for i in self.dizhi])
        twelvelucks_hour = self.find_shier_luck(gz[3][0])
        twelvelucks_hour1 = "".join([self.find_shier_luck(gz[3][0]).get(i)+"　" for i in self.dizhi])
        try:
            father_luck = self.multi_key_dict_get({("衰　","病　","死　","墓　","絕　"):"父母爻處衰絕，主隊軍師老髦也，守舊保守也。",
                 ("長生","沐浴","冠帶","臨官","帝旺"):"父母爻處旺相，主隊軍師少壯也，開明進取也。",
                 ("胎　","養　"):"父母爻處胎、養，主隊軍師不威重也，欠謀略。"},  twelvelucks_hour.get(b3[b2.index("父")][1]))
        except (ValueError,IndexError):
            father_luck = ""
        a = "起卦時間︰{}年{}月{}日{}時{}分\n".format(year, month, day, hour, minute)
        b = "農曆︰{}{}月{}日\n".format(cn2an.transform(str(year)+"年", "an2cn"), an2cn(self.lunar_date_d(year, month, day).get("月")), an2cn(self.lunar_date_d(year,month, day).get("日")))
        c = "干支︰{}年  {}月  {}日  {}時\n".format(gz[0], gz[1], gz[2], gz[3])
        j_q = jq(year, month, day, hour, minute)
        c0 = "節氣︰{} | 旺︰{} | 相︰{}\n".format(j_q, gong_wangzhuai(j_q)[1].get("旺"), gong_wangzhuai(j_q)[1].get("相"))
        c1 = "旬空︰　　　  　　　  {}    {}\n".format(daykong, hourkong)
        c2 = "月建︰　　　  {}\n\n".format(build_month)
        c3 = "　　　　"+ "".join([i+"　　" for i in self.dizhi]) +"\n"
        c4 = "　　　　"+"".join([self.Ganzhiwuxing(i)+"　　" for i in self.dizhi] )+"\n"
        c5 = "日支運︰"+ twelvelucks+"\n"
        c5_1 = "時支運︰"+ twelvelucks_hour1+"\n\n"
        d = "　　　　　　　       　 　{}卦　　　　　　　　　　 　　　　　              　  {}卦                \n".format(bengua.get("卦"), ggua.get("卦"))
        e = "六神　  伏神　　         本卦　　　　　　　　　　　       互卦               伏神　　   之卦\n"
        f = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}　\n".format(smons[5],fufu[5],b1[5],b2[5],b3[5],b4[5],twelvelucks_hour.get(b3[5][1]),b5[5].replace("六","　"), bg[5],by[5],wgb[5],fufu2[5],g1[5],g2[5],g3[5],g4[5],g5[5].replace("六","　"),gb1[5])
        g = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n".format(smons[4],fufu[4],b1[4],b2[4],b3[4],b4[4],twelvelucks_hour.get(b3[4][1]),b5[4].replace("五","　"), bg[4],by[4],wgb[4],fufu2[4],g1[4],g2[4],g3[4],g4[4],g5[4].replace("五","　"),gb1[4])
        h = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n".format(smons[3],fufu[3],b1[3],b2[3],b3[3],b4[3],twelvelucks_hour.get(b3[3][1]),b5[3].replace("四","　"), bg[3],by[3],wgb[3],fufu2[3],g1[3],g2[3],g3[3],g4[3],g5[3].replace("四","　"),gb1[3])
        i = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n".format(smons[2],fufu[2],b1[2],b2[2],b3[2],b4[2],twelvelucks_hour.get(b3[2][1]),b5[2].replace("三","　"), bg[2],by[2],wgb[2],fufu2[2],g1[2],g2[2],g3[2],g4[2],g5[2].replace("三","　"),gb1[2])
        j = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n".format(smons[1],fufu[1],b1[1],b2[1],b3[1],b4[1],twelvelucks_hour.get(b3[1][1]),b5[1].replace("二","　"), bg[1],by[1],wgb[1],fufu2[1],g1[1],g2[1],g3[1],g4[1],g5[1].replace("二","　"),gb1[1])
        k = "　{} 　　{}　　 {} {}{}{} {} {}{} {}      {}      {}　　 {} {}{}{} {}{}  \n\n\n".format(smons[0],fufu[0],b1[0],b2[0],b3[0],b4[0],twelvelucks_hour.get(b3[0][1]),b5[0].replace("初","　"), bg[0],by[0],wgb[0],fufu2[0],g1[0],g2[0],g3[0],g4[0],g5[0].replace("初","　"),gb1[0])
        l = "【大衍筮法】\n"
        
        try:
            m = "求得【{}之{}】，{}{}{}\n\n".format(oo[1], oo[2], oo[4][0], oo[4][2], oo[4][3])
        except IndexError:
            m = "求得【{}之{}】，{}{}\n\n".format(oo[1], oo[2], oo[4][0], oo[4][2])
        n = "【{}卦】\n卦辭︰{}\n彖︰{}\n{}\n{}\n{}\n{}\n{}\n{}\n\n".format(oo[1],oo[3].get(0), oo[3].get(7)[2:], oo[3].get(6), oo[3].get(5), oo[3].get(4), oo[3].get(3), oo[3].get(2), oo[3].get(1)  )
        eightgua = { '777':"乾金",  '778':"兌金",  '787':"離火",  '788':"震木",  '877':"巽木", '878':"坎水",  '887':"艮土",  '888':"坤土"}
        downgua = eightgua.get(ogua[0:3].replace("6","8").replace("9","7"))
        upgua = eightgua.get(ogua[3:6].replace("6","8").replace("9","7"))
        status = {("旺","相"):"，吉也",("胎","沒"):"，平也",("死","囚","休","廢"):"，凶也"} 
        downgua1 =  "【"+gong_wangzhuai(j_q)[0].get(downgua[0])+"】" + self.multi_key_dict_get(status, gong_wangzhuai(j_q)[0].get(downgua[0]) )
        upgua1 = "【"+gong_wangzhuai(j_q)[0].get(upgua[0])+"】" + self.multi_key_dict_get(status, gong_wangzhuai(j_q)[0].get(upgua[0]) )
        shi =  bg_yaolist[["世" in i  for i in bg_yaolist].index(True)]
        ying = bg_yaolist[["應" in i  for i in bg_yaolist].index(True)]
        hour_status = self.find_shier_luck(gz[3][0])
        shi_luck = hour_status.get(shi[2])
        ying_luck = hour_status.get(ying[2])
        if shi_luck == "帝旺" or shi_luck == "臨官" and ying_luck != "帝旺" or ying_luck != "臨官":
            s_vs_y_dist = "世旺應衰者，我強彼弱，宜攻也。"
        if ying_luck == "帝旺" or ying_luck == "臨官" and shi_luck != "帝旺" or shi_luck != "臨官" :
            s_vs_y_dist = "世衰應旺者，我弱彼強，宜守也。"
        if shi_luck == "帝旺" or shi_luck == "臨官" and ying_luck == "帝旺" or ying_luck == "臨官" :
            s_vs_y_dist = "世應皆旺，必不交鋒，戰亦勝負難決也。"
        else:
            s_vs_y_dist = "世應皆不旺，戰亦勝負難決也。"
        shi_yy = {"陽":"世陽而動者，宜出師。", "陰":"世陰而靜者，宜堅壁也。"}.get(self.multi_key_dict_get(yingyang, shi[1]))
        down_vs_up = self.multi_key_dict_get(wuxing_relation_2,  downgua[1]+upgua[1])
        shi_vs_ying = self.find_wx_relation(shi[2], ying[2])
        shi_vs_ying2 =  {"我尅":"世尅應爻，我軍必勝",
                        "尅我":"應尅世爻，我軍必敗",
                        "比和":"世應比和，勢軍力敵",
                        "我生":"世生應爻，我軍不利",
                        "生我":"應生世爻，彼軍不利",
                        }.get(shi_vs_ying)
        sy_monster = {"龍":"臨【青龍】，良將也。",
			   "虎":"臨【白虎】，猛將也。",
			   "陳":"臨【勾陳】，密遣擒賊也。",
			   "雀":"臨【朱雀】，號令嚴明也。",
			   "蛇":"臨【螣蛇】，變幻不測也。",
			   "武":"臨【玄武】，善用囊沙背水之術，或巧於偷營劫寨也。"}
        shi_monster = "世爻" + sy_monster.get(smons[b5.index("世")])
        ying_monster = "應爻" + sy_monster.get(smons[b5.index("應")])
        dongyao = oo[4][0][4]
        if shi[2] == daykong[0] or shi[2] == daykong[1] or shi[2] == hourkong[1] or shi[2] == hourkong[0]:
            sk_dist = "，世爻主隊遇旬空，不利"
        else:
            sk_dist = ""
        god_dist1 = {"兄":"，忌神持世，不利","父":"，仇神持世，不利","妻":"，用神持世，有利", "子":"，原神持世，費心", "官":"，泄神持世，有利"}  
        god_dist2 = {"兄":"，忌神持應，不利","父":"，仇神持應，不利","妻":"，用神持應，有利", "子":"，原神持應，費心", "官":"，泄神持應，有利"}  
        s_dist2 = god_dist1.get(shi[0])
        y_dist2 = god_dist2.get(ying[0])
        s_dist3 = {"父":"父母持世，大敗之兆",
        		  "妻":"妻財持世，如旺相，如獨發便嬴",
        		  "官":"官鬼持世。皆敗，乃彼我不得地，世旺克應，我勝；應旺克也，彼勝",
        		  "兄":"兄弟持世，主有奸人在軍中，世下伏鬼亦然",
        		  "子":"子孫持世，如旺相，或獨發便贏，若鬼兄財爻動便輸"}.get(shi[0])
        if ying[2] == daykong[0] or ying[2] == daykong[1] or ying[2] == hourkong[1] or ying[2] == hourkong[0]:
            yk_dist = "，應爻客隊遇旬空，不利"
        else:
            yk_dist = ""
        if "官" in shi == True:
            sguan = "，世見官鬼爻，皆敗"
        else:
            sguan = ""
        if "官" in ying == True:
            yguan = "，應見官鬼爻，皆敗"
        else:
            yguan = ""
        if dongyao == "0":
            if  flyfu_dist == "":
                o = "【斷主客勝負】\n1.客隊下卦為【{}】，主隊上卦為【{}】，主客關係為【{}】。內卦為我寨，處{}，外卦為彼營，處{}。{} \n2.主隊世爻，{}世爻為【{}】{}{}{}，{}；{}客隊應爻為【{}】{}{}{}，{}主客關係為【{}】，{}。\n3.日干下主隊世爻臨【{}】，客隊應爻臨【{}】，時干下{}{}".format(downgua,upgua, down_vs_up,downgua1,upgua1,father_luck,shi_yy,shi[0:4],sk_dist,sguan,s_dist2,s_dist3,shi_monster,ying[0:4],yk_dist,yguan,y_dist2,ying_monster,shi_vs_ying,shi_vs_ying2, gettwelve.get(shi[2]), gettwelve.get(ying[2]), s_vs_y_dist, gua_no_yao)
            if  flyfu_dist != "":
                o = "【斷主客勝負】\n1.客隊下卦為【{}】，主隊上卦為【{}】，主客關係為【{}】。內卦為我寨，處{}，外卦為彼營，處{}。{} \n2.主隊世爻，{}世爻為【{}】{}{}{}，{}；{}客隊應爻為【{}】{}{}{}，{}主客關係為【{}】，{}。\n3.日干下主隊世爻臨【{}】，客隊應爻臨【{}】，時干下{}{} \n5.{}{}".format(downgua,upgua, down_vs_up,downgua1,upgua1,father_luck,shi_yy,shi[0:4],sk_dist,sguan,s_dist2,s_dist3,shi_monster,ying[0:4],yk_dist,yguan,y_dist2,ying_monster,shi_vs_ying,shi_vs_ying2, gettwelve.get(shi[2]), gettwelve.get(ying[2]), s_vs_y_dist, gua_no_yao, flyfu_dist,father_lay_dist)
        if dongyao == "1":
            try:
                num = int(ogua.index("9")) 
                dong = bg_yaolist[int(ogua.index("9"))]
            except ValueError:
                num = int(ogua.index("6")) 
                dong = bg_yaolist[int(ogua.index("6"))]
            if self.multi_key_dict_get(yingke, gz[2][1]+dong[2]) is None and  self.multi_key_dict_get(yingke, gz[3][1]+dong[2]) is None:
                dd_dist = "動爻與日辰地支沒有刑克。"
            if self.multi_key_dict_get(yingke, gz[2][1]+dong[2]) =="刑" or self.multi_key_dict_get(yingke, gz[3][1]+dong[2]) =="刑":
                dd_dist = "動爻與日辰地支刑克。"
            dong_dist = {"父":"【父母】爻發動，乃大敗之兆。",
			"官":"【官鬼】爻發動，我軍不嬴。",
			"子":"【子孫】爻發動，我軍勝。",
			"妻":"【妻財】爻發動，我軍不利。",
			"兄":"【兄弟】爻發動，凶，我軍輸。"}.get(dong[0])
            
            dong2 = self.multi_key_dict_get({(0,1,2):"動爻在下卦，即客隊，", (3,4,5):"動爻在上卦，即主隊，"},num)
            if dong2[3] == "下":
                bian = eightgua.get(gb[0:3])
                vs = self.multi_key_dict_get(wuxing_relation_2,  bian[1]+upgua[1])
            if dong2[3] == "上":
                bian = eightgua.get(gb[3:6])
                vs = self.multi_key_dict_get(wuxing_relation_2,  downgua[1]+bian[1])
            try:
                vs2 = self.find_wx_relation(shi[2],dong[2])
                vs3 = self.find_wx_relation(ying[2],dong[2])
            except IndexError:
                vs2 = ""
                vs3 = ""
            if  flyfu_dist == "":
                o = "【斷主客勝負】\n1.客隊下卦為【{}】，主隊上卦為【{}】，主客關係為【{}】。內卦為我寨，處{}，外卦為彼營，處{}。{}\n2.主隊世爻，{}世爻為【{}】{}{}{}，{}；{}客隊應爻為【{}】{}{}{}，{}主客關係為【{}】，{}。 \n3.{}變為【{}】，主客關係為【{}】。 \n4.動爻【{}】，主隊世爻【{}】，關係為【{}】。 \n5.動爻【{}】，客隊應爻【{}】，關係為【{}】。\n6.{}。\n7.{} \n8.日干下主隊世爻臨【{}】，客隊應爻臨【{}】，時干下{}{}".format(downgua,upgua, down_vs_up,downgua1,upgua1,father_luck,shi_yy,shi[0:4],sk_dist,sguan,s_dist2,s_dist3,shi_monster,ying[0:4],yk_dist,yguan,y_dist2,ying_monster,shi_vs_ying,shi_vs_ying2,dong2, bian, vs, dong[:-1],shi[0:4], vs2, dong[:-1],ying[0:4], vs3, dd_dist,dong_dist, gettwelve.get(shi[2]), gettwelve.get(ying[2]), s_vs_y_dist, gua_no_yao)
            if  flyfu_dist != "":
                o = "【斷主客勝負】\n1.客隊下卦為【{}】，主隊上卦為【{}】，主客關係為【{}】。內卦為我寨，處{}，外卦為彼營，處{}。{}\n2.主隊世爻，{}世爻為【{}】{}{}{}，{}；{}客隊應爻為【{}】{}{}{}，{}主客關係為【{}】，{}。 \n3.{}變為【{}】，主客關係為【{}】。 \n4.動爻【{}】，主隊世爻【{}】，關係為【{}】。 \n5.動爻【{}】，客隊應爻【{}】，關係為【{}】。\n6.{}{}{} \n7.{} \n8.日干下主隊世爻臨【{}】，客隊應爻臨【{}】，時干下{}{}".format(downgua,upgua, down_vs_up,downgua1,upgua1,father_luck,shi_yy,shi[0:4],sk_dist,sguan,s_dist2,s_dist3,shi_monster,ying[0:4],yk_dist,yguan,y_dist2,ying_monster,shi_vs_ying,shi_vs_ying2,dong2, bian, vs, dong[:-1],shi[0:4], vs2, dong[:-1],ying[0:4], vs3,dd_dist,flyfu_dist,father_lay_dist, dong_dist,gettwelve.get(shi[2]), gettwelve.get(ying[2]), s_vs_y_dist, gua_no_yao)
        return a+b+c0+c+c1+c2+c3+c4+c5+c5_1+d+e+f+g+h+i+j+k+l+m+n+o
    #qin_elements
    #
    
    
if __name__ == '__main__':
    print(Iching().display_pan(2023,5,30,8,30))
    #print(Iching().display_pan(2023,5,29,15,30))
    #print(Iching().qigua_time(2023,5,28,13,30))
