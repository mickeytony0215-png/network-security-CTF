# CTF Write-up: 奪取_奧地利 - What a small word!

| 分數 | 分類 | 關鍵技術 |
| :--- | :--- | :--- |
| 30 Pts | Steganography | docx Structure Analysis, XML Inspection, Hex Decoding |

## 1. 題目背景與描述
題目提供一個 Word 檔案 `HelloWord_....docx`，並給出提示：「What a small word!」以及「To be at one with the Word」。類別標註為 **Steganography**，暗示 Flag 隱藏在文件的結構或非可見層中。

## 2. 偵查階段
### A. 檔案結構拆解
由於 `.docx` 檔案本質上是一個 **ZIP 壓縮檔**，首先使用 `unzip` 指令將其解壓縮，以觀察內部的 XML 結構：

```bash
unzip HelloWord_3481ebe6dd6e9724ea82affdbcbaf580.docx -d challenge_files
```

### B. 異常檔案鑑定
在解開的目錄結構中，發現一個非常不尋常的路徑與檔名：
- **`word/_rels/IncludePicture.xml`**

在標準的 docx 規範中，`_rels` 資料夾通常僅包含 `.rels` 後綴的關聯定義檔。出現一個自定義名稱的 `.xml` 檔案是極其明顯的隱寫徵兆。

## 3. 漏洞分析與解密
檢查該異常 XML 檔案的內容：
```xml
<?xml version="1.0" encoding="UTF-8"?> 
<Picture> 
    <Raw Content="464C41477B596F752063616E277420736565206D652C206D792074696D65206973206E6F77217D"/> 
</Picture>
```

### 十六進位 (Hex) 徵兆
觀察 `Raw Content` 的值，開頭字元為 `464C4147`。根據 ASCII 編碼表：
- `46` = **F**
- `4C` = **L**
- `41` = **A**
- `47` = **G**

這確認了該字串為 Flag 的 **Hex 編碼** 形式。

## 4. 解決方案
在 Linux 終端機中使用 `xxd` 工具將十六進位字串轉換回純文字：

```bash
echo "464C41477B596F752063616E277420736565206D652C206D792074696D65206973206E6F77217D" | xxd -r -p
```

**🚩 FLAG: `FLAG{You can't see me, my time is now!}`**

## 5. 知識總結
1.  **docx 即是 ZIP**：處理 Office 系列檔案的隱寫題，第一步永遠是解壓縮檢查 XML。
2.  **尋找結構異樣**：注意不符合 OpenXML 標準的檔名或資料夾路徑，出題者常藉此隱藏資料。
3.  **Hex 敏感度**：熟記常見字串（如 `FLAG`, `GIF89`, `PK`）的十六進位開頭，能幫助在大量 XML 原始碼中快速鎖定目標。