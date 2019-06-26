# 周易筮法卜卦 Iching Shifa (stalk divination)


筮是傳統的周易起卦方式。古人以50根蓍草作為占卜工具，名為策，故此法亦稱"籌策"占卜。《周易系辭上傳》辭曰："大衍之數五十，其用四十有九。分而為二以像兩，掛一以像三， 揲之以四以像四時，歸奇於扐以像閏，五歲再閏，故再扐而後掛。 天一地二，天三地四，天五地六，天七地八，天九地十。天數五，地數五，五位相得而各有合。天數二十有五，地數三十，凡天地之數五十有五。此所以成變化而行鬼神也。"

**三變**︰

```python
n=2
stalks_first = 50-1 #拿走太一，分為二象
first_division = np.random.multinomial(stalks_first, np.ones(n)/2, size=1)[0] #一變過程 (分二、掛一、揲四、歸奇)
guayi = 1
right = first_division[0] - guayi
left_extract = first_division[1] % 4 
if left_extract == 0:
    left_extract = 4
right_extract = right % 4
if right_extract == 0:
    right_extract = 4
bian  = left_extract + right_extract + guayi
```
上述為一變，一變重複三次，49策 - 一變 - 二變 - 三變 = 爻。而每一根爻的數值可以是**6(老陰)、7(少陽)、8(少陰)或者 9(老陽)**。



**處理變爻的方法︰**

1. 凡卦六爻皆不變則占本卦彖辭而以內卦為貞外卦為悔彖辭為卦下之辭

2. 一爻變則以本卦變爻辭

3. 二爻變則以本卦二變爻辭占仍以上爻為主

4. 三爻變則占本卦及之卦之彖辭即以本卦為貞之卦為悔前十卦主貞後十卦主悔

5. 四爻變則以之卦二不變爻占仍以下爻為主經𫝊亦無文今以例推之當如此

6. 五爻變則以之卦不變爻占

7. 六爻變則乾坤占二用餘卦占之卦彖辭

_參考自【宋】‧朱熹、蔡元定《易學啟蒙》卷下 考變占︰_
