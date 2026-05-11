#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def solve():
    # 1. 原始 JavaScript 中的 Hex 混淆陣列 (_0x6e73797375)
    # 我們直接把這些 Hex 字串放入陣列，Python 會自動識別 \x 並轉為字元
    obfuscated_array = [
        "\x69\x6e\x64\x65\x78\x2e\x70\x68\x70",  # [0] index.php
        "\x23\x65\x72\x72\x6f\x72",              # [1] #error
        "\x68\x61",                              # [2] ha
        "\x6c\x6f\x63\x61\x74\x69\x6f\x6e",      # [3] location
        "\x23\x63\x70\x61\x73\x73",              # [4] #cpass
        "\x6b\x65\x72",                          # [5] ker
        "\x68\x72\x65\x66",                      # [6] href
        "\x3f\x6b\x65\x79\x3d",                  # [7] ?key=
        "",                                      # [8] (HTML 警報碼，略過)
        "\x63\x6c\x69\x63\x6b",                  # [9] click
        "\x76\x61\x6c",                          # [10] val
        "\x2e\x73\x75\x62\x6d\x69\x74\x5f\x62\x75\x74\x74\x6f\x6e", # [11] .submit_button
        "\x62\x6c\x61",                          # [12] bla
        "\x69\x6e\x64\x65\x78\x4f\x66",          # [13] indexOf
        "\x68\x74\x6d\x6c"                       # [14] html
    ]

    print("--- 正在還原字串池 ---")
    for i, s in enumerate(obfuscated_array):
        print(f"陣列索引 [{i:2}]: {s}")

    # 2. 模擬 JavaScript 的變數定義
    # _0x737461726a_2 = _0x6e73797375[12] + _0x6e73797375[12] + _0x6e73797375[12];
    bla = obfuscated_array[12]
    var2 = bla + bla + bla
    
    ker = obfuscated_array[5]
    ha = obfuscated_array[2]

    # 3. 模擬最終的密碼拼接邏輯 (if 判斷式內容)
    # _0x737461726a_1 == _0x6e73797375[5] + _0x6e73797375[5] + _0x737461726a_2 + _0x6e73797375[2] * 4
    password = ker + ker + var2 + (ha * 4)

    print("\n" + "="*30)
    print(f"解出的正確密碼為: {password}")
    print("="*30)

    # 4. 生成最終的 Flag URL 參考
    print(f"\n請在網頁輸入上述密碼，或直接訪問：")
    print(f"http://[題目網址]/?key={password}")

if __name__ == "__main__":
    solve()