import base64

def rot13(s):
    return s.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))

# 你的目標字串
target = "WgZjB1MVIRNu"

# 組合 A: 先 ROT13 再 Base64 解碼
try:
    print("組合 A:", base64.b64decode(rot13(target)).decode())
except: pass

# 組合 B: 先反轉再 Base64 解碼
try:
    print("組合 B:", base64.b64decode(target[::-1]).decode())
except: pass

# 組合 C: 先 Base64 解碼再 ROT13 (這可能輸出 binary)
try:
    print("組合 C:", rot13(base64.b64decode(target).decode()))
except: pass