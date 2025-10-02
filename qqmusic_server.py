#!/usr/bin/env python3
"""
独立的QQ音乐下载服务
不依赖原项目的其他爬虫代码,仅提供QQ音乐功能
"""

import os
import yaml
import asyncio
import tempfile
import yt_dlp

from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

# 读取配置
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)


# ============ 数据模型 ============

class QQMusicDownloadRequest(BaseModel):
    """QQ音乐下载请求"""
    cookie: str = Field(..., description="QQ音乐Cookie (Netscape格式)")
    url: str = Field(..., description="歌曲或歌单链接")
    format: Optional[str] = Field(default="128mp3", description="音频格式")


class SongInfo(BaseModel):
    """歌曲信息"""
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    download_url: Optional[str] = None
    duration: Optional[int] = None
    filesize: Optional[int] = None
    format: Optional[str] = None
    error: Optional[str] = None


# ============ FastAPI应用 ============

app = FastAPI(
    title="QQ Music Downloader",
    description="QQ音乐下载服务",
    version="1.0.0"
)


# ============ API端点 ============

@app.post("/api/qqmusic/download")
async def qqmusic_download(request: Request, req: QQMusicDownloadRequest = Body(...)):
    """获取QQ音乐下载链接"""

    cookie_file = None
    try:
        # 创建临时cookie文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            cookie_file = f.name
            f.write(req.cookie)

        # 配置yt-dlp
        ydl_opts = {
            'cookiefile': cookie_file,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'format': req.format if req.format != 'bestaudio' else 'bestaudio',
            'ignoreerrors': True,
        }

        songs = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=False)

            if 'entries' in info:
                # 歌单
                for entry in info['entries']:
                    if entry is None:
                        continue

                    song = SongInfo(
                        title=entry.get('title', 'Unknown'),
                        artist=entry.get('artist') or entry.get('uploader'),
                        album=entry.get('album'),
                        download_url=entry.get('url'),
                        duration=entry.get('duration'),
                        filesize=entry.get('filesize') or entry.get('filesize_approx'),
                        format=entry.get('ext'),
                        error=None if entry.get('url') else "无法获取下载链接"
                    )
                    songs.append(song.dict())
            else:
                # 单曲
                song = SongInfo(
                    title=info.get('title', 'Unknown'),
                    artist=info.get('artist') or info.get('uploader'),
                    album=info.get('album'),
                    download_url=info.get('url'),
                    duration=info.get('duration'),
                    filesize=info.get('filesize') or info.get('filesize_approx'),
                    format=info.get('ext'),
                    error=None if info.get('url') else "无法获取下载链接"
                )
                songs.append(song.dict())

        return {
            "code": 200,
            "router": request.url.path,
            "data": {
                "total": len(songs),
                "songs": songs
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": 400,
                "router": request.url.path,
                "params": {"url": req.url, "format": req.format, "error": str(e)}
            }
        )

    finally:
        # 清理临时文件
        if cookie_file and os.path.exists(cookie_file):
            try:
                os.unlink(cookie_file)
            except:
                pass


# ============ Web界面 ============

