# final_solve.py
import base64

# --- 1. 破解出來的 RSA 參數 ---
n = 80336074090353650275669953264266039272354840751901775007157826889477899735129
e = 65537

p = 273644295692283542487988795083308537753
q = 293578471596179653447031682100309849793

# --- 2. 計算私鑰 d ---
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)

# --- 3. 檔案解密與還原邏輯 ---
enc_files = ['tooSmallflag.enc', 'tooSmallflag2.enc', 'tooSmallflag3.enc']
full_flag = ""

for file in enc_files:
    try:
        with open(file, 'rb') as f:
            c = int.from_bytes(f.read(), 'big')
            
            # 核心解密：m = c^d mod n
            m_int = pow(c, d, n)
            m_bytes = m_int.to_bytes((m_int.bit_length() + 7) // 8, 'big')
            
            # 過濾 PKCS#1 v1.5 Padding，用 \x00 切割並取最後一塊乾淨明文
            clean_bytes = m_bytes.split(b'\x00')[-1]
            part = clean_bytes.decode('utf-8').strip()
            
            full_flag += part
            
    except FileNotFoundError:
        pass # 忽略錯誤輸出，保持畫面乾淨

# 只印出最終的 Flag
print(full_flag)