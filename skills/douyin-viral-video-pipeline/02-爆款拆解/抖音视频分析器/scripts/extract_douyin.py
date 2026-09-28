#!/usr/bin/env python3
"""抖音视频一键提取：链接 → 文字稿 → AI 总结"""

import argparse, json, os, subprocess, sys, time, yaml
from pathlib import Path

def load_cookies(path):
    """从 YAML 配置文件加载 cookies"""
    with open(path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    return cfg.get('cookies', {}) or {}

MEDIA_TYPES = ('video', 'audio', 'octet')

def get_video_url(douyin_url, cookies_dict):
    """Playwright 获取视频源地址

    策略（按优先级）：
    1. 页面 video 元素的 src（旧版页面有效）
    2. 网络请求拦截：监听所有响应，按 Content-Type 收集真实媒体流地址
       （2026 年起抖音 PC 端改为 blob+MSE 播放，DOM 里只有 blob: URL，
       真实地址只能从网络层拦截到 douyinvod.com 的 media-video/media-audio 请求）
    """
    from playwright.sync_api import sync_playwright

    media_urls = []

    def on_response(resp):
        try:
            ct = resp.headers.get('content-type', '')
            if any(k in ct for k in MEDIA_TYPES):
                media_urls.append(resp.url)
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            'Chrome/120.0 Safari/537.36'))
        for name, value in cookies_dict.items():
            if value and name:
                ctx.add_cookies([{
                    'name': name, 'value': str(value),
                    'domain': '.douyin.com', 'path': '/'
                }])
        page = ctx.new_page()
        page.on('response', on_response)
        page.goto(douyin_url, timeout=45000, wait_until='domcontentloaded')
        page.wait_for_timeout(8000)
        # 策略 1：DOM 直取（非 blob 时）
        src = page.evaluate("""() => {
            const v = document.querySelector('video source') || document.querySelector('video');
            return v ? (v.currentSrc || v.src || '') : '';
        }""")
        title = page.title()
        browser.close()

    if src and not src.startswith('blob:'):
        return src, title
    # 策略 2：从拦截结果里挑真实媒体流（排除占位 uuu_*.mp4）
    real = [u for u in media_urls if 'uuu_' not in u]
    if not real:
        raise RuntimeError(
            f"无法获取视频地址（DOM 与网络拦截均失败）: {title}\n"
            "提示：需要有效 cookies，或用脚本内导出的 cookies 走 yt-dlp 兜底")
    video = next((u for u in real if 'media-video' in u), real[0])
    return video, title

def extract_audio(video_url, output_path, ffmpeg_path='ffmpeg'):
    """ffmpeg 提取音频流（不下载视频）"""
    cmd = [
        ffmpeg_path,
        '-headers', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36',
        '-headers', 'Referer: https://www.douyin.com/',
        '-i', video_url,
        '-vn',                     # 不处理视频
        '-acodec', 'libmp3lame',
        '-ab', '128k',
        '-y',                      # 覆盖
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 失败: {result.stderr[:200]}")
    return os.path.getsize(output_path)

def transcribe(audio_path, use_gpu=True):
    """faster-whisper 转写"""
    from faster_whisper import WhisperModel
    
    if use_gpu:
        try:
            model = WhisperModel('tiny', device='cuda', compute_type='float16')
        except Exception:
            model = WhisperModel('tiny', device='cpu', compute_type='int8')
            print("GPU 不可用，回退到 CPU int8")
    else:
        model = WhisperModel('tiny', device='cpu', compute_type='int8')
    
    segments, info = model.transcribe(audio_path, language='zh', beam_size=1)
    return [s.text.strip() for s in segments if s.text.strip()]

def main():
    parser = argparse.ArgumentParser(description='抖音视频提取文字稿')
    parser.add_argument('url', help='抖音分享链接')
    parser.add_argument('--cookies', '-c', default='config.yml',
                       help='cookies 配置文件路径 (默认: config.yml)')
    parser.add_argument('--output', '-o', default=None,
                       help='输出文件路径 (默认: 桌面 dy_transcript.txt)')
    parser.add_argument('--no-gpu', action='store_true',
                       help='强制使用 CPU')
    parser.add_argument('--ffmpeg', default='ffmpeg',
                       help='ffmpeg 路径')
    args = parser.parse_args()
    
    # 加载 cookies
    cookies = load_cookies(args.cookies)
    if not cookies:
        print("错误: 未找到 cookies，请先运行 cookie_fetcher 扫码登录")
        sys.exit(1)
    
    # 获取视频地址
    print(f"正在解析: {args.url}")
    video_url, title = get_video_url(args.url, cookies)
    print(f"标题: {title[:80]}")
    
    # 提取音频
    tmp_audio = os.path.join(os.environ.get('TMP', '/tmp'), 'dy_audio.mp3')
    print("正在提取音频...")
    size = extract_audio(video_url, tmp_audio, args.ffmpeg)
    print(f"音频: {size/1024:.0f}KB")
    
    # 转写
    print("正在转写（faster-whisper tiny）...")
    start = time.time()
    segments = transcribe(tmp_audio, use_gpu=not args.no_gpu)
    elapsed = time.time() - start
    print(f"转写完成: {len(segments)} 段, 耗时 {elapsed:.0f}s")
    
    # 保存文字稿
    desktop = os.path.join(Path.home(), 'Desktop')
    output = args.output or os.path.join(desktop, 'dy_transcript.txt')
    with open(output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(segments))
    print(f"文字稿: {output}")
    
    # 清理
    os.remove(tmp_audio)
    print("临时音频已删除")

if __name__ == '__main__':
    main()
