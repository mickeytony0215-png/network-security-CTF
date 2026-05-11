# [CTF Write-up] 奪取_土庫曼 - An Evaluation For One's Patience

## 📝 題目資訊
* **類別 (Category):** Forensics (數位鑑識)
* **分數 (Score):** 80
* **提示 (Hint):** "To become a proficient digital investigator, one must cultivate a heightened sense of patience. Endeavor to locate the flag within the accompanying slides, remaining cognizant that even the **minutest character** may hold significant value." (極微小的字元可能具有重要價值)

## 🔍 解題步驟

### 1. 檔案識別 (File Identification)
題目給定了一個沒有副檔名的檔案 `Lorem_555b8b9486dfcb313d638ada3d85e38e`。
首先使用 `file` 指令確認其真實格式：
```bash
file Lorem_555b8b9486dfcb313d638ada3d85e38e
# 輸出結果：Microsoft PowerPoint 2007+
```
確認該檔案為一個 `.pptx` 簡報檔。

### 2. 結構解構與文字提取 (Extraction & Strings Analysis)
由於 `.pptx` 本質上是 ZIP 壓縮檔，直接將其解壓縮以分析底層 XML 結構：
```bash
mkdir ppt_extract
cp Lorem_555b8b9486dfcb313d638ada3d85e38e ppt_extract/Lorem.zip
cd ppt_extract
unzip Lorem.zip
```

直接對解壓縮後的 XML 檔案進行字串提取，發現投影片文字內容被異常切碎成單一字母：
```bash
grep -oP '(?<=<a:t>).*?(?=</a:t>)' ppt/slides/slide*.xml
```
提取出的內容包含：
* `This is nothing important and nothing hide here.` (干擾訊息)
* `Do u no how to spell Mississippi with one “i”?` (干擾訊息)
* `ANSWER https://youtu.be/A81IwlDeV6c?t=198` (表面上的解答連結)

### 3. 尋找「極微小字元」 (Finding the "Minutest Character")
呼應題目的提示，撰寫 Python 腳本解析 XML 中的字體大小 (`sz`) 屬性。在 `slide3.xml` 的解析結果中，發現了一個重大異常：
```text
字體大小: 23.0   | 文字: https://
字體大小: 1.0    | 文字:  
字體大小: 24.0   | 文字: youtu.be
```
在網址字串中間，隱藏了一個**字體大小被設定為 1.0 pt 的空白字元**。在 PowerPoint 中，這通常是用來隱藏超連結的手法。

### 4. 解析關聯檔案 (Extracting Hidden Hyperlinks)
為了找出該 1.0pt 空白字元綁定的超連結，直接檢查 Slide 3 的關聯檔案 (`.rels`)：
```bash
grep -oP 'Target=".*?"' ppt/slides/_rels/slide3.xml.rels
```
得到以下幾個外部連結目標：
1. `https://youtu.be/A81IwlDeV6c?t=198` (投影片上可見的干擾影片)
2. `https://youtu.be/D6YyX1l9FAo` (隱藏連結，影片標題為假 Flag：`flag{Th1s_1S_nOt_f1Ag_Y0U_@Re_10Ok1n9_F0r_!}`)
3. `https://www.youtube.com/watch?v=0HKeCllNkSw&t=198` (隱藏連結 2)

### 5. 繞過陷阱，取得 Flag (Bypassing Rabbit Holes)
出題者佈置了多層 Rabbit Hole 消耗參賽者的耐心。
經查證，第三個隱藏連結 `https://www.youtube.com/watch?v=0HKeCllNkSw&t=198` (The Kids' Guide to the Internet) 為最終正確路徑。

展開該 YouTube 影片的「資訊欄 (Description)」，在落落長的 90 年代網路介紹文末，找到了真正的 Flag：
```text
Oh, you want flag?
FLAG{Tremendous_L1NKs}
```

## 🚩 Flag
`FLAG{Tremendous_L1NKs}`