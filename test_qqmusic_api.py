#!/usr/bin/env python3
"""
测试QQ音乐下载API
"""
import yt_dlp
import tempfile
import os

# 读取cookie
with open('/tmp/qq_cookies.txt', 'r') as f:
    cookie_content = f.read()

# 创建临时cookie文件
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    cookie_file = f.name
    f.write(cookie_content)

try:
    # 配置yt-dlp
    ydl_opts = {
        'cookiefile': cookie_file,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'format': '128mp3',
        'ignoreerrors': True,
    }

    # 测试歌单(使用之前成功的URL)
    test_url = "https://y.qq.com/n/ryqq/playlist/9482566232"

    print(f"正在测试URL: {test_url}")
    print("=" * 60)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(test_url, download=False)

        if info:
            # 判断是歌单还是单曲
            if 'entries' in info:
                print(f"\n✅ 成功提取歌单信息:")
                print(f"  歌单名: {info.get('title', 'Unknown')}")
                print(f"  总歌曲数: {len(list(info['entries']))}")
                print(f"\n前5首歌曲:")
                for idx, entry in enumerate(list(info['entries'])[:5], 1):
                    if entry:
                        print(f"  {idx}. {entry.get('title', 'Unknown')} - {entry.get('artist') or entry.get('uploader')}")
                        print(f"     下载URL: {'有' if entry.get('url') else '无'}")
            else:
                print(f"\n✅ 成功提取歌曲信息:")
                print(f"  标题: {info.get('title', 'Unknown')}")
                print(f"  艺术家: {info.get('artist') or info.get('uploader')}")
                print(f"  专辑: {info.get('album')}")
                print(f"  时长: {info.get('duration')}秒")
                print(f"  格式: {info.get('ext')}")
                print(f"  下载URL: {info.get('url', 'N/A')[:100]}...")
                print(f"  文件大小: {info.get('filesize') or info.get('filesize_approx')} 字节")
        else:
            print("❌ 无法提取信息")

finally:
    # 清理临时文件
    if os.path.exists(cookie_file):
        os.unlink(cookie_file)
    print("\n✅ 测试完成")
