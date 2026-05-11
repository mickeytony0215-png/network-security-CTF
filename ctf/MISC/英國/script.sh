#!/bin/bash

ORIGINAL_FILE="ao1Esena_3cdb472aa33b91bff72ce93a7feb910d"
count=0
CHECKPOINT=100  # 每 100 層輸出一次
PREV_SIZE=0

echo "[*] 開始極速拆彈模式，目標：$ORIGINAL_FILE"

# 取得初始大小
if [ -f "$ORIGINAL_FILE" ]; then
    PREV_SIZE=$(stat -c %s "$ORIGINAL_FILE")
    echo "[*] 初始檔案大小: $PREV_SIZE bytes"
fi

# 第一層先解開
unzip -q -o "$ORIGINAL_FILE"

while true; do
    # 尋找當前目錄下的 Zip 和空檔案 (排除原始檔和腳本)
    ZIP_FILE=$(file * | grep "Zip archive" | grep -v "$ORIGINAL_FILE" | cut -d: -f1 | head -n 1)
    PASS_FILE=$(file * | grep "empty" | cut -d: -f1 | head -n 1)

    if [ -z "$ZIP_FILE" ] || [ -z "$PASS_FILE" ]; then
        echo -e "\n[+] 停止！解壓程序結束。總共解開了 $count 層。"
        break
    fi

    # 執行解壓
    if unzip -q -o -P "$PASS_FILE" "$ZIP_FILE"; then
        count=$((count + 1))
        
        # 定點輸出進度與大小變動
        if (( count % CHECKPOINT == 0 )); then
            CUR_SIZE=$(stat -c %s "$ZIP_FILE")
            DIFF=$((PREV_SIZE - CUR_SIZE))
            echo -e "\n[Checkpoint] 第 $count 層 | 當前大小: $CUR_SIZE bytes | 較上次紀錄縮減: $DIFF bytes"
            PREV_SIZE=$CUR_SIZE
        else
            echo -ne "\r[*] 目前進度：第 $count 層 | 處理中: $ZIP_FILE "
        fi
        
        # 刪除舊檔案
        rm "$ZIP_FILE" "$PASS_FILE"
    else
        echo -e "\n[-] 解壓失敗，發生在第 $count 層。"
        break
    fi
done

echo -e "\n[*] 剩餘檔案檢查："
ls -F