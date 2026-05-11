import wave

# 讀取相減後的檔案
with wave.open('difference.wav', 'rb') as w:
    frames = bytearray(w.readframes(w.getparams().nframes))

# 提取每個 sample 的 LSB (假設是 16-bit，每兩個 byte 是一個 sample)
# 我們取每個 16-bit 小端序採樣的最低位元
extracted_bits = ""
for i in range(0, len(frames), 2):
    # frames[i] 是低位字節，最後一位就是 LSB
    extracted_bits += str(frames[i] & 1)

# 將 bit 轉回 bytes
def bits_to_bytes(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        chars.append(int(byte[::-1], 2)) # 試試看正序或反序，通常是反序
    return bytes(chars)

with open('secret_data.bin', 'wb') as f:
    f.write(bits_to_bytes(extracted_bits))

print("LSB data extracted to secret_data.bin")