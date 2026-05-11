# CTF 解題紀錄：Can you see the flag? (伊朗)

## 1. 題目資訊
- **題目名稱**：Can you see the flag?
- **分類**：Web
- **分數**：6 分
- **關鍵暗示**：題目敘述提到「我傳了 Flag 給你後，把你重定向（Redirected）到了 Hanzo 的家。」

## 2. 題目分析
### 誘餌與煙霧彈
* **HTML 註解**：原始碼中雖然有 ``，但那張圖裡面的貓只是出題者用來惡搞（Troll）的內容，並非真正的 Flag。
* **自動跳轉**：瀏覽器在接收到伺服器的 **HTTP 302** 回應時，會因為 `Location` 標頭的指令，在毫秒內自動跳轉到 `welcome.html`，導致使用者看不見原始回應的內容。

## 3. 解題過程 (WSL2 流程)
利用 `curl` 工具獲取伺服器的原始回應，避免瀏覽器的自動跳轉行為。

### 執行指令
```bash
curl -v http://idsctf.mis.nsysu.edu.tw:9010/
```

### 關鍵輸出解析
在 `curl` 的詳細輸出（Verbose）中，可以看到以下內容：
```http
< HTTP/1.1 302 Found
< Date: Sat, 02 May 2026 17:13:42 GMT
< Server: Apache/2.4.7 (Ubuntu)
< Location: welcome.html
< Content-Length: 22
< Content-Type: text/html
<
flag{THe_fLaG_i5_h3re}
```
伺服器回傳了 **302 Found**，但其 **Response Body**（也就是 `Content-Length: 22` 的部分）存放的正是 Flag 字串。

## 4. 最終答案
- **Flag**：**`flag{THe_fLaG_i5_h3re}`**

---

## 5. 知識點總結
* **HTTP 狀態碼 (301/302)**：這類狀態碼用於重定向。在資安鑑識中，跳轉前的「中間頁面」常被用來隱藏敏感資訊或 Flag。
* **標頭 (Headers) vs 內容 (Body)**：
    * Flag 可能藏在 `Set-Cookie` 或自定義 Header（如 `X-Flag`）。
    * Flag 也可能像本題一樣，藏在跳轉頁面的 Body 裡。
* **curl 的妙用**：`curl -v` (詳細) 或 `curl -I` (僅看標頭) 是 Web CTF 中最重要的偵查工具，能看到瀏覽器隱藏的通訊細節。