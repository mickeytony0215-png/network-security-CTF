u = "administrator"
k = [176, 214, 205, 246, 264, 255, 227, 237, 242, 244, 265, 270, 283]

password = ""
for i in range(len(u)):
    # 根據公式反推字元代碼
    char_code = k[i] - ord(u[i]) - (i * 10)
    password += chr(char_code)

print(f"解出的密碼是: {password}")