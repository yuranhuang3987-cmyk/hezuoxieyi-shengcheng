# -*- coding: utf-8 -*-
"""
版权保护中心登录 - Playwright 版本
"""

import asyncio
import os
import time
import hashlib
import requests

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
        self.session.trust_env = False  # 忽略系统代理
        # 完全禁用代理
        self.session.proxies = {}
        self.session.headers.update({'Connection': 'close'})

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
            try:
                data = json.loads(result)
                if data.get('err_no') == 0:
                    return {'success': True, 'code': data.get('pic_str')}
                else:
                    return {'success': False, 'error': data.get('err_str', result)}
            except:
                return {'success': False, 'error': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}


async def login():
    """执行登录"""
    cjy = ChaojiyingClient(username='h3789766205', password='d94dpb1l', soft_id='977839')
    
    login_url = 'https://register.ccopyright.com.cn/login.html'
    username = "山东万成"
    password = "AAaa1234567!"
    
    print("=" * 50)
    print("  版权保护中心登录 - Playwright v2")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        try:
            print("\n[1] 打开登录页...")
            await page.goto(login_url)
            await page.wait_for_timeout(2000)
            
            print("[2] 切换到机构登录...")
            await page.click("text=机构")
            await page.wait_for_timeout(1000)
            
            print("[3] 输入账号密码...")
            await page.fill("input[placeholder*='用户名']", username)
            await page.fill("input[placeholder*='密码']", password)
            print(f"   用户名: {username}")
            
            print("[4] 点击登录...")
            await page.click("button:has-text('立即登录')")
            await page.wait_for_timeout(3000)
            
            print("[5] 等待验证码...")
            await page.wait_for_selector(".yidun_popup", timeout=5000)
            
            # 尝试最多10次
            for attempt in range(1, 11):
                print(f"\n{'='*40}")
                print(f"第 {attempt} 次尝试")
                print('='*40)
                
                # 获取背景图
                bg_img = await page.query_selector("img.yidun_bg-img")
                if not bg_img:
                    bg_img = await page.query_selector(".yidun_bg-img")
                
                if not bg_img:
                    print("未找到背景图")
                    await page.wait_for_timeout(1000)
                    continue
                
                # 截取背景图
                bg_box = await bg_img.bounding_box()
                print(f"背景图: x={bg_box['x']:.0f}, y={bg_box['y']:.0f}, w={bg_box['width']:.0f}, h={bg_box['height']:.0f}")
                
                bg_screenshot = await page.screenshot(clip={
                    'x': bg_box['x'],
                    'y': bg_box['y'],
                    'width': bg_box['width'],
                    'height': bg_box['height']
                })
                
                # 识别验证码
                print("发送超级鹰识别...")
                result = cjy.post_pic(bg_screenshot, 9101)
                
                if not result['success']:
                    print(f"识别失败: {result.get('error')}")
                    await page.wait_for_timeout(1500)
                    continue
                
                coord_str = result['code']
                print(f"识别结果: {coord_str}")
                
                # 解析坐标 (格式: "x,y")
                parts = coord_str.split(',')
                gap_x = int(parts[0])
                
                # 计算目标位置（屏幕坐标）
                # 截图坐标 = 屏幕坐标 - bg_box['x']
                # 所以: 屏幕坐标 = 截图坐标 + bg_box['x']
                target_x = bg_box['x'] + gap_x
                
                print(f"缺口截图位置: {gap_x}px")
                print(f"缺口屏幕位置: {target_x:.0f}px")
                
                # 找滑块图标（要拖动的那个小图标）
                slider_icon = await page.query_selector(".yidun_slider__icon")
                if not slider_icon:
                    # 尝试其他选择器
                    slider_icon = await page.query_selector(".yidun_slider i, .yidun-slider__icon")
                
                if not slider_icon:
                    print("未找到滑块图标")
                    await page.wait_for_timeout(1500)
                    continue
                
                icon_box = await slider_icon.bounding_box()
                icon_x = icon_box['x'] + icon_box['width'] / 2
                icon_y = icon_box['y'] + icon_box['height'] / 2
                
                print(f"滑块图标: x={icon_x:.0f}, y={icon_y:.0f}")
                
                # 计算拖动距离
                drag_distance = target_x - icon_x
                print(f"拖动距离: {drag_distance:.0f}px")
                
                if abs(drag_distance) < 20:
                    print("距离太短，可能识别错误")
                    await page.wait_for_timeout(1500)
                    continue
                
                # 执行拖动
                print("开始拖动...")
                
                # 移动到滑块图标
                await page.mouse.move(icon_x, icon_y)
                await page.wait_for_timeout(100)
                
                # 按下
                await page.mouse.down()
                await page.wait_for_timeout(150)
                
                # 分步拖动（模拟人类）
                steps = 35
                moved = 0
                for i in range(steps):
                    progress = (i + 1) / steps
                    # 使用缓动函数：先快后慢
                    eased = progress * progress * (3 - 2 * progress)  # smoothstep
                    current_x = icon_x + drag_distance * eased
                    y_jitter = 2 * ((i * 7 % 5) - 2) / 5  # 轻微抖动
                    
                    await page.mouse.move(current_x, icon_y + y_jitter)
                    moved = current_x - icon_x
                    await page.wait_for_timeout(10)
                
                # 确保到达目标
                await page.mouse.move(target_x, icon_y)
                await page.wait_for_timeout(200)
                
                # 释放
                await page.mouse.up()
                print(f"拖动完成，移动了 {moved:.0f}px")
                
                # 等待验证结果
                await page.wait_for_timeout(2500)
                
                # 检查是否成功
                current_url = page.url
                if 'login' not in current_url.lower():
                    print("\n" + "="*50)
                    print("  登录成功！")
                    print("="*50)
                    print(f"当前页面: {current_url}")
                    
                    # 截图保存
                    await page.screenshot(path='C:\\Temp\\login_success_final.png')
                    print("已保存截图: C:\\Temp\\login_success_final.png")
                    
                    await page.wait_for_timeout(10000)
                    await browser.close()
                    return True
                
                # 检查验证码弹框
                popup = await page.query_selector(".yidun_popup")
                if not popup:
                    print("验证码弹框消失")
                    await page.wait_for_timeout(2000)
                    if 'login' not in page.url.lower():
                        print("\n>>> 登录成功!")
                        await browser.close()
                        return True
                
                print("验证未通过，准备重试...")
                
                # 尝试刷新验证码
                refresh = await page.query_selector(".yidun_refresh")
                if refresh:
                    await refresh.click()
                    await page.wait_for_timeout(1500)
            
            print("\n达到最大尝试次数，请手动完成...")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        
        await browser.close()
        return False


if __name__ == '__main__':
    asyncio.run(login())
