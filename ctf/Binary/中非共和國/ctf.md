# CTF Writeup: 奪取_中非共和國 - 8EchoRifts

## 📌 題目資訊
* **類別:** Binary / Pwn
* **目標檔案:** `leaky_9227a882a429cfff81d5cde2cb022dab.exe` (32-bit PE)
* **漏洞類型:** Format String Vulnerability (格式化字串漏洞)
* **Flag:** `Flag{%x4b} `

## 🔍 1. 靜態分析 (Static Analysis)

透過 `radare2` 對執行檔進行反組譯分析。

### 核心漏洞點
在 `main` 函數中，程式透過 `read` 讀取使用者輸入後，直接呼叫了 `printf`：
```assembly
0x00401328      mov dword [esp], 0x404060   ; 使用者輸入的緩衝區位址
0x0040132f      call sym._printf             ; 漏洞：printf(buffer)
```
**分析：** 這裡程式沒有提供格式化控制字串（如 `"%s"`），而是直接將使用者輸入作為第一個參數傳給 `printf`。這允許攻擊者傳入格式化字元（如 `%p`, `%x`）來讀取或寫入記憶體。

### 記憶體中的秘密 (The Rifts)
在 `main` 的開頭，程式在 Stack 上初始化了 8 個 4-byte 變數：
* 其中 7 個的值為 `0x52696674` (ASCII: "Rift")。
* 其中 1 個的值為 **`0x25783462`**。



## 🚀 2. 漏洞利用 (Exploitation)

### A. 資訊洩漏 (Information Leak)
為了讀取 Stack 上的變數，我們使用 `%p`（印出指標位址）來進行記憶體傾印：
```bash
# 輸入 Payload
%p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p
```

### B. 觀察輸出結果
在回傳的資料中，我們觀察到從第 10 個 Offset 開始出現目標資料：
`... 52696674 52696674 52696674 25783462 52696674 ...`

這證實了我們的秘密就藏在 Stack 上。

## 🧮 3. 數據解碼 (Decoding)

目標十六進位數值：**`0x25783462`**

在 32 位元架構中，`printf` 印出的數值順序通常直接對應字元的組成。我們將其轉換為 ASCII 字元：
1. `0x25` $\rightarrow$ **%**
2. `0x78` $\rightarrow$ **x**
3. `0x34` $\rightarrow$ **4**
4. `0x62` $\rightarrow$ **b**

組合結果：**`%x4b`**

### 💡 為什麼這是 "Secret"？
題目提示說：「我會 Echo 你的輸入，但秘密除外。」
當你嘗試輸入 `%x4b` 時，由於 `%x` 是一個格式化指令，`printf` 會試著去尋找一個參數並以十六進位印出，而不會直接印出 `%x` 這兩個字。因此，這個字串在該程式中永遠無法被正確地「原樣回傳」，這也是題目設計的精妙之處。

## 🚩 Flag
`Flag{%x4b} `
