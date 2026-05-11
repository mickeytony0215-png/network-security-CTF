import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def solve():
    # 1. 模擬 JS 的字串轉 UTF-8 行為
    # 在 JS 中 "\x93" 是字元，轉成 UTF-8 會變成多個位元組
    js_string = "\x93\x39\x02\x49\x83\x02\x82\xf3\x23\xf8\xd3\x13\x37"
    seed_bytes = js_string.encode('utf-8') 
    
    # 計算 SHA256
    k_hex = hashlib.sha256(seed_bytes).hexdigest()
    
    # 取得 Key 和 IV (AES-128-CBC)
    key = bytes.fromhex(k_hex[0:32])
    iv = bytes.fromhex(k_hex[32:64])

    print(f"[*] Correct Key (Hex): {key.hex()}")
    print(f"[*] Correct IV (Hex): {iv.hex()}")

    # 2. 準備密文
    ciphertext = base64.b64decode("ob1xQz5ms9hRkPTx+ZHbVg==")

    try:
        # 3. 執行 AES 解密
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_raw = cipher.decrypt(ciphertext)
        
        # 嘗試移除 PKCS7 Padding
        plaintext = unpad(decrypted_raw, AES.block_size)
        
        print("-" * 30)
        print(f"🚩 FLAG (Password): {plaintext.decode('utf-8')}")
        print("-" * 30)
        
    except Exception as e:
        print(f"\n[!] 解密失敗: {e}")
        print(f"[*] 解出的原始資料 (可能是編碼問題): {decrypted_raw}")

if __name__ == "__main__":
    solve()