# CTF 解題紀錄：奪取_哈薩克 - Revenge of hash

## 1. 題目資訊
- **題目名稱**：奪取_哈薩克 - Revenge of hash
- **分類**：Cryptography (密碼學)
- **分數**：80 分
- **核心漏洞**：SHA-1 雜湊碰撞 (Cryptographic Hash Collision) / SHAttered 攻擊

## 2. 題目分析
### 線索探查
1. **網頁標題與提示**：
   - 標題「Shattered Memories」與「Pathetic Hash」明確暗示了 2017 年 Google 發表的 **SHAttered** 攻擊（人類史上首個 SHA-1 實用碰撞）。
   - 提示提到 "Maybe online crackers will not help you this time"，表示不能單純查表，必須給予伺服器真實的碰撞資料。
2. **防禦機制**：
   - 首頁圖片中的人物台詞 "Not this method, CC!" 加上擦汗動作，暗示後端已封鎖了 PHP 常見的「陣列繞過漏洞 (`is_array()` 檢查)」。

### 漏洞原理
- **雜湊碰撞 (Hash Collision)**：當兩個內容完全不同的檔案，經過雜湊函數運算後，產生了完全相同的雜湊值（例如皆為 `38762cf7f5593...`）。
- 題目後端的核心邏輯為：
  ```php
  if ($obj1 !== $obj2 && sha1($obj1) === sha1($obj2)) {
      echo $flag;
  }
  ```
- **攻擊思路**：取得已知會發生 SHA-1 碰撞的兩份 PDF 檔案（shattered-1.pdf 與 shattered-2.pdf），並將其作為表單參數 `object1` 與 `object2` 送出。

## 3. 解題過程
### 嘗試與排錯
1. **第一次嘗試：16進位字串傳輸**
   - 嘗試傳送代表碰撞區塊的 16 進位轉字串，但因 `application/x-www-form-urlencoded` 的編碼機制，導致二進位控制字元（如 `\x00`）在傳輸時損毀，被伺服器判定為不同 Hash。
2. **第二次嘗試：直接下載官網 PDF (失敗)**
   - 撰寫 Python 爬蟲前往 `shattered.io` 下載原檔。但因缺乏 `User-Agent` 且遇上 Cloudflare 防護，導致下載了 0 bytes 或是 15KB 的驗證網頁，被伺服器以 `Files are identical` 踢退。

### 正確破解
- **構造 Payload / 解密過程**：
  直接從密碼學家 Marc Stevens 的 GitHub 測試資料庫，下載兩份真實的碰撞 PDF 原檔（大小各為 422,435 bytes）。為了避免字元在 HTTP POST 過程中損毀，使用 `requests` 庫的 `files` 參數發送 `multipart/form-data` 請求，將檔案偽裝成普通的 POST 變數送出。

- **解題腳本 (Python)**：
  ```python
  import requests
  import re

  target_url = "[http://idsctf.mis.nsysu.edu.tw:9019/checksum.php](http://idsctf.mis.nsysu.edu.tw:9019/checksum.php)"

  # 1. 從 GitHub Raw (無反爬蟲) 下載真實的 SHA-1 碰撞檔案
  url_1 = "[https://raw.githubusercontent.com/cr-marcstevens/sha1collisiondetection/master/test/shattered-1.pdf](https://raw.githubusercontent.com/cr-marcstevens/sha1collisiondetection/master/test/shattered-1.pdf)"
  url_2 = "[https://raw.githubusercontent.com/cr-marcstevens/sha1collisiondetection/master/test/shattered-2.pdf](https://raw.githubusercontent.com/cr-marcstevens/sha1collisiondetection/master/test/shattered-2.pdf)"

  pdf1 = requests.get(url_1).content
  pdf2 = requests.get(url_2).content

  # 2. 使用 multipart/form-data 發送，避免二進位字元因 URL 編碼而損毀
  multipart_data = {
      'object1': (None, pdf1),
      'object2': (None, pdf2)
  }

  response = requests.post(target_url, files=multipart_data)
  
  if "flag{" in response.text:
      print(re.findall(r'flag\{.*?\}', response.text)[0])
  ```

## 4. 最終結果
- **關鍵輸入**：Marc Stevens 提供的 `shattered-1.pdf` 與 `shattered-2.pdf` 的原始二進位資料。
- **Flag**：`Flag{Sh4ttEr_ShA1!!!}`

---

## 5. 知識點總結
- **核心概念**：SHA-1 已在 2017 年被證實不再安全。在 CTF 中，若題目封鎖了 PHP 的陣列繞過，我們就必須提供真實的密碼學碰撞區塊。
- **實戰技巧**：傳輸含有不可見字元的二進位 payload 時，絕不能使用標準的字串拼接或 URL Encoding，必須改用 `multipart/form-data` 確保資料的完整性 (Data Integrity)。
- **防禦手段**：
  全面棄用 SHA-1 與 MD5，升級至 **SHA-256** 或更高的雜湊演算法來確保資料完整性與數位簽章的安全性。