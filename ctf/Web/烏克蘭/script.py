import hashlib
import itertools
import string
import time

# 題目給的目標 SHA1 雜湊值
target_hash = "b89356ff6151527e89c4f3e3d30c8e6586c63962"

# 設定搜尋範圍：小寫字母 (a-z)
# 如果怕有數字，可以改為 string.ascii_lowercase + string.digits
chars = string.ascii_lowercase 

def brute_force():
    start_time = time.time()
    print(f"開始破解雜湊值: {target_hash}...")

    # 嘗試不同的長度，從 1 位到 6 位
    for length in range(1, 7):
        print(f"正在嘗試長度為 {length} 的組合...")
        
        # itertools.product 會生成所有可能的組合（笛卡兒積）
        for guess in itertools.product(chars, repeat=length):
            password = "".join(guess)
            
            # 計算該組合的 SHA1 雜湊值
            h = hashlib.sha1(password.encode()).hexdigest()
            
            # 比對
            if h == target_hash:
                end_time = time.time()
                print("-" * 30)
                print(f"破解成功！")
                print(f"明文密碼為: {password}")
                print(f"總共耗時: {end_time - start_time:.2f} 秒")
                return password

if __name__ == "__main__":
    brute_force()