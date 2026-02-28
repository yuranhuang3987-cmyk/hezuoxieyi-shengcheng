from docx import Document
from docx.oxml.ns import qn

doc = Document(r'C:\Temp\contracts\中安-合作协议\合作协议-2方.docx')
body = doc.element.body
paras = body.findall(qn('w:p'))

print('模板段落分析:')
found_first = False
for i, para in enumerate(paras):
    text = ''.join(t.text for t in para.findall('.//' + qn('w:t')) if t.text)
    text = text.strip()
    
    if text == '甲方：':
        if found_first:
            print(f'{i:2d}: {text} <-- 第二个甲方（签名部分）')
        else:
            print(f'{i:2d}: {text} <-- 第一个甲方（开头）')
            found_first = True
    elif text:
        print(f'{i:2d}: {text[:40]}')
    else:
        print(f'{i:2d}: [空]')
