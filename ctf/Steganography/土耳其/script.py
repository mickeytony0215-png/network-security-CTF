import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal

# 1. 讀取音檔
fs, data = wavfile.read('Easy_a44c4fa8fadb58d8077c61b9e936fe07.wav')
if len(data.shape) > 1: data = data[:, 0]

# 2. 生成高解析度頻譜
# nperseg 設為 4096 以獲得極高的頻率解析度
f, t, Sxx = signal.spectrogram(data, fs, nperseg=4096, noverlap=2048)

# 3. 鎖定 Flag 所在的 16kHz - 22kHz 區間
mask = (f >= 16000) & (f <= 22000)
f_zoom = f[mask]
Sxx_zoom = Sxx[mask, :]

# 4. 對數增強與二值化 (Thresholding)
# 透過調整閥值 (0.6) 讓雜訊消失，只留下文字
Sxx_log = 10 * np.log10(Sxx_zoom + 1e-10)
Sxx_norm = (Sxx_log - np.min(Sxx_log)) / (np.max(Sxx_log) - np.min(Sxx_log))
binary_image = Sxx_norm > 0.6 

# 5. 繪圖輸出
plt.figure(figsize=(25, 8))
plt.imshow(binary_image, aspect='auto', origin='lower', cmap='binary',
           extent=[t[0], t[-1], 16000, 22000])
plt.title("CTF Spectrogram Flag Recovery", fontsize=20)
plt.xlabel("Time (s)", fontsize=14)
plt.ylabel("Frequency (Hz)", fontsize=14)
plt.grid(False)
plt.savefig('the_real_flag.png', bbox_inches='tight', dpi=300)
print("顯影完成！請打開同目錄下的 the_real_flag.png 查看。")