# 🔮 Python IchingShifa — 周易筮法六爻卜卦 (Stalk Divination)

[![Python](https://img.shields.io/pypi/pyversions/ichingshifa)](https://pypi.org/project/ichingshifa/)
[![PIP](https://img.shields.io/pypi/v/ichingshifa)](https://pypi.org/project/ichingshifa/)
[![Downloads](https://img.shields.io/pypi/dm/ichingshifa)](https://pypi.org/project/ichingshifa/)
[![TG Me](https://img.shields.io/badge/chat-on%20telegram-blue)](https://t.me/haizhonggum)
[![TG Channel](https://img.shields.io/badge/chat-on%20telegram-red)](https://t.me/numerology_coding)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)&nbsp;

![Yarrow stalks](https://upload.wikimedia.org/wikipedia/commons/a/af/French_Polished_Yarrow_stalks_from_LPKaster.jpg "蓍草 Stalk divination")

> **周易筮法**是中國最古老的占卜術之一，以蓍草演算六爻卦，推算吉凶禍福。  
> **IchingShifa** is a Python library implementing the ancient Chinese I Ching (周易) stalk divination method, complete with Najia (納甲) hexagram interpretation, Chinese calendar integration, and a full 64-hexagram database.

---

## 📖 目錄 Table of Contents

1. [簡介 Introduction](#簡介-introduction)
2. [功能特色 Features](#功能特色-features)
3. [背景 Background](#背景-background)
4. [大衍之數 The Number of DaYan](#1-大衍之數太一分二掛一揲四歸奇-the-number-of-dayan)
5. [處理變爻 Handling Changed Lines](#2-處理變動爻的方法the-way-in-handling-the-change-of-linesyaos)
6. [納甲 Najia](#3-納甲-najia)
7. [安裝 Installation](#4-安裝套件-installation)
8. [快速起卦 Quick Start](#5-快速起卦-quick-start)
9. [API 說明 API Reference](#6-api-說明-api-reference)
10. [排盤範例 Display Example](#7-排盤範例-display-example)
11. [軟件 Application](#8-軟件-application)
12. [微信公眾號 WeChat](#9-微信公眾號-wechat)
13. [授權 License](#10-授權-license)

---

## 簡介 Introduction

**ichingshifa** 是一個以 Python 實現的周易六爻筮法套件庫，提供完整的大衍蓍草起卦算法、納甲排盤、干支五行推算及六十四卦解讀，是學習及研究周易六爻的強大工具。

**ichingshifa** is a Python library that faithfully implements the classical I Ching (Zhouyi 周易) stalk divination algorithm. It provides:
- Authentic **DaYan (大衍)** yarrow-stalk simulation
- Full **Najia (納甲)** hexagram layout with Heavenly Stems and Earthly Branches
- **64-hexagram** database with line texts (爻辭), judgments (彖辭), and images (象辭)
- Integration with the **Chinese lunisolar calendar** (干支紀日)
- Support for divination by **random**, **current datetime**, **custom datetime**, or **manual line input**
- A ready-to-use **Streamlit** web application

---

## 功能特色 Features

| 功能 Feature | 說明 Description |
|---|---|
| 🎋 大衍蓍草筮法 | 模擬真實蓍草起卦過程 / Authentic yarrow-stalk simulation |
| 📅 按時間起卦 | 以指定或當前年月日時起卦 / Divination by date and time |
| ✍️ 手動輸入爻值 | 輸入六爻數值（6/7/8/9）自動排盤 / Manual line-value input |
| 🗂️ 六十四卦資料庫 | 完整卦辭、爻辭、彖辭及象辭 / Full 64-hexagram text database |
| ☯️ 納甲排盤 | 干支、五行、六親、六獸、世應、伏神 / Najia with full metadata |
| 🌙 農曆換算 | 自動換算公曆與農曆干支 / Solar ↔ lunisolar calendar conversion |
| ⚔️ 主客勝負 | 分析比賽或事件雙方優劣 / Host vs. guest outcome analysis |
| 📱 移動端應用 | Kivy 編寫的 Android App / Android app built with Kivy |
| 🌐 網頁應用 | Streamlit 網頁排盤系統 / Streamlit web divination board |

---

## 背景 Background

### 中文

"筮"是傳統的周易起卦方式。古人以50根蓍草作為占卜工具，名為策，故此法亦稱"籌策"占卜。《周易系辭上傳》辭曰：

> "大衍之數五十，其用四十有九。分而為二以像兩，掛一以像三，揲之以四以像四時，歸奇於扐以像閏，五歲再閏，故再扐而後掛。天一地二，天三地四，天五地六，天七地八，天九地十。天數五，地數五，五位相得而各有合。天數二十有五，地數三十，凡天地之數五十有五。此所以成變化而行鬼神也。"

整個起卦過程是要求得十八個隨機數目，當中包括"六次"（即六根爻）的"三變"。每爻數值為 **6（老陰）**、**7（少陽）**、**8（少陰）** 或 **9（老陽）** 之一，六爻由下而上排列成本卦（BenGua 本卦）。老陰（6）與老陽（9）為動爻，動爻變化後另成之卦（ZhiGua 之卦）。

### English

**"Shi" (筮)**, or Stalk Divination, is one of the oldest I Ching divination methods in Chinese civilization. Ancient diviners used 50 yarrow stalks as their oracle tools. According to the *Xici Zhuan* (繫辭傳) commentary of the Zhouyi, the number of *DaYan* (大衍) is 50, with one set aside, leaving 49 stalks for use.

The 49 stalks are split randomly into two groups, one stalk is set aside from the right group (*guayi* 掛一), and the remainder of each group is counted off in fours (*shesi* 揲四). This process is repeated three times to determine a single line value of **6 (Old Yin 老陰)**, **7 (Young Yang 少陽)**, **8 (Young Yin 少陰)**, or **9 (Old Yang 老陽)**.

Repeating this for all six lines (bottom to top) produces the *BenGua* (本卦, Primary Hexagram). Lines valued 6 or 9 are "changing lines" — Old Yin transforms into Young Yang and Old Yang into Young Yin — producing the *ZhiGua* (之卦, Derived Hexagram).

---

## **1. 大衍之數、太一、分二、掛一、揲四、歸奇 The Number of DaYan**

以下為一變的 Python 實現（Three-Change process, first change shown）：

```python
import random

# 一變的過程 / First Change
n = 2
stalks_first = 50 - 1          # 把太一拿走 / Remove the TaiYi stalk
dividers = sorted(random.sample(range(24, stalks_first), n - 1))  # 分二 / Split into two groups
division = [a - b for a, b in zip(dividers + [stalks_first + 10], [10] + dividers)]
guayi = 1                       # 掛一 / Set aside one stalk from right group
right = division[0] - guayi
left_extract = division[1] % 4  # 揲四 / Count off in fours (left)
if left_extract == 0:
    left_extract = 4
right_extract = right % 4       # 揲四 / Count off in fours (right)
if right_extract == 0:
    right_extract = 4           # 歸奇 / Collect the remainders
bian = left_extract + right_extract + guayi  # 一變結果 / First-change value
# 其餘二變倣效此法 / Repeat for 2nd and 3rd changes
```

三變完成後，以 `(49 - 一變 - 二變 - 三變) ÷ 4` 得出爻值（6、7、8 或 9）。

After three changes, the line value is `(49 − first change − second change − third change) ÷ 4`, yielding 6, 7, 8, or 9.

---

## **2. 處理變(動)爻的方法︰The Way in Handling the Change of Line(s)(Yao(s))**

_參考自【宋】‧朱熹、蔡元定《易學啟蒙》卷下 考變占 / Based on ZhuXi's "Yi Xue Qi Meng", Song Dynasty_

| 動爻數 Changed Lines | 中文斷法 Chinese Rule | English Rule |
|---|---|---|
| 0 爻不變 | 占本卦彖辭，以內卦為貞，外卦為悔 | Consult the judgment (彖辭) of the Primary Hexagram |
| 1 爻變 | 以本卦變爻辭為主 | Use the text of the single changed line |
| 2 爻變 | 以本卦二變爻辭占，以上爻為主 | Use both changed-line texts; the upper line takes precedence |
| 3 爻變 | 占本卦及之卦彖辭；初爻變主貞（本卦），二爻起變主悔（之卦） | Consult both hexagram judgments; lower change → BenGua; upper change → ZhiGua |
| 4 爻變 | 以之卦二不變爻占，以下爻為主 | Use the two unchanged lines of ZhiGua; lower line takes precedence |
| 5 爻變 | 以之卦唯一不變爻占 | Use the single unchanged line of ZhiGua |
| 6 爻皆變 | 乾坤占二用爻，餘卦占之卦彖辭 | For Qian/Kun use the "用" lines; others use ZhiGua's judgment |

![Hexagram result example](https://github.com/kentang2017/iching_shifa/blob/master/data/results.png?raw=true)

---

## **3. 納甲 Najia**

### 中文

漢元帝時期，易學名家**京房**（師從焦延壽）開創京氏易學，將筮法融入干支納甲體系：以八宮卦為綱，每爻配以天干地支，再結合五行生剋、六親（父母、官鬼、妻財、兄弟、子孫）、六獸（青龍、朱雀、勾陳、螣蛇、白虎、玄武）、五星（太白、太陰、歲星、熒惑、填星）、月建、日辰及二十八宿，構成完整的六爻象數推演體系，為後世六爻學奠定基礎。

### English

During the Han Dynasty, I Ching master **Jing Fang** (京房), a student of Jiao Yanshou, founded the Jing-style I Ching school. He integrated the yarrow-stalk method with the *Najia* (納甲) system, mapping Heavenly Stems and Earthly Branches onto each hexagram line. Subsequent scholars further enriched the system with:

- **Five Elements (五行)**: Wood, Fire, Earth, Metal, Water and their interactions
- **Six Relatives (六親)**: Parents (父母), Officials (官鬼), Wife/Wealth (妻財), Siblings (兄弟), Children (子孫)
- **Six Spirits (六獸)**: Azure Dragon (青龍), Vermilion Bird (朱雀), Hook Chen (勾陳), Flying Serpent (螣蛇), White Tiger (白虎), Dark Warrior (玄武)
- **Five Planets (五星)**, **28 Lunar Mansions (二十八宿)**, and **month/day branches**

This forms the complete Six-Line (六爻) divination system still in use today.

---

## **4. 安裝套件 Installation**

### 透過 PyPI 安裝 / Install via PyPI

```bash
pip install sxtwl
pip install --upgrade ichingshifa
```

**依賴套件 Dependencies**：`sxtwl`（農曆），`ephem`（天文曆算），`cn2an`（中文數字轉換），`bidict`，`numpy`

### 本地開發 / Local Development

本項目使用 `src/` 目錄佈局。克隆倉庫後，Python 文件位於 `src/` 目錄下：

This project uses a `src/` directory layout. After cloning the repository, Python files are located under the `src/` directory:

```
ichingshifa/
├── src/
│   ├── app.py                  # Streamlit 網頁應用入口 / Streamlit web app entry
│   └── ichingshifa/            # 核心套件 / Core package
│       ├── __init__.py
│       ├── ichingshifa.py
│       ├── d.py
│       ├── jieqi.py
│       ├── cerebras_client.py
│       └── data.pkl
├── data/
├── docs/
├── system_prompts.json
└── requirements.txt
```

如需在本地運行（不通過 pip 安裝），請先將 `src/` 加入 Python 路徑：

To run locally (without pip install), add `src/` to the Python path first:

```bash
export PYTHONPATH=src:$PYTHONPATH
```

---

## **5. 快速起卦 Quick Start**

```python
from ichingshifa.ichingshifa import Iching

iching = Iching()

# 隨機大衍筮法起卦 / Random stalk divination
iching.bookgua_details()

# 手動輸入六爻值（初爻→上爻）/ Manually input line values (bottom to top)
# 爻值：6=老陰, 7=少陽, 8=少陰, 9=老陽
# Line values: 6=Old Yin, 7=Young Yang, 8=Young Yin, 9=Old Yang
iching.mget_bookgua_details('789789')

# 指定年月日時起卦 / Divination by specific date and time
iching.datetime_bookgua('年', '月', '日', '時')   # e.g. datetime_bookgua(2024, 8, 15, 14)

# 按現在時間起卦（只有一動爻）/ Current datetime (one changing line only)
iching.current_bookgua()

# 手動排本卦納甲 / Manual Najia layout
iching.decode_gua("787987", "庚寅")

# 完整起卦資訊（返回字典）/ Full divination result (returns dict)
iching.qigua_now()
```

---

## **6. API 說明 API Reference**

| 方法 Method | 參數 Parameters | 說明 Description |
|---|---|---|
| `bookgua_details()` | — | 隨機大衍筮法，顯示完整排盤 / Random stalk divination with full layout |
| `mget_bookgua_details(lines)` | `lines`: 6位字符串如 `'789789'` | 手動輸入六爻值排盤 / Manual line-value input |
| `datetime_bookgua(y, m, d, h)` | 年月日時 (int) | 按指定日期時間起卦 / Divination by specified datetime |
| `current_bookgua()` | — | 按當前時間起卦 / Divination using current time |
| `decode_gua(lines, rizhi)` | 爻值字符串、日柱干支 | 手動排本卦納甲 / Manual Najia layout for given lines and day branch |
| `qigua_now()` | — | 返回完整起卦字典 / Returns full divination result as dict |
| `display_pan(y, m, d, h, minute)` | 年月日時分 (int) | 打印格式化排盤圖 / Print formatted hexagram board |

### 返回結果示例 Example Result

```python
from ichingshifa.ichingshifa import Iching
print(Iching().qigua_now())
# {
#   '日期': '辛丑年戊戌月庚寅日甲申時',
#   '大衍筮法': ['887888', '謙', '謙', {
#       0: '亨，君子有終。',
#       1: '初六：謙謙君子，用涉大川，吉。',
#       ...
#       7: '彖︰謙，亨，天道下濟而光明...'
#   }, ('動爻有【0】根。', '主要看【謙】卦彖辭。', '謙，亨...')],
#   '本卦': {
#       '卦': '謙', '五星': '太白', '世應卦': '五世卦',
#       '納甲': ['丙辰', '丙午', '丙申', '癸丑', '癸亥', '癸酉'],
#       '五行': ['土', '火', '金', '土', '水', '金'],
#       '六親用神': ['父', '官', '兄', '父', '子', '兄'],
#       '六獸': ['虎', '武', '龍', '雀', '陳', '蛇'],
#       ...
#   },
#   '之卦': { ... },
#   '飛神': ''
# }
```

---

## **7. 排盤範例 Display Example**

```python
from ichingshifa.ichingshifa import Iching
print(Iching().display_pan(2023, 5, 27, 16, 0))
```

```
起卦時間︰2023年5月27日16時0分
農曆︰二零二三年四月九日
干支︰癸卯年  丁巳月  乙酉日  甲申時
旬空︰　　　  　　　  午未    午未
月建︰丁巳
日干支長生十二運︰子  丑  寅  卯  辰  巳  午  未  申  酉  戌  亥
　　　　　　　　　病  衰  帝旺  臨冠  冠帶  沐浴  長生  養  胎  絕  墓  死

　　　　　　　夬卦　　　　　　　　　　　　　革卦
六神    伏神        本卦                     伏神      之卦
　武             角 兄丁未土 　▅▅　▅▅           　　　虛 官丁未土 應▅▅　▅▅
　虎             亢 子丁酉金 世▅▅▅▅▅           　　　危 父丁酉金 　▅▅▅▅▅
　蛇             氐 妻丁亥水 　▅▅▅▅▅ 身         　　　室 兄丁亥水 世▅▅▅▅▅
　陳             房 兄甲辰土 　▅▅▅▅▅          妻戊午火  壁 兄己亥水 　▅▅▅▅▅
　雀   父乙巳火    心 官甲寅木 應▅▅▅▅▅ O         　　　奎 官己丑土 　▅▅　▅▅
　龍             尾 妻甲子水 　▅▅▅▅▅           　　　婁 子己卯木 　▅▅▅▅▅

【大衍筮法】
求得【夬之革】，動爻有【1】根。主要看【九二】九二：惕號，莫夜有戎，勿恤。

夬卦
【卦辭】︰揚於王庭，孚號，有厲，告自邑，不利即戎，利有攸往。
【彖】︰夬，決也，剛決柔也。健而說，決而和...
```

---

## **8. 軟件 Application**

### 🌐 網頁排盤系統 Web App — 堅六爻

A Streamlit web application **堅六爻** (Kinliuyao) is available for online divination and hexagram layout:

🔗 [https://iching.streamlitapp.com](https://iching.streamlitapp.com)  
（國內用戶需要翻牆訪問 / Mainland China users may require a VPN）

本地運行 / Run locally:

```bash
streamlit run src/app.py
```

### 📱 手機應用 Mobile App

An Android mobile app of IchingShifa written in **Kivy**:

🔗 [kinshifa-0.2-release.apk](https://github.com/kentang2017/iching_shifa/blob/master/kinshifa-0.2-release.apk)

---

## **9. 微信公眾號 WeChat**

歡迎關注微信公眾號，獲取更多易學資訊與更新通知。  
Follow our WeChat Official Account for I Ching updates and insights.

![WeChat QR](https://raw.githubusercontent.com/kentang2017/kinliuren/refs/heads/master/pic/%E5%9C%96%E7%89%87_20260316084147.jpg)

---

## **10. 授權 License**

本項目採用 [MIT License](LICENSE) 授權。  
This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**🙏 如覺有用，歡迎打賞支持 / If you find this useful, donations are welcome 🙏**

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)

_"易者，變也。隨時變易以從道。"_  
_"Yi means change — adapt with the times to follow the Dao."_

</div>

