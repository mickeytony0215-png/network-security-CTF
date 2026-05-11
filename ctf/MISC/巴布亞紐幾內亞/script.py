def brute_force_xor_all_offsets():
    with open("test", "rb") as f:
        data = f.read()
    
    # flag{ 之後的 10 個加密位元組
    target = data[0x35:0x3F]
    
    print(f"{'Offset':<10} | {'Decoded Flag Content'}")
    print("-" * 40)
    
    # 遍歷檔案中所有可能的 Key 起始位址
    for i in range(len(data) - len(target)):
        key = data[i : i + len(target)]
        # 進行 XOR 運算
        decoded = "".join([chr(t ^ k) for t, k in zip(target, key)])
        
        # 過濾：只顯示全是可讀 ASCII 字元且有意義的結果
        if all(32 <= ord(c) <= 126 for c in decoded):
            # 特別檢查是否包含常見的 PNG 關鍵字
            print(f"0x{i:04x}     | flag{{{decoded}}}")

if __name__ == "__main__":
    brute_force_xor_all_offsets()