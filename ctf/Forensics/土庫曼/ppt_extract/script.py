import re

# 讀取 Slide 1 的 XML
with open('ppt/slides/slide1.xml', 'r', encoding='utf-8') as f:
    data = f.read()

# 用正規表達式抓取 sz (大小) 和對應的 a:t (文字)
# 在 PPT 裡，sz 通常是實際 pt 數值的 100 倍
matches = re.findall(r'sz="(\d+)".*?<a:t>(.*?)</a:t>', data)

print("提取出的字元與大小：")
for sz, text in matches:
    print(f"字元: {text: <5} | sz數值: {sz}")