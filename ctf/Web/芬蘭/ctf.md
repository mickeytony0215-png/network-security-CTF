# CTF 解題紀錄：Secure Login (芬蘭)

## 1. 題目資訊
- **題目名稱**：奪取_芬蘭 - Secure Login
- **分類**：Web / JavaScript Obfuscation
- **分數**：6 分
- **核心漏洞**：Client-side Authentication (前端驗證漏洞)

## 2. 題目分析
### 原始碼觀察
網頁提供一個簡單的登入介面。查看原始碼後發現，登入按鈕的點擊事件（`click`）會觸發一段內嵌的 JavaScript 進行驗證，而非傳送到伺服器後端。

### 驗證邏輯
```javascript
if(u == "admin" && p == String.fromCharCode(74,97,118,97,83,99,114,105,112,116,73,115,83,101,99,117,114,101))
```
* **帳號 (u)**：必須為 `admin`。
* **密碼 (p)**：與 `String.fromCharCode()` 函式轉換出的字串進行比對。

## 3. 解題步驟
### 密碼還原
利用 Python 或瀏覽器開發者工具（Console）將這串 ASCII 代碼轉換回可讀文字。

**WSL2 / Python 指令：**
```bash
python3 -c "print(''.join([chr(x) for x in [74,97,118,97,83,99,114,105,112,116,73,115,83,101,99,117,114,101]]))"
```
- **解碼結果**：`JavaScriptIsSecure`

### 取得 Flag
1.  在 Username 欄位輸入 `admin`。
2.  在 Password 欄位輸入 `JavaScriptIsSecure`。
3.  按下 Login 後，網頁跳轉並顯示 Flag。

## 4. 最終答案
- **Flag**：**`FLAG{Java_5cript_Is_5o_5ecure}`**

---

## 5. 知識點總結
* **不要信任客戶端**：任何在客戶端（瀏覽器）執行的程式碼都是可以被使用者讀取、修改與繞過的。
* **ASCII 轉換**：`String.fromCharCode` (JS) 與 `chr()` (Python) 是處理簡單混淆字串時最常用的工具。
* **弱點識別**：看到網頁登入卻沒有網路請求（Network Request）到後端時，通常代表驗證邏輯藏在前端的 `.js` 檔案或 `<script>` 標籤中。