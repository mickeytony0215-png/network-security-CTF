# CTF 解題紀錄：Do a robo rotation

## 1. 題目資訊
- **題目名稱**：奪取_波蘭 - Do a robo rotation
- **分類**：Cryptography (密碼學)
- **分數**：6 分
- **題目檔案**：`secret_1159561eb85b28ed00e90ac7da2dca0a`

## 2. 題目分析
### 線索探查
1. **題目名稱**：`Do a robo rotation`
   - 其中 "Rotation" 指的是位移加密（Caesar Cipher）。
   - "robo" 與 "ROT" 諧音。
2. **題目提示**：
   > "Even those of antiquity possess the means to decipher it, harnessing the **force of thirteen**."
   - "force of thirteen" 明確指出位移量為 **13**。
3. **結論**：
   - 判斷該加密法為 **ROT13**（凱撒密碼的一種，將字母向後移 13 位，因英文字母共 26 個，所以加密與解密方式相同）。

## 3. 解題過程
在 WSL2 (Ubuntu 22.04) 環境下，利用 `cat` 讀取檔案內容，並透過 `tr` 指令進行字母位移處理。

### 執行指令
```bash
# 使用 tr 工具進行 A-Z 與 a-z 的 13 位轉換
cat secret_1159561eb85b28ed00e90ac7da2dca0a | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

### 終端機輸出
```text
flag{I_hAtE_roTteN_ApPlE}%
```
*(註：後方的 `%` 為 Zsh 提示符號，代表檔案末尾無換行符，非 Flag 內容)*

## 4. 最終答案
- **Flag**：`flag{I_hAtE_roTteN_ApPlE}`

## 5. 知識點總結
- **ROT13**：一種簡單的替換式密碼，常出現於入門級 CTF。
- **Linux 指令技巧**：
    - `cat`：輸出檔案內容。
    - `tr` (translate)：替換字元，常用於處理簡單的位移加密。
    - `|` (pipe)：將前一個指令的輸出作為後一個指令的輸入。

---