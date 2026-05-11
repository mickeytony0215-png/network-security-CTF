import requests
import re

target_url = "http://idsctf.mis.nsysu.edu.tw:9019/checksum.php"

print("[*] 正在從 GitHub Raw 下載真正的 SHA-1 碰撞檔案 (無反爬蟲)...")

# 來自學者 Marc Stevens 的官方檢測工具 Repo 內的真實測試檔
url_1 = "https://raw.githubusercontent.com/cr-marcstevens/sha1collisiondetection/master/test/shattered-1.pdf"
url_2 = "https://raw.githubusercontent.com/cr-marcstevens/sha1collisiondetection/master/test/shattered-2.pdf"

try:
    print("[*] 正在下載 shattered-1.pdf ...")
    pdf1 = requests.get(url_1).content
    print("[*] 正在下載 shattered-2.pdf ...")
    pdf2 = requests.get(url_2).content
    
    print(f"[*] 下載成功！檔案大小分別為: {len(pdf1)} bytes 與 {len(pdf2)} bytes")
    
    # 真正的 SHAttered 檔案大小必須是 422435 bytes
    if len(pdf1) != 422435 or len(pdf2) != 422435:
        print("[!] 檔案大小不正確，下載可能又被中斷了。請改用瀏覽器手動下載。")
        exit()
        
    print("[*] 正在將這兩份二進位檔案發送至 CTF 伺服器...")
    
    # 使用 multipart/form-data 無損發送，欺騙 $_POST 變數
    multipart_data = {
        'object1': (None, pdf1),
        'object2': (None, pdf2)
    }
    
    response = requests.post(target_url, files=multipart_data)
    
    print("\n[*] 伺服器回應：")
    print("-" * 40)
    
    if "flag{" in response.text:
        print("🎉 成功達成 SHA-1 密碼學碰撞！")
        flag = re.findall(r'flag\{.*?\}', response.text)
        print(f"🚩 擷取到 Flag: {flag[0] if flag else '請自行在下方尋找'}")
    else:
        print("[-] 還是沒有 Flag，請檢查輸出的 Hash 值。")
        
    print("\n[完整 HTML 回應]")
    print(response.text)
    print("-" * 40)
    
except Exception as e:
    print(f"[!] 發生錯誤: {e}")