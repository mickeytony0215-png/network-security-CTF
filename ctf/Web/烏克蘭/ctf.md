# CTF 解題紀錄：Hash Is Perfect (烏克蘭)

## 1. 題目資訊
- **題目名稱**：Hash Is Perfect
- **分類**：Web / Cryptography
- **目標 Hash**：`b89356ff6151527e89c4f3e3d30c8e6586c63962` (SHA1)

## 2. 漏洞分析
該題目將身分驗證邏輯放置在前端 JavaScript 中，並硬編碼了目標 SHA1 雜湊值。由於雜湊函數對於固定輸入會產生固定輸出，且 SHA1 對於簡單短字串的保護能力極低，攻擊者可透過暴力破解還原明文。

## 3. 解題過程 (Python 暴力破解)
### 破解思路
1. **定義範圍**：設定搜尋空間為小寫英文字母。
2. **迭代嘗試**：使用 Python `itertools` 模組依序生成 1 至 6 位長度的所有可能字串。
3. **雜湊比對**：將每個字串透過 `hashlib.sha1` 運算後，與目標值進行比對。

### 關鍵程式碼
```python
for guess in itertools.product(string.ascii_lowercase, repeat=6):
    if hashlib.sha1("".join(guess).encode()).hexdigest() == target:
        print("Success")
```

## 4. 最終答案
- **解出密碼**：`adminz`
- **Flag**：`FLAG{Shal_Hash_Is_Very_Secure}`

## 5. 知識點總結
- **Brute-force (暴力破解)**：當搜尋空間（Search Space）有限時，這是一種最保底的解題手段。
- **Hash 弱點**：SHA1 在現代資安規範中已不建議用於密碼存儲。
- **前端安全**：永遠不要將任何驗證用的「標準答案」暴露在前端腳本中，不論它是否經過雜湊處理。