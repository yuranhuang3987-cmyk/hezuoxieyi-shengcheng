# -*- coding: utf-8 -*-
"""
R41 填报监控脚本 - 持续截图分析
"""

import asyncio
import os

# 禁用代理
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(key, None)

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        # 连接到已打开的浏览器（需要用户手动启动带调试端口的浏览器）
        # 或者我们直接用截图方式
        
        # 简单方案：持续截屏
        import subprocess
        
        count = 0
        print("开始监控截图，每5秒一张...")
        print("按 Ctrl+C 停止")
        
        while True:
            count += 1
            try:
                # 使用 PowerShell 截图
                result = subprocess.run([
                    'powershell.exe', '-Command',
                    '''
                    Add-Type -AssemblyName System.Windows.Forms
                    $bitmap = New-Object System.Drawing.Bitmap(1400, 900)
                    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                    $graphics.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size(1400, 900)))
                    $bitmap.Save('C:\\Temp\\r41_monitor_''' + str(count) + '''.png')
                    $graphics.Dispose()
                    $bitmap.Dispose()
                    '''
                ], capture_output=True, timeout=10)
                
                print(f"截图 {count} 已保存")
            except Exception as e:
                print(f"截图失败: {e}")
            
            await asyncio.sleep(5)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n监控停止")
