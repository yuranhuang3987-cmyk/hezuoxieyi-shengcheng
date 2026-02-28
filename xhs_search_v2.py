# -*- coding: utf-8 -*-
"""
小红书搜索自动化 v2 - 支持手动登录
"""

import asyncio
import os
import json
import csv
from datetime import datetime

for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(key, None)

from playwright.async_api import async_playwright


async def search_xiaohongshu(keyword="openclaw"):
    """搜索小红书 - 需要手动登录"""
    
    results = []
    
    async with async_playwright() as p:
        # 使用持久化上下文保存登录状态
        user_data_dir = 'C:/Temp/xhs_browser_data'
        os.makedirs(user_data_dir, exist_ok=True)
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            print("=" * 50)
            print(f"  小红书搜索: {keyword}")
            print("=" * 50)
            
            print("\n[1] 打开小红书...")
            await page.goto('https://www.xiaohongshu.com')
            await page.wait_for_timeout(3000)
            
            # 检查是否登录
            print("\n[2] 检查登录状态...")
            print("如果未登录，请在浏览器中手动登录！")
            print("登录后按 Enter 继续...")
            
            # 等待用户输入（通过检查页面状态）
            for i in range(60):  # 最多等待60秒
                # 检查是否有登录按钮
                login_btn = await page.query_selector('button:has-text("登录"), .login-btn, [class*="login"]')
                if not login_btn:
                    print("检测到已登录！")
                    break
                await page.wait_for_timeout(1000)
                if i % 10 == 9:
                    print(f"  等待登录中... ({i+1}秒)")
            else:
                print("\n请在浏览器中完成登录，然后按 Enter 继续...")
                # 在PowerShell中无法直接等待用户输入，我们继续执行
            
            # 搜索
            print(f"\n[3] 搜索关键词: {keyword}")
            search_url = f'https://www.xiaohongshu.com/search_result?keyword={keyword}&source=unknown'
            await page.goto(search_url)
            await page.wait_for_timeout(5000)
            
            # 截图
            await page.screenshot(path='C:/Temp/xhs_search_v2.png')
            
            # 等待搜索结果
            print("[4] 等待搜索结果加载...")
            await page.wait_for_timeout(3000)
            
            # 提取帖子
            print("[5] 提取帖子信息...")
            
            posts = await page.evaluate('''() => {
                const results = [];
                
                // 方法1: 查找所有帖子链接
                const links = document.querySelectorAll('a[href*="/explore/"]');
                const seen = new Set();
                
                links.forEach(link => {
                    const href = link.href;
                    if (seen.has(href)) return;
                    seen.add(href);
                    
                    // 尝试获取标题
                    let title = '';
                    const parent = link.closest('section, div[class*="note-item"], div[class*="card"]');
                    if (parent) {
                        const titleEl = parent.querySelector('[class*="title"], span, div');
                        if (titleEl && titleEl.innerText) {
                            title = titleEl.innerText.trim().split('\\n')[0];
                        }
                    }
                    
                    // 从URL提取帖子ID
                    const match = href.match(/explore\\/([a-zA-Z0-9]+)/);
                    const postId = match ? match[1] : '';
                    
                    results.push({
                        title: title || `帖子 ${postId}`,
                        url: href,
                        postId: postId,
                        author: '',
                        likes: '',
                        type: 'post'
                    });
                });
                
                return results;
            }''')
            
            print(f"初步找到 {len(posts)} 条结果")
            
            # 滚动加载更多
            print("[6] 滚动加载更多...")
            for i in range(5):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
                
                # 再次提取
                more = await page.evaluate('''() => {
                    const results = [];
                    const links = document.querySelectorAll('a[href*="/explore/"]');
                    const seen = new Set();
                    
                    links.forEach(link => {
                        const href = link.href;
                        if (seen.has(href)) return;
                        seen.add(href);
                        
                        let title = '';
                        const parent = link.closest('section, div[class*="note-item"], div[class*="card"]');
                        if (parent) {
                            const titleEl = parent.querySelector('[class*="title"]');
                            if (titleEl && titleEl.innerText) {
                                title = titleEl.innerText.trim().split('\\n')[0];
                            }
                        }
                        
                        const match = href.match(/explore\\/([a-zA-Z0-9]+)/);
                        const postId = match ? match[1] : '';
                        
                        results.push({
                            title: title || `帖子 ${postId}`,
                            url: href,
                            postId: postId,
                            author: '',
                            likes: '',
                            type: 'post'
                        });
                    });
                    
                    return results;
                }''')
                
                # 合并
                existing = {p['url'] for p in posts}
                for p in more:
                    if p['url'] not in existing:
                        posts.append(p)
                        existing.add(p['url'])
                
                print(f"  滚动 {i+1} 后共 {len(posts)} 条")
            
            results = posts
            
            # 最终截图
            await page.screenshot(path='C:/Temp/xhs_search_final_v2.png', full_page=True)
            
            print(f"\n共获取 {len(results)} 条帖子")
            
            # 保持浏览器打开
            print("\n浏览器保持打开，可以手动查看...")
            print("按 Ctrl+C 或关闭窗口退出")
            await page.wait_for_timeout(60000)
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        
        await context.close()
    
    return results


def save_results(results, keyword):
    """保存结果"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_dir = 'C:/Temp/xiaohongshu'
    os.makedirs(base_dir, exist_ok=True)
    
    # JSON
    json_file = f'{base_dir}/xhs_{keyword}_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"JSON: {json_file}")
    
    # CSV
    csv_file = f'{base_dir}/xhs_{keyword}_{timestamp}.csv'
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'url', 'postId', 'author', 'likes', 'type', 'category'])
        writer.writeheader()
        
        for post in results:
            title = post.get('title', '').lower()
            if '教程' in title or '使用' in title:
                category = '教程'
            elif '测评' in title:
                category = '测评'
            elif '开源' in title:
                category = '开源'
            else:
                category = '其他'
            post['category'] = category
            writer.writerow(post)
    print(f"CSV: {csv_file}")
    
    # 汇总
    summary = f'{base_dir}/xhs_{keyword}_{timestamp}_summary.md'
    with open(summary, 'w', encoding='utf-8') as f:
        f.write(f"# 小红书搜索: {keyword}\n\n")
        f.write(f"**时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**数量:** {len(results)} 条\n\n")
        
        # 分类统计
        cats = {}
        for p in results:
            c = p.get('category', '其他')
            cats[c] = cats.get(c, 0) + 1
        
        f.write("## 分类统计\n\n| 分类 | 数量 |\n|------|------|\n")
        for c, n in sorted(cats.items(), key=lambda x: -x[1]):
            f.write(f"| {c} | {n} |\n")
        
        f.write("\n## 帖子列表\n\n")
        for i, p in enumerate(results, 1):
            f.write(f"{i}. [{p.get('title', '无标题')}]({p.get('url', '')})\n")
    
    print(f"汇总: {summary}")
    
    return json_file, csv_file, summary


async def main():
    results = await search_xiaohongshu("openclaw")
    if results:
        save_results(results, "openclaw")


if __name__ == '__main__':
    asyncio.run(main())
