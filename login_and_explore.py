# -*- coding: utf-8 -*-
"""
版权保护中心登录 + 手动探索模式
登录成功后保持浏览器打开，等待用户操作
"""

import asyncio
import os
import hashlib
import requests

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
            import json
            data = json.loads(response.text)
            if data.get('err_no') == 0:
                return {'success': True, 'code': data.get('pic_str')}
            return {'success': False, 'error': data.get('err_str')}
        except Exception as e:
            return {'success': False, 'error': str(e)}


async def main():
    cjy = ChaojiyingClient('h3789766205', 'd94dpb1l', '977839')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_viewport_size({"width": 1400, "height": 900})
        
        try:
            print("打开登录页...")
            await page.goto('https://register.ccopyright.com.cn/login.html')
            await page.wait_for_timeout(2000)
            
            print("切换机构登录...")
            await page.click("text=机构")
            await page.wait_for_timeout(1000)
            
            print("输入账号密码...")
            await page.fill("input[placeholder*='用户名']", "山东万成")
            await page.fill("input[placeholder*='密码']", "AAaa1234567!")
            
            print("点击登录...")
            await page.click("button:has-text('立即登录')")
            await page.wait_for_timeout(3000)
            
            # 处理验证码
            for attempt in range(1, 10):
                if 'login' not in page.url.lower():
                    break
                    
                print(f"验证码尝试 {attempt}...")
                
                bg_img = await page.query_selector("img.yidun_bg-img") or await page.query_selector(".yidun_bg-img")
                if bg_img:
                    bg_box = await bg_img.bounding_box()
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
            
            if 'login' not in page.url.lower():
                print("\n✓ 登录成功！")
                print(f"当前页面: {page.url}")
                print("\n浏览器保持打开，请手动操作探索 R41 填报流程...")
                print("按 Ctrl+C 或关闭此窗口退出")
                
                # 持续截图保存页面状态
                screenshot_count = 0
                while True:
                    await page.wait_for_timeout(10000)  # 每10秒
                    screenshot_count += 1
                    screenshot_path = f'C:/Temp/r41_explore_{screenshot_count}.png'
                    await page.screenshot(path=screenshot_path)
                    print(f"已保存截图: {screenshot_path}")
                    
                    # 保存当前 URL
                    with open('C:/Temp/r41_current_url.txt', 'w') as f:
                        f.write(page.url)
            else:
                print("登录失败")
                
        except KeyboardInterrupt:
            print("\n退出")
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
