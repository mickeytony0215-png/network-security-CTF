# CTF 解題紀錄：奪取_格陵蘭 - RSA (tooSmall)

## 1. 題目資訊
- **題目名稱**：奪取_格陵蘭 - RSA (tooSmall)
- **分類**：Cryptography (密碼學)
- **分數**：40 分
- **核心漏洞**：RSA 模數過小 (Small Modulus) / 大數分解

## 2. 題目分析
### 線索探查
1. **解壓縮與檔案偵測**：
   一開始嘗試使用 `z` 參數解壓縮失敗，透過 `file` 指令確認檔案類型後成功解開。
   ```bash
   tar -zxvf tooSmall_9759a80e9f9677717f74f8f0c703da77.tar.gz # 失敗：not in gzip format
   file tooSmall_9759a80e9f9677717f74f8f0c703da77.tar.gz # 顯示 POSIX tar archive
   tar -xvf tooSmall_9759a80e9f9677717f74f8f0c703da77.tar.gz # 成功解開
   ```
2. **分析公鑰**：
   使用 OpenSSL 提取資訊，發現 Public-Key 長度僅為 **256 bit**。
   ```bash
   openssl rsa -pubin -in public_key.pem -text -noout
   # 輸出: Public-Key: (256 bit)
   # Modulus: 00:b1:9c:9b:49...
   # Exponent: 65537 (0x10001)
   ```
3. **提取參數**：
   利用 Python 將十六進位模數轉為十進位大整數 $n$。
   ```bash
   python3 -c "print(int('b19c9b496154e2cc6e9d7be29b3990c12f436b66fb229acc0381bd10cc6cd059', 16))"
   # 結果: 80336074090353650275669953264266039272354840751901775007157826889477899735129
   ```

### 漏洞原理
- **RSA 模數過小**：RSA 的安全性建立在大整數分解的困難度上。256-bit（約 77 位十進位）的模數 $n$ 過小，可以輕易在個人電腦上利用進階演算法被分解回質因數 $p$ 與 $q$。
- **攻擊思路**：使用本地端的數學工具強行分解 $n$ 取得 $p$ 和 $q$，計算歐拉函數 $\phi(n)$ 求出私鑰 $d$，最後利用 $m = c^d \pmod n$ 解密三個檔案。

## 3. 解題過程
### 嘗試與排錯
1. **Python 效能瓶頸**：初期嘗試寫 Python 腳本跑 Pollard's rho 與費馬分解法，但迭代千萬次仍未收斂。
2. **工具鏈缺失**：嘗試安裝傳統分解工具 `msieve` 失敗。
   ```bash
   sudo apt-get install msieve
   # 報錯: E: Unable to locate package msieve
   ```
3. **終端機 Alias 衝突**：改用 `PARI/GP` 數學軟體，但執行 `gp` 時被系統 Alias 攔截。
   ```bash
   gp -q -c "factor(...)"
   # 報錯: fatal: not a git repository (系統誤判為 git push)
   ```
4. **記憶體溢出 (Stack Overflow)**：使用 `\gp` 略過別名並透過 Pipeline 餵指令，卻遇到記憶體不足。
   ```bash
   echo "factor(80336...)" | \gp -q
   # 報錯: *** factor: the PARI stack overflows ! current stack size: 8000000 (7.629 Mbytes)
   ```

### 正確破解
- **構造 Payload / 解密過程**：
  加上 `-s 500000000` 參數強制分配 500MB 記憶體給 PARI/GP 解決 Stack Overflow，瞬間秒殺分解：
  ```bash
  echo "factor(80336074090353650275669953264266039272354840751901775007157826889477899735129)" | \gp -q -s 500000000
  ```
- **關鍵數值**：
  - `p` = `273644295692283542487988795083308537753`
  - `q` = `293578471596179653447031682100309849793`
- **執行邏輯**：
  將 $p$、$q$ 帶入自製 Python 腳本計算私鑰，解密後的明文含有不可讀的 PKCS#1 v1.5 填充字元（`\x02\x87\xe3...`）。透過 `split(b'\x00')[-1]` 暴力切斷前面的 Padding 區塊，順利提取並組合出乾淨的 Flag。
  ```bash
  python3 final_solve.py
  # 輸出: FLAG{RSA_KEr_keR}
  ```

## 4. 最終結果
- **關鍵指令一**：`\gp -q -s 500000000` (略過 Alias 並加大記憶體配額)
- **關鍵輸入二**：解密腳本中的 Padding 過濾邏輯 `split(b'\x00')[-1]`
- **Flag**：`FLAG{RSA_KEr_keR}`

---

## 5. 知識點總結
- **核心概念**：RSA 金鑰長度決定安全性，低於 1024-bit 的模數極容易被強行分解；實戰中常遇見教科書 RSA 疊加 PKCS#1 v1.5 填充，需具備手動過濾 Padding 的能力。
- **防禦手段**：
  1. 採用現代安全標準的金鑰長度（至少 2048-bit 甚至 4096-bit）。
  2. 使用 OAEP (Optimal Asymmetric Encryption Padding) 等更安全的填充機制，以抵抗進階密碼學攻擊。