import sys

def brainfuck_interpreter(code):
    # 初始化 30,000 個記憶體單元 (Cells)
    cells = [0] * 30000
    ptr = 0  # 記憶體指標
    pc = 0   # 程式計數器 (Program Counter)
    output = []

    # 1. 預處理：建立括號跳轉表，優化循環效率
    jump_table = {}
    stack = []
    for i, char in enumerate(code):
        if char == '[':
            stack.append(i)
        elif char == ']':
            start = stack.pop()
            jump_table[start] = i
            jump_table[i] = start

    # 2. 執行程式碼
    while pc < len(code):
        cmd = code[pc]

        if cmd == '>':
            ptr += 1
        elif cmd == '<':
            ptr -= 1
        elif cmd == '+':
            cells[ptr] = (cells[ptr] + 1) % 256
        elif cmd == '-':
            cells[ptr] = (cells[ptr] - 1) % 256
        elif cmd == '.':
            output.append(chr(cells[ptr]))
        elif cmd == ',':
            # 簡單處理輸入，如果沒有輸入則給 0
            cells[ptr] = ord(sys.stdin.read(1)) if sys.stdin.isatty() else 0
        elif cmd == '[':
            if cells[ptr] == 0:
                pc = jump_table[pc]
        elif cmd == ']':
            if cells[ptr] != 0:
                pc = jump_table[pc]

        pc += 1

    return "".join(output)

# 題目給的 Brainfuck 字串
bf_code = "-[------->+<]>---.--[--->+<]>.-----------.++++++.[----->+<]>.-[->+++<]>-.>+[--->++<]>+++.++++++.+++.+[->++++++<]>.[------>+<]>--.++++++++.+++++.---------------.++++++++++.+[-->+<]>.-----[->++<]>-.+++++++.-[--->+<]>+.[-->+<]>+++++++.++++++++.>--[-->+++<]>.建设"

if __name__ == "__main__":
    print("[*] 正在解譯 Brainfuck 代碼...")
    result = brainfuck_interpreter(bf_code)
    print("-" * 20)
    print(f"解密結果: {result}")
    print("-" * 20)