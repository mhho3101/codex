#!/usr/bin/env python3
"""导出 Playwright 会话 cookies 为 Netscape 格式（供 yt-dlp 使用）

用法：
    python scripts/export_cookies.py "https://v.douyin.com/xxxx/" -o cookies.txt
    yt-dlp --cookies cookies.txt "https://v.douyin.com/xxxx/"
"""
import argparse

def export_cookies(douyin_url, output_path):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(user_agent=(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            'Chrome/120.0 Safari/537.36'))
        pg = ctx.new_page()
        pg.goto(douyin_url, timeout=45000, wait_until='domcontentloaded')
        pg.wait_for_timeout(6000)
        lines = ['# Netscape HTTP Cookie File']
        for c in ctx.cookies():
            if 'douyin' not in c['domain'] or not c['name']:
                continue
            exp = int(c.get('expires', 0) or 0)
            sec = str(c.get('secure', False)).upper()
            lines.append('%s\tTRUE\t%s\t%s\t%d\t%s\t%s' % (
                c['domain'], c['path'], sec, exp, c['name'], c['value']))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        b.close()
    print(f'已导出 {len(lines) - 1} 条 cookies → {output_path}')


def main():
    parser = argparse.ArgumentParser(description='导出抖音 cookies（Netscape 格式）')
    parser.add_argument('url', help='抖音分享链接')
    parser.add_argument('-o', '--output', default='cookies.txt', help='输出文件')
    args = parser.parse_args()
    export_cookies(args.url, args.output)


if __name__ == '__main__':
    main()
