# -*- coding: utf-8 -*-
"""
版权保护中心 R41 填报流程探索
"""

import asyncio
import os
import time
import hashlib
import requests
import json

# 强制禁用所有代理
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']:
    os.environ.pop(key, None)
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

from playwright.async_api import async_playwright


class ChaojiyingClient:
    """超级鹰API客户端"""
    def __init__(self, username, password, soft_id):
        self.username = username
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.soft_id = soft_id
        self.base_url = 'https://upload.chaojiying.net/Upload/Processing.php'
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.proxies = {}

    def post_pic(self, img_data, codetype):
        params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
            'codetype': str(codetype),
        }
        files = {'userfile': ('captcha.jpg', img_data)}
        try:
            response = self.session.post(
                self.base_url, 
                data=params, 
                files=files, 
                timeout=30,
                proxies={'http': None, 'https': None}
            )
            result = response.text
            import json
            data = json.loads(result)
            if data.get('err_no') == 0:
                return {'success': True, 'code': data.get('pic_str')}
            else:
                return {'success': False, 'error': data.get('err_str', result)}
        except Exception as e:
            return {'success': False, 'error': str(e)}


async def explore_r41():
    """探索 R41 填报流程"""
    cjy = ChaojiyingClient(username='h3789766205', password='d94dpb1l', soft_id='977839')
    
    login_url = 'https://register.ccopyright.com.cn/login.html'
    username = "山东万成"
    password = "AAaa1234567!"
    
    print("=" * 60)
    print("  版权保护中心 R41 填报流程探索")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_viewport_size({"width": 1400, "height": 900})
        
        # 收集 API 请求
        api_requests = []
        
        async def log_request(request):
            if 'api' in request.url.lower() or 'register' in request.url.lower():
                api_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers)
                })
        
        page.on('request', log_request)
        
        try:
            # ========== 登录 ==========
            print("\n[1] 打开登录页...")
            await page.goto(login_url)
            await page.wait_for_timeout(2000)
            
            print("[2] 切换到机构登录...")
            await page.click("text=机构")
            await page.wait_for_timeout(1000)
            
            print("[3] 输入账号密码...")
            await page.fill("input[placeholder*='用户名']", username)
            await page.fill("input[placeholder*='密码']", password)
            
            print("[4] 点击登录...")
            await page.click("button:has-text('立即登录')")
            await page.wait_for_timeout(3000)
            
            # 处理验证码
            await page.wait_for_selector(".yidun_popup", timeout=5000)
            
            for attempt in range(1, 6):
                print(f"\n验证码尝试 {attempt}...")
                
                bg_img = await page.query_selector("img.yidun_bg-img")
                if not bg_img:
                    bg_img = await page.query_selector(".yidun_bg-img")
                
                if bg_img:
                    bg_box = await bg_img.bounding_box()
                    bg_screenshot = await page.screenshot(clip=bg_box)
                    
                    result = cjy.post_pic(bg_screenshot, 9101)
                    
                    if result['success']:
                        coord_str = result['code']
                        parts = coord_str.split(',')
                        gap_x = int(parts[0])
                        target_x = bg_box['x'] + gap_x
                        
                        slider = await page.query_selector(".yidun_slider__icon")
                        if slider:
                            slider_box = await slider.bounding_box()
                            slider_x = slider_box['x'] + slider_box['width'] / 2
                            slider_y = slider_box['y'] + slider_box['height'] / 2
                            
                            drag_distance = target_x - slider_x
                            
                            await page.mouse.move(slider_x, slider_y)
                            await page.mouse.down()
                            await page.wait_for_timeout(150)
                            
                            steps = 30
                            for i in range(steps):
                                progress = (i + 1) / steps
                                eased = 1 - (1 - progress) ** 2
                                current_x = slider_x + drag_distance * eased
                                await page.mouse.move(current_x, slider_y)
                                await page.wait_for_timeout(12)
                            
                            await page.mouse.up()
                            await page.wait_for_timeout(2000)
                            
                            if 'login' not in page.url.lower():
                                print("✓ 登录成功！")
                                break
                
                await page.wait_for_timeout(1500)
            
            # ========== 进入系统后探索 ==========
            print("\n[5] 探索主页结构...")
            await page.wait_for_timeout(2000)
            
            # 截图主页
            await page.screenshot(path='C:/Temp/r41_step1_homepage.png')
            print("已保存主页截图")
            
            # 获取页面内容
            page_content = await page.content()
            with open('C:/Temp/r41_homepage.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            print("已保存主页 HTML")
            
            # 查找 R41 相关入口
            print("\n[6] 查找 R41 登记入口...")
            
            # 尝试找登记/申请相关的链接
            r41_keywords = ['R41', '计算机软件', '软件登记', '著作权登记', '登记申请', '我要登记']
            
            links = await page.query_selector_all('a, button, [class*="menu"], [class*="nav"]')
            print(f"找到 {len(links)} 个可点击元素")
            
            # 收集所有链接文本和 href
            link_info = []
            for link in links:
                try:
                    text = await link.inner_text()
                    href = await link.get_attribute('href')
                    onclick = await link.get_attribute('onclick')
                    class_name = await link.get_attribute('class')
                    link_info.append({
                        'text': text.strip()[:50] if text else '',
                        'href': href,
                        'onclick': onclick,
                        'class': class_name
                    })
                except:
                    pass
            
            # 保存链接信息
            with open('C:/Temp/r41_links.json', 'w', encoding='utf-8') as f:
                json.dump(link_info, f, ensure_ascii=False, indent=2)
            print(f"已保存 {len(link_info)} 个链接信息")
            
            # 尝试点击可能的登记入口
            print("\n[7] 尝试进入登记页面...")
            
            # 常见的入口文本
            entry_texts = ['我要登记', '登记申请', '软件登记', '计算机软件著作权登记', 'R41', '申请登记']
            
            clicked = False
            for entry_text in entry_texts:
                try:
                    element = await page.query_selector(f'text={entry_text}')
                    if element:
                        print(f"找到入口: {entry_text}")
                        await element.click()
                        clicked = True
                        await page.wait_for_timeout(3000)
                        break
                except:
                    pass
            
            if not clicked:
                # 尝试找菜单
                print("尝试通过菜单导航...")
                menu_items = await page.query_selector_all('[class*="menu"] li, [class*="nav"] li, .el-menu-item')
                for item in menu_items:
                    try:
                        text = await item.inner_text()
                        if '登记' in text or '软件' in text or '申请' in text:
                            print(f"找到菜单项: {text}")
                            await item.click()
                            await page.wait_for_timeout(2000)
                            break
                    except:
                        pass
            
            # 截图当前状态
            await page.screenshot(path='C:/Temp/r41_step2_after_click.png')
            print("已保存点击后截图")
            
            # 保存当前页面 URL 和内容
            current_url = page.url
            print(f"\n当前页面: {current_url}")
            
            page_content = await page.content()
            with open('C:/Temp/r41_step2.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            # 查找表单元素
            print("\n[8] 分析表单结构...")
            form_elements = await page.query_selector_all('input, select, textarea')
            print(f"找到 {len(form_elements)} 个表单元素")
            
            form_info = []
            for elem in form_elements:
                try:
                    elem_type = await elem.get_attribute('type')
                    elem_name = await elem.get_attribute('name')
                    elem_id = await elem.get_attribute('id')
                    elem_placeholder = await elem.get_attribute('placeholder')
                    elem_class = await elem.get_attribute('class')
                    
                    # 获取关联的 label
                    label = None
                    if elem_id:
                        label_elem = await page.query_selector(f'label[for="{elem_id}"]')
                        if label_elem:
                            label = await label_elem.inner_text()
                    
                    form_info.append({
                        'type': elem_type,
                        'name': elem_name,
                        'id': elem_id,
                        'placeholder': elem_placeholder,
                        'class': elem_class,
                        'label': label
                    })
                except:
                    pass
            
            with open('C:/Temp/r41_form_fields.json', 'w', encoding='utf-8') as f:
                json.dump(form_info, f, ensure_ascii=False, indent=2)
            print(f"已保存 {len(form_info)} 个表单字段信息")
            
            # 保存 API 请求日志
            with open('C:/Temp/r41_api_requests.json', 'w', encoding='utf-8') as f:
                json.dump(api_requests, f, ensure_ascii=False, indent=2)
            print(f"已保存 {len(api_requests)} 个 API 请求")
            
            print("\n" + "=" * 60)
            print("探索完成！已保存以下文件：")
            print("  - r41_step1_homepage.png (主页截图)")
            print("  - r41_homepage.html (主页 HTML)")
            print("  - r41_links.json (所有链接)")
            print("  - r41_step2_after_click.png (点击后截图)")
            print("  - r41_step2.html (点击后 HTML)")
            print("  - r41_form_fields.json (表单字段)")
            print("  - r41_api_requests.json (API 请求)")
            print("=" * 60)
            
            # 保持浏览器打开，让用户观察
            print("\n浏览器保持打开，按 Ctrl+C 关闭...")
            await page.wait_for_timeout(300000)  # 5分钟
            
        except KeyboardInterrupt:
            print("\n用户中断")
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(explore_r41())
