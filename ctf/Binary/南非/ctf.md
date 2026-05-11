# CTF Writeup: 奪取_南非 - African Simulator (Flare-On 5: Ultimate Minesweeper)

## 📌 題目資訊
* **類別:** Binary / Reverse Engineering
* **目標檔案:** `African_sim_6f9e0f6946d856deaa02e961fbf17445.exe`
* **提示:** "The prize string is your flag. It doesn't start with Flag{"

## 🔍 1. 初始勘查與架構分析
在 WSL2 中執行初步測試，發現該程式為一款「一按就踩雷結束」的作弊版踩地雷遊戲。
使用 `rabin2 -z` 傾印字串與資源時，發現了 `<assemblyIdentity>` 以及 `.NET Framework` 的特徵：
```text
23  0x00138c42 0x0053ae42 16  34   .rsrc   utf16le Assembly Version
24  0x00138c64 0x0053ae64 7   16   .rsrc   utf16le 1.0.1.0
```
這證實了該執行檔為 **C# (.NET) 應用程式**，可直接利用 **dnSpy** 進行近乎完美的原始碼反編譯，無須啃底層組合語言。

## ⚙️ 2. 核心邏輯逆向 (dnSpy)
將程式載入 dnSpy 後，鎖定核心 UI 類別 `MainForm`，發現兩個關鍵漏洞與機制：

### A. 脆弱的 Flag 生成演算法 (`GetKey`)
遊戲勝利時會呼叫 `GetKey(List<uint> revealedCells)`。
```csharp
private string GetKey(List<uint> revealedCells)
{
    revealedCells.Sort();
    Random random = new Random(Convert.ToInt32(revealedCells[0] << 20 | revealedCells[1] << 10 | revealedCells[2]));
    // ... 後續為產生 32 bytes 亂數與陣列進行 XOR 解密 ...
}
```
**漏洞點：** `.NET` 的 `Random` (PRNG) 使用了固定的 Seed。而這個 Seed 僅由玩家翻開的**前 3 個最小安全格子索引值** (Index) 決定。只要找出地圖上這 3 個安全的格子，就能直接算出 Seed 並偽造解密金鑰，完全不需要實際玩完遊戲。

### B. 佈雷邏輯與混淆 (`AllocateMemory`)
尋找產生炸彈的邏輯，發現一個名為 `AllocateMemory` 的函數。出題者刻意將記錄地雷的二維陣列 `minesPresent` 重新包裝成屬性 `GarbageCollect` 來混淆視聽。
```csharp
private void AllocateMemory(MineField mf)
{
    for (uint num = 0U; num < MainForm.VALLOC_NODE_LIMIT; num += 1U) {
        for (uint num2 = 0U; num2 < MainForm.VALLOC_NODE_LIMIT; num2 += 1U) {
            bool flag = true; // 預設全是地雷
            uint r = num + 1U;
            uint c = num2 + 1U;
            if (this.VALLOC_TYPES.Contains(this.DeriveVallocType(r, c))) {
                flag = false; // 滿足特定條件才是安全格子
            }
            mf.GarbageCollect[(int)num2, (int)num] = flag;
        }
    }
}
```
免死條件為：`~(r * 30 + c) == VALLOC_TYPE`。

## 🧮 3. 數學計算與座標還原
透過檢視 `MainForm` 頂部宣告，取得關鍵常數：
* 地圖大小 `VALLOC_NODE_LIMIT` = 30
* 三個免死金牌數值 `VALLOC_TYPES` 分別為：`4294966400U`, `4294966657U`, `4294967026U`

對這些數值進行位元反轉 (Bitwise NOT, `~`) 並推導出行列座標 (1-based)：
1. `~4294966400U` = 895 $\rightarrow$ `895 / 30 = 29 (r)`, `895 % 30 = 25 (c)`
2. `~4294966657U` = 638 $\rightarrow$ `638 / 30 = 21 (r)`, `638 % 30 = 8 (c)`
3. `~4294967026U` = 269 $\rightarrow$ `269 / 30 = 8 (r)`, `269 % 30 = 29 (c)`

將座標轉換為 0-based 的一維陣列索引 (Index = `(r-1) * 30 + (c-1)`)：
* Cell 1: `28 * 30 + 24 = 864`
* Cell 2: `20 * 30 + 7 = 607`
* Cell 3: `7 * 30 + 28 = 238`

排序後得到：`[238, 607, 864]`。
計算 PRNG Seed：`(238 << 20) | (607 << 10) | 864` = **250183520**

## 🚀 4. Exploit (C# Keygen)
撰寫腳本直接模擬原本的解密邏輯，印出 Flag。

```csharp
using System;
using System.Text;

public class Exploit {
    public static void Main() {
        // 1. 設定推導出的完美 Seed
        int seed = 250183520; 
        Random random = new Random(seed);
        
        // 2. 從 dnSpy 提取出的密文陣列
        byte[] encryptedFlag = new byte[] {
            245, 75, 65, 142, 68, 71, 100, 185, 74, 127, 62, 130, 
            231, 129, 254, 243, 28, 58, 103, 179, 60, 91, 195, 215, 
            102, 145, 154, 27, 57, 231, 241, 86
        };
        byte[] keyStream = new byte[32];
        
        // 3. 產生金鑰並進行 XOR 解密
        random.NextBytes(keyStream);
        for (uint i = 0U; i < (uint)encryptedFlag.Length; i += 1U) {
            encryptedFlag[(int)i] = (byte)(encryptedFlag[(int)i] ^ keyStream[(int)i]);
        }
        
        Console.WriteLine("Flag: " + Encoding.ASCII.GetString(encryptedFlag));
    }
}
```

## 🚩 5. Flag
`Ch3aters_Alw4ys_W1n@flare-on.com`