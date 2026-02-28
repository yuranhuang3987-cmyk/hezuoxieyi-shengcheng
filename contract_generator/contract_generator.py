# -*- coding: utf-8 -*-
"""
软件著作权合作协议生成器
从申请表提取信息，生成合作协议
"""

import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict
from datetime import datetime
import os


# 天干称谓（甲方、乙方、丙方...）
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
# 超过10人后的称谓
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
        'short_name': '',
        'version': 'V1.0',
        'completion_date': '',
        'publish_date': '',
        'owners': [],
        'contact': {}
    }
    
    for table in tables:
        for i, row in enumerate(table):
            if not row:
                continue
            
            # 软著信息
            if '软著名称' in row:
                if i + 1 < len(table):
                    data_row = table[i + 1]
                    if len(data_row) >= 1:
                        info['software_name'] = data_row[0]
                    if len(data_row) >= 3:
                        info['version'] = data_row[2] or 'V1.0'
                    if len(data_row) >= 4:
                        info['completion_date'] = data_row[3]
                    if len(data_row) >= 5:
                        info['publish_date'] = data_row[4]
            
            # 著作权人信息
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
    # 尝试多种格式
    formats = [
        '%Y年%m月%d日',
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y.%m.%d'
    ]
    
    date_str = date_str.strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            pass
    
    # 默认返回当前日期
    return datetime.now()


def format_date(dt: datetime) -> str:
    """格式化日期为中文格式"""
    return f'{dt.year}年{dt.month}月{dt.day}日'


def generate_contract(info: Dict) -> str:
    """
    生成合作协议内容
    
    参数:
        info: 包含软件信息的字典
        
    返回:
        协议文本
    """
    
    # 计算协议日期（开发完成时间 - 3个月）
    completion_date = parse_date(info['completion_date'])
    # 减3个月
    contract_year = completion_date.year
    contract_month = completion_date.month - 3
    if contract_month <= 0:
        contract_month += 12
        contract_year -= 1
    contract_date = datetime(contract_year, contract_month, completion_date.day)
    contract_date_str = format_date(contract_date)
    
    # 软件名称和版本
    software_full_name = f'{info["software_name"]}{info["version"]}'
    
    # 著作权人数量
    owner_count = len(info['owners'])
    
    # 协议份数 = 著作权人数 + 1（备案）
    copy_count = owner_count + 1
    
    # 生成当事人部分
    parties_section = ''
    party_signatures = ''
    
    for i, owner in enumerate(info['owners']):
        party_title = get_party_title(i)
        parties_section += f'{party_title}：\n{owner["name"]}\n\n'
        party_signatures += f'{party_title}：\n\n'
    
    # 生成协议正文
    contract = f'''  合作开发协议书

{parties_section}经各方友好协商，就合作开发"{software_full_name}"订立本协议书，各方共同遵守：

1、各方的分工：各方负责软件的需求分析和设计框架，然后各方共同完成编程和调度工作。

2、软件开发完成后，共同负责组织鉴定以及办理软件著作权登记，其著作权均由合作方共同享有。

3、各方在没有统一意见下，不允许单方授权其它人，单方面不得将有关技术开发的任何秘密向第三方泄露。

4、合作各方在编写软件的过程中，不得有侵犯他人知识产权的行为，否则，应对外承担全部侵权责任。

5、合作各方之间如发生纠纷，应共同协商，本着有利于事业发展的原则予以解决。

6、协议自签订之日起生效，各方需自觉遵守各项条款。

7、本协议如有未尽事宜，应由合作人集体讨论补充或修改。补充和修改的内容与本协议具有同等效力。

8、本协议一式{copy_count}份，甲方留一份，其余几方留一份，交国家版权局备案一份。

{party_signatures}日期：{contract_date_str}
'''
    
    return contract


def process_application(docx_path: str, output_dir: str = None) -> Dict:
    """
    处理申请表，生成合作协议
    
    参数:
        docx_path: 申请表文件路径
        output_dir: 输出目录
        
    返回:
        包含提取信息和生成结果的字典
    """
    
    # 解析申请表
    tables = parse_docx_tables(docx_path)
    info = extract_software_info_from_tables(tables)
    
    # 生成协议
    contract = generate_contract(info)
    
    # 保存
    if output_dir is None:
        output_dir = os.path.dirname(docx_path)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为文本文件
    output_file = os.path.join(output_dir, f'合作协议-{info["software_name"]}.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(contract)
    
    return {
        'info': info,
        'contract': contract,
        'output_file': output_file
    }


# 测试
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
    else:
        docx_path = '/home/huang777/.openclaw/media/inbound/蚯蚓堆肥体系中全氟类污染物迁移规律与分布特征分析系统---673808e2-e794-4ad6-bd8c-d756f017a69c.docx'
    
    print(f"处理文件: {docx_path}")
    print("=" * 60)
    
    result = process_application(docx_path, '/home/huang777/.openclaw/workspace/contract_generator/output')
    
    info = result['info']
    print(f"软件名称: {info['software_name']}")
    print(f"版本号: {info['version']}")
    print(f"开发完成时间: {info['completion_date']}")
    print(f"著作权人: {len(info['owners'])}人")
    for i, owner in enumerate(info['owners']):
        print(f"  {get_party_title(i)}: {owner['name']}")
    
    print("\n" + "=" * 60)
    print("生成的合作协议:")
    print("=" * 60)
    print(result['contract'])
    
    print(f"\n已保存到: {result['output_file']}")
