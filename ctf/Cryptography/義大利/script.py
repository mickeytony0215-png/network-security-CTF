def vigenere_decrypt(ciphertext, key):
    """
    標準的維吉尼亞密碼解密函式
    - 僅對英文字母進行解密轉換
    - 保留大小寫與特殊符號（如底線、括號）
    """
    plaintext = ""
    key_idx = 0
    key = key.lower() # 確保金鑰皆為小寫以方便計算
    
    for char in ciphertext:
        if char.isalpha():
            # 計算目前金鑰字元的偏移量 (a=0, b=1, ..., z=25)
            shift = ord(key[key_idx % len(key)]) - ord('a')
            
            if char.isupper():
                # 大寫字母解密：C = (P - K) mod 26
                decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                plaintext += decrypted_char
            else:
                # 小寫字母解密
                decrypted_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                plaintext += decrypted_char
                
            # 只有遇到英文字母時，金鑰索引才會往前推進
            key_idx += 1
        else:
            # 非英文字母（如底線、空格等）直接保留，不推進金鑰索引
            plaintext += char
            
    return plaintext

if __name__ == "__main__":
    # 透過 KPA (已知明文攻擊) 推導出的金鑰
    key = "tobeornottobe"
    
    print("[*] 開始解密...")
    print(f"[*] 使用金鑰: {key}\n")

    # ---------------------------------------------------------
    # 由於出題者將外層的 flag 與內層的內容分開加密，
    # 導致金鑰的對齊索引在括號處重置，因此我們也將其拆開解密。
    # ---------------------------------------------------------
    
    # 1. 解密外層標頭 "yzbk" -> "flag"
    header_cipher = "yzbk"
    header_plain = vigenere_decrypt(header_cipher, key)
    
    # 2. 解密括號內部 "dDb_mG_UnbZxfpyl" -> "kPa_iS_DanGerous"
    inner_cipher = "dDb_mG_UnbZxfpyl"
    inner_plain = vigenere_decrypt(inner_cipher, key)
    
    # 組合最終 Flag
    final_flag = f"{header_plain}{{{inner_plain}}}"
    
    print("-" * 30)
    print(f"🏁 最終 Flag: {final_flag}")
    print("-" * 30)