# CTF Writeup: 奪取_利比亞 - Least Privilege Principle

## 📌 題目資訊
* **類別:** Binary / Reverse Engineering (Windows)
* **目標檔案:** `ck_44d7b697c2428478108478ad0755ede2.exe`
* **Flag:** `Flag{n0t_aDm1n_but_priv1leged}`
* **核心概念:** 最小權限原則 (Least Privilege)、UAC 繞過 (Manifest Bypass)、Windows Token 檢查。

## 🔍 1. 靜態分析 (Static Analysis)

透過 `radare2` 分析字串與清單 (Manifest)，發現了程式邏輯中的 **「矛盾設計」**：

1.  **程式碼清單 (Manifest)**:
    在資源區段中發現 `<requestedExecutionLevel level='requireAdministrator' />`。這代表 Windows 在執行此程式前，會強制跳出 UAC 視窗要求管理員權限。
2.  **程式碼邏輯 (Internal Code)**:
    字串清單中存在 `Welcome, admin. But you are not allowed here.\n`，且導入了 `CheckTokenMembership` API。這代表程式執行後會檢查：**「如果你是管理員，我就拒絕執行。」**

**分析結論：** 這是一個 **Catch-22 (左右為難)** 的陷阱。系統層面強制要求 Admin，但應用程式層面拒絕 Admin。

## ⚙️ 2. 漏洞邏輯 (The Catch-22 Trap)

程式的執行流如下：
1.  使用者雙擊執行 $\rightarrow$ Windows 讀取 Manifest $\rightarrow$ 彈出 UAC 要求 **Admin**。
2.  使用者提供 Admin 權限 $\rightarrow$ 程式啟動。
3.  程式呼叫 `CheckTokenMembership` $\rightarrow$ 確認使用者是 **Admin** $\rightarrow$ 印出拒絕訊息並退出。

要拿到 Flag，必須設法**同時滿足**兩者：讓 Windows 啟動程式，但讓程式認為我們只是 **普通使用者 (Invoker)**。

## 🚀 3. 漏洞利用 (Exploitation)

我們使用了 Windows 應用程式相容性層 (Compatibility Layer) 的環境變數後門：**`__COMPAT_LAYER = "RunAsInvoker"`**。

這個變數會告訴 Windows 的應用程式載入器 (Loader)：**無視該程式 Manifest 中的 `requireAdministrator` 要求**，直接以當前啟動者的權限等級執行。

### 執行指令：
```powershell
# 在 PowerShell 中暫時設置環境變數並執行
$env:__COMPAT_LAYER = "RunAsInvoker"; .\ck_44d7b697c2428478108478ad0755ede2.exe
```

## 🚩 4. 最終結果
由於我們成功以「非管理員」身分啟動了程式，程式內部的 `CheckTokenMembership` 檢查失敗（回傳 False），進而進入了隱藏的 Flag 分支。

**Flag:**
`Flag{n0t_aDm1n_but_priv1leged}`
