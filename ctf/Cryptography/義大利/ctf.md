# CTF 解題紀錄：奪取_義大利 - KPA & VC

## 1. 題目資訊
- **題目名稱**：奪取_義大利 - KPA & VC
- **分類**：Cryptography (密碼學)
- **分數**：50 分
- **核心漏洞**：Vigenère Cipher (維吉尼亞密碼) / Known-Plaintext Attack (已知明文攻擊)

## 2. 題目分析
### 線索探查
1. **標題解析**：KPA 代表 Known-Plaintext Attack (已知明文攻擊)，VC 代表 Vigenère Cipher (維吉尼亞密碼)。
2. **已知明文**：題目 Hint 明確給出 `Lorem ipsum dolor sit amet, consectetur adipiscing elit...`。
3. **密文對比**：附件第一行密文為 `Ecsia zcgnf rpphf tmh rzsm, vcowxquihle...`，其單字長度與標點符號的斷點與前述的 "Lorem ipsum..." 完美對應。

### 漏洞原理
- **已知明文攻擊 (KPA)**：當攻擊者同時掌握部分「明文」與對應的「密文」時，可以透過演算法的逆運算推導出加密「金鑰」。
- **維吉尼亞密碼逆算**：加密公式為 $C = (P + K) \pmod{26}$。由於已知 $C$ 與 $P$，可透過 $K = (C - P) \pmod{26}$ 反推金鑰。

## 3. 解題過程
### 嘗試與排錯
- **加密細節陷阱**：出題者在加密最後的 Flag 時，將外層的 `flag` 與括號內部的字串**分開加密**。這導致維吉尼亞密碼的「金鑰輪替索引」在遇到 `{` 後被重置。若直接將整串 `yzbk{dDb_mG_UnbZxfpyl}` 丟入解密，括號內的明文會因索引錯位而解碼失敗。

### 正確破解
- **第一步：手動/腳本推算金鑰**
  將密文 `Ecsia` 與明文 `Lorem` 對應的字母 ASCII 值相減：
  - `E`(4) - `L`(11) = `t`(19)
  - `c`(2) - `o`(14) = `o`(14)
  - `s`(18) - `r`(17) = `b`(1)
  推導出循環金鑰為 `tobeornottobe`，完美呼應提示中的「名言 (famous sayings)」。

- **第二步：構造 Payload / 撰寫解密腳本**
  針對金鑰重置的特性，撰寫 Python 腳本將標頭與內部內容拆開解密。

```python
def vigenere_decrypt(ciphertext, key):
    """
    標準的維吉尼亞密碼解密函式
    - 僅對英文字母進行解密轉換
    - 保留大小寫與特殊符號（如底線、括號）
    """
    plaintext = ""
    key_idx = 0
    key = key.lower()
    
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('a')
            if char.isupper():
                plaintext += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                plaintext += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            key_idx += 1
        else:
            plaintext += char
    return plaintext

# 透過 KPA 推導出的金鑰
key = "tobeornottobe"

# 將外層標頭與括號內部拆開解密，確保金鑰索引正確對齊
header_plain = vigenere_decrypt("yzbk", key)              # -> flag
inner_plain = vigenere_decrypt("dDb_mG_UnbZxfpyl", key)  # -> kPa_iS_DanGerous

print(f"Final Flag: {header_plain}{{{inner_plain}}}")
```

## 4. 最終結果
- **推導出之金鑰**：`tobeornottobe`
- **Flag**：`flag{kPa_iS_DanGerous}`

---

## 5. 知識點總結
- **核心概念**：維吉尼亞密碼能抵禦單字母頻率分析，但在遭遇「已知明文攻擊 (KPA)」時，其金鑰會原形畢露。此外，實戰中需特別注意加密工具處理非字母字元（如標點符號、括號）時，金鑰索引是否會繼續推進或重置。
- **防禦手段**：
  1. 避免在密文開頭使用可預測的格式或佔位符（如 Lorem ipsum、標準協議標頭）。
  2. 古典多表替換密碼已不具備現代安全性，應全面改用 AES 等現代區塊/串流加密演算法。