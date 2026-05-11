# CTF 解題紀錄：奪取_烏茲別克 - Revenge of encoding

## 1. 題目資訊
- **題目名稱**：奪取_烏茲別克 - Revenge of encoding
- **分類**：Cryptography (密碼學)
- **分數**：80 分
- **核心漏洞**：多層混合 Base 編碼 (Base32, Base45, Base64, Base85) / 腳本自動化解碼

## 2. 題目分析
### 線索探查
1. **題目提示**：
   - "Tired of easy base64 quizzes?"
   - "CyberChef cannot help you much this time."
   - "follow the key~"
   以上暗示了這不是單純的單一編碼，且手工使用線上工具（如 CyberChef）會非常費時或無法實現。
2. **檔案結構**：
   解開 `revenger.zip` 後，獲得兩個檔案：
   - `encoded.txt`：充滿特殊符號（包含 `|`, `~`, `^` 等）的超長亂碼字串，具備 Base85/Ascii85 的特徵。
   - `key.txt`：內容為 `@UU@U   U@UU  -UU@  -@@-  U@-@U@@@@-UUUUU-UU@U--U-`，總長度 50 個字元。

### 漏洞原理
- **ASCII 映射加密法 (密碼學彩蛋)**：
  觀察 `key.txt` 僅包含 4 種字元：` ` (空白)、`-`、`@`、`U`。將這四個字元轉換為 ASCII 十進位數值後，會發現驚人的巧合：
  - ` ` (空白) = **32** -> 對應 **Base32**
  - `-` (減號) = **45** -> 對應 **Base45**
  - `@` (小老鼠) = **64** -> 對應 **Base64**
  - `U` (大寫 U) = **85** -> 對應 **Base85 / Ascii85**
  這意味著出題者將明文依照這 50 個字元的順序，像包洋蔥一樣進行了 50 層的 Base 系列編碼。

## 3. 解題過程
### 嘗試與排錯
1. **手動解碼失敗**：因層數高達 50 層，手動貼上解碼工具不切實際。
2. **腳本解碼中斷**：初次撰寫 Python 腳本時，遇到印出半成品亂碼的狀況。經分析，發現是因 Base64/Base32 在多次編解碼過程中遺失了結尾的 Padding (`=`)，導致 Python 解碼庫報錯中斷。

### 正確破解
- **終極化解碼腳本**：
  撰寫自動化 Python 腳本，加入 `fix_padding` 函數自動補齊遺失的等號，並按照 `key.txt` 的正向順序（由左至右）依序剝離 50 層編碼。

```python
import base64
import base45 # 需 pip install base45

# 自動修補缺失的等號 padding
def fix_padding(b):
    return b + b'=' * (-len(b) % 4)

with open('key.txt', 'r') as f:
    key = f.read().rstrip('\r\n') 

with open('encoded.txt', 'r') as f:
    data = f.read().strip().encode()

# 依照 key 的順序進行解碼
for i, char in enumerate(key):
    if char == ' ':
        data = base64.b32decode(fix_padding(data))
    elif char == '-':
        data = base45.b45decode(data)
    elif char == '@':
        data = base64.b64decode(fix_padding(data))
    elif char == 'U':
        try:
            data = base64.b85decode(data)
        except:
            data = base64.a85decode(data)

print(f"Flag: {data.decode('utf-8')}")
```

## 4. 最終結果
- **執行輸出**：`🎉 成功跑完 50 層解碼！`
- **Flag**：`Flag{sT1ll_E45Y_rIghT}`

---

## 5. 知識點總結
- **編碼變體識別**：
  - Base64：`A-Z`, `a-z`, `0-9`, `+`, `/`，結尾常有 `=`。
  - Base32：僅包含大寫字母 `A-Z` 與數字 `2-7`。
  - Base45：常用於 QR Code（如歐盟疫苗護照），包含字母數字及少量符號。
  - Base85/Ascii85：字元集更廣，常出現 `!`, `~`, `<~`, `~>` 等特殊符號，經常用於 PDF 壓縮格式中。
- **實戰技巧**：遇到 CTF 提示 "CyberChef cannot help" 時，通常意味著巨量的重複操作（如本題的 50 層洋蔥）或自定義字母表，必須具備自行撰寫 Python 腳本處理邊界條件（如 Padding）的能力。