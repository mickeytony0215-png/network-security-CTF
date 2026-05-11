import base64

def solve():
    # 原始數據
    raw = bytes.fromhex("464c41deda5997ccdb0d45f6d70615c8cd")
    
    # 題目提示：Mr. Right, Ms. Right, Right
    keys = [b"Right", b"Mr. Right", b"Ms. Right", b"Mr.Right", b"Ms.Right"]
    
    print("--- 嘗試多種邏輯組合 ---")
    
    # 邏輯 A: 直接位移還原 (不論 sex)
    # 我們看到 de->o, da->m，這很可能是 "om" (man)
    res_shift = "FLA" + "".join(chr(b >> 1) for b in raw[3:])
    print(f"[*] 位移還原: {res_shift}")

    # 邏輯 B: 使用 'Right' 進行 XOR，但從 FLA 之後開始
    for k in keys:
        dec = bytearray(raw)
        for i in range(3, len(raw)):
            # 這裡嘗試將位移與 XOR 結合 (因為 Right 既是右移也是密鑰)
            dec[i] = (raw[i] >> 1) ^ k[(i-3) % len(k)]
        print(f"[*] Key '{k.decode()}': {'FLA' + dec[3:].decode(errors='replace')}")

solve()