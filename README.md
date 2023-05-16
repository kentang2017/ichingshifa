# Python IchingShifa Python 周易 筮法 六爻 卜卦 (stalk divination)

[![Python](https://img.shields.io/pypi/pyversions/ichingshifa)](https://pypi.org/project/ichingshifa/)
[![PIP](https://img.shields.io/pypi/v/ichingshifa)](https://pypi.org/project/ichingshifa/)
[![Downloads](https://img.shields.io/pypi/dm/ichingshifa)](https://pypi.org/project/ichingshifa/)
[![TG Me](https://img.shields.io/badge/chat-on%20telegram-blue)](https://t.me/gnatnek)
[![TG Channel](https://img.shields.io/badge/chat-on%20telegram-red)](https://t.me/numerology_coding)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)&nbsp;

![alt text](https://upload.wikimedia.org/wikipedia/commons/a/af/French_Polished_Yarrow_stalks_from_LPKaster.jpg "Stalk divination")

"筮"是傳統的周易起卦方式。古人以50根蓍草作為占卜工具，名為策，故此法亦稱"籌策"占卜。《周易系辭上傳》辭曰："大衍之數五十，其用四十有九。分而為二以像兩，掛一以像三， 揲之以四以像四時，歸奇於扐以像閏，五歲再閏，故再扐而後掛。 天一地二，天三地四，天五地六，天七地八，天九地十。天數五，地數五，五位相得而各有合。天數二十有五，地數三十，凡天地之數五十有五。此所以成變化而行鬼神也。"整個起卦過程是要求得十八個隨機數目，當中包括"六次"(即六根爻)的"三變"。


**"Shi"(筮)** or so-called Stalk divination, one of the oldest IChing divination method in the Chinese society, in which the ancient Chinese used 50 sticks of yarrow stalks to do divination or prediction. According to Zhouyi 周易, the number of "Da Yan" (大衍) is 50 while 1 is taken away and 49 sticks of yarrow stalks were used in divination. 49 stalks were seperated into 2 bunches respectively held by both left hand and right hand, and then one stick would be extracted from the right hand, the bunch of stalks held by right hand was divided by four, until the remainder comes, that is called the change (or 'bian'), repeating thrice. The whole process of this divination includes getting 18 random numbers. The value of Line may come after  "Three Changes", that is  (49 stalks - first change - second change - third change) divided by 4, it will be either **6(old yin 老陰)**, **7(young yang 少陽)**, **8(young yin 少陰)**, or **9(old yang 老陽)**.  The BenGua (本卦) is formed when the value of Line is formed from the bottom to the top. If the line with value of either 6 or 9, meaning that line must have a change, like 6(old yin) change to 7(young yang), and 9 (old yang) change to 8 (old yin). Each of the lines has its own meaning or explantion. BianGua (變卦) or ZhiGua (之卦) is also formed after BenGua with value 6 or 9 has been changed. 


## **1. 大衍之數、太一、分二、掛一、揲四、歸奇 The number of DaYan**︰

```python
#一變的過程
n=2
stalks_first = 50-1  #把太一拿走
dividers = sorted(random.sample(range(24, stalks_first), n - 1)) #分二
division  = [a - b for a, b in zip(dividers + [stalks_first+10], [10] + dividers)]
guayi = 1 #掛一
right = division[0] - guayi 
left_extract = division[1] % 4  #揲四
if left_extract == 0:
    left_extract = 4
right_extract = right % 4
if right_extract == 0:
    right_extract = 4 #歸奇
bian  = left_extract + right_extract + guayi #一變，其餘二變倣效此法，如果做for loop 這裡的掛一可以拿走，不用加上。
```

## **2. 處理變(動)爻的方法︰The way in handling the change of line(s)(yao(s))**

1. 凡卦六爻皆不變，則占本卦彖辭，而以內卦為貞，外卦為悔，彖辭為卦下之辭。

2. 一爻變，則以本卦變爻辭

3. 二爻變，則以本卦二變爻辭占，仍以上爻為主

4. 三爻變，則占本卦及之卦之彖辭，即以本卦為貞，之卦為悔，前十卦(初爻出現變爻)主貞，後十卦(非初爻出現變爻)主悔

5. 四爻變，則以之卦二不變爻占，仍以下爻為主經，亦無文，今以例推之當如此。

6. 五爻變，則以之卦不變爻占。

7. 六爻變，則乾、坤占二用，餘卦占之卦彖辭。

_參考自【宋】‧朱熹、蔡元定《易學啟蒙》卷下 考變占︰_

1. If the Six lines without any changed lines, the explantion of Gua is based on the general explanation of BenGua. 
2. If the Six lines with one line changed, the explanation is depended on there. 
3. If the Six lines with two lines changed, the upper one is the main explanation. 
4. If the Six lines with three lines changed, the explanation is lied on the BenGua's general explanation if the change line starts from the first line, while the explantion is base on BianGua's general explanation if the change line starts from the second line. 
5. If the Six lines with four lines changed,  the explanation is upon the lower line of BianGua. 
6. If the Six lines with five lines changed,  the explanation is upon the one line without change on BianGua. 
7. If the Six lines with six lines changed, except for QianGua and KunGua with explanation on 用, use the general explanation  
_The above method is advocated by ZhuXi, a Confucian of Song Dynasty_

![alt text](https://github.com/kentang2017/iching_shifa/blob/master/data/results.png?raw=true)

## **3. 納甲 Najia**
其後漢元帝師從梁人焦延壽的京房開創京氏易學，把筮法加入干支納甲，後世學者再加以五行、五星、六親及二十八宿等加以詳推。

Later on, an iching expert Jing Fang during the Han Dynasty created a najia method of hexagram interpretation among iching. which correlates their separate lines with elements of the Chinese calendar.


## **4. 安裝套件 Installation**:
```
pip install sxtwl
pip install --upgrade ichingshifa
```

## **5. 快速起卦 Quick Start**:
```
from ichingshifa import ichingshifa #導入周易筮法套件庫 Import ichingshifa


ichingshifa.Iching().mget_bookgua_details() #手動起卦，從下而上，適合以蓍草起卦者使用，譬如 "初爻7, 二爻8, 三爻9, 四爻7, 五爻8, 上爻9"，即 ichingshifa.mget_bookgua_details('789789') Manually input each of lines' value, e.g. Iching().mget_bookgua_details('789789')
ichingshifa.Iching().bookgua_details() #顯示隨機起卦結果 Making divination randomly
ichingshifa.Iching().datetime_bookgua('年', '月', '日', '時') #指定年月日時起卦 make divination with the specific datetime
ichingshifa.Iching().current_bookgua() #按現在的年月日時起卦，此法只有一動爻 make divination with the current datetime
ichingshifaIching().decode_gua("787987", "庚寅") #手動起卦，從下而上，起本卦之卦納甲
ichingshifa.Iching().qigua_now() #{'日期': '辛丑年戊戌月庚寅日甲申時', '大衍筮法': ['887888', '謙', '謙', {0: '亨，君子有終。', 1: '初六：謙謙君子，用涉大川，吉。', 2: '六二，鳴謙，貞吉。', 3: '九三，勞謙，君子有終，吉。', 4: '六四：無不利，撝謙。', 5: '六五：不富，以其鄰，利用侵伐，無不利。', 6: '上六：鳴謙，利用行師，征邑國。', 7: '彖︰謙，亨，天道下濟而光明，地道卑而上行。天道虧盈而益謙，地道變盈而流謙，鬼神害盈而福謙，人道惡盈而好謙。謙尊而光，卑而不可踰，君子之終也。'}, ('動爻有【0】根。', '主要看【謙】卦彖辭。', '謙，亨，天道下濟而光明，地道卑而上行。天道虧盈而益謙，地道變盈而流謙，鬼神害盈而福謙，人道惡盈而好謙。謙尊而光，卑而不可踰，君子之終也。')], '本卦': {'卦': '謙', '五星': '太白', '世應卦': '五世卦', '星宿': ['亢', '角', '軫', '翼', '張', '星'], '天干': ['丙', '丙', '丙', '癸', '癸', '癸'], '地支': ['辰', '午', '申', '丑', '亥', '酉'], '五行': ['土', '火', '金', '土', '水', '金'], '世應爻': ['初', '應', '三', '四', '世', '六'], '身爻': '兄癸酉金', '六親用神': ['父', '官', '兄', '父', '子', '兄'], '伏神': {'伏神所在爻': '官', '伏神六親': '妻', '伏神排爻數字': 1, '本卦伏神所在爻': '官丙午火', '伏神爻': '妻丁卯木'}, '六獸': ['虎', '武', '龍', '雀', '陳', '蛇'], '納甲': ['丙辰', '丙午', '丙申', '癸丑', '癸亥', '癸酉'], '建月': ['庚申', '辛酉', '壬戌', '癸亥', '甲子', '乙丑'], '積算': [['乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午'], ['辛未', '壬申', '癸酉', '甲戌', '乙亥', '丙子'], ['丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午'], ['癸未', '甲申', '乙酉', '丙戌', '丁亥', '戊子'], ['己丑', '庚寅', '辛卯', '壬辰', '癸巳', '甲午'], ['乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子'], ['辛丑', '壬寅', '癸卯', '甲辰', '乙巳', '丙午'], ['丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子'], ['癸丑', '甲寅', '乙卯', '丙辰', '丁巳', '戊午'], ['己未', '庚申', '辛酉', '壬戌', '癸亥', '甲子']]}, '之卦': {'卦': '謙', '五星': '太白', '世應卦': '五世卦', '星宿': ['亢', '角', '軫', '翼', '張', '星'], '天干': ['丙', '丙', '丙', '癸', '癸', '癸'], '地支': ['辰', '午', '申', '丑', '亥', '酉'], '五行': ['土', '火', '金', '土', '水', '金'], '世應爻': ['初', '應', '三', '四', '世', '六'], '身爻': '兄癸酉金', '六親用神': ['父', '官', '兄', '父', '子', '兄'], '伏神': {'伏神所在爻': '官', '伏神六親': '妻', '伏神排爻數字': 1, '本卦伏神所在爻': '官丙午火', '伏神爻': '妻丁卯木'}, '六獸': ['虎', '武', '龍', '雀', '陳', '蛇'], '納甲': ['丙辰', '丙午', '丙申', '癸丑', '癸亥', '癸酉'], '建月': ['庚申', '辛酉', '壬戌', '癸亥', '甲子', '乙丑'], '積算': [['乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午'], ['辛未', '壬申', '癸酉', '甲戌', '乙亥', '丙子'], ['丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午'], ['癸未', '甲申', '乙酉', '丙戌', '丁亥', '戊子'], ['己丑', '庚寅', '辛卯', '壬辰', '癸巳', '甲午'], ['乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子'], ['辛丑', '壬寅', '癸卯', '甲辰', '乙巳', '丙午'], ['丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子'], ['癸丑', '甲寅', '乙卯', '丙辰', '丁巳', '戊午'], ['己未', '庚申', '辛酉', '壬戌', '癸亥', '甲子']]}, '飛神': ''}

```
## **6. 軟件 Application**
A mobile app of Ichingshifa written in Kivy
https://github.com/kentang2017/iching_shifa/blob/master/kinshifa-0.2-release.apk
