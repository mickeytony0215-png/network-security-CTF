# CTF 解題紀錄：Flag in the deep ocean (冰島)

## 1. 題目資訊
* **題目名稱**：奪取_冰島 - Flag in the deep ocean
* **分類**：MISC (雜項)
* **分數**：8 分
* **題目檔案**：`HbI4YGg3nKIAc_dc88573c5b0fe8f9fdba1ddb33b79302`

## 2. 題目分析
### 線索探查
1. **題目描述**：提到 "vast expanse of textual waves"（廣大的文字波浪），暗示 Flag 淹沒在大量的文字數據中。
2. **檔案觀察**：使用 `cat` 查看檔案時，發現內容由大量的大寫、小寫字母及數字組成（例如 `c2VyLmRlc2t0...`），這是典型的 **Base64** 編碼特徵。
3. **推論**：Flag 被 Base64 編碼後隱藏在同樣經過編碼的系統檔案列表（或亂碼）中。

## 3. 解題過程 (WSL2 指令)
由於檔案過大，無法透過肉眼搜尋，因此使用管道（Pipe）結合解碼與過濾工具。

### 執行指令
```bash
cat HbI4YGg3nKIAc_dc88573c5b0fe8f9fdba1ddb33b79302 | base64 -d | grep -i "flag"
```

### 指令邏輯解釋
* `cat`：讀取原始檔案內容。
* `base64 -d`：將讀取到的內容進行 Base64 解碼。
* `grep -i "flag"`：從解碼後的文字中，不分大小寫搜尋包含 "flag" 的字串。

### 終端機輸出
```text
FLAG{QAQ_Y0U_FOUND_me}
```

## 4. 最終答案
* **Flag**：**`FLAG{QAQ_Y0U_FOUND_me}`**

---

## 5. 知識點總結
* **Base64 識別**：當看到一串字元包含 `A-Z`, `a-z`, `0-9` 且結尾偶爾出現 `=` 時，優先考慮 Base64。
* **Linux 組合技**：學會使用 `|` (Pipe) 將不同的處理工具（如解碼、搜尋）串接在一起，是處理大數據量 CTF 題目的核心技巧。
* **grep 搜尋**：在不確定 Flag 格式時，使用 `-i` 忽略大小寫可以避免遺漏。