@app.get("/", response_class=HTMLResponse)
async def index():
    """主页"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎵 QQ音乐下载器</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }

            body {
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }

            h1 {
                text-align: center;
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
            }

            .subtitle {
                text-align: center;
                color: #7f8c8d;
                margin-bottom: 30px;
            }

            .info-box {
                background: #e7f3ff;
                border-left: 4px solid #1c7ed6;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 25px;
                color: #163a5f;
            }

            .form-group {
                margin-bottom: 20px;
            }

            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #2c3e50;
            }

            textarea, input, select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }

            textarea:focus, input:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }

            textarea {
                min-height: 150px;
                font-family: monospace;
                resize: vertical;
            }

            button {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }

            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }

            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            #result {
                margin-top: 30px;
            }

            .song-item {
                background: #f8f9fa;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
                transition: transform 0.2s;
            }

            .song-item:hover {
                transform: translateX(5px);
            }

            .song-title {
                font-size: 1.2em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 8px;
            }

            .song-meta {
                color: #7f8c8d;
                font-size: 0.9em;
                margin-bottom: 10px;
            }

            .download-btn {
                display: inline-block;
                padding: 8px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 20px;
                font-weight: 600;
                transition: all 0.3s;
            }

            .download-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
            }

            .error {
                color: #e03131;
                margin-top: 10px;
            }

            .success-box {
                background: #e6f4ea;
                border-left: 4px solid #2f9e44;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                color: #1e4620;
            }

            .loading {
                text-align: center;
                padding: 20px;
                color: #667eea;
                font-size: 1.1em;
            }

            .warning-box {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                color: #856404;
            }

            .progress-info {
                background: #e7f3ff;
                border-left: 4px solid #1c7ed6;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                color: #163a5f;
            }

            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(102, 126, 234, 0.3);
                border-radius: 50%;
                border-top-color: #667eea;
                animation: spin 1s ease-in-out infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 QQ音乐下载器</h1>
            <p class="subtitle">支持单曲和歌单批量下载</p>

            <div class="info-box">
                <strong>📌 使用说明:</strong><br/>
                1. 使用Cookie导出工具从QQ音乐网站导出Cookie (Netscape格式)<br/>
                2. 粘贴歌曲或歌单链接<br/>
                3. 选择音频格式,点击获取下载链接
            </div>

            <form id="downloadForm">
                <div class="form-group">
                    <label for="cookie">🍪 QQ音乐Cookie (Netscape格式) *</label>
                    <textarea id="cookie" required placeholder="# Netscape HTTP Cookie File
.qq.com	TRUE	/	FALSE	0	uin	12345
.qq.com	TRUE	/	FALSE	0	qm_keyst	xxxxx"></textarea>
                </div>

                <div class="form-group">
                    <label for="url">🔗 歌曲或歌单链接 *</label>
                    <input type="url" id="url" required placeholder="https://y.qq.com/n/ryqq/playlist/...">
                    <div id="urlTypeHint" style="margin-top: 8px; font-size: 0.9em; font-weight: 600;"></div>
                </div>

                <div class="form-group">
                    <label for="format">🎧 音频格式</label>
                    <select id="format">
                        <option value="128mp3">128kbps MP3 (推荐)</option>
                        <option value="320mp3">320kbps MP3</option>
                        <option value="flac">FLAC无损</option>
                        <option value="m4a">M4A</option>
                        <option value="bestaudio">最佳音质</option>
                    </select>
                </div>

                <button type="submit" id="submitBtn">🚀 获取下载链接</button>
            </form>

            <div id="result"></div>
        </div>

        <script>
            const form = document.getElementById('downloadForm');
            const submitBtn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');

            // 下载歌曲函数
            function downloadSong(url, filename, statusId) {
                const statusDiv = document.getElementById(statusId + '_status');
                statusDiv.innerHTML = '<span style="color: #667eea;">⏳ 已触发下载...</span>';

                try {
                    // 获取文件扩展名
                    const ext = url.includes('.m4a') ? '.m4a' :
                                url.includes('.flac') ? '.flac' :
                                url.includes('.mp3') ? '.mp3' : '.m4a';

                    const safeFilename = filename.replace(/[<>:"/\\|?*]/g, '_') + ext;

                    // 直接创建下载链接(浏览器原生下载)
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = safeFilename;
                    a.style.display = 'none';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);

                    statusDiv.innerHTML = '<span style="color: #2f9e44;">✅ 下载已开始(由浏览器处理)</span>';

                    // 5秒后清除状态
                    setTimeout(() => {
                        statusDiv.innerHTML = '';
                    }, 5000);
                } catch (error) {
                    statusDiv.innerHTML = '<span style="color: #e03131;">❌ 触发失败: ' + error.message + '</span>';
                }
            }

            // 检测URL类型并显示提示
            const urlInput = document.getElementById('url');
            urlInput.addEventListener('input', (e) => {
                const url = e.target.value;
                const hintDiv = document.getElementById('urlTypeHint');

                if (url.includes('/playlist/')) {
                    hintDiv.innerHTML = '💡 检测到歌单链接 - 解析歌单需要较长时间,请耐心等待';
                    hintDiv.style.color = '#ffc107';
                } else if (url.includes('/songDetail/')) {
                    hintDiv.innerHTML = '✅ 检测到单曲链接 - 解析速度较快';
                    hintDiv.style.color = '#2f9e44';
                } else {
                    hintDiv.innerHTML = '';
                }
            });

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const cookie = document.getElementById('cookie').value;
                const url = document.getElementById('url').value;
                const format = document.getElementById('format').value;

                // 判断是歌单还是单曲
                const isPlaylist = url.includes('/playlist/');

                // 显示加载状态
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ 处理中...';

                if (isPlaylist) {
                    resultDiv.innerHTML = `
                        <div class="warning-box">
                            <strong>⏰ 正在解析歌单</strong><br/>
                            歌单解析需要较长时间,请耐心等待...<br/>
                            <div style="margin-top: 10px;">
                                <span class="spinner"></span>
                                <span style="margin-left: 10px;">正在逐首提取歌曲信息</span>
                            </div>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = '<div class="loading">正在获取歌曲信息,请稍候...</div>';
                }

                try {
                    const response = await fetch('/api/qqmusic/download', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ cookie, url, format })
                    });

                    const data = await response.json();

                    if (data.code === 200) {
                        const songs = data.data.songs;
                        const total = data.data.total;

                        let html = `<div class="success-box"><strong>✅ 解析成功!</strong><br/>共找到 ${total} 首歌曲</div>`;

                        songs.forEach((song, index) => {
                            const songId = `song_${index}`;
                            html += `
                                <div class="song-item">
                                    <div class="song-title">${index + 1}. ${song.title}</div>
                                    <div class="song-meta">
                                        🎤 ${song.artist || 'Unknown'}
                                        ${song.album ? `| 💿 ${song.album}` : ''}
                                        ${song.duration ? `| ⏱️ ${Math.floor(song.duration / 60)}:${(song.duration % 60).toString().padStart(2, '0')}` : ''}
                                    </div>
                                    ${song.download_url ?
                                        `<button class="download-btn" onclick="downloadSong('${song.download_url}', '${song.title.replace(/'/g, "\\'")} - ${(song.artist || 'Unknown').replace(/'/g, "\\'")}', '${songId}')">⬇️ 下载</button>` :
                                        `<div class="error">⚠️ ${song.error || '无法获取下载链接'}</div>`
                                    }
                                    <div id="${songId}_status" style="margin-top: 8px; font-size: 0.9em;"></div>
                                </div>
                            `;
                        });

                        resultDiv.innerHTML = html;
                    } else {
                        resultDiv.innerHTML = `<div class="info-box" style="background: #fdecea; border-left-color: #e03131; color: #5c2b29;">❌ 解析失败: ${data.detail?.params?.error || '未知错误'}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="info-box" style="background: #fdecea; border-left-color: #e03131; color: #5c2b29;">❌ 发生错误: ${error.message}</div>`;
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 获取下载链接';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ============ 启动服务 ============

if __name__ == "__main__":
    print("="*60)
    print("🎵 QQ音乐下载服务")
    print("="*60)
    print("📍 Web界面: http://localhost:8080")
    print("📍 API文档: http://localhost:8080/docs")
    print("="*60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
