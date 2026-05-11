# CTF Writeup: 奪取_查德 - The Sovereign

## 📌 題目資訊
* **類別:** Binary / Reverse Engineering (Windows)
* **目標檔案:** `my_system_ce6768dc4f0765a00cdfc8afc7e64fe9.exe`
* **Flag:** `Flag{I_aM_tH3_sYstem}`
* **核心概念:** Windows 權限提升、SID (Security Identifiers) 檢查、二進位修補 (Patching)。

## 🔍 1. 初始勘查 (Static Analysis)

透過 `radare2` 的 `iz` 指令進行字串分析，發現以下關鍵線索：
* **`S-1-5-18`**: 這是 Windows 中 **LocalSystem** 帳戶的安全性識別碼 (SID)。
* **`Access denied.`**: 當執行身分不符時，程式會跳出的警告訊息。
* **`OKKlYguFuMuQWsY`**: 一段加密過的密文字串，長度與 Flag 相似。

## ⚙️ 2. 核心邏輯逆向 (Reverse Engineering)

透過追蹤 `S-1-5-18` 字串的引用位址，我們定位到了關鍵的權限檢查函數 `fcn.1400012ca`。

### 邏輯流程分析：
1. **取得 SID**: 程式會呼叫 Windows API 獲取當前執行使用者的 SID 並轉換為字串。
2. **字串比較**:
   ```assembly
   0x1400012ca   lea rdx, str.S_1_5_18  ; 載入 SYSTEM SID
   0x1400012d1   call strcmp             ; 與目前使用者比較
   ```
3. **判定權限**:
   ```assembly
   0x1400012fb   test ebx, ebx           ; 檢查 strcmp 結果 (0 代表相等)
   0x1400012fd   0f94c3 (sete bl)       ; 若相等則將 bl 設為 1 (True)
   ```
4. **分支跳轉**: 呼叫者 (Caller) 會根據回傳的 `bl` 值決定是要解密並顯示 Flag，還是跳出 `Access denied.`。

## 🛠️ 3. 漏洞利用與修補 (Exploitation & Patching)

由於本機測試環境中，一般使用者 (或 Administrator) 的 SID 與 `S-1-5-18` 不符，導致程式無法執行 Flag 分支。我們採用了 **二進位修補 (Binary Patching)** 的方式直接繞過檢查。

### 修補操作：
我們將 `0x1400012fd` 的 `sete bl` 指令替換為強制賦值指令，讓程式誤以為權限檢查永遠通過。

* **原始指令**: `0F 94 C3` (sete bl)
* **修改後指令**: `B3 01 90` (mov bl, 1; nop)

**r2 操作指令：**
```bash
r2 -w my_system_...exe
s 0x1400012fd
wx b30190
q
```

## 🚩 4. 最終結果
修改完成後，直接執行程式（或透過 Wine），程式跳過權限比對邏輯，直接進入 Flag 顯示區塊。

**解密結果顯示於 MessageBox 視窗：**
`Flag{I_aM_tH3_sYstem}`