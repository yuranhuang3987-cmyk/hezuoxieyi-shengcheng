# -*- coding: utf-8 -*-
"""
中国版权保护中心登录自动化脚本 - 全自动版本
使用超级鹰打码平台识别网易易盾验证码
支持三种登录类型: 个人用户、机构管理员、机构员工
"""

import os
import time
import base64
import hashlib
import requests
from pathlib import Path

# 禁用系统代理
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'


class LoginType:
    """登录类型枚举"""
    PERSONAL = "个人用户"           # 个人用户-密码登录
    ORG_ADMIN = "机构管理员"        # 机构-管理员登录
    ORG_EMPLOYEE = "机构员工"       # 机构-员工登录


class ChaojiyingClient:
    """超级鹰API客户端"""

    def __init__(self, username, password, soft_id):
        self.username = username
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.soft_id = soft_id
        self.base_url = 'https://upload.chaojiying.net/Upload/Processing.php'

    def post_pic(self, img_data, codetype):
        """上传图片进行识别，返回JSON格式结果"""
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

            # 新API返回JSON格式
            if 'OK' in result or 'err_no' in result:
                import json
                try:
                    data = json.loads(result)
                    if data.get('err_no') == 0:
                        return {'success': True, 'code': data.get('pic_str'), 'raw': result}
                    else:
                        return {'success': False, 'error': data.get('err_str', result), 'raw': result}
                except json.JSONDecodeError:
                    # 兼容旧格式
                    if result.find('OK') > -1:
                        parts = result.split('|')
                        return {'success': True, 'code': parts[1], 'raw': result}
                    return {'success': False, 'error': result, 'raw': result}
            else:
                return {'success': False, 'error': result, 'raw': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class CopyrightLoginBot:
    """版权保护中心登录机器人 - 全自动版本"""

    def __init__(self, username, password, login_type=LoginType.PERSONAL):
        """
        初始化登录机器人
        username: 登录用户名
        password: 登录密码
        login_type: 登录类型 (LoginType.PERSONAL/ORG_ADMIN/ORG_EMPLOYEE)
        """
        self.login_url = 'https://register.ccopyright.com.cn/login.html'
        self.login_username = username
        self.login_password = password
        self.login_type = login_type

        # 超级鹰配置
        self.cjy = ChaojiyingClient(
            username='h3789766205',
            password='d94dpb1l',
            soft_id='977839'
        )

    def switch_login_type(self, driver):
        """
        切换登录类型标签（两级选择）
        第一级：个人用户 / 机构
        第二级（机构）：管理员 / 员工
        """
        try:
            from selenium.webdriver.common.by import By

            # 根据登录类型确定选择路径
            if self.login_type == LoginType.PERSONAL:
                # 点击"个人用户"
                tabs = driver.find_elements(By.XPATH, "//li[text()='个人用户']")
                if tabs:
                    tab = tabs[0]
                    if 'cur' not in (tab.get_attribute('class') or ''):
                        print("切换到: 个人用户")
                        tab.click()
                        time.sleep(1)
                    else:
                        print("当前已是: 个人用户")
                return True

            elif self.login_type in (LoginType.ORG_ADMIN, LoginType.ORG_EMPLOYEE):
                # 先点击"机构"
                org_tabs = driver.find_elements(By.XPATH, "//li[text()='机构']")
                if org_tabs:
                    org_tab = org_tabs[0]
                    if 'cur' not in (org_tab.get_attribute('class') or ''):
                        print("切换到: 机构")
                        org_tab.click()
                        time.sleep(1)

                # 再选择子类型：管理员或员工
                if self.login_type == LoginType.ORG_ADMIN:
                    sub_type = "管理员"
                else:
                    sub_type = "员工"

                sub_tabs = driver.find_elements(By.XPATH, f"//li[text()='{sub_type}']")
                if sub_tabs:
                    sub_tab = sub_tabs[0]
                    if 'cur' not in (sub_tab.get_attribute('class') or ''):
                        print(f"切换到: {sub_type}")
                        sub_tab.click()
                        time.sleep(1)
                    else:
                        print(f"当前已是: {sub_type}")
                return True

            return False

        except Exception as e:
            print(f"切换登录类型失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_captcha_images(self, driver):
        """
        获取网易易盾验证码图片
        优先从img标签获取（yidun_bg-img背景图）
        """
        try:
            from selenium.webdriver.common.by import By

            time.sleep(2)

            # 方法1: 从img标签获取yidun背景图
            bg_img = None
            slider_img = None

            img_elements = driver.find_elements(By.TAG_NAME, "img")
            for img in img_elements:
                class_name = img.get_attribute('class') or ''
                src = img.get_attribute('src') or ''

                if 'yidun_bg-img' in class_name or ('yidun' in src.lower() and ('bg' in src.lower() or 'captcha' in src.lower())):
                    bg_url = src
                    print(f"找到背景图URL: {bg_url}")
                    try:
                        bg_response = requests.get(bg_url, timeout=10)
                        if bg_response.status_code == 200:
                            bg_img = bg_response.content
                            debug_path = Path(__file__).parent / 'captcha_bg.jpg'
                            with open(debug_path, 'wb') as f:
                                f.write(bg_img)
                            print(f"已保存背景图: {debug_path}, 大小={len(bg_img)}字节")
                    except Exception as e:
                        print(f"下载背景图失败: {e}")

                elif 'yidun_jigsaw' in class_name or ('yidun' in src.lower() and 'jigsaw' in src.lower()):
                    slider_url = src
                    print(f"找到滑块图URL: {slider_url}")
                    try:
                        slider_response = requests.get(slider_url, timeout=10)
                        if slider_response.status_code == 200:
                            slider_img = slider_response.content
                            debug_path = Path(__file__).parent / 'captcha_slider.png'
                            with open(debug_path, 'wb') as f:
                                f.write(slider_img)
                            print(f"已保存滑块图: {debug_path}, 大小={len(slider_img)}字节")
                    except Exception as e:
                        print(f"下载滑块图失败: {e}")

            if bg_img:
                return bg_img, slider_img

            # 方法2: 从页面源码提取图片URL
            page_source = driver.page_source
            import re
            bg_pattern = r'https://[^"\']*yidun[^"\']*bg[^"\']*\.jpg[^"\']*'
            slider_pattern = r'https://[^"\']*yidun[^"\']*jigsaw[^"\']*\.png[^"\']*'

            bg_urls = re.findall(bg_pattern, page_source)
            slider_urls = re.findall(slider_pattern, page_source)

            print(f"从源码找到背景图URL: {len(bg_urls)}个")
            print(f"从源码找到滑块图URL: {len(slider_urls)}个")

            if bg_urls:
                bg_url = bg_urls[0]
                print(f"背景图URL: {bg_url}")
                try:
                    bg_response = requests.get(bg_url, timeout=10)
                    if bg_response.status_code == 200:
                        debug_path = Path(__file__).parent / 'yidun_bg.jpg'
                        with open(debug_path, 'wb') as f:
                            f.write(bg_response.content)
                        print(f"已保存背景图: {debug_path}")
                        return bg_response.content, None
                except Exception as e:
                    print(f"下载背景图失败: {e}")

            return None, None

        except Exception as e:
            print(f"获取验证码图片失败: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def parse_coordinates(self, coord_str):
        """
        解析超级鹰返回的坐标字符串
        格式可能是: "x,y" 或 "x1,y1,x2,y2" 或 "x1,y1|x2,y2"
        返回需要拖动的距离（x坐标）
        """
        try:
            if not coord_str:
                return None

            print(f"原始坐标: {coord_str}")

            # 处理多种格式
            if '|' in coord_str:
                # 多坐标格式: "x1,y1|x2,y2"
                coords = coord_str.split('|')
                first_coord = coords[0].split(',')
                return int(first_coord[0])
            elif ',' in coord_str:
                parts = coord_str.split(',')
                if len(parts) == 2:
                    # 单坐标格式: "x,y"
                    return int(parts[0])
                elif len(parts) >= 4:
                    # 矩形格式: "x1,y1,x2,y2"，取第一个x坐标
                    return int(parts[0])

            # 尝试直接转整数
            return int(coord_str)
        except Exception as e:
            print(f"坐标解析失败: {e}")
            return None

    def detect_captcha_type(self, driver):
        """
        检测验证码类型
        返回: 'slider' (滑块拼图), 'click_text' (文字点选), 'click_shape' (图形点选)
        """
        try:
            from selenium.webdriver.common.by import By

            # 检查页面源码中的提示文字
            page_source = driver.page_source

            # 文字点选特征
            if '请依次点击' in page_source or '点击下列' in page_source:
                if '请依次点击' in page_source:
                    # 提取需要点击的文字
                    import re
                    match = re.search(r'请依次点击[:：]\s*([^。\n]+)', page_source)
                    if match:
                        text = match.group(1)
                        print(f"检测到文字点选验证码: {text}")
                        return 'click_text', text
                return 'click_text', None

            # 检查是否有滑块元素
            slider_elements = driver.find_elements(By.CLASS_NAME, 'yidun_jigsaw')
            if slider_elements:
                print("检测到滑块拼图验证码")
                return 'slider', None

            # 默认尝试滑块
            print("无法确定验证码类型，默认尝试滑块")
            return 'slider', None

        except Exception as e:
            print(f"检测验证码类型失败: {e}")
            return 'slider', None

    def recognize_captcha(self, bg_image, slider_image, captcha_type):
        """
        根据验证码类型调用不同的识别方法
        captcha_type: 'slider', 'click_text', 'click_shape'
        """
        if captcha_type == 'slider':
            return self.recognize_slider_captcha(bg_image)
        elif captcha_type in ('click_text', 'click_shape'):
            return self.recognize_click_captcha(bg_image)
        else:
            print(f"未知验证码类型: {captcha_type}")
            return None, None

    def recognize_slider_captcha(self, bg_image):
        """
        识别滑块拼图验证码
        优先使用9101类型（滑动拼图），备选9900类型
        """
        # 9101是专门针对滑动拼图的类型
        codetypes = [9101, 9900]

        for ct in codetypes:
            result = self.cjy.post_pic(bg_image, ct)
            if result['success']:
                coord_str = result['code']
                distance = self.parse_slider_distance(coord_str, ct)
                if distance is not None:
                    print(f"滑块验证码识别成功 (类型{ct}): 距离={distance}px, 原始={coord_str}")
                    return ('slider', distance), ct
                else:
                    print(f"类型{ct}坐标解析失败: {coord_str}")
            else:
                print(f"类型{ct}识别失败: {result.get('error', '未知错误')}")

        return None, None

    def parse_slider_distance(self, coord_str, codetype):
        """
        解析滑块拖动距离
        codetype: 验证码类型，影响坐标格式
        返回: 拖动距离(像素)
        """
        try:
            if not coord_str:
                return None

            if codetype == 9101:
                # 9101滑动拼图返回: "x,y" 中心点坐标
                if ',' in coord_str:
                    parts = coord_str.split(',')
                    if len(parts) >= 2:
                        return int(parts[0])  # 返回x坐标
            elif codetype == 9900:
                # 9900滑块图形块定位返回: "x1,y1,x2,y2" 矩形区域
                if ',' in coord_str:
                    parts = coord_str.split(',')
                    if len(parts) >= 4:
                        # 取矩形中心x坐标
                        x1, y1 = int(parts[0]), int(parts[1])
                        x2, y2 = int(parts[2]), int(parts[3])
                        return (x1 + x2) // 2
                    elif len(parts) >= 2:
                        return int(parts[0])

            return int(coord_str)
        except Exception as e:
            print(f"滑块距离解析失败: {e}")
            return None

    def recognize_click_captcha(self, bg_image):
        """
        识别点选验证码（文字或图形）
        使用超级鹰的9004类型（坐标多点击）
        """
        codetypes = [9004]

        for ct in codetypes:
            result = self.cjy.post_pic(bg_image, ct)
            if result['success']:
                coord_str = result['code']
                coords = self.parse_click_coordinates(coord_str)
                if coords:
                    print(f"点选验证码识别成功 (类型{ct}): {len(coords)}个坐标 {coords}")
                    return ('click', coords), ct
                else:
                    print(f"坐标解析失败: {coord_str}")
            else:
                print(f"类型{ct}识别失败: {result.get('error', '未知错误')}")

        return None, None

    def parse_click_coordinates(self, coord_str):
        """
        解析点击坐标字符串
        格式可能是: "x,y" 或 "x1,y1|x2,y2" 或 "x1,y1|x2,y2|x3,y3|x4,y4"
        返回坐标列表 [(x1, y1), (x2, y2), ...]
        """
        try:
            if not coord_str:
                return None

            coords = []
            if '|' in coord_str:
                parts = coord_str.split('|')
                for part in parts:
                    if ',' in part:
                        x, y = part.split(',')
                        coords.append((int(x), int(y)))
            elif ',' in coord_str:
                x, y = coord_str.split(',')
                coords.append((int(x), int(y)))

            return coords if coords else None
        except Exception as e:
            print(f"坐标解析失败: {e}")
            return None

    def _split_move(self, total_distance, min_step, max_step):
        """将总距离分割成多个随机步长"""
        import random
        steps = []
        remaining = total_distance
        while remaining > 0:
            step = min(random.randint(min_step, max_step), remaining)
            steps.append(step)
            remaining -= step
        return steps

    def check_captcha_success(self, driver):
        """
        检查验证码是否验证成功
        返回: True=成功, False=失败, None=不确定
        """
        try:
            from selenium.webdriver.common.by import By

            time.sleep(1)

            current_url = driver.current_url
            if 'login' not in current_url.lower():
                print("验证成功: 已跳转离开登录页")
                return True

            page_source = driver.page_source
            if '退出' in page_source or '欢迎' in page_source:
                print("验证成功: 发现登录成功标记")
                return True

            yidun_elements = driver.find_elements(By.CLASS_NAME, 'yidun_popup')
            if not yidun_elements:
                print("验证成功: 弹框已消失")
                return True

            try:
                slider = driver.find_element(By.CLASS_NAME, 'yidun_slider__icon')
                slider_x = slider.location['x']
                if slider_x < 560:
                    print(f"验证失败: 滑块回到初始位置 (x={slider_x})")
                    return False
            except:
                pass

            print("验证结果不确定")
            return None

        except Exception as e:
            print(f"检查验证码结果时出错: {e}")
            return None

    def simulate_slider_drag(self, driver, distance, img_width=None):
        """
        模拟人类拖动滑块的行为 - 使用JavaScript直接操作
        distance: 超级鹰返回的缺口x坐标（基于原图尺寸）
        img_width: 原始图片宽度，用于缩放校正
        """
        try:
            from selenium.webdriver.common.by import By

            # 获取背景图元素
            bg_imgs = driver.find_elements(By.CSS_SELECTOR, ".yidun_bg-img, img.yidun_bg-img")
            if not bg_imgs:
                print("未找到背景图元素")
                return False
            
            bg_img = bg_imgs[0]
            
            # 使用JavaScript获取精确的位置信息并执行拖动
            result = driver.execute_script("""
                var bgImg = arguments[0];
                var distance = arguments[1];  // 超级鹰返回的缺口x坐标
                var imgWidth = arguments[2];  // 原图宽度
                
                var bgRect = bgImg.getBoundingClientRect();
                var scale = bgRect.width / imgWidth;
                var gapX = bgRect.x + distance * scale;
                
                // 找滑块图标
                var slider = document.querySelector('.yidun_slider__icon');
                if (!slider) {
                    return {success: false, error: '未找到滑块元素'};
                }
                
                var sliderRect = slider.getBoundingClientRect();
                var startX = sliderRect.x + sliderRect.width / 2;
                var startY = sliderRect.y + sliderRect.height / 2;
                
                // 需要拖动的距离 = 缺口位置 - 滑块当前位置 - 滑块宽度的一半
                var dragDist = gapX - startX - sliderRect.width / 2;
                
                console.log('背景图:', bgRect.x, bgRect.width);
                console.log('缩放:', scale);
                console.log('缺口屏幕位置:', gapX);
                console.log('滑块起点:', startX);
                console.log('拖动距离:', dragDist);
                
                // 创建鼠标事件
                function createMouseEvent(type, x, y) {
                    return new MouseEvent(type, {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        clientX: x,
                        clientY: y,
                        button: 0
                    });
                }
                
                // 模拟拖动
                slider.dispatchEvent(createMouseEvent('mousedown', startX, startY));
                
                var steps = 25;
                var currentX = startX;
                var stepSize = dragDist / steps;
                
                for (var i = 1; i <= steps; i++) {
                    (function(idx) {
                        setTimeout(function() {
                            var x = startX + stepSize * idx;
                            var y = startY + (Math.random() - 0.5) * 3;
                            document.dispatchEvent(createMouseEvent('mousemove', x, y));
                            
                            if (idx === steps) {
                                setTimeout(function() {
                                    document.dispatchEvent(createMouseEvent('mouseup', x, y));
                                }, 30);
                            }
                        }, idx * 12);
                    })(i);
                }
                
                return {
                    success: true,
                    bgX: bgRect.x,
                    bgWidth: bgRect.width,
                    scale: scale,
                    gapX: gapX,
                    startX: startX,
                    dragDist: dragDist
                };
            """, bg_img, distance, img_width)
            
            print(f"JS执行结果: {result}")
            
            if result and result.get('success'):
                print(f"背景图: x={result['bgX']:.1f}, width={result['bgWidth']:.1f}")
                print(f"缩放: {result['scale']:.3f}")
                print(f"缺口位置: {result['gapX']:.1f}px")
                print(f"滑块起点: {result['startX']:.1f}px")
                print(f"拖动距离: {result['dragDist']:.1f}px")
                # 等待动画完成
                time.sleep(0.8)
                return True
            else:
                print(f"JS拖动失败: {result}")
                return False

        except Exception as e:
            print(f"模拟拖动失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def simulate_click_captcha(self, driver, coords, img_width=None, img_height=None):
        """
        模拟点击文字验证码
        coords: 坐标列表 [(x1, y1), (x2, y2), ...]
        img_width, img_height: 原始图片尺寸（用于缩放校正）
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.action_chains import ActionChains
            import random

            # 优先找yidun_bg-img图片元素
            captcha_element = None
            bg_imgs = driver.find_elements(By.CLASS_NAME, 'yidun_bg-img')
            if bg_imgs:
                captcha_element = bg_imgs[0]
                print(f"找到验证码图片元素: yidun_bg-img")

            # 备选：找其他元素
            if not captcha_element:
                captcha_xpaths = [
                    "//img[contains(@class, 'yidun')]",
                    "//div[contains(@class, 'yidun')]//canvas",
                ]
                for xpath in captcha_xpaths:
                    try:
                        elements = driver.find_elements(By.XPATH, xpath)
                        if elements:
                            captcha_element = elements[0]
                            print(f"找到验证码元素: {xpath}")
                            break
                    except:
                        continue

            if not captcha_element:
                print("无法找到验证码图片元素")
                return False

            # 获取验证码图片的位置
            location = captcha_element.location
            size = captcha_element.size
            print(f"验证码元素位置: {location}, 大小: {size}")

            # 计算缩放比例（如果提供了原始图片尺寸）
            scale_x = 1.0
            scale_y = 1.0
            if img_width and img_height:
                scale_x = size['width'] / img_width
                scale_y = size['height'] / img_height
                print(f"缩放比例: {scale_x:.2f}x, {scale_y:.2f}x (原始{img_width}x{img_height} -> 显示{size['width']}x{size['height']})")

            action = ActionChains(driver)

            # 按顺序点击每个坐标
            for i, (x, y) in enumerate(coords):
                # 应用缩放并计算点击位置
                scaled_x = int(x * scale_x)
                scaled_y = int(y * scale_y)

                print(f"点击第{i+1}个坐标: 原始({x}, {y}) -> 缩放后({scaled_x}, {scaled_y})")

                # 移动到元素并点击偏移位置
                action.move_to_element_with_offset(captcha_element, scaled_x, scaled_y)
                time.sleep(random.uniform(0.1, 0.3))

            # 执行所有点击
            for _ in coords:
                action.click()
                action.perform()
                action = ActionChains(driver)  # 创建新的action
                time.sleep(random.uniform(0.2, 0.5))

            print(f"文字验证码点击完成，共{len(coords)}个点")
            return True

        except Exception as e:
            print(f"模拟点击失败: {e}")
            import traceback
            traceback.print_exc()
            return False

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
            print("      中国版权保护中心 - 全自动登录工具")
            print("=" * 60)

            print("\n[1/7] 启动浏览器...")
            driver = webdriver.Chrome(executable_path=r'D:\biancheng\python\Scripts\chromedriver.exe', options=chrome_options)
            driver.set_window_size(1280, 800)

            print("[2/7] 打开登录页面...")
            driver.get(self.login_url)
            time.sleep(3)

            print("[3/7] 选择登录类型...")
            self.switch_login_type(driver)

            print("[4/7] 输入账号密码...")
            username_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入用户名/手机号/邮箱']")
            username_input.clear()
            username_input.send_keys(self.login_username)
            print(f"   用户名: {self.login_username}")

            password_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入密码']")
            password_input.clear()
            password_input.send_keys(self.login_password)
            print(f"   密码: ********")

            print("\n[5/7] 点击登录按钮触发验证码...")
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), '立即登录')]")
            login_button.click()
            time.sleep(3)

            # 截图
            driver.save_screenshot(str(Path(__file__).parent / 'before_captcha.png'))

            print("\n[6/7] 检测验证码类型...")
            captcha_type, captcha_info = self.detect_captcha_type(driver)
            if captcha_info:
                print(f"验证码信息: {captcha_info}")

            print("\n[7/7] 获取并识别验证码...")
            bg_image, slider_image = self.get_captcha_images(driver)

            if bg_image:
                # 保存背景图
                captcha_path = Path(__file__).parent / 'captcha_bg.png'
                with open(captcha_path, 'wb') as f:
                    f.write(bg_image)
                print(f"验证码背景图已保存: {captcha_path}")

                # 获取图片尺寸
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(bg_image))
                img_width, img_height = img.size
                print(f"原始验证码图片尺寸: {img_width}x{img_height}")

                # 最多尝试3次
                max_attempts = 3
                for attempt in range(1, max_attempts + 1):
                    if attempt > 1:
                        print(f"\n=== 第{attempt}次尝试 ===")
                        # 重新获取验证码图片（因为可能刷新了）
                        time.sleep(2)
                        bg_image_retry, _ = self.get_captcha_images(driver)
                        if bg_image_retry:
                            bg_image = bg_image_retry
                            img = Image.open(io.BytesIO(bg_image))
                            img_width, img_height = img.size

                    # 根据类型识别验证码
                    result, codetype = self.recognize_captcha(bg_image, slider_image, captcha_type)

                    if result:
                        result_type, result_data = result

                        print(f"\n[7/7] 执行验证码操作... (第{attempt}次)")

                        if result_type == 'slider':
                            print(f"拖动滑块，距离: {result_data}px")
                            success = self.simulate_slider_drag(driver, result_data, img_width)
                            after_screenshot = f'after_slider_attempt{attempt}.png'
                        elif result_type == 'click':
                            print(f"点击验证码，{len(result_data)}个坐标点")
                            success = self.simulate_click_captcha(driver, result_data, img_width, img_height)
                            after_screenshot = f'after_click_attempt{attempt}.png'
                        else:
                            print(f"未知验证码结果类型: {result_type}")
                            success = False
                            after_screenshot = 'after_unknown.png'

                        if success:
                            time.sleep(3)
                            current_url = driver.current_url
                            page_source = driver.page_source

                            driver.save_screenshot(str(Path(__file__).parent / after_screenshot))

                            if 'login' not in current_url.lower() or '退出' in page_source:
                                print("\n>>> 登录成功!")
                                print(f"当前页面: {current_url}")
                                time.sleep(60)
                                driver.quit()
                                return True
                            else:
                                # 检查验证码是否还在
                                yidun_elements = driver.find_elements(By.CLASS_NAME, 'yidun_popup')
                                if not yidun_elements:
                                    print("\n>>> 验证码弹框已消失，可能登录成功")
                                    time.sleep(3)
                                    current_url = driver.current_url
                                    if 'login' not in current_url.lower():
                                        print(">>> 登录成功!")
                                        time.sleep(60)
                                        driver.quit()
                                        return True

                                print(f"\n第{attempt}次验证失败，验证码仍然存在")
                                if attempt < max_attempts:
                                    print("等待2秒后重试...")
                                    time.sleep(2)
                                else:
                                    print("已达到最大尝试次数")
                    else:
                        print(f"第{attempt}次识别验证码失败")
                        if attempt < max_attempts:
                            time.sleep(2)
                            time.sleep(5)
                            current_url = driver.current_url
                            if 'login' not in current_url.lower():
                                print(">>> 登录成功!")
                                time.sleep(60)
                                driver.quit()
                                return True

            print("\n自动识别失败，切换到手动模式...")
            print("请在浏览器中手动完成验证码...")
            time.sleep(60)

            driver.quit()
            return False

        except Exception as e:
            print(f"\n登录过程出错: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    # 配置登录信息 - 根据实际使用情况修改
    LOGIN_TYPE = LoginType.ORG_ADMIN     # 登录类型: PERSONAL/ORG_ADMIN/ORG_EMPLOYEE
    USERNAME = "山东万成"                # 登录用户名
    PASSWORD = "AAaa1234567!"            # 登录密码

    bot = CopyrightLoginBot(USERNAME, PASSWORD, LOGIN_TYPE)

    print("\n")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     中国版权保护中心全自动登录工具 v3.0             ║")
    print("║     支持滑块/文字点选/图形点选验证码                  ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print(f"\n登录类型: {LOGIN_TYPE}")
    print(f"用户名: {USERNAME}")

    success = bot.login()

    if success:
        print("\n>>> 登录成功!")
    else:
        print("\n>>> 登录未完成")


if __name__ == '__main__':
    main()
