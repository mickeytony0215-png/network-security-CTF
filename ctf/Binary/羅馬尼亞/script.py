import base64

def solve():
    encoded = "RkxB3tpZl8zbDUX21wYVyM0="
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    
    # 根據我們剛才算的差距 38
    shift = 38 
    # 建立向右位移後的自定義 Alphabet
    custom_alphabet = alphabet[shift:] + alphabet[:shift]
    
    # 建立轉換表
    table = str.maketrans(custom_alphabet, alphabet)
    try:
        # 將加密字串映射回標準 Base64 進行解碼
        flag = base64.b64decode(encoded.translate(table))
        print(f"\n[+] 成功解密!")
        print(f"[+] 原始加密字串: {encoded}")
        print(f"[+] 最終 Flag: {flag.decode()}")
    except Exception as e:
        print(f"[-] 解碼失敗: {e}")

solve()