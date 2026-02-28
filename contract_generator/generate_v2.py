# -*- coding: utf-8 -*-
"""
合作协议批量生成器 - python-docx 版本
使用模板 .docx 文件，保持原格式
"""

import os
import sys
import glob
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from copy import deepcopy

# 添加 Windows Python 路径
sys.path.insert(0, r'C:\Users\yuran\AppData\Local\Programs\Python\Python37\Lib\site-packages')

try:
    from docx import Document
    from docx.shared import Pt
except ImportError:
    print("请先安装 python-docx: pip install python-docx")
    sys.exit(1)


# 天干
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']


def get_party_title(index: int) -> str:
    """获取第N方的称谓"""
    if index < 10:
        return f'{TIAN_GAN[index]}方'
    else:
        return f'第{index + 1}方'


def parse_date(date_str: str) -> datetime:
    """解析日期字符串"""
    date_str = date_str.strip()
    if '年' in date_str and '月' in date_str and '日' in date_str:
        try:
            parts = date_str.replace('年', ' ').replace('月', ' ').replace('日', '').split()
            return datetime(int(parts[0]), int(parts[1]), int(parts[2]))
        except:
            pass
    return datetime.now()


def calc_contract_date(completion_str: str) -> str:
    """计算协议日期（开发完成时间 - 3个月）"""
    dt = parse_date(completion_str)
    y, m = dt.year, dt.month - 3
    if m <= 0:
        m += 12
        y -= 1
    return f'{y}年{m}月{dt.day}日'


def parse_docx_tables(docx_path: str) -> list:
    """解析 docx 文件中的表格"""
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    tables = []
    with zipfile.ZipFile(docx_path, 'r') as zf:
        xml_content = zf.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        
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


def extract_info(tables: list) -> dict:
    """从表格提取信息"""
    info = {
        'software_name': '',
        'version': 'V1.0',
        'completion_date': '',
        'owners': []
    }
    
    for table in tables:
        for i in range(len(table)):
            row = table[i]
            row_text = ' '.join(row)
            
            # 软著信息
            if '软著名称' in row_text and i + 1 < len(table):
                data = table[i + 1]
                info['software_name'] = data[0] if data else ''
                info['version'] = data[2] if len(data) > 2 and data[2] else 'V1.0'
                info['completion_date'] = data[3] if len(data) > 3 else ''
            
            # 著作权人信息
            if '著作权人信息' in row_text:
                for j in range(i + 1, min(i + 3, len(table))):
                    if '公司/单位' in ' '.join(table[j]):
                        header_idx = j
                        for k in range(header_idx + 1, len(table)):
                            r = table[k]
                            if '联系人' in ' '.join(r) or not r or not r[0]:
                                break
                            if '公司' in r[0] or '营业执照' in r[0]:
                                continue
                            info['owners'].append({
                                'name': r[0],
                                'id_number': r[1] if len(r) > 1 else '',
                                'location': r[2] if len(r) > 2 else ''
                            })
                        break
    
    return info


def replace_text_in_paragraph(paragraph, old_text: str, new_text: str):
    """在段落中替换文本"""
    if old_text in paragraph.text:
        # 需要遍历所有 runs 来保持格式
        full_text = paragraph.text
        for run in paragraph.runs:
            if old_text in run.text:
                run.text = run.text.replace(old_text, new_text)
            elif run.text:
                # 可能文本分布在多个 run 中
                pass
        
        # 如果上面的方法没成功，直接替换整个段落
        if old_text in paragraph.text:
            # 保存第一个 run 的格式
            if paragraph.runs:
                first_run = paragraph.runs[0]
                for run in paragraph.runs:
                    run.text = ''
                first_run.text = full_text.replace(old_text, new_text)


def generate_contract(app_path: str, template_dir: str, output_dir: str) -> dict:
    """生成合作协议"""
    
    # 提取信息
    tables = parse_docx_tables(app_path)
    info = extract_info(tables)
    
    if not info['software_name']:
        return {'success': False, 'error': '无法提取软件名称'}
    if not info['owners']:
        return {'success': False, 'error': '无法提取著作权人'}
    
    owner_count = len(info['owners'])
    template_path = os.path.join(template_dir, f'合作协议-{owner_count}方.docx')
    
    if not os.path.exists(template_path):
        return {'success': False, 'error': f'模板不存在: {owner_count}方'}
    
    # 计算日期和份数
    contract_date = calc_contract_date(info['completion_date'])
    software_full = f"{info['software_name']}{info['version']}"
    copy_count = owner_count + 1
    
    # 打开模板
    doc = Document(template_path)
    
    # 替换软件名称
    old_software = '智能心理压力情绪疏导与调解平台V1.0'
    
    # 替换日期
    old_date = '2025-3-10'
    
    # 模板中的示例名字
    sample_names = ['王红梅', '汪庆军', '吴六韬', '赖羽羽', '刘茜茜', 
                    '丁姿慧', '刘澈', '曹冬梅', '谢奇秀', '钟海玲']
    
    # 遍历所有段落进行替换
    for para in doc.paragraphs:
        # 替换软件名称
        if old_software in para.text:
            replace_text_in_paragraph(para, old_software, software_full)
        
        # 替换日期
        if old_date in para.text:
            replace_text_in_paragraph(para, old_date, contract_date)
        
        # 替换当事人名字
        for i, owner in enumerate(info['owners']):
            if i < len(sample_names):
                if sample_names[i] in para.text:
                    replace_text_in_paragraph(para, sample_names[i], owner['name'])
        
        # 替换份数
        num_chars = ['三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二', '十三', '十四']
        for nc in num_chars:
            old_count = f'{nc}份'
            if old_count in para.text:
                replace_text_in_paragraph(para, old_count, f'{copy_count}份')
    
    # 保存
    safe_name = info['software_name'].replace('/', '-').replace('\\', '-').replace(':', '-')
    output_path = os.path.join(output_dir, f'合作协议-{safe_name}.docx')
    doc.save(output_path)
    
    return {
        'success': True,
        'software_name': info['software_name'],
        'owners_count': owner_count,
        'output_file': output_path
    }


def batch_process(input_dir: str, output_dir: str, template_dir: str):
    """批量处理"""
    
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找申请表
    files = glob.glob(os.path.join(input_dir, '*.docx'))
    
    if not files:
        print(f"没有找到申请表文件: {input_dir}")
        return
    
    print(f"找到 {len(files)} 个申请表文件")
    
    results = []
    for f in files:
        print(f"\n处理: {os.path.basename(f)}")
        
        try:
            result = generate_contract(f, template_dir, output_dir)
            results.append(result)
            
            if result['success']:
                print(f"  [OK] 生成: {os.path.basename(result['output_file'])}")
            else:
                print(f"  [FAIL] {result['error']}")
        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({'success': False, 'error': str(e)})
    
    # 统计
    success = sum(1 for r in results if r.get('success'))
    print(f"\n处理完成! 成功: {success}/{len(results)}")
    
    return results


if __name__ == '__main__':
    print("=" * 50)
    print("  软件著作权合作协议批量生成器")
    print("  python-docx 版本")
    print("=" * 50)
    
    # 路径
    input_dir = r'C:\Temp\contracts\input'
    output_dir = r'C:\Temp\contracts\output'
    template_dir = r'C:\Temp\contracts\中安-合作协议'
    
    print(f"\n输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"模板目录: {template_dir}")
    print()
    
    batch_process(input_dir, output_dir, template_dir)
