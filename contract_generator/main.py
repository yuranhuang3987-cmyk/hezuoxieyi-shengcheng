# -*- coding: utf-8 -*-
"""
软件著作权合作协议批量生成器
- 批量处理申请表
- 生成 .docx 格式
- 保持原模板格式
"""

import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime
import os
import shutil
import glob


# 天干称谓
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']


def get_party_title(index: int) -> str:
    """获取第N方的称谓"""
    if index < 10:
        return f'{TIAN_GAN[index]}方'
    else:
        return f'第{index + 1}方'


def parse_docx_tables(docx_path: str) -> List[List[List[str]]]:
    """解析 docx 文件中的所有表格"""
    with zipfile.ZipFile(docx_path, 'r') as zf:
        xml_content = zf.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        tables = []
        for tbl in tree.findall('.//w:tbl', ns):
            table_data = []
            for row in tbl.findall('.//w:tr', ns):
                row_data = []
                for cell in row.findall('.//w:tc', ns):
                    cell_text = ''
                    for text in cell.findall('.//w:t', ns):
                        if text.text:
                            cell_text += text.text
                    row_data.append(cell_text.strip())
                if row_data:
                    table_data.append(row_data)
            if table_data:
                tables.append(table_data)
        
        return tables


def extract_software_info_from_tables(tables: List[List[List[str]]]) -> Dict:
    """从表格中提取软件著作权申请信息"""
    
    info = {
        'software_name': '',
        'version': 'V1.0',
        'completion_date': '',
        'owners': []
    }
    
    for table in tables:
        for i, row in enumerate(table):
            if not row:
                continue
            
            if '软著名称' in row:
                if i + 1 < len(table):
                    data_row = table[i + 1]
                    if len(data_row) >= 1:
                        info['software_name'] = data_row[0]
                    if len(data_row) >= 3:
                        info['version'] = data_row[2] or 'V1.0'
                    if len(data_row) >= 4:
                        info['completion_date'] = data_row[3]
            
            if '著作权人信息' in ' '.join(row):
                header_idx = -1
                for j in range(i + 1, min(i + 3, len(table))):
                    if '公司/单位/个人名称' in ' '.join(table[j]):
                        header_idx = j
                        break
                
                if header_idx >= 0:
                    for j in range(header_idx + 1, len(table)):
                        data_row = table[j]
                        if '联系人信息' in ' '.join(data_row):
                            break
                        if not data_row or not data_row[0]:
                            break
                        
                        owner = {
                            'name': data_row[0] if len(data_row) > 0 else '',
                            'id_number': data_row[1] if len(data_row) > 1 else '',
                            'location': data_row[2] if len(data_row) > 2 else ''
                        }
                        if owner['name']:
                            info['owners'].append(owner)
    
    return info


def parse_date(date_str: str) -> datetime:
    """解析日期字符串"""
    formats = [
        '%Y年%m月%d日',
        '%Y-%m-%d',
        '%Y/%m/%d'
    ]
    
    date_str = date_str.strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            pass
    
    return datetime.now()


def format_date(dt: datetime) -> str:
    """格式化日期"""
    return f'{dt.year}年{dt.month}月{dt.day}日'


def create_contract_docx(info: Dict, template_path: str, output_path: str):
    """
    根据模板创建合作协议 .docx
    
    参数:
        info: 软件信息
        template_path: 模板文件路径
        output_path: 输出文件路径
    """
    
    # 计算协议日期
    completion_date = parse_date(info['completion_date'])
    contract_year = completion_date.year
    contract_month = completion_date.month - 3
    if contract_month <= 0:
        contract_month += 12
        contract_year -= 1
    contract_date = datetime(contract_year, contract_month, completion_date.day)
    contract_date_str = format_date(contract_date)
    
    # 软件全名
    software_full_name = f'{info["software_name"]}{info["version"]}'
    
    # 协议份数
    copy_count = len(info['owners']) + 1
    
    # 复制模板
    shutil.copy(template_path, output_path)
    
    # 修改 docx 内容
    with zipfile.ZipFile(output_path, 'r') as zf:
        # 读取 document.xml
        xml_content = zf.read('word/document.xml')
    
    # 替换占位符
    xml_str = xml_content.decode('utf-8')
    
    # 生成当事人列表
    parties_text = ''
    signatures_text = ''
    for i, owner in enumerate(info['owners']):
        party_title = get_party_title(i)
        parties_text += f'{party_title}：{owner["name"]}\n'
        signatures_text += f'{party_title}：\n'
    
    # 替换内容
    replacements = {
        '【软件名称】': software_full_name,
        '【份数】': str(copy_count),
        '【日期】': contract_date_str,
        '【当事人】': parties_text,
        '【签名】': signatures_text
    }
    
    for old, new in replacements.items():
        xml_str = xml_str.replace(old, new)
    
    # 如果模板没有占位符，直接替换整个段落内容
    # 这需要更复杂的处理...
    
    # 写回 docx
    with zipfile.ZipFile(output_path, 'w') as zf:
        # 复制所有文件，只替换 document.xml
        with zipfile.ZipFile(template_path, 'r') as src:
            for item in src.namelist():
                if item != 'word/document.xml':
                    zf.writestr(item, src.read(item))
        
        zf.writestr('word/document.xml', xml_str.encode('utf-8'))


