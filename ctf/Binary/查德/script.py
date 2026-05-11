cipher = "OKKlYguFuMuQWsY"
# 測試 XOR (9 + index)
for i, c in enumerate(cipher):
    print(chr(ord(c) ^ (9 + i)), end="")
print("\n---")
# 測試 XOR (9 - index)
for i, c in enumerate(cipher):
    print(chr(ord(c) ^ (abs(9 - i))), end="")