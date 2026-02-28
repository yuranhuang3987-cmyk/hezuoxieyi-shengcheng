# -*- coding: utf-8 -*-
"""
R41 表单结构深度分析
"""

import asyncio
import os
import hashlib
import requests
import json
import re

# 禁用代理
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(key, None)
os.environ['NO_PROXY'] = '*'

from playwright.async_api import async_playwright


class ChaojiyingClient:
    def __init__(self, username, password, soft_id):
        self.username = username
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.soft_id = soft_id
        self.base_url = 'https://upload.chaojiying.net/Upload/Processing.php'
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.proxies = {}

    def post_pic(self, img_data, codetype):
        params = {'user': self.username, 'pass2': self.password, 'softid': self.soft_id, 'codetype': str(codetype)}
        files = {'userfile': ('captcha.jpg', img_data)}
        try:
            response = self.session.post(self.base_url, data=params, files=files, timeout=30, proxies={'http': None, 'https': None})
            data = json.loads(response.text)
            if data.get('err_no') == 0:
                return {'success': True, 'code': data.get('pic_str')}
            return {'success': False, 'error': data.get('err_str')}
        except Exception as e:
            return {'success': False, 'error': str(e)}


async def analyze_form(page):
    """深度分析表单结构"""
    form_data = await page.evaluate('''() => {
        const result = {
            inputs: [],
            selects: [],
            textareas: [],
            buttons: [],
            uploadFields: [],
            steps: []
        };
        
        // 获取所有输入框
        document.querySelectorAll('input, select, textarea').forEach(el => {
            const info = {
                tag: el.tagName,
                type: el.type || el.tagName,
                name: el.name,
                id: el.id,
                placeholder: el.placeholder,
                value: el.value,
                required: el.required,
                class: el.className,
                label: ''
            };
            
            // 尝试获取关联的label
            if (el.id) {
                const label = document.querySelector(`label[for="${el.id}"]`);
                if (label) info.label = label.innerText.trim();
            }
            
            // 尝试从父元素获取label
            if (!info.label) {
                const parent = el.closest('.form-item, .el-form-item, .form-group');
                if (parent) {
                    const labelEl = parent.querySelector('label, .label, .el-form-item__label');
                    if (labelEl) info.label = labelEl.innerText.trim();
                }
            }
            
            if (el.tagName === 'INPUT') {
                result.inputs.push(info);
                if (el.type === 'file') {
                    result.uploadFields.push(info);
                }
            } else if (el.tagName === 'SELECT') {
                // 获取选项
                info.options = Array.from(el.options).map(opt => ({value: opt.value, text: opt.text}));
                result.selects.push(info);
            } else {
                result.textareas.push(info);
            }
        });
        
        // 获取按钮
        document.querySelectorAll('button, input[type="submit"], .btn, .el-button').forEach(el => {
            result.buttons.push({
                text: el.innerText || el.value,
                type: el.type,
                class: el.className,
                id: el.id
            });
        });
        
        // 尝试获取步骤条
        document.querySelectorAll('.steps, .el-steps, .step-item').forEach(el => {
            result.steps.push(el.innerText);
        });
        
        return result;
    }''');
    
    return form_data


