# CTF 解題紀錄：Ordinary PDF (阿爾及利亞)

## 1. 題目資訊
- **題目名稱**：Ordinary PDF
- **分類**：Forensics (數位鑑識)
- **分數**：10 分
- **檔案**：`secret_af8b3c4fb08939e4126989ba0c5c2ff4.pdf`

## 2. 題目分析
題目提供一個看似空白的 PDF 檔案。在 Forensics 類別中，這通常代表數據被隱藏在 PDF 物件流（Object Streams）中，或者是以不可見的方式（如 JavaScript）嵌入。

## 3. 解題過程 (WSL2 流程)

### 第一階段：檔案結構還原
由於 PDF 的數據流通常經過壓縮（FlateDecode），直接搜尋會失敗。使用 `qpdf` 工具將其解壓為原始格式：
```bash
qpdf --qdf --object-streams=disable secret_af8b3c4fb08939e4126989ba0c5c2ff4.pdf decompressed.pdf
```

### 第二階段：內容分析與過濾
對解壓後的檔案進行字串提取，發現其中包含 JavaScript 腳本區塊：
```bash
strings decompressed.pdf | grep -C 5 "alert"
```
- **輸出發現**：
  ```javascript
  app.alert("Can you find the flag?",3);
  //You are almost get it!
  ////RkxBR3tQREZfamF2YXNjcmlwdF9lbmMwZGVkfQo=
  ```
- 腳本註解中包含一段明顯的 Base64 字串。

### 第三階段：最終解碼
將提取出的 Base64 字串進行解碼：
```bash
echo "RkxBR3tQREZfamF2YXNjcmlwdF9lbmMwZGVkfQo=" | base64 -d
```

## 4. 最終答案
- **Flag**：**`FLAG{PDF_javascript_enc0ded}`**

## 5. 知識點總結
- **PDF 結構分析**：PDF 物件可能經過壓縮，直接使用 `strings` 不一定能抓到所有內容。
- **PDF JavaScript**：PDF 支援嵌入 JS 腳本，這是常見的隱藏資訊位置。
- **qpdf**：強大的 PDF 處理工具，`--qdf` 模式是進行 PDF 手動鑑識的必備功能。