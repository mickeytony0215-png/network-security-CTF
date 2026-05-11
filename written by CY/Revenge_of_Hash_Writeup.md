# 奪取_哈薩克 — Revenge of hash (Cryptography, 80pt)

## 題目

```
Hmm...
Maybe online crackers will not help you this time. LOL
Your hope is now completely shattered.

BY 苦碩JJ青衫濕
```

附 `[Link 1]` → `http://idsctf.mis.nsysu.edu.tw:9019/`

題目頁面：

- 標題列：`Pathetic Hash`
- 大標：`Shattered Memories`
- 一個 `<form method="POST" action="checksum.php">`，兩個欄位 `object1`、`object2`，按 `Go!` 送出

---

## Flag

```
Flag{Sh4ttEr_ShA1!!!}
```

---

## 為什麼一看到題目就鎖定 SHAttered

CTF 題目的文字幾乎沒有廢話，每個字都是 hint。把這四個訊號疊起來看，方向其實已經被釘死：

| 訊號 | 解讀 |
|---|---|
| `Maybe online crackers will not help` | 否決「拿去 crackstation / hashes.com 查表」這條路。也就是說，這題不是「給你 hash，反推原文」 |
| `Your hope is now completely **shattered**` | "shattered" 不只是修辭。Google 2017 年公布的 SHA-1 第一筆碰撞攻擊，網站名稱就叫 **shattered.io**，論文標題就是 *The first collision for full SHA-1* |
| 頁面標題 `Pathetic Hash` + `Shattered Memories` | "Pathetic" 形容 SHA-1（早就被宣告不安全），"Shattered Memories" 再次點名 |
| 題目名 *Revenge of hash* | 「復仇版」暗示前一題（IDSCTF 的 hash 題）是普通可查表的弱 hash；這題是把它升級，所以不能再用查表方式解 |

四個訊號同時指向同一件事：**這題不是要你反推原文，而是要你交出兩個不同的輸入，但 hash 值相同 — 也就是 hash collision**。而且演算法幾乎可以斷定是 **SHA-1**。

到這一步還沒碰電腦，已經有了完整假設。接下來不是去亂試，而是去**驗證假設**。

---

## 為什麼要先 probe server，而不是直接丟 SHAttered PDF

新手常見錯誤：看到題目像 SHAttered，馬上把 shattered.io 兩個 PDF 拖進表單按送出。這樣做的問題：

1. 不知道 server 比較邏輯 — 是 `hash(a) == hash(b) AND a != b`？還是只要 hash 相同就好？還是字串比對？
2. 不知道演算法 — 是 SHA-1 還是 MD5？兩者所需的 collision pair 完全不同
3. 不知道輸入是當 raw bytes 還是當 hex 字串處理
4. 失敗時不知道是「collision 不對」還是「我用錯方法上傳」

所以正確順序是：**先用低成本輸入打探伺服器**，把上面四個問題答清楚，再決定要用哪種 payload。

### 探測 1：丟兩個不同字串

目的：確認 hash 演算法、確認伺服器有沒有對輸入做額外處理。

#### 瀏覽器做法（最直觀）

1. 打開 `http://idsctf.mis.nsysu.edu.tw:9019/`
2. Value 1 欄填 `hello`，Value 2 欄填 `world`
3. 按 `Go!`，畫面跳到 `checksum.php`，只看到一張 `!!` 圖
4. **關鍵動作：按 Ctrl+U（檢視網頁原始碼）**

原始碼裡藏著 debug 註解：

```html
<div class="result">
  <!-- <p>Hash of Object 1: aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d</p> -->
  <!-- <p>Hash of Object 2: 7c211433f02071597741e6ff5a8ea34789abbf43</p> -->
</div>
```

出題者忘了把開發階段的 debug 輸出移掉，所以雖然頁面表面只給「失敗圖」，原始碼裡完整保留了兩個 hash 值。**沒看原始碼就漏掉一半情報** — 這是這題第一個關鍵動作。任何 CTF 看到不知所云的頁面，反射動作就是 Ctrl+U + 開 F12 看 Network。

#### curl 做法（等價，但更乾淨）

```bash
curl -sS -X POST "http://idsctf.mis.nsysu.edu.tw:9019/checksum.php" \
  --data-urlencode "object1=hello" \
  --data-urlencode "object2=world"
```

- `--data-urlencode "name=value"`：curl 幫你做 URL 編碼，模擬 HTML form 送出
- 整段 HTML 連同註解直接吐到終端機，不用切視窗去看 source

#### 兩種做法都拿到一樣的情報

- Hash 長度 = **40 hex chars = 160 bits → SHA-1 確認**
- `aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d` 正好是 `sha1("hello")` → 確認伺服器是對「輸入字串原始 bytes」做 SHA-1，沒有額外加 salt、沒有 hex 解碼、沒有任何前處理

### 探測 2：丟兩個相同字串