async def main():
    cjy = ChaojiyingClient('h3789766205', 'd94dpb1l', '977839')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_viewport_size({"width": 1400, "height": 900})
        
        # 收集API请求
        api_calls = []
        
        async def log_response(response):
            if 'api' in response.url.lower() or 'register' in response.url.lower():
                try:
                    headers = dict(response.headers)
                    api_calls.append({
                        'url': response.url,
                        'status': response.status,
                        'method': response.request.method,
                        'headers': headers
                    })
                except:
                    pass
        
        page.on('response', log_response)
        
        try:
            print("=" * 60)
            print("  R41 表单结构深度分析")
            print("=" * 60)
            
            # 登录
            print("\n[1] 登录...")
            await page.goto('https://register.ccopyright.com.cn/login.html')
            await page.wait_for_timeout(2000)
            await page.click("text=机构")
            await page.wait_for_timeout(1000)
            await page.fill("input[placeholder*='用户名']", "山东万成")
            await page.fill("input[placeholder*='密码']", "AAaa1234567!")
            await page.click("button:has-text('立即登录')")
            await page.wait_for_timeout(3000)
            
            # 处理验证码
            for attempt in range(1, 10):
                if 'login' not in page.url.lower():
                    break
                bg_img = await page.query_selector("img.yidun_bg-img") or await page.query_selector(".yidun_bg-img")
                if bg_img:
                    bg_box = await bg_img.bounding_box()
                    if bg_box:
                        bg_screenshot = await page.screenshot(clip=bg_box)
                        result = cjy.post_pic(bg_screenshot, 9101)
                        if result['success']:
                            gap_x = int(result['code'].split(',')[0])
                            target_x = bg_box['x'] + gap_x
                            slider = await page.query_selector(".yidun_slider__icon")
                            if slider:
                                slider_box = await slider.bounding_box()
                                if slider_box:
                                    slider_x = slider_box['x'] + slider_box['width'] / 2
                                    slider_y = slider_box['y'] + slider_box['height'] / 2
                                    drag_distance = target_x - slider_x
                                    await page.mouse.move(slider_x, slider_y)
                                    await page.mouse.down()
                                    await page.wait_for_timeout(150)
                                    for i in range(30):
                                        progress = (i + 1) / 30
                                        eased = 1 - (1 - progress) ** 2
                                        await page.mouse.move(slider_x + drag_distance * eased, slider_y)
                                        await page.wait_for_timeout(12)
                                    await page.mouse.up()
                                    await page.wait_for_timeout(2000)
                await page.wait_for_timeout(1500)
            
            if 'login' in page.url.lower():
                print("登录失败")
                return
            
            print("✓ 登录成功")
            
            # 进入 R41 登记页面
            print("\n[2] 进入 R41 登记...")
            await page.goto('https://register.ccopyright.com.cn/r11.html')
            await page.wait_for_timeout(3000)
            
            # 分析当前页面
            print("\n[3] 分析 R41 表单结构...")
            current_url = page.url
            print(f"当前URL: {current_url}")
            
            # 截图
            await page.screenshot(path='C:/Temp/r41_analysis_1.png')
            
            # 获取表单结构
            form_data = await analyze_form(page)
            
            print(f"\n发现表单元素:")
            print(f"  - 输入框: {len(form_data['inputs'])} 个")
            print(f"  - 下拉框: {len(form_data['selects'])} 个")
            print(f"  - 文本域: {len(form_data['textareas'])} 个")
            print(f"  - 上传字段: {len(form_data['uploadFields'])} 个")
            print(f"  - 按钮: {len(form_data['buttons'])} 个")
            
            # 保存详细数据
            with open('C:/Temp/r41_form_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(form_data, f, ensure_ascii=False, indent=2)
            print("\n已保存表单结构到: r41_form_analysis.json")
            
            # 获取页面HTML
            html = await page.content()
            with open('C:/Temp/r41_form_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("已保存页面HTML到: r41_form_page.html")
            
            # 尝试点击下一步，分析多步骤表单
            print("\n[4] 分析多步骤流程...")
            step_count = 1
            max_steps = 10
            
            while step_count < max_steps:
                # 检查是否有"下一步"或"保存并下一步"按钮
                next_btns = await page.query_selector_all('button:has-text("下一步"), button:has-text("保存"), .el-button:has-text("下一")')
                
                if not next_btns:
                    break
                
                # 获取当前步骤信息
                step_info = await page.evaluate('''() => {
                    const steps = document.querySelectorAll('.el-step__title, .step-title');
                    return Array.from(steps).map(s => s.innerText);
                }''')
                
                print(f"\n步骤 {step_count}: {step_info}")
                
                # 分析当前步骤的表单
                current_form = await analyze_form(page)
                
                # 保存当前步骤数据
                with open(f'C:/Temp/r41_step{step_count}_form.json', 'w', encoding='utf-8') as f:
                    json.dump(current_form, f, ensure_ascii=False, indent=2)
                
                await page.screenshot(path=f'C:/Temp/r41_step{step_count}.png')
                
                # 点击下一步
                try:
                    await next_btns[0].click()
                    await page.wait_for_timeout(3000)
                    step_count += 1
                except:
                    break
            
            # 保存API调用
            with open('C:/Temp/r41_api_calls.json', 'w', encoding='utf-8') as f:
                json.dump(api_calls, f, ensure_ascii=False, indent=2)
            print(f"\n已保存 {len(api_calls)} 个API调用记录")
            
            print("\n" + "=" * 60)
            print("分析完成！生成以下文件:")
            print("  - r41_form_analysis.json (表单结构)")
            print("  - r41_form_page.html (页面HTML)")
            print("  - r41_step*_form.json (各步骤表单)")
            print("  - r41_step*.png (各步骤截图)")
            print("  - r41_api_calls.json (API调用)")
            print("=" * 60)
            
            # 保持浏览器打开
            print("\n浏览器保持打开，可手动操作...")
            await page.wait_for_timeout(300000)
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
