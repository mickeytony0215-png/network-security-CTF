# CTF 解題紀錄：Mathematics Is So Good (日本)

## 1. 題目資訊
- **題目名稱**：奪取_日本 - Mathematics Is So Good
- **分類**：Web / JavaScript Reverse
- **分數**：8 分
- **核心漏洞**：Client-side Authentication (前端驗證漏洞)

## 2. 題目分析
### 原始碼觀察
網頁原始碼中包含一段 jQuery 腳本，負責處理登入邏輯。該腳本並未將帳號密碼傳送至後端驗證，而是直接在瀏覽器端進行 ASCII 編碼計算比對。

### 驗證邏輯
1. **帳號 (u)**：必須為 `administrator`。
2. **比對數組 (k)**：`[176, 214, 205, 246, 264, 255, 227, 237, 242, 244, 265, 270, 283]`。
3. **公式**：
   $$u.charCodeAt(i) + p.charCodeAt(i) + (i \times 10) = k[i]$$
4. **目標**：已知 $u$ 與 $k$，反求密碼 $p$。



## 3. 解題過程 (WSL2 / Python)
利用 Python 遍歷 `administrator` 的每個字元，並根據公式反推出密碼的 ASCII 代碼，最後轉回字元。

### 執行腳本
```python
u = "administrator"
k = [176, 214, 205, 246, 264, 255, 227, 237, 242, 244, 265, 270, 283]

password = "".join([chr(k[i] - ord(u[i]) - (i * 10)) for i in range(len(u))])
print(f"Password: {password}") 
# Output: OhLord4309111
```

將得到的密碼 `OhLord4309111` 輸入登入框，網頁成功跳轉並顯示 Flag。

## 4. 最終答案
- **Flag**：**`FLAG{It_Seems_Like_U_Are_Good_At_Math_huh?}`**

## 5. 知識點總結
- **Client-side Logic**：任何在前端運行的驗證代碼對攻擊者來說都是透明的，極易被逆向破解。
- **ASCII 與 Unicode**：熟練掌握 `charCodeAt` (JS) 或 `ord/chr` (Python) 的轉換是解密碼學與網頁逆向題的基本功。
- **Redirects**：觀察代碼中的 `document.location` 行為，可以發現 Flag 往往隱藏在跳轉後的參數或頁面內容中。