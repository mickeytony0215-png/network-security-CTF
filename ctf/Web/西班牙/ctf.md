# CTF Write-up: 奪取_西班牙 - True Encryption

| 分數 | 分類 | 關鍵技術 |
| :--- | :--- | :--- |
| 20 Pts | Web / Crypto | AES-128-CBC、SHA-256、UTF-8 字串編碼差異 |

## 1. 題目背景與描述
網頁模擬一個具有加密保護的登入頁面，宣稱「沒有 Key 絕對無法破解」。附件提供 `index.html`，內部含有加密邏輯的 JavaScript 程式碼。

## 2. 漏洞分析
### A. 前端金鑰硬編碼 (Hardcoded Key Seed)
在 JavaScript 中，解密金鑰並非動態生成或從後端取得，而是由一段固定的位元組字串透過 SHA-256 哈希後產生：
- **Seed**: `\x93\x39\x02\x49\x83\x02\x82\xf3\x23\xf8\xd3\x13\x37`
- **Key**: 取 SHA-256 結果的前 32 個 Hex 字元 (128 bit)。
- **IV**: 取 SHA-256 結果的後 32 個 Hex 字元 (128 bit)。

### B. 編碼陷阱 (Encoding Inconsistency)
JavaScript 的 `CryptoJS` 在處理字串時，會預設將其視為 **Unicode** 並轉為 **UTF-8** 編碼進行運算。例如 `\x93` 在 UTF-8 中會變為 `0xc2 0x93`。若在 Python 中直接以原始位元組 (`bytes`) 運算，將導致金鑰完全錯誤。

### C. 驗證機制缺陷
原始碼中的 `if(!CryptoJS.AES.encrypt(...) == "...")` 存在語法優先級錯誤（`!` 會先作用於物件），導致前端驗證恆真。然而，真正的 Flag 需透過正確密碼作為 URL 參數 (`?key=p`) 才能從伺服器端獲取。

## 3. 解題過程
使用 Python 撰寫逆向腳本，精準還原 JavaScript 的加密流程並解密密文 `ob1xQz5ms9hRkPTx+ZHbVg==`。

### 核心解密腳本
```python
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 1. 模擬 JS 的 UTF-8 編碼轉換
seed_str = "\x93\x39\x02\x49\x83\x02\x82\xf3\x23\xf8\xd3\x13\x37"
k_hex = hashlib.sha256(seed_str.encode('utf-8')).hexdigest()

# 2. 提取 AES-128-CBC 參數
key = bytes.fromhex(k_hex[0:32])
iv = bytes.fromhex(k_hex[32:64])

# 3. 解密密文
ciphertext = base64.b64decode("ob1xQz5ms9hRkPTx+ZHbVg==")
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

print(f"解出的密碼: {plaintext.decode('utf-8')}")
```

## 4. 最終奪取 Flag
1.  執行腳本獲得密碼：**`PassW0RD!289%!*`**。
2.  構造跳轉後的 URL 或手動填入表單：`index.php?key=PassW0RD!289%!*`。
3.  頁面跳轉後，成功獲取 Flag。

**🚩 FLAG: `FLAG{SOOOOOO_Many_JavaScript_Crpt0_To0ls}`**

---

## 5. 知識總結與反思
* **不要信任前端加密**：加密邏輯若完全放在前端，其安全性等同於明文傳輸。
* **跨語言開發的編碼一致性**：處理加密通訊時，必須嚴格對齊不同語言（如 Python vs JS）對字串與位元組轉換的預設行為。
* **隱晦式安全 (Security by Obscurity)**：僅靠混淆加密邏輯無法抵抗具備逆向工程能力的攻擊者。