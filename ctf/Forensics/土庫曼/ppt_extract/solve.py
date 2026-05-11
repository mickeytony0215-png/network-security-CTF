import xml.etree.ElementTree as ET
import glob

# 定義 PPTX XML 的 Namespace
namespaces = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'
}

# 遍歷所有 slide 的 XML 檔
for filepath in glob.glob('ppt/slides/slide*.xml'):
    print(f"\n========== 正在分析: {filepath} ==========")
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # 尋找所有的文字段落 (Paragraph)
        for p in root.findall('.//a:p', namespaces):
            # 尋找段落中的所有文字區塊 (Run)
            for r in p.findall('a:r', namespaces):
                # 取得文字內容
                t = r.find('a:t', namespaces)
                text_content = t.text if t is not None else ""
                
                if not text_content:
                    continue
                
                # 取得字體屬性
                rPr = r.find('a:rPr', namespaces)
                if rPr is not None and 'sz' in rPr.attrib:
                    # PPT 的 sz 是實際 pt 的 100 倍
                    pt_size = int(rPr.attrib['sz']) / 100
                else:
                    pt_size = "預設大小"
                
                # 印出結果
                print(f"字體大小: {str(pt_size):<6} | 文字: {text_content}")
                
    except Exception as e:
        print(f"解析錯誤: {e}")