# CTF 解題紀錄：Unreadable Functions (印度)

## 1. 題目資訊
- **題目名稱**：奪取_印度 - Unreadable Functions
- **分類**：Web / Reverse Engineering
- **分數**：10 分
- **核心概念**：JavaScript 字串混淆 (String Obfuscation)、十六進位編碼 (Hex Encoding)

## 2. 題目分析
### 原始碼觀察
網頁原始碼中使用了一段高度混淆的 JavaScript。這段代碼並非無法讀取，而是透過以下手段增加分析難度：
1. **Hex 編碼字串**：將所有字串以 `\xHH` 格式呈現（例如 `\x6b\x65\x72` 代表 `ker`）。
2. **字串池 (String Pool)**：將所有關鍵字、選擇器及邏輯碎片存放在陣列 `_0x6e73797375` 中，後續僅透過索引值調用。
3. **無意義變數名**：使用 `_0x....` 這種不具語義的名稱來阻礙邏輯追蹤。

## 3. 解題過程 (Python 逆向腳本)
為了自動化還原密碼，我們編寫了 Python 腳本來模擬原始代碼的邏輯。

### 逆向邏輯還原
1. **還原字串池**：
    - `_0x6e73797375[5]` = `ker`
    - `_0x6e73797375[12]` = `bla`
    - `_0x6e73797375[2]` = `ha`
2. **重組拼接公式**：
    - 變數 `_0x737461726a_2` = `bla` + `bla` + `bla`
    - 最終密碼 = `ker` + `ker` + `_0x737461726a_2` + (`ha` * 4)

### 執行 Python 腳本
```python
# 核心邏輯
ker = "ker"
bla = "bla"
ha = "ha"

var2 = bla + bla + bla
password = ker + ker + var2 + (ha * 4)

print(f"Password: {password}") 
# 輸出結果：kerkerblablablahahahaha
```

## 4. 最終答案
- **密碼**：`kerkerblablablahahahaha`
- **Flag**：**`FLAG{JavaScript_Function_Is_So0o0o0o0_Secure}`**

---

## 5. 知識點總結
* **Security by Obscurity (隱晦式安全)**：這是一個反面教材。僅靠弄亂代碼（Obfuscation）來保護系統是無效的，因為所有邏輯最終都必須在客戶端還原才能執行。
* **反混淆技巧**：
    * **Static Analysis (靜態分析)**：如本題，手動或用腳本還原字串陣列。
    * **Dynamic Analysis (動態分析)**：在瀏覽器 Console 直接輸入變數名（例如輸入 `_0x6e73797375`）即可直接看到解碼後的陣列內容。
* **十六進位轉 ASCII**：了解 `\x` 後接兩個十六進位數值的編碼方式，是閱讀混淆代碼的基本功。