目的：把「兩值相等」的回應長相先記下來。這一步看起來無聊，但**後面救命**（見「為什麼第一次提交會誤判」那節）。

#### 瀏覽器做法

1. 重新打開首頁
2. Value 1 填 `same`，Value 2 也填 `same`
3. 按 `Go!`
4. 畫面直接顯示文字 `Files are identical` 加一張 `b.jpg`

#### curl 做法

```bash
curl -sS -X POST "http://idsctf.mis.nsysu.edu.tw:9019/checksum.php" \
  --data-urlencode "object1=same" \
  --data-urlencode "object2=same"
```

回傳：`<div class="result">Files are identical</div><img src="b.jpg" alt="Files are identical!">`

#### 三種回應狀態整理

失敗 / 成功 / 相同三種狀態的回應已經摸清：

| 狀態 | 顯示 |
|---|---|
| 兩值不同、hash 不同 | `<img src="c.png" alt="!!">` |
| 兩值相同 | `Files are identical` + `b.jpg` |
| 兩值不同、hash 相同 | （還沒看到，預期會給 flag + `a.png`） |

伺服器邏輯逆推：**`object1 != object2 AND sha1(object1) == sha1(object2)` → 給 flag**。這正好是 collision 的定義。假設驗證完成。

### 為何最後選 curl 而不是繼續用瀏覽器

探測階段瀏覽器其實可以做完，但繼續走下去會撞牆。curl 有三個優勢，正好是 CTF 必備能力：

1. **送任意 bytes 進 text input** — 最後的 320-byte mini collision 充滿不可印字元（控制字元、`\x00`、高位元 byte）。瀏覽器的 `<input type="text">` 沒辦法乾淨地貼進這些 byte（剪貼簿會把它們吃掉或當亂碼）。curl 用 `--data-urlencode "object1@mini1.bin"` 直接讀檔當值，每個 byte 都會被正確 `%XX` 編碼送出。**這一步瀏覽器做不到，是攻擊成立的關鍵**
2. **看完整 raw HTML（含註解、隱藏欄位）** — 不用每次 Ctrl+U 切視窗
3. **可重複、可寫進 writeup** — 別人能照抄驗證；瀏覽器點點點沒有可重現性

簡單講：**探測階段瀏覽器可以、攻擊階段一定要 curl**。所以一開始就用 curl 把流程串起來，省得後面重做。

---

## 為什麼選 corkami 的 PDF 而不是別處

需要的東西是：兩個不同的 byte sequence，其 SHA-1 相同。最現成的就是 SHAttered 的 PDF pair。但有兩個現實阻礙：

1. `https://shattered.io/static/shattered-1.pdf` 回 **HTTP 410 Gone**（網站已下架）
2. 必須找一個有原始 PDF（或等效 collision pair）的鏡像

GitHub 上的 `corkami/collisions` repo 是 Ange Albertini 維護的 hash collision 資料庫，裡面有 `examples/shattered1.pdf` 與 `examples/shattered2.pdf`。下載後驗證：

```
sha1sum shattered1.pdf shattered2.pdf
f7a68375a6c167d692bdd6f7c077a5d7fbfb84ba  shattered1.pdf
f7a68375a6c167d692bdd6f7c077a5d7fbfb84ba  shattered2.pdf

md5sum shattered1.pdf shattered2.pdf
439838ec42fd8f347e6d294f57b6d8f0  shattered1.pdf
a02eb77d05d4ae1c5cd2b90212719aea  shattered2.pdf
```

SHA-1 相同、MD5 不同、檔案內容不同 — 就是合法 collision pair。注意這對檔案的 SHA-1 不是 shattered.io 原版的 `38762cf7f55934b34d179ae6a4c80cadccbb7f0a`，是 corkami 自己用 chosen-prefix collision 技術重新生成的延伸版（3.8 MB）。**對伺服器來說只要它們 SHA-1 相同就行，原版號或變體無關緊要**。

---

## 為什麼第一次提交會誤判為 "Files are identical"

把兩個 PDF 用 `--data-urlencode "object1@shattered1.pdf"` 直接 POST，結果伺服器回 `Files are identical`。

這個回應在前面探測時對應「兩個輸入相等」。但我們提交的是兩個不同 byte 內容的檔案，怎麼可能相等？

關鍵推論：**PHP 不是回應「字串內容相等」，是回應「`$_POST['object1']` 跟 `$_POST['object2']` 都是空 / 都是同樣的東西」**。為什麼會空？

URL-encoded 編碼把不可印 byte 變成 `%XX`（3 bytes 表示 1 byte）。PDF 大部分內容是二進位，膨脹比約 3 倍：

```
單檔  3.8 MB → URL-encoded 後 ~11 MB
兩檔合計     → ~22 MB POST body
```

PHP 5.5 預設 `post_max_size = 8M`。POST body 一旦超過上限，PHP 會把 `$_POST` 清空成空陣列。於是 `$_POST['object1'] === $_POST['object2'] === null`，被當成「相等」。

