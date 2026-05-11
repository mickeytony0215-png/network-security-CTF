### CTF 解題紀錄：奪取_瑞典 - ヽ(#`Д´)ﾉ

## 1. 題目資訊
- **題目名稱**：奪取_瑞典 - ヽ(#`Д´)ﾉ
- **分類**：Cryptography (密碼學)
- **分數**：20 分
- **核心漏洞**：AAencode 混淆 (Javascript Obfuscation)

## 2. 題目分析
### 線索探查
1. **編碼識別**：附件 `emoticon.txt` 開頭為 `ﾟωﾟﾉ= /｀ｍ´）ﾉ`，這是典型的 **AAencode** 特徵。
2. **傳輸障礙**：下載時伺服器憑證過期，需透過 `--no-check-certificate` 繞過。

### 漏洞原理
- **AAencode** 是一種將 JavaScript 代碼轉換為日系表情符號的混淆技術。它將代碼隱藏在變數映射中，並在執行期動態還原。如果解碼後的內容並非有效的 JS 指令（例如直接是一串 Flag 字串），執行環境會報錯，但錯誤訊息往往會洩漏解碼後的內容。

## 3. 解題過程
### 指令紀錄
- **下載並執行**：
  ```bash
  # 下載檔案
  wget --no-check-certificate https://idsctf.mis.nsysu.edu.tw/data/attachments/emoticon_d3819b29dc94a53022f46f0276e06d91.txt -O emoticon.txt

  # 嘗試使用 Node.js 執行
  node -e "$(cat emoticon.txt)"
  ```
- **報錯內容分析**：
  Node.js 執行時回傳了：
  ```text
  flag{emoticon_strike_is_fun!!}
      ^
  SyntaxError: Unexpected token '{'
  ```
  這顯示解碼後的內容為 `flag{emoticon_strike_is_fun!!}`，因為非標準 JS 語法導致解析失敗。

## 4. 最終結果
- **Flag**：`flag{emoticon_strike_is_fun!!}`

---

## 5. 知識點總結
- **AAencode 的本質**：它只是 JavaScript 的一種混淆表現形式。
- **錯誤訊息洩漏**：在 CTF 中，有時候「執行失敗」的錯誤訊息（Error Stack Trace）比「執行成功」更有用。
- **環境差異**：如果在瀏覽器 Console 執行，可能會彈出一個錯誤或直接印出該字串，端看混淆器最後是用什麼方式去呼叫這段解碼後的內容。
