#!/bin/bash

# 基於 HTML 原始碼定義的新路徑清單
# 包含 a, b, c, d, e, f, g, h, i, jj 以及隱藏的 flag.html
targets=("image/a" "image/b" "image/c" "image/d" "image/e" "image/f" "image/g" "image/h" "image/i" "image/jj" "flag.html")

BASE_URL="http://idsctf.mis.nsysu.edu.tw:9017"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

echo "[*] 開始針對 HTML 標籤路徑進行掃描..."
echo "--------------------------------------------------------------"

for path in "${targets[@]}"; do
    url="$BASE_URL/$path"
    echo ">>> 正在測試路徑: $path"
    
    # 使用完整的偽裝 Header 進行請求
    # -i 顯示 Header, -L 跟隨重導向, -s 靜音模式
    response=$(curl -s -i -A "$UA" -e "$BASE_URL/" \
        -H "X-Forwarded-For: 127.0.0.1" \
        -H "X-Real-IP: 127.0.0.1" \
        "$url")

    # 1. 檢查 Header 裡的 Flag 或異常資訊
    echo "$response" | grep -iE "Flag|Copyright|Notice|Set-Cookie"
    
    # 2. 檢查 Body 裡的隱藏註解或 {.*} 格式的 Flag
    echo "$response" | grep -iE "|\{[a-zA-Z0-9_-]+\}"

    # 3. 針對「國歌 (image/f)」或是同學說的「同顏色區塊」進行原始碼快速檢查
    if [[ "$path" == "image/f" ]]; then
        echo "[!] 偵測到國歌路徑，檢查是否有異常顏色代碼或隱藏標籤..."
        echo "$response" | grep -oE "color:#[0-9a-fA-F]{6}" | sort | uniq -c
    fi
    
    echo "--------------------------------------------------------------"
done

# 針對 flag.html 單獨進行完整下載檢查，避免漏掉
echo "[*] 嘗試完整提取 flag.html 內容..."
curl -s -A "$UA" -e "$BASE_URL/" "$BASE_URL/flag.html" > fetched_flag.html
echo "已存至 fetched_flag.html，請手動檢查原始碼。"