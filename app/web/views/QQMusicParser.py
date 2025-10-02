import asyncio
import os
import httpx
import json

import yaml
from pywebio.input import *
from pywebio.output import *

from app.web.views.ViewsUtils import ViewsUtils

# 读取配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)


def qqmusic_parser():
    """QQ音乐解析功能"""

    # 添加CSS样式
    put_html("""
    <style>
    :root {
        --vc-bg: #faf5cf;
        --vc-primary: #667eea;
        --vc-primary-2: #764ba2;
        --vc-info-text: #163a5f;
        --vc-info-bg: #e7f3ff;
        --vc-info-border: #b6daff;
        --vc-info-accent: #1c7ed6;
        --vc-error-text: #5c2b29;
        --vc-error-bg: #fdecea;
        --vc-error-border: #f5c2c7;
        --vc-error-accent: #e03131;
        --vc-success-text: #1e4620;
        --vc-success-bg: #e6f4ea;
        --vc-success-border: #b7e2c1;
        --vc-success-accent: #2f9e44;
    }

    body, .pywebio-content, .container, .container-fluid,
    .form-group, .form-control, #pywebio-scope-ROOT {
        background-color: var(--vc-bg) !important;
    }

    div {
        background-color: inherit !important;
    }

    .form-submit-btn, .btn-primary {
        background: linear-gradient(135deg, var(--vc-primary) 0%, var(--vc-primary-2) 100%) !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    .form-submit-btn:hover, .btn-primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }

    .vc-info {
        color: var(--vc-info-text) !important;
        background: var(--vc-info-bg) !important;
        border: 1px solid var(--vc-info-border) !important;
        border-left: 4px solid var(--vc-info-accent) !important;
        padding: 12px 14px !important;
        border-radius: 8px !important;
        margin: 10px 0 !important;
    }

    .vc-success {
        color: var(--vc-success-text) !important;
        background: var(--vc-success-bg) !important;
        border: 1px solid var(--vc-success-border) !important;
        border-left: 4px solid var(--vc-success-accent) !important;
        padding: 12px 14px !important;
        border-radius: 8px !important;
        margin: 10px 0 !important;
    }

    .vc-alert {
        color: var(--vc-error-text) !important;
        background: var(--vc-error-bg) !important;
        border: 1px solid var(--vc-error-border) !important;
        border-left: 4px solid var(--vc-error-accent) !important;
        padding: 12px 14px !important;
        border-radius: 8px !important;
        margin: 10px 0 !important;
    }

    .song-item {
        background: white !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        transition: transform 0.2s ease !important;
    }

    .song-item:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }

    .song-title {
        font-size: 1.2em !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
        margin-bottom: 5px !important;
    }

    .song-meta {
        color: #7f8c8d !important;
        font-size: 0.9em !important;
    }

    .download-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        text-decoration: none !important;
        display: inline-block !important;
        margin-top: 10px !important;
        transition: all 0.3s ease !important;
    }

    .download-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5) !important;
    }

    .download-status {
        margin-top: 8px !important;
        font-size: 0.9em !important;
    }
    </style>

    <script>
    // 通过歌曲ID下载 - 从全局变量获取数据（避免HTML转义和特殊字符问题）
    function downloadSongById(songId) {
        const statusDiv = document.getElementById(songId + '_status');

        // 从全局变量获取歌曲数据
        if (!window.songData || !window.songData[songId]) {
            statusDiv.innerHTML = '<span style="color: #e03131;">❌ 无法获取下载链接</span>';
            return;
        }

        const songInfo = window.songData[songId];
        const url = songInfo.url;
        const filename = songInfo.filename;

        statusDiv.innerHTML = '<span style="color: #667eea;">⏳ 正在下载...</span>';

        try {
            // 获取文件扩展名
            const ext = url.includes('.m4a') ? '.m4a' :
                        url.includes('.flac') ? '.flac' :
                        url.includes('.mp3') ? '.mp3' : '.m4a';

            const safeFilename = filename.replace(/[<>:"/\\\\|?*]/g, '_') + ext;

            // 直接创建下载链接
            const a = document.createElement('a');
            a.href = url;
            a.download = safeFilename;
            a.target = '_blank';  // 新窗口打开，避免当前页面跳转
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            statusDiv.innerHTML = '<span style="color: #2f9e44;">✅ 下载已触发</span>';

            // 5秒后清除状态
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 5000);
        } catch (error) {
            console.error('下载错误:', error);
            statusDiv.innerHTML = '<span style="color: #e03131;">❌ 触发失败: ' + error.message + '</span>';
        }
    }
    </script>
    """)

    # 输入提示
    put_html(f"""
    <div class="vc-info">
        <div style="font-weight: 700; margin-bottom: 8px;">🎵 {ViewsUtils.t('QQ音乐下载说明', 'QQ Music Download Instructions')}</div>
        <div style="font-weight: 400;">
            {ViewsUtils.t('1. 支持单曲和歌单链接<br/>2. 需要提供QQ音乐Cookie用于VIP歌曲下载<br/>3. Cookie格式为Netscape格式',
            '1. Supports single song and playlist links<br/>2. QQ Music Cookie required for VIP songs<br/>3. Cookie should be in Netscape format')}
        </div>
    </div>
    """)

    # 获取用户输入
    form_data = input_group(ViewsUtils.t("请输入以下信息", "Please enter the following information"), [
        textarea(
            ViewsUtils.t('QQ音乐Cookie (Netscape格式)', 'QQ Music Cookie (Netscape format)'),
            name='cookie',
            required=True,
            placeholder=ViewsUtils.t(
                '粘贴Netscape格式的Cookie内容，例如:\n# Netscape HTTP Cookie File\n.qq.com\tTRUE\t/\tFALSE\t0\tuin\t12345',
                'Paste Netscape format cookie, e.g.:\n# Netscape HTTP Cookie File\n.qq.com\tTRUE\t/\tFALSE\t0\tuin\t12345'
            )
        ),
        input(
            ViewsUtils.t('歌曲或歌单链接', 'Song or Playlist URL'),
            name='url',
            required=True,
            placeholder='https://y.qq.com/n/ryqq/playlist/...'
        ),
        select(
            ViewsUtils.t('音频格式', 'Audio Format'),
            name='format',
            options=[
                ('128kbps MP3 (推荐)', '128mp3'),
                ('320kbps MP3', '320mp3'),
                ('FLAC无损', 'flac'),
                ('M4A', 'm4a'),
                ('最佳音质', 'bestaudio')
            ],
            value='128mp3'
        )
    ])

    cookie = form_data['cookie']
    url = form_data['url']
    audio_format = form_data['format']

    # 显示处理中提示
    put_html('<br>')
    with use_scope('loading'):
        put_html(f"""
        <div class="vc-info">
            <div style="font-weight: 700;">{ViewsUtils.t('正在处理...', 'Processing...')}</div>
            <div style="font-weight: 400;">{ViewsUtils.t('请稍候，正在获取歌曲信息', 'Please wait, fetching song information')}</div>
        </div>
        """)

    try:
        # 调用后端API
        api_url = f"http://127.0.0.1:{config['API']['Host_Port']}/api/qqmusic/download"

        # 使用同步httpx client，设置更长的超时时间（300秒=5分钟）
        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                api_url,
                json={
                    'cookie': cookie,
                    'url': url,
                    'format': audio_format
                }
            )
            result = response.json()

        # 清除加载提示
        clear('loading')

        if result.get('code') == 200:
            data = result.get('data', {})
            songs = data.get('songs', [])
            total = data.get('total', 0)
            success = data.get('success', total)
            failed = data.get('failed', 0)

            # 显示成功提示（带统计信息）
            put_html(f"""
            <div class="vc-success">
                <div style="font-weight: 700;">✅ {ViewsUtils.t('解析完成', 'Completed')}</div>
                <div style="font-weight: 400;">
                    {ViewsUtils.t(f'总计: {total} 首 | 成功: {success} 首 | 失败: {failed} 首',
                                 f'Total: {total} | Success: {success} | Failed: {failed}')}
                </div>
            </div>
            """)

            put_html('<br>')
            put_html(f"<h3>🎵 {ViewsUtils.t('歌曲列表', 'Song List')}</h3>")

            # 创建歌曲数据映射表（避免HTML转义和特殊字符问题）
            song_data_map = {}
            for idx, song in enumerate(songs, 1):
                if song.get('download_url'):
                    title = song.get('title', 'Unknown')
                    artist = song.get('artist', 'Unknown')
                    song_data_map[f"song_{idx}"] = {
                        'url': song.get('download_url'),
                        'filename': f"{title} - {artist}"
                    }

            # 将歌曲数据映射表注入到JavaScript（使用json.dumps确保正确转义）
            song_data_json = json.dumps(song_data_map)
            put_html(f"""
            <script>
            window.songData = {song_data_json};
            </script>
            """)

            # 显示每首歌曲
            for idx, song in enumerate(songs, 1):
                title = song.get('title', 'Unknown')
                artist = song.get('artist', 'Unknown')
                album = song.get('album', '')
                duration = song.get('duration')
                download_url = song.get('download_url')
                error = song.get('error')

                # 格式化时长
                duration_str = ''
                if duration:
                    minutes = int(duration) // 60
                    seconds = int(duration) % 60
                    duration_str = f"{minutes}:{seconds:02d}"

                song_id = f"song_{idx}"

                # 构建歌曲信息HTML
                song_html = f"""
                <div class="song-item">
                    <div class="song-title">{idx}. {title}</div>
                    <div class="song-meta">
                        🎤 {artist or 'Unknown'}
                        {f' | 💿 {album}' if album else ''}
                        {f' | ⏱️ {duration_str}' if duration_str else ''}
                    </div>
                """

                if download_url:
                    # 从JavaScript全局变量获取数据，避免HTML转义和特殊字符问题
                    song_html += f"""
                        <button class="download-btn" onclick="downloadSongById('{song_id}')">
                            ⬇️ {ViewsUtils.t('下载', 'Download')}
                        </button>
                        <div id="{song_id}_status" class="download-status"></div>
                    """
                elif error:
                    song_html += f"""
                        <div style="color: #e03131; margin-top: 10px;">
                            ⚠️ {error}
                        </div>
                    """

                song_html += "</div>"
                put_html(song_html)

        else:
            # 显示错误
            error_detail = result.get('detail', {})
            error_msg = error_detail.get('params', {}).get('error', '未知错误')

            put_html(f"""
            <div class="vc-alert">
                <div style="font-weight: 700;">❌ {ViewsUtils.t('解析失败', 'Failed')}</div>
                <div style="font-weight: 400;">{error_msg}</div>
            </div>
            """)

    except Exception as e:
        clear('loading')
        put_html(f"""
        <div class="vc-alert">
            <div style="font-weight: 700;">❌ {ViewsUtils.t('发生错误', 'Error occurred')}</div>
            <div style="font-weight: 400;">{str(e)}</div>
        </div>
        """)
