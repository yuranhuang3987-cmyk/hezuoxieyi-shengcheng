# -*- coding: utf-8 -*-
"""
软件著作权申请表解析器 v3
正确处理表格结构
"""

import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import re


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
        'short_name': '',
        'version': 'V1.0',
        'completion_date': '',
        'publish_date': '',
        'owners': [],
        'contact': {
            'name': '',
            'phone': '',
            'address': '',
            'email': ''
        }
    }
    
    for table in tables:
        for i, row in enumerate(table):
            if not row:
                continue
            
            # 检查是否是软著信息标题行
            if '软著名称' in row:
                # 下一行是数据
                if i + 1 < len(table):
                    data_row = table[i + 1]
                    if len(data_row) >= 1:
                        info['software_name'] = data_row[0]
                    if len(data_row) >= 2:
                        info['short_name'] = data_row[1]
                    if len(data_row) >= 3:
                        info['version'] = data_row[2] or 'V1.0'
                    if len(data_row) >= 4:
                        info['completion_date'] = data_row[3]
                    if len(data_row) >= 5:
                        info['publish_date'] = data_row[4]
            
            # 检查是否是著作权人信息
            if '著作权人信息' in ' '.join(row):
                # 找列标题行
                header_idx = -1
                for j in range(i + 1, min(i + 3, len(table))):
                    if '公司/单位/个人名称' in ' '.join(table[j]):
                        header_idx = j
                        break
                
                if header_idx >= 0:
                    # 数据从 header_idx + 1 开始
                    for j in range(header_idx + 1, len(table)):
                        data_row = table[j]
                        # 遇到联系人信息就停止
                        if '联系人信息' in ' '.join(data_row):
                            break
                        # 遇到空行或非数据行就停止
                        if not data_row or not data_row[0]:
                            break
                        # 跳过看起来像标题的行
                        if '公司' in data_row[0] and '营业执照' in str(data_row):
                            continue
                        
                        owner = {
                            'name': data_row[0] if len(data_row) > 0 else '',
                            'id_number': data_row[1] if len(data_row) > 1 else '',
                            'location': data_row[2] if len(data_row) > 2 else ''
                        }
                        if owner['name']:
                            info['owners'].append(owner)
            
            # 检查是否是联系人信息
            if '联系人信息' in ' '.join(row):
                # 联系人可能在后面的行中
                for j in range(i + 1, min(i + 5, len(table))):
                    data_row = table[j]
                    if not data_row:
                        continue
                    
                    row_text = ' '.join(data_row)
                    
                    # 公司名称行可能包含联系人姓名
                    if '公司/单位/个人名称' in row_text:
                        if len(data_row) >= 2 and data_row[1]:
                            info['contact']['name'] = data_row[1]
                        continue
                    
                    # 手机号码
                    if '手机号码' in row_text:
                        if len(data_row) >= 2:
                            info['contact']['phone'] = data_row[1]
                        elif len(data_row) >= 4:
                            info['contact']['phone'] = data_row[3]
                    
                    # 详细地址
                    if '详细地址' in row_text:
                        if len(data_row) >= 2:
                            info['contact']['address'] = data_row[1]
                    
                    # 邮箱
                    if '邮箱' in row_text:
                        if len(data_row) >= 2:
                            info['contact']['email'] = data_row[1]
    
    return info


def parse_application(docx_path: str) -> Dict:
    """解析申请表文档"""
    tables = parse_docx_tables(docx_path)
    return extract_software_info_from_tables(tables)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
    else:
        docx_path = '/home/huang777/.openclaw/media/inbound/蚯蚓堆肥体系中全氟类污染物迁移规律与分布特征分析系统---673808e2-e794-4ad6-bd8c-d756f017a69c.docx'
    
    print(f"解析文件: {docx_path}")
    print("=" * 60)
    
    info = parse_application(docx_path)
    
    print(f"软件名称: {info['software_name']}")
    print(f"版本号: {info['version']}")
    print(f"开发完成时间: {info['completion_date']}")
    print(f"发表时间: {info['publish_date']}")
    print(f"\n著作权人 ({len(info['owners'])}人):")
    for i, owner in enumerate(info['owners'], 1):
        print(f"  {i}. {owner['name']}")
        print(f"     证件号: {owner['id_number']}")
        print(f"     位置: {owner['location']}")
    
    print(f"\n联系人:")
    print(f"  姓名: {info['contact'].get('name', '-')}")
    print(f"  电话: {info['contact'].get('phone', '-')}")
    print(f"  地址: {info['contact'].get('address', '-')}")
    print(f"  邮箱: {info['contact'].get('email', '-')}")