所以問題不在 collision，是 **payload 太大被伺服器丟掉**。需要更小的 collision pair。

---

## 為什麼 320 bytes 就足夠 — SHA-1 的結構性質

不需要去重新跑 SHAttered 的計算（要 6500 CPU 年 + 110 GPU 年），可以直接從現有的 PDF 切出最小 collision。理由要回到 SHA-1 的內部結構：

### SHA-1 的處理方式（Merkle-Damgård）

1. 把訊息切成 **64-byte block**
2. 維持一個 160-bit 的 **chaining value** (CV)，初始為固定 IV
3. 每個 block 經 compression function 把 CV 更新：`CV_{i+1} = f(CV_i, block_i)`
4. 最後把訊息長度做 padding，再走最後一個 block
5. 最終 CV 就是 hash

### Collision 的本質

SHAttered 找到的是：兩段不同的 message $M_1$、$M_2$，**處理過某幾個 block 後 chaining value 變成相同**。一旦 CV 重新合流，後面如果接相同內容（且總長度相同 → padding 相同），最終 hash 必然相同。

所以一對 SHA-1 collision PDF 的結構長這樣：

```
偏移   |  bytes 0—191   bytes 192—319   bytes 320—end
       |  (3 blocks)    (2 blocks)      (剩下所有 block)
-------+----------------------------------------------
PDF 1  |  相同前綴      不同的 NCB-1    相同尾段
PDF 2  |  相同前綴      不同的 NCB-2    相同尾段
                       ^^^^^^^^^^^^^^
                       這裡 CV 重新合流
```

NCB = near-collision block（兩個 block 共 128 bytes）。

### 用 `cmp` 驗證假設

```
$ cmp -l shattered1.pdf shattered2.pdf | awk 'NR==1{first=$1} {last=$1} END{print first, last}'
193 320
```

差異 byte 偏移從 193 到 320（1-indexed），完全吻合 SHA-1 collision 理論預測：只有 bytes 192-319 不同，這 128 bytes 就是 2 個 NCB。

### 推論：截前 320 bytes 還是合法 collision

把兩個 PDF 各切前 320 bytes（剛好 5 個 SHA-1 block）：

- 兩段內容**不同**（差在 bytes 192-319 那 128 bytes）→ 滿足 `object1 != object2`
- 走過這 5 個 block 後 CV 已合流 → 中間狀態相同
- 兩段都剛好 320 bytes → SHA-1 finalize 時 length padding 完全一樣
- 最後一個 padding block 把同樣的 CV 推到同樣的最終 hash → SHA-1 相同

```bash
head -c 320 shattered1.pdf > mini1.bin
head -c 320 shattered2.pdf > mini2.bin

sha1sum mini1.bin mini2.bin
f92d74e3874587aaf443d1db961d4e26dde13e9c  mini1.bin
f92d74e3874587aaf443d1db961d4e26dde13e9c  mini2.bin

md5sum mini1.bin mini2.bin
80e808e7abdbe9109903c71f049a30f7  mini1.bin
736acaed4ec96ab7120fb5fd750f1f07  mini2.bin
```

驗證通過。每邊 320 bytes，URL-encoded 後最多 ~960 bytes，兩個合起來 ~2 KB，遠低於 `post_max_size`。

---

## 最終提交

```bash
curl -X POST http://idsctf.mis.nsysu.edu.tw:9019/checksum.php \
  --data-urlencode "object1@mini1.bin" \
  --data-urlencode "object2@mini2.bin"
```

回應：

```html
<div class="result">Flag{Sh4ttEr_ShA1!!!}</div><img src="a.png" alt="False Twins!!">
```

`a.png` 的 alt text 是 "False Twins!!" — 兩個假雙胞胎，正是 hash collision 的形象說法。

---

## 思路總結

1. **題目訊號集中、不會誤導** — "shattered" / "Pathetic Hash" / "Revenge of hash" 三條線指向同一個目標：SHA-1 collision。先讓假設成形，再去執行
2. **先 probe，再 attack** — 用 hello / world 探出演算法與比較邏輯，再用 same / same 探出失敗回應。這一步幾乎決定後續所有選擇
3. **失敗時先懷疑環境，再懷疑邏輯** — `Files are identical` 表面像「資料被視為相等」，實際是 `post_max_size` 截掉。判讀錯訊號就會浪費時間
4. **不要重做別人已經做完的工作** — SHAttered 已經給了一對 collision PDF，不需要自己跑碰撞。只要懂 SHA-1 結構，把它縮到 320 bytes 就行

## 相關資源

- SHAttered 原始論文 (Stevens et al., CRYPTO 2017): *The first collision for full SHA-1*
- `corkami/collisions` GitHub repo（hash collision 範例庫）
- RFC 3174 — SHA-1 規範（Merkle-Damgård 結構與 block 處理）
