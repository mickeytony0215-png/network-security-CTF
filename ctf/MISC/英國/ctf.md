# CTF Write-up: 奪取_英國 - Oops, your file is encrypted

| 分數 | 分類 | 核心技術 |
| :--- | :--- | :--- |
| 40 Pts | MISC | 多層嵌套壓縮檔、自動化腳本 (Bash/Python)、環境偵察 |

## 1. 題目描述
題目提供一個名為 `ao1Esena_...` 的壓縮檔，背景模擬 **WannaCry** 勒索軟體。提示提到：「You need to **bash on** with this encrypted file.」，並暗示可以支付 1 Bitcoin 作為贖金。

## 2. 偵查階段
### 初步分析
透過 `file` 指令確認原始檔案格式：
```bash
file ao1Esena_3cdb472aa33b91bff72ce93a7feb910d
# 結果: Zip archive data
```

### 規律發現
1.  **第一層**：解壓後獲得一個 Zip 檔 (`fohpaW2i`) 與一個空檔案 (`wo6Eenai`)。
2.  **密碼邏輯**：嘗試多種密碼（如 WannaCry 常見密碼）失敗後，發現 **「同層級空檔案之檔名」** 即為 **「該層 Zip 檔之解壓密碼」**。
3.  **諧音提示**：題目中的「bash on」即為 **Base64** 的諧音。

## 3. 攻擊過程 (Automation)
由於手動解壓至第四層後發現仍有無窮無盡的 Zip，確認此題為 **「深度嵌套壓縮檔 (Deeply Nested ZIP)」**，必須撰寫自動化腳本處理。

### 解題腳本 (Bash)
為了監控解壓進度與檔案縮減狀況，編寫具備計數器與大小觀測功能的腳本：

```bash
#!/bin/bash
ORIGINAL_FILE="ao1Esena_3cdb472aa33b91bff72ce93a7feb910d"
count=0
PREV_SIZE=$(stat -c %s "$ORIGINAL_FILE")

unzip -q -o "$ORIGINAL_FILE"

while true; do
    # 尋找 Zip 檔與密碼檔 (empty file)
    ZIP_FILE=$(file * | grep "Zip archive" | grep -v "$ORIGINAL_FILE" | cut -d: -f1 | head -n 1)
    PASS_FILE=$(file * | grep "empty" | cut -d: -f1 | head -n 1)

    if [ -z "$ZIP_FILE" ]; then break; fi

    # 執行解壓並計數
    if unzip -q -o -P "$PASS_FILE" "$ZIP_FILE"; then
        count=$((count + 1))
        # 每 100 層印出大小變動
        if (( count % 100 == 0 )); then
            CUR_SIZE=$(stat -c %s "$ZIP_FILE")
            echo "第 $count 層 | 當前大小: $CUR_SIZE bytes"
        fi
        rm "$ZIP_FILE" "$PASS_FILE"
    else
        break
    fi
done
```

## 4. 最終奪取 Flag
在經歷 **9487 層** 解壓後，腳本停止。最終目錄下出現一個名為 `flag` 的檔案。

### 獲取 Flag
```bash
cat flag
# FLAG{NOW_U_kn0W_hOw_to_write_a_script_TO_Decrypt}
```

## 5. 總結與心得
* **自動化是關鍵**：當層數超過 10 層時，手動操作已不具備效率，需立即轉換思維編寫腳本。
* **環境清理**：在自動化過程中，需確保及時刪除舊有的 `Zip` 與 `Password` 檔案，避免腳本誤抓造成 `Bad Password` 錯誤。
* **諧音梗與主題**：CTF 題目常結合時事（WannaCry）與諧音（bash on = Base64），細心的訊息偵察能節省大量時間。