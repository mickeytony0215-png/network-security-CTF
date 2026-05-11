# 密文內容
secret = "背胲胧胭脁肻胺胯胒胲胥胙肷胳胶胲肹胥胸胏胭胮胚脃"

# 根據題目提示推導出的偏移量 (Intel 8086)
offset = 0x8086

# 解碼邏輯：將每個漢字的 Unicode 碼位減去偏移量
flag = "".join(chr(ord(c) - offset) for c in secret)

print(f"[*] 正在進行 Unicode 逆向旋轉 (Offset: {hex(offset)})...")
print("-" * 30)
print(f"解密結果: {flag}")
print("-" * 30)