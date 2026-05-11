import zipfile
import os
import glob

# 1. 設定初始大魔王檔名
original_file = "ao1Esena_3cdb472aa33b91bff72ce93a7feb910d"

def get_file_info():
    """ 找出目錄下的 Zip 檔與空檔案（密碼） """
    all_files = [f for f in os.listdir('.') if f not in ['script.py', original_file, 'solve.py']]
    zip_file = None
    pass_file = None
    
    for f in all_files:
        if zipfile.is_zipfile(f):
            zip_file = f
        elif os.path.getsize(f) == 0:
            pass_file = f
            
    return zip_file, pass_file

def main():
    if not os.path.exists(original_file):
        print(f"[-] 找不到原始檔案: {original_file}")
        return

    # 第一層通常沒密碼，先手動解開
    print("[*] 解開第一層...")
    with zipfile.ZipFile(original_file) as z:
        z.extractall()
    
    count = 1
    while True:
        # 尋找當前目錄下的 Zip 和 密碼檔
        target_zip, password_src = get_file_info()
        
        if not target_zip:
            print(f"\n[+] 沒偵測到新的 Zip，看來解完了！總共 {count} 層。")
            break
            
        if not password_src:
            # 有時候最後一層只有一個檔案（Flag 本身）
            print(f"\n[*] 剩餘檔案中沒有密碼檔，這可能是最後一關。")
            break

        print(f"\r[*] 第 {count} 層 | 處理: {target_zip} | 密碼: {password_src} ", end="")
        
        try:
            with zipfile.ZipFile(target_zip) as z:
                # 使用 password_src 作為密碼解壓
                z.extractall(pwd=password_src.encode())
            
            # 重要：解壓成功後，把「舊的」Zip 和「舊的」密碼刪掉，以免干擾下一圈
            os.remove(target_zip)
            os.remove(password_src)
            count += 1
            
        except Exception as e:
            print(f"\n[!] 解壓失敗: {e}")
            break

    # 顯示成果
    remaining = [f for f in os.listdir('.') if f not in ['script.py', original_file, 'solve.py']]
    print("\n[*] 剩下的檔案:", remaining)
    for f in remaining:
        with open(f, 'rb') as fin:
            head = fin.read(100)
            print(f"[*] {f} 內容預覽: {head}")
            # 自動嘗試 Base64
            try:
                import base64
                print(f"🚩 可能的 FLAG: {base64.b64decode(head).decode('utf-8', errors='ignore')}")
            except:
                pass

if __name__ == "__main__":
    main()