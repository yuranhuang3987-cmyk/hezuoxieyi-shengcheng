# -*- coding: utf-8 -*-
"""
中国版权保护中心登录自动化脚本 - v2 简化版
使用超级鹰打码平台识别网易易盾验证码
"""

import os
import time
import hashlib
import requests
from pathlib import Path

# 禁用系统代理
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'


class LoginType:
    """登录类型枚举"""
    PERSONAL = "个人用户"
    ORG_ADMIN = "机构管理员"
    ORG_EMPLOYEE = "机构员工"


class ChaojiyingClient:
    """超级鹰API客户端"""

    def __init__(self, username, password, soft_id):
        self.username = username
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.soft_id = soft_id
        self.base_url = 'https://upload.chaojiying.net/Upload/Processing.php'

    def post_pic(self, img_data, codetype):
        """上传图片进行识别"""
        params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
            'codetype': str(codetype),
        }
        files = {'userfile': ('captcha.jpg', img_data)}
        try:
            response = requests.post(self.base_url, data=params, files=files, timeout=30)
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


class CopyrightLoginBot:
    """版权保护中心登录机器人"""

    def __init__(self, username, password, login_type=LoginType.PERSONAL):
        self.login_url = 'https://register.ccopyright.com.cn/login.html'
        self.login_username = username
        self.login_password = password
        self.login_type = login_type
        self.cjy = ChaojiyingClient('h3789766205', 'd94dpb1l', '977839')

    def switch_login_type(self, driver):
        """切换登录类型"""
        try:
            from selenium.webdriver.common.by import By
            if self.login_type == LoginType.PERSONAL:
                tabs = driver.find_elements(By.XPATH, "//li[text()='个人用户']")
                if tabs and 'cur' not in (tabs[0].get_attribute('class') or ''):
                    tabs[0].click()
                    time.sleep(1)
            elif self.login_type in (LoginType.ORG_ADMIN, LoginType.ORG_EMPLOYEE):
                org_tabs = driver.find_elements(By.XPATH, "//li[text()='机构']")
                if org_tabs and 'cur' not in (org_tabs[0].get_attribute('class') or ''):
                    org_tabs[0].click()
                    time.sleep(1)
                sub_type = "管理员" if self.login_type == LoginType.ORG_ADMIN else "员工"
                sub_tabs = driver.find_elements(By.XPATH, f"//li[text()='{sub_type}']")
                if sub_tabs:
                    sub_tabs[0].click()
                    time.sleep(1)
            return True
        except Exception as e:
            print(f"切换登录类型失败: {e}")
            return False

    def get_captcha_image(self, driver):
        """获取验证码背景图"""
        try:
            from selenium.webdriver.common.by import By
            time.sleep(2)
            bg_imgs = driver.find_elements(By.CSS_SELECTOR, ".yidun_bg-img, img.yidun_bg-img")
            if bg_imgs:
                src = bg_imgs[0].get_attribute('src')
                if src:
                    resp = requests.get(src, timeout=10)
                    if resp.status_code == 200:
                        return resp.content
            return None
        except Exception as e:
            print(f"获取验证码失败: {e}")
            return None

    def do_slider_captcha(self, driver, gap_x, img_width):
        """
        执行滑块验证码 - 使用Selenium ActionChains
        gap_x: 超级鹰返回的缺口x坐标（原图坐标）
        img_width: 原图宽度
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.action_chains import ActionChains
            import random
            
            # 获取背景图元素
            bg_imgs = driver.find_elements(By.CSS_SELECTOR, ".yidun_bg-img")
            if not bg_imgs:
                print("未找到背景图")
                return False
            bg_img = bg_imgs[0]
            
            # 获取滑块拖动按钮
            slider_btn = driver.find_elements(By.CSS_SELECTOR, ".yidun_slider")
            if not slider_btn:
                print("未找到滑块按钮")
                return False
            slider = slider_btn[0]
            
            # 获取位置
            bg_loc = bg_img.location
            bg_size = bg_img.size
            slider_loc = slider.location
            slider_size = slider.size
            
            print(f"背景图: x={bg_loc['x']}, width={bg_size['width']}")
            print(f"滑块: x={slider_loc['x']}, width={slider_size['width']}")
            
            # 计算缩放比例
            scale = bg_size['width'] / img_width
            print(f"缩放比例: {scale:.3f}")
            
            # 目标位置 = 背景图左边缘 + 缺口x * 缩放
            target_x = bg_loc['x'] + gap_x * scale
            
            # 滑块当前位置（中心点）
            slider_center_x = slider_loc['x'] + slider_size['width'] / 2
            
            # 需要拖动的距离
            drag_distance = int(target_x - slider_center_x)
            
            print(f"目标X: {target_x:.1f}, 滑块中心X: {slider_center_x:.1f}, 拖动距离: {drag_distance}")
            
            # 使用ActionChains拖动
            actions = ActionChains(driver)
            
            # 移动到滑块
            actions.move_to_element(slider)
            actions.perform()
            time.sleep(0.2)
            
            # 按下
            actions = ActionChains(driver)
            actions.move_to_element(slider)
            actions.click_and_hold()
            actions.perform()
            time.sleep(0.1)
            
            # 生成轨迹并拖动
            track = self._generate_track(drag_distance)
            total = 0
            for step_x, step_y in track:
                actions = ActionChains(driver)
                actions.move_by_offset(step_x, step_y)
                actions.perform()
                total += step_x
                time.sleep(random.uniform(0.005, 0.015))
            
            # 释放
            time.sleep(0.2)
            actions = ActionChains(driver)
            actions.release()
            actions.perform()
            
            print(f"拖动完成，目标: {drag_distance}px，实际: {total}px")
            return True
            
        except Exception as e:
            print(f"拖动失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_track(self, distance):
        """生成人类化拖动轨迹"""
        import random
        track = []
        current = 0
        
        # 加速阶段 (0-30%)
        # 匀速阶段 (30-70%)
        # 减速阶段 (70-100%)
        
        mid1 = distance * 0.3
        mid2 = distance * 0.7
        
        while current < distance - 2:
            if current < mid1:
                step = random.randint(3, 8)
            elif current < mid2:
                step = random.randint(6, 12)
            else:
                remaining = distance - current
                step = min(random.randint(2, 5), remaining)
            
            step = min(step, distance - current)
            y_offset = random.randint(-1, 1)
            track.append((int(step), y_offset))
            current += step
        
        # 最后精确到位
        if current < distance:
            track.append((int(distance - current), 0))
        
        return track

    def login(self):
        """执行登录"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
        except ImportError:
            print("Selenium未安装")
            return False

        chrome_options = Options()
        chrome_options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_argument('--no-proxy-server')

        try:
            print("=" * 60)
            print("      中国版权保护中心 - 全自动登录工具 v2")
            print("=" * 60)

            print("\n[1/6] 启动浏览器...")
            driver = webdriver.Chrome(executable_path=r'D:\biancheng\python\Scripts\chromedriver.exe', options=chrome_options)
            driver.set_window_size(1280, 800)

            print("[2/6] 打开登录页面...")
            driver.get(self.login_url)
            time.sleep(3)

            print("[3/6] 选择登录类型...")
            self.switch_login_type(driver)

            print("[4/6] 输入账号密码...")
            username_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入用户名/手机号/邮箱']")
            username_input.clear()
            username_input.send_keys(self.login_username)
            
            password_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入密码']")
            password_input.clear()
            password_input.send_keys(self.login_password)

            print("[5/6] 点击登录按钮触发验证码...")
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), '立即登录')]")
            login_button.click()
            time.sleep(3)

            print("[6/6] 处理验证码...")
            
            # 最多尝试5次
            for attempt in range(1, 6):
                print(f"\n=== 第{attempt}次尝试 ===")
                
                # 获取验证码图片
                bg_image = self.get_captcha_image(driver)
                if not bg_image:
                    print("获取验证码失败，重试...")
                    time.sleep(2)
                    continue
                
                # 获取图片尺寸
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(bg_image))
                img_width, img_height = img.size
                print(f"验证码图片尺寸: {img_width}x{img_height}")
                
                # 保存图片
                captcha_path = Path('C:/Temp/captcha_v2.png')
                with open(captcha_path, 'wb') as f:
                    f.write(bg_image)
                
                # 调用超级鹰识别
                result = self.cjy.post_pic(bg_image, 9101)
                if not result['success']:
                    print(f"识别失败: {result.get('error')}")
                    time.sleep(2)
                    continue
                
                coord_str = result['code']
                print(f"超级鹰返回: {coord_str}")
                
                # 解析坐标
                try:
                    parts = coord_str.split(',')
                    gap_x = int(parts[0])
                    print(f"缺口x坐标: {gap_x}")
                except:
                    print(f"坐标解析失败: {coord_str}")
                    time.sleep(2)
                    continue
                
                # 执行拖动
                success = self.do_slider_captcha(driver, gap_x, img_width)
                
                if success:
                    time.sleep(3)
                    # 检查是否登录成功
                    current_url = driver.current_url
                    page_source = driver.page_source
                    
                    if 'login' not in current_url.lower() or '退出' in page_source:
                        print("\n>>> 登录成功!")
                        print(f"当前页面: {current_url}")
                        driver.save_screenshot('C:/Temp/login_success.png')
                        time.sleep(10)
                        driver.quit()
                        return True
                    
                    # 检查验证码弹框是否消失
                    time.sleep(2)
                    yidun_popup = driver.find_elements(By.CLASS_NAME, 'yidun_popup')
                    if not yidun_popup:
                        print("验证码弹框已消失，检查登录状态...")
                        time.sleep(3)
                        if 'login' not in driver.current_url.lower():
                            print(">>> 登录成功!")
                            driver.save_screenshot('C:/Temp/login_success.png')
                            time.sleep(10)
                            driver.quit()
                            return True
                
                print(f"第{attempt}次验证失败")
                driver.save_screenshot(f'C:/Temp/attempt_{attempt}.png')
                time.sleep(2)
            
            print("\n自动验证失败")
            driver.quit()
            return False

        except Exception as e:
            print(f"\n登录过程出错: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    LOGIN_TYPE = LoginType.ORG_ADMIN
    USERNAME = "山东万成"
    PASSWORD = "AAaa1234567!"

    bot = CopyrightLoginBot(USERNAME, PASSWORD, LOGIN_TYPE)
    print(f"\n登录类型: {LOGIN_TYPE}")
    print(f"用户名: {USERNAME}")
    
    success = bot.login()
    print("\n>>> 登录成功!" if success else "\n>>> 登录失败")


if __name__ == '__main__':
    main()
