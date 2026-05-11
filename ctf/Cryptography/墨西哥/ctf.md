# CTF 解題紀錄：Common Encoding (墨西哥)

## 1. 題目資訊
- **題目名稱**：奪取_墨西哥 - Common Encoding
- **分類**：Cryptography (密碼學) / Forensics
- **分數**：8 分
- **原始檔案**：`WgZjB1MVIRNu_f020f9b605e8b8cde6b656f043f32f86`

## 2. 題目分析
題目提示「編碼無法保證機密性」，並提供了一個看似字串但實際上是二進位數據的檔案。這代表 Flag 被隱藏在層層的編碼與壓縮封裝之中。

## 3. 解題過程 (WSL2 流程)

### 第一階段：檔案識別與解壓縮
1.  **檔案檢查**：使用 `file` 指令確認檔案類型。
    ```bash
    file WgZjB1MVIRNu_f020f9b605e8b8cde6b656f043f32f86
    ```
    - 輸出：`gzip compressed data`
2.  **解壓縮**：將 Gzip 檔案解壓。
    ```bash
    gunzip -c WgZjB1MVIRNu_f020f9b605e8b8cde6b656f043f32f86 > out.bin
    ```
3.  **二次檢查**：檢查解壓後的檔案。
    ```bash
    file out.bin
    ```
    - 輸出：`POSIX tar archive`

### 第二階段：歸檔提取
1.  **提取 Tar 內容**：
    ```bash
    tar -xvf out.bin
    ```
    - 輸出：提取出一個名為 `YmFzZTY0Cg==` 的檔案。

### 第三階段：檔名與內容解碼
1.  **解析隱藏檔名**：
    ```bash
    echo "YmFzZTY0Cg==" | base64 -d
    # 得到：base64
    ```
    - 這暗示了該檔案的內容處理方式。
2.  **最終解碼**：讀取檔案內容並進行 Base64 解碼。
    ```bash
    cat "YmFzZTY0Cg==" | base64 -d
    ```
    - 輸出：`FLAG{Base64_is_very_common}`

## 4. 最終答案
- **Flag**：`FLAG{Base64_is_very_common}`

## 5. 知識點總結
- **File Integrity**：檔案的副檔名不代表其真實格式，使用 `file` 指令是鑑識的第一步。
- **Nested Encapsulation**：CTF 題目常將多種技術（Gzip -> Tar -> Base64）嵌套使用，需要耐心逐層剝離。
- **Base64 識別**：檔名結尾的 `==` 是 Base64 填充符（Padding）的典型特徵。
