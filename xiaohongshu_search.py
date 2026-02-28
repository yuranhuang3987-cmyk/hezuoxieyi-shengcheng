# -*- coding: utf-8 -*-
"""
小红书搜索自动化
"""

import asyncio
import os
import json
import csv
from datetime import datetime

# 禁用代理（小红书可能不需要）
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(key, None)

from playwright.async_api import async_playwright


async def search_xiaohongshu(keyword="openclaw"):
    """搜索小红书"""
    
    results = []
    
    async with async_playwright() as p:
        # 启动浏览器（非无头模式，方便观察和登录）
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"[1] 打开小红书...")
            await page.goto('https://www.xiaohongshu.com')
            await page.wait_for_timeout(3000)
            
            # 检查是否需要登录
            print("[2] 检查登录状态...")
            
            # 尝试搜索
            print(f"[3] 搜索关键词: {keyword}")
            
            # 方法1: 直接访问搜索URL
            search_url = f'https://www.xiaohongshu.com/search_result?keyword={keyword}'
            await page.goto(search_url)
            await page.wait_for_timeout(5000)
            
            # 截图
            await page.screenshot(path='C:/Temp/xhs_search_page.png')
            print("已保存搜索页面截图")
            
            # 获取搜索结果
            print("[4] 获取搜索结果...")
            
            # 等待搜索结果加载
            await page.wait_for_timeout(3000)
            
            # 提取帖子信息
            posts = await page.evaluate('''() => {
                const results = [];
                
                // 尝试多种选择器
                const selectors = [
                    '.search-result-list .note-item',
                    '.feeds-page .note-item',
                    '[class*="search-result"] [class*="note"]',
                    '.note-list .note-item',
                    'section.note-item'
                ];
                
                let noteElements = [];
                for (const selector of selectors) {
                    noteElements = document.querySelectorAll(selector);
                    if (noteElements.length > 0) break;
                }
                
                // 如果上面的选择器都没找到，尝试更通用的方式
                if (noteElements.length === 0) {
                    // 查找所有可能包含帖子的元素
                    const allLinks = document.querySelectorAll('a[href*="/explore/"], a[href*="/discovery/item/"]');
                    const uniqueLinks = new Set();
                    
                    allLinks.forEach(link => {
                        const href = link.href;
                        if (!uniqueLinks.has(href)) {
                            uniqueLinks.add(href);
                            const parent = link.closest('div[class*="note"], div[class*="item"], section');
                            const titleEl = parent ? parent.querySelector('span, div[class*="title"], a') : link;
                            
                            results.push({
                                title: titleEl ? titleEl.innerText.trim() : '',
                                url: href,
                                author: '',
                                likes: '',
                                type: 'post'
                            });
                        }
                    });
                } else {
                    noteElements.forEach(note => {
                        try {
                            const titleEl = note.querySelector('a, span[class*="title"], div[class*="title"]');
                            const authorEl = note.querySelector('[class*="author"], [class*="name"]');
                            const likesEl = note.querySelector('[class*="like"], [class*="count"]');
                            const linkEl = note.querySelector('a[href*="/explore/"], a[href*="/discovery/"]');
                            
                            results.push({
                                title: titleEl ? titleEl.innerText.trim() : '',
                                url: linkEl ? linkEl.href : '',
                                author: authorEl ? authorEl.innerText.trim() : '',
                                likes: likesEl ? likesEl.innerText.trim() : '',
                                type: 'post'
                            });
                        } catch (e) {}
                    });
                }
                
                return results;
            }''')
            
            print(f"找到 {len(posts)} 条结果")
            
            # 如果没找到结果，保存页面HTML用于分析
            if len(posts) == 0:
                html = await page.content()
                with open('C:/Temp/xhs_search_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("已保存页面HTML用于分析")
            
            results = posts
            
            # 滚动加载更多
            print("[5] 滚动加载更多结果...")
            for i in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
                
                # 再次提取
                more_posts = await page.evaluate('''() => {
                    const results = [];
                    const allLinks = document.querySelectorAll('a[href*="/explore/"], a[href*="/discovery/item/"]');
                    const seen = new Set();
                    
                    allLinks.forEach(link => {
                        const href = link.href;
                        if (!seen.has(href) && !href.includes('search_result')) {
                            seen.add(href);
                            const parent = link.closest('div[class*="note"], div[class*="item"], section, li');
                            let title = '';
                            
                            if (parent) {
                                const titleEl = parent.querySelector('span:not(:empty), div[class*="title"]');
                                title = titleEl ? titleEl.innerText.trim().split('\\n')[0] : '';
                            }
                            
                            if (!title) {
                                title = link.innerText.trim().split('\\n')[0];
                            }
                            
                            results.push({
                                title: title || '无标题',
                                url: href,
                                author: '',
                                likes: '',
                                type: 'post'
                            });
                        }
                    });
                    
                    return results;
                }''')
                
                # 合并结果（去重）
                existing_urls = {p['url'] for p in results}
                for post in more_posts:
                    if post['url'] not in existing_urls:
                        results.append(post)
                        existing_urls.add(post['url'])
                
                print(f"  滚动 {i+1} 后共 {len(results)} 条结果")
            
            # 最终截图
            await page.screenshot(path='C:/Temp/xhs_search_final.png', full_page=True)
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 保持浏览器打开一段时间
            print("\n浏览器将保持打开30秒，可手动操作...")
            await page.wait_for_timeout(30000)
            await browser.close()
    
    return results


def save_results(results, keyword):
    """保存结果到文件"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_dir = 'C:/Temp/xiaohongshu'
    os.makedirs(base_dir, exist_ok=True)
    
    # 保存JSON
    json_file = f'{base_dir}/xhs_{keyword}_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"已保存JSON: {json_file}")
    
    # 保存CSV
    csv_file = f'{base_dir}/xhs_{keyword}_{timestamp}.csv'
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'url', 'author', 'likes', 'type', 'category'])
        writer.writeheader()
        
        for post in results:
            # 简单分类
            title = post.get('title', '').lower()
            if '教程' in title or '使用' in title or '入门' in title:
                category = '教程'
            elif '测评' in title or '评测' in title or '体验' in title:
                category = '测评'
            elif '开源' in title or 'github' in title:
                category = '开源项目'
            elif 'ai' in title or '人工智能' in title:
                category = 'AI相关'
            else:
                category = '其他'
            
            post['category'] = category
            writer.writerow(post)
    
    print(f"已保存CSV: {csv_file}")
    
    # 生成汇总
    summary_file = f'{base_dir}/xhs_{keyword}_{timestamp}_summary.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# 小红书搜索结果汇总\n\n")
        f.write(f"**关键词:** {keyword}\n")
        f.write(f"**搜索时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**结果数量:** {len(results)} 条\n\n")
        
        # 按分类统计
        categories = {}
        for post in results:
            cat = post.get('category', '其他')
            categories[cat] = categories.get(cat, 0) + 1
        
        f.write("## 分类统计\n\n")
        f.write("| 分类 | 数量 |\n")
        f.write("|------|------|\n")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            f.write(f"| {cat} | {count} |\n")
        
        f.write("\n## 帖子列表\n\n")
        for i, post in enumerate(results, 1):
            f.write(f"### {i}. {post.get('title', '无标题')}\n")
            f.write(f"- **链接:** {post.get('url', '')}\n")
            f.write(f"- **作者:** {post.get('author', '未知')}\n")
            f.write(f"- **点赞:** {post.get('likes', '未知')}\n")
            f.write(f"- **分类:** {post.get('category', '其他')}\n\n")
    
    print(f"已保存汇总: {summary_file}")
    
    return json_file, csv_file, summary_file


async def main():
    keyword = "openclaw"
    
    print("=" * 50)
    print(f"  小红书搜索: {keyword}")
    print("=" * 50)
    
    results = await search_xiaohongshu(keyword)
    
    if results:
        print(f"\n共获取 {len(results)} 条结果")
        save_results(results, keyword)
    else:
        print("\n未获取到结果，可能需要登录或遇到反爬")
        print("请查看截图: C:/Temp/xhs_search_page.png")


if __name__ == '__main__':
    asyncio.run(main())