def create_contract_from_scratch(info: Dict, output_path: str):
    """
    从头创建合作协议 .docx（不依赖模板）
    """
    
    # 计算协议日期
    completion_date = parse_date(info['completion_date'])
    contract_year = completion_date.year
    contract_month = completion_date.month - 3
    if contract_month <= 0:
        contract_month += 12
        contract_year -= 1
    contract_date = datetime(contract_year, contract_month, completion_date.day)
    contract_date_str = format_date(contract_date)
    
    software_full_name = f'{info["software_name"]}{info["version"]}'
    copy_count = len(info['owners']) + 1
    
    # 生成当事人部分
    parties_xml = ''
    signatures_xml = ''
    
    for i, owner in enumerate(info['owners']):
        party_title = get_party_title(i)
        # 每个段落
        parties_xml += f'''
        <w:p>
            <w:pPr><w:rPr><w:b/></w:rPr></w:pPr>
            <w:r><w:t>{party_title}：</w:t></w:r>
        </w:p>
        <w:p>
            <w:r><w:t>{owner["name"]}</w:t></w:r>
        </w:p>'''
        
        signatures_xml += f'''
        <w:p>
            <w:r><w:t>{party_title}：</w:t></w:r>
        </w:p>
        <w:p><w:r><w:t></w:t></w:r></w:p>'''
    
    # 构建 document.xml
    document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
    <w:p><w:r><w:t>  合作开发协议书</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    {parties_xml}
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:t>经各方友好协商，就合作开发"{software_full_name}"订立本协议书，各方共同遵守：</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:t>1、各方的分工：各方负责软件的需求分析和设计框架，然后各方共同完成编程和调度工作。</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:t>2、软件开发完成后，共同负责组织鉴定以及办理软件著作权登记，其著作权均由合作方共同享有。</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:t>3、各方在没有统一意见下，不允许单方授权其它人，单方面不得将有关技术开发的任何秘密向第三方泄露。</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:t>4、合作各方在编写软件的过程中，不得有侵犯他人知识产权的行为，否则，应对外承担全部侵权责任。</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:t>5、合作各方之间如发生纠纷，应共同协商，本着有利于事业发展的原则予以解决。</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:t>6、协议自签订之日起生效，各方需自觉遵守各项条款。</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:t>7、本协议如有未尽事宜，应由合作人集体讨论补充或修改。补充和修改的内容与本协议具有同等效力。</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:t>8、本协议一式{copy_count}份，甲方留一份，其余几方留一份，交国家版权局备案一份。</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    {signatures_xml}
    <w:p><w:r><w:t>日期：{contract_date_str}</w:t></w:r></w:p>
</w:body>
</w:document>'''
    
    # 创建 .docx 文件
    with zipfile.ZipFile(output_path, 'w') as zf:
        # [Content_Types].xml
        zf.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>''')
        
        # _rels/.rels
        zf.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')
        
        # word/_rels/document.xml.rels
        zf.writestr('word/_rels/document.xml.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>''')
        
        # word/document.xml
        zf.writestr('word/document.xml', document_xml.encode('utf-8'))


def process_single_file(docx_path: str, output_dir: str) -> Dict:
    """
    处理单个申请表文件
    
    返回:
        处理结果
    """
    # 解析
    tables = parse_docx_tables(docx_path)
    info = extract_software_info_from_tables(tables)
    
    if not info['software_name']:
        return {
            'success': False,
            'error': '无法提取软件名称',
            'file': docx_path
        }
    
    if not info['owners']:
        return {
            'success': False,
            'error': '无法提取著作权人信息',
            'file': docx_path
        }
    
    # 生成输出文件名
    safe_name = info['software_name'].replace('/', '-').replace('\\', '-').replace(':', '-')
    output_path = os.path.join(output_dir, f'合作协议-{safe_name}.docx')
    
    # 创建协议
    create_contract_from_scratch(info, output_path)
    
    return {
        'success': True,
        'software_name': info['software_name'],
        'owners_count': len(info['owners']),
        'output_file': output_path,
        'file': docx_path
    }


def batch_process(input_dir: str, output_dir: str) -> List[Dict]:
    """
    批量处理目录下的所有申请表
    
    参数:
        input_dir: 输入目录（包含 .docx 申请表）
        output_dir: 输出目录
        
    返回:
        处理结果列表
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找所有 .docx 文件
    docx_files = glob.glob(os.path.join(input_dir, '*.docx'))
    
    results = []
    for docx_path in docx_files:
        print(f'处理: {os.path.basename(docx_path)}')
        result = process_single_file(docx_path, output_dir)
        results.append(result)
        
        if result['success']:
            print(f'  [OK] 生成: {os.path.basename(result["output_file"])}')
        else:
            print(f'  [FAIL] 失败: {result["error"]}')
    
    return results


# 主程序
if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("  软件著作权合作协议批量生成器")
    print("=" * 60)
    
    if len(sys.argv) > 2:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
    else:
        # 默认路径
        input_dir = 'C:/Temp/contracts/input'
        output_dir = 'C:/Temp/contracts/output'
    
    print(f"\n输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    results = batch_process(input_dir, output_dir)
    
    # 统计
    success_count = sum(1 for r in results if r['success'])
    print(f"\n处理完成: {success_count}/{len(results)} 成功")
    
    if success_count < len(results):
        print("\n失败的文件:")
        for r in results:
            if not r['success']:
                print(f"  - {os.path.basename(r['file'])}: {r['error']}")
