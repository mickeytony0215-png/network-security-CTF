from pwn import *

# 自動切換 32/64 bit 模式
elf = ELF('./easy_math_85c325e5fde035a09791a94a0689e992')
r = remote('140.117.80.61', 4445)

# 1. 處理 Warmup
print(r.recvuntil(b'>').decode())

# 我們先試試看 1337 是否能開啟數學題
r.sendline(b'1337') 

# 2. 觀察後續
# 如果輸入 1337 後開始噴數學題，腳本就繼續算
# 如果輸入 1337 後沒反應，我們嘗試發送一個超長字串看看會不會 Crash
# r.sendline(b'A' * 100) 

r.interactive()