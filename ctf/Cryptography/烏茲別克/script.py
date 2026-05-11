import base64
try:
    import base45
except ImportError:
    print("[!] 請先安裝套件: pip install base45")
    exit()

# 自動修補 Base32/Base64 缺失的等號 padding
def fix_padding(b):
    return b + b'=' * (-len(b) % 4)

# 讀取密鑰與密文
with open('key.txt', 'r') as f:
    key = f.read().rstrip('\r\n') 

with open('encoded.txt', 'r') as f:
    data = f.read().strip().encode()

# 我們同時測試兩種順序
paths = {
    "【正向解碼】 (依照 Key 由左至右)": key,
    "【反向解碼】 (依照 Key 由右至左)": key[::-1]
}

for path_name, current_path in paths.items():
    print(f"\n[*] 正在嘗試 {path_name} ...")
    current_data = data
    success = True
    
    for i, char in enumerate(current_path):
        try:
            if char == ' ':
                current_data = base64.b32decode(fix_padding(current_data))
            elif char == '-':
                current_data = base45.b45decode(current_data)
            elif char == '@':
                current_data = base64.b64decode(fix_padding(current_data))
            elif char == 'U':
                # Base85 有兩種常見變體，先試標準的，報錯再試 Ascii85
                try:
                    current_data = base64.b85decode(current_data)
                except:
                    current_data = base64.a85decode(current_data)
            else:
                print(f"  [!] 第 {i+1} 層遇到未知字元: {char}")
                success = False
                break
                
        except Exception as e:
            print(f"  [-] 失敗於第 {i+1} 層 (解碼器 '{char}') : {e}")
            success = False
            break  # 停止當前路徑，換下一個路徑測試
            
    if success:
        print("-" * 40)
        print("🎉 成功跑完 50 層解碼！")
        print(f"🚩 最終明文 Flag:\n{current_data.decode('utf-8', errors='ignore')}")
        print("-" * 40)
        break # 已經成功，不需再測另一種順序