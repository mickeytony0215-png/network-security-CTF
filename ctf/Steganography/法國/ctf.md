# CTF Write-up: 奪取_法國 - People in lab?

| 分數 | 分類 | 關鍵技術 |
| :--- | :--- | :--- |
| 20 Pts | Steganography | Metadata Analysis (Exif/XMP), Base64 Decoding |

## 1. 題目背景與描述
題目提供一張 JPEG 圖片 `People_in_LAB_....jpg`，詢問：「Is there any hidden message?」。背景圖案與名稱暗示實驗室場景，需尋找隱藏其中的訊息。

## 2. 偵查階段
### A. 檔案鑑定
首先使用 `file` 指令確認檔案類型，結果為標準 JPEG 格式，包含 Exif 資訊。

### B. 中繼資料分析 (Metadata)
使用 `exiftool` 提取圖片的所有 Metadata。這通常是隱碼題的第一個檢查點，因為出題者常將 Flag 藏在註解、作者或版權欄位中。



## 3. 漏洞分析與解密
在 `exiftool` 的輸出結果中，發現多個欄位的內容疑似為 **Base64** 編碼：
- **Copyright**: `ZXhpZnRvb2wgeG1wIGlzIGdvb2Q=` (解碼為 "exiftool xmp is good")
- **Creator**: `RkxBR3tMQUJfISRfNDF3QHk1X0VtcHR5fQ==`

### Base64 徵兆
字串 `RkxBR3` 是 `FLAG` 經過 Base64 編碼後的固定開頭，這是一個極其明顯的特徵。

## 4. 解決方案
在 Linux 終端機中使用 `base64` 工具進行解碼：

```bash
echo "RkxBR3tMQUJfISRfNDF3QHk1X0VtcHR5fQ==" | base64 -d
```

執行後成功還原出明文字串。

**🚩 FLAG: `FLAG{LAB_!$_41w@y5_Empty}`**

## 5. 知識總結
1.  **Exiftool 是隱碼必備**：許多初階隱碼題會將資訊藏在 `Comment`、`Artist` 或 XMP 資料區段中。
2.  **Base64 敏感度**：在 CTF 中看到結尾為 `==` 或開頭為 `RkxBR` 的字串，應第一時間直覺反應為 Base64。
3.  **不要過度分析**：雖然 `binwalk` 在進階題很有用，但 20 分的題目通常只需要基礎的工具組合（`strings`, `exiftool`, `stegsolve`）就能解決。