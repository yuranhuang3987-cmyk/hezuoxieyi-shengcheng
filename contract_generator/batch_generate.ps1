# -*- coding: utf-8 -*-
"""
合作协议批量生成器 - 弬叫 Word COM 保持模板格式
"""

import os
import sys
import glob
import zipfile
import shutil
from datetime import datetime


# 天干
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']


def get_party_title(index: int) -> str:
    if index < 10:
        return f'{TIAN_GAN[index]}方'
    else:
        return f'第{index + 1}方'


def parse_date(date_str: str) -> datetime:
    formats = [
        '%Y年%m月%d日',
        '%Y-%m-%d',
        '%Y.%m.%d'
    ]
    
    date_str = date_str.strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            pass
    
    return datetime.now()


def format_date(dt: datetime) -> str:
    return f'{dt.year}年{dt.month}月{dt.day}日'


def get_software_info(docx_path: str) -> Dict:
    """从申请表提取信息"""
    
    tables = parse_docx_tables(docx_path)
    return extract_so_info_from_tables(tables)


    
    # 计算协议日期
    completion_date = parse_date(info['completion_date'])
    contract_year = completion_date.year
    contract_month = completion_date.month - 3
    if contract_month <= 0:
        contract_month += 12
        contract_year -= 1
    contract_date = datetime(contract_year, contract_month, completion_date.day)
    
    # 软件全名
    software_full_name = f"{info['software_name']}{info['version']}"
    
    # 协议份数
    copy_count = len(info['owners']) + 1
    
    # 生成当事人部分
    parties_section = ''
    for i, owner in enumerate(info['owners']):
        party_title = get_party_title(i)
        parties_section += f'{party_title}：\n{owner["name"]}\n\n'
        party_signatures = ''
        for i, range(len(info['owners'])):
            party_title = get_party_title(i)
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


def select_template(owner_count: int, -> str:
    """根据著作权人数量选择合适的模板"""
    template_name = ''
    if owner_count <= 2:
        template_name = '合作协议-2方.doc'
    elif owner_count == 3:
        template_name = '合作协议-3方.doc'
    elif owner_count == 4:
        template_name = '合作协议-4方.doc'
    elif owner_count == 5:
        template_name = '合作协议-5方.doc'
    elif owner_count == 6:
        template_name = '合作协议-6方.doc'
    elif owner_count == 7:
        template_name = '合作协议-7方.doc'
    elif owner_count == 8:
        template_name = '合作协议-8方.doc'
    elif owner_count == 9:
        template_name = '合作协议-9方.doc'
    elif owner_count == 10:
        template_name = '合作协议-10方.doc'
    elif owner_count == 11:
        template_name = '合作协议-11方.doc'
    elif owner_count == 12:
        template_name = '合作协议-12方.doc'
    elif owner_count == 13:
        template_name = '合作协议-13方.doc'
    else:
        print(f"警告: 財书人数量 {owner_count} 超出模板范围")
        return None
    
    # 选择模板
    template_path = os.path.join(template_dir, template_name)
    if not os.path.exists(template_path):
        print(f"错误: 模板文件不存在: {template_path}")
        return None, None
    
    # 启动 Word
    word = win32.COMObject("Word.Application")
    word.Visible = False
    
    try:
        # 打开模板
        template_doc = word.Documents.Open(template_path)
        template_content = template_doc.Content.Text
        
        # 替换内容
        # 替换软件名称和版本
        template_content = template_content.replace('智能心理压力情绪疏导与调解平台V1.0', software_full_name)
        # 替换当事人
        # 构建新的当事人列表
        new_parties = ""
        for i, range(owner_count):
            new_parties += f"{get_party_title(i)}：{owner['name']}\r\n"
        
        # 替换签名
        new_signatures = ""
        for i in range(owner_count):
            new_signatures += f"{get_party_title(i)}：\r\n"
        
        # 替换份数
        old_copy_count = template_content.count('三份')
        new_copy_count = copy_count
        template_content = template_content.replace('三份', str(str(copy_count))
        
        # 替换日期
        contract_date_str = template_content = template_content.replace('2025-3-10', contract_date_str)
        
        # 另存为
        output_path = join(output_dir, f'合作协议-{software_name}.docx')
        
        # 保存
        template_doc.Save()
        template_doc.Save()
        word.Quit()
        
        return {
            'success': True,
            'software_name': info['software_name'],
            'owners_count': owner_count,
            'output_file': output_path,
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    
    finally:
        if word:
            word.Quit()
    
    return results


def batch_process(input_dir: str, output_dir: str, template_dir: str) -> List[Dict]:
    """批量处理申请表"""
    
    # 确保目录存在
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 获取所有 .docx 文件
    docx_files = glob.glob(os.path.join(input_dir, '*.docx'))
    
    if not docx_files:
        print(f"输入目录为空， {input_dir}")
        return []
    
    print(f"找到 {len(docx_files)} 个申请表文件")
    
    # 处理每个文件
    results = []
    for docx_path in docx_files:
        print(f"\n处理: {os.path.basename(docx_path)}")
        
        try:
            result = generate_contract(docx_path, output_dir, template_dir)
            results.append(result)
            
            if result['success']:
                print(f"  [OK] 生成: {os.path.basename(result['output_file'])}")
            else:
                print(f"  [FAIL] 失败: {result['error']}")
        else:
            print(f"  [FAIL] 跳过: {os.path.basename(docx_path)}")
        
    except Exception as e:
        print(f"  [FAIL] 错误: {e}")
        results.append({
            'success': False,
            'error': str(e),
            'file': docx_path
        })
    
    # 统计
    success_count = sum(1 for r['success'] for r in results)
    failed_count = len(results) - success_count
    
    return results


if __name__ == '__main__':
    # 测试
    if __name__ == '__main__':
        test_docx_path = '/home/huang777/.openclaw/media/inbound/蚯蚓堆肥体系中全氟类污染物迁移规律与分布特征分析系统---673808e2-e794-4ad6-bd8c-d756f017a69c.docx'
        
        # 复制到输入目录
        input_dir = 'C:/Temp/contracts/input'
        cp /home/huang777/.openclaw/workspace/contract_generator/sample_input/test.docx /home/huang777/.openclaw/workspace/contract_generator'
        
        # 运行
        os.chdir('/home/huang777/.openclaw/workspace/contract_generator')
        python3 batch_generate.py "C:/Temp/contracts/input" "C:/Temp/contracts/output" 2>&1
        
        # 检查结果
        print(f"\n生成文件:")
        print(f"  输入目录: {input_dir}")
        print(f"  输出目录: {output_dir}")
        print(f"  模板目录: {template_dir}")
        print()
        
        # 查找输入文件
        input_files = glob.glob(os.path.join(input_dir, '*.docx'))
        print(f"找到 {len(input_files)} 个申请表文件")
        
        if not input_files:
            print("没有找到申请表文件！")
            return
        
        # 处理每个文件
        for input_file in input_files:
            print(f"\n处理: {os.path.basename(input_file)}")
            result = process_single_file(input_file, output_dir, template_dir, word_app)
            results.append(result)
            
            if result['success']:
                print(f"  [OK] 生成: {os.path.basename(result['output_file'])}")
            else:
                print(f"  [FAIL] {result['error']}")
        
        # 总结
        print(f"\n完成! 成功: {sum(1 for r in results if r['success'])}/{len(results)}")
        if any(r['success'] for r in results if not r['success']:
            print(f"\n生成的文件:")
            for r in results:
                if r['success']:
                    print(f"  - {os.path.basename(r['output_file'])}")
        
    finally:
        if 'word' in locals():
            word = win32.ComObject("Word.Application")
            word.Quit()
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='软件著作权合作协议批量生成器')
    parser.add_argument('--input', '-i', help='输入目录')
    parser.add_argument('--output', '-o', help='输出目录')
    parser.add_argument('--templates', '-t', help='模板目录')
    
    args = parser.parse_args()
    
    main(args.input, args.output, args.templates)
