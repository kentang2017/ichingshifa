# 周易筮法卜卦 Iching Shifa (stalk divination)

![alt text](https://upload.wikimedia.org/wikipedia/commons/a/af/French_Polished_Yarrow_stalks_from_LPKaster.jpg "Stalk divination")

"筮"是傳統的周易起卦方式。古人以50根蓍草作為占卜工具，名為策，故此法亦稱"籌策"占卜。《周易系辭上傳》辭曰："大衍之數五十，其用四十有九。分而為二以像兩，掛一以像三， 揲之以四以像四時，歸奇於扐以像閏，五歲再閏，故再扐而後掛。 天一地二，天三地四，天五地六，天七地八，天九地十。天數五，地數五，五位相得而各有合。天數二十有五，地數三十，凡天地之數五十有五。此所以成變化而行鬼神也。"

整個起卦過程是要求得十八次的隨機數目，當中包括"六次"(即六根爻)的"三變"。

## **1. 大衍之數、太一、分二、掛一、揲四、歸奇**︰

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
上述為一變，一變重複三次，49策 - 一變 - 二變 - 三變 = 爻。(建議三變不要以for loop做；for loop做出來的六爻動概率稍高。)分二的時候，原來設定隨機數範圍為1至49，但本人使用實物求筮時，分二左右手各得的策數目應該不會相差太遠，所以稍微調節了隨機數的範圍。以四十九除以二，即二十四作為下限。

而每一根爻的數值可以是**6(老陰)、7(少陽)、8(少陰)或者 9(老陽)**。

上述求爻數值重複六次，第一爻為初爻，從底而上，形成本卦，然後依據卦的變爻多寡求出占卜結果。

## **2. 處理變(動)爻的方法︰**

1. 凡卦六爻皆不變，則占本卦彖辭，而以內卦為貞，外卦為悔，彖辭為卦下之辭。

2. 一爻變，則以本卦變爻辭

3. 二爻變，則以本卦二變爻辭占，仍以上爻為主

4. 三爻變，則占本卦及之卦之彖辭，即以本卦為貞，之卦為悔，前十卦(初爻出現變爻)主貞，後十卦(非初爻出現變爻)主悔

5. 四爻變，則以之卦二不變爻占，仍以下爻為主經，亦無文，今以例推之當如此。

6. 五爻變，則以之卦不變爻占。

7. 六爻變，則乾、坤占二用，餘卦占之卦彖辭。

_參考自【宋】‧朱熹、蔡元定《易學啟蒙》卷下 考變占︰_


![alt text](https://github.com/kentang2017/iching_shifa/blob/master/data/results.png?raw=true)



## **3. 安裝套件**:
```
pip install --upgrade ichingshifa
```

## **4. 快速起卦**:
```
from ichingshifa import ichingshifa #導入周易筮法套件庫
ichingshifa.mget_bookgua_details() #手動起卦，從底而上，適合以蓍草起卦者使用，譬如 "初爻7, 二爻8, 三爻9, 四爻7, 五爻8, 上爻9"，即 ichingshifa.mget_bookgua_details('789789')
ichingshifa.bookgua_details() #顯示隨機起卦結果
ichingshifa.datetime_bookgua('年', '月', '日', '時') #指定年月日時起卦
ichingshifa.current_bookgua() #按現在的年月日時起卦，此法只有一動爻

```
