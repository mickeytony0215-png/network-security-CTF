# CTF Write-up: 奪取_德國 - Complicated Obfuscation

| 分數 | 分類 | 關鍵技術 |
| :--- | :--- | :--- |
| 20 Pts | Web | JS 混淆、函數式編程 (Functional Programming)、reduceRight、Currying |

## 1. 題目描述
網頁提供一個登入頁面，要求輸入 Password。核心驗證邏輯隱藏在一段使用了高度函數式編程技巧的 JavaScript 代碼中。提示為：「Quite complicated right? Ha! Ha! Ha!」。

## 2. 代碼靜態分析

### A. 密碼格式檢查
`validatekey` 函數中定義了密碼必須滿足以下條件：
- 必須包含 4 個 `-`，即分為 5 個部分（`a[0]` 到 `a[4]`）。
- 每個部分的長度必須剛好為 4。

### B. 核心組件
1.  **`genFunc(_part)`**: 
    - 根據 `_part` 字串動態生成一個新的匿名函數。
    - 參數名：`_part.substring(1,3)`
    - 邏輯：`this.[_part[3]] = 參數 + _part[0]`。
    - 例如：`ABGH` 會生成 `function(BG) { this.H = BG + 'A'; }`。
2.  **`callback(x, y, i, a)`**:
    - `reduceRight` 的回呼函數。
    - 核心操作：`y.call(x, a[a["length"]-1-i].toString().slice(19,21))`。
    - 這代表目前函數 `y` 的參數值，來自於「對應位置」函數定義中的**參數名稱字串切片**。
3.  **`reduceRight` 流程**:
    - `var o = a.map(genFunc).reduceRight(callback, new (genFunc(a[4]))(Function));`
    - 從 `a[4]` 開始作為初始物件，反向執行到 `a[0]`。

## 3. 邏輯逆向推導

目標物件為 `ref = {T : "BG8", J : "jep", j : "M2L", K : "L23", H : "r1A"}`。
由於 `Object.keys` 順序敏感，我們必須依照 `T -> J -> j -> K -> H` 的順序構造各個 Part。

### 依賴鏈對照表：
根據 `reduceRight` 與 `callback` 的參數抓取邏輯：

| 索引 | 目標屬性 (Key) | 目標值後綴 (Suffix) | 參數來源 (來自 `a[4-i]`) | 構造 Part ([Suffix][Param][Key]) |
| :--- | :--- | :--- | :--- | :--- |
| **a[0]** | H | A | BG (來自 a[4] 的參數名) | **ABGH** |
| **a[1]** | K | 3 | je (來自 a[3] 的參數名) | **3jeK** |
| **a[2]** | j | L | M2 (來自 a[2] 的參數名) | **LM2j** |
| **a[3]** | J | p | L2 (來自 a[1] 的參數名) | **pL2J** |
| **a[4]** | T | 8 | r1 (來自 a[0] 的參數名) | **8r1T** |

*註：參數名稱是由 `slice(19,21)` 從函數 `toString()` 中切出的，對應 `_part.substring(1,3)`。*

## 4. 實作推導腳本 (Python)

```python
import collections

# 目標物件
ref = collections.OrderedDict([
    ("T", "BG8"), ("J", "jep"), ("j", "M2L"), ("K", "L23"), ("H", "r1A")
])

# 逆向推導邏輯
# a[0] 加入 H，suffix A，param BG -> ABGH
# a[1] 加入 K，suffix 3，param je -> 3jeK
# a[2] 加入 j，suffix L，param M2 -> LM2j
# a[3] 加入 J，suffix p，param L2 -> pL2J
# a[4] 加入 T，suffix 8，param r1 -> 8r1T

results = ["ABGH", "3jeK", "LM2j", "pL2J", "8r1T"]
print("Key:", "-".join(results))
```

## 5. 最終 Flag
輸入 `ABGH-3jeK-LM2j-pL2J-8r1T` 進行跳轉，獲得最終 Flag。

**🚩 FLAG: `FLAG{Its_All_Ab0ut_Try_And_Error_And_00000000000veride}`**

---
## 6. 知識總結
1.  **JS 動態特性**：`new Function` 與 `toString()` 的結合可以實現高度混淆的自定義邏輯。
2.  **函數式編程陷阱**：`reduceRight` 改變了處理順序，結合 `call` 指令與動態參數抓取，使得靜態閱讀代碼變得極其困難。
3.  **物件鍵序**：在 JS 中，`Object.keys` 的順序通常與屬性定義的先後順序有關，此題利用此點強化驗證強度。