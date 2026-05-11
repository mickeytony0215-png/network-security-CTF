import re

# 1. 讀取原始碼
with open("anthem.html", "r") as f:
    content = f.read()

# 2. 提取所有顏色
colors = re.findall(r'#([0-9a-fA-F]{6})', content)

# 3. 提取位元 (嘗試將出現次數少的設為 1)
# 這裡我們用 c[-1] 的奇偶性來判斷
bits = ""
for c in colors:
    # 如果最後一位是奇數（如 1, 3, 5, 7, 9, b, d, f）設為 1，否則設為 0
    bits += str(int(c[-1], 16) % 2)

# 4. 轉換為 Byte 陣列並存檔
byte_data = bytearray()
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    if len(byte) == 8:
        byte_data.append(int(byte, 2))

# 5. 輸出成檔案
with open("extracted_data.bin", "wb") as f:
    f.write(byte_data)

print("[*] 資料已存至 extracted_data.bin")