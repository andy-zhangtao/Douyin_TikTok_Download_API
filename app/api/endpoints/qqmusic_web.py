from typing import List, Optional
from fastapi import APIRouter, Body, Request, HTTPException
from pydantic import BaseModel, Field
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel
import yt_dlp
import tempfile
import os


router = APIRouter()


class QQMusicDownloadRequest(BaseModel):
    """QQ音乐下载请求模型"""
    cookie: str = Field(..., description="QQ音乐Cookie字符串 (Netscape格式)", example="# Netscape HTTP Cookie File\n.qq.com\tTRUE\t/\tFALSE\t0\tuin\t179644359")
    url: str = Field(..., description="QQ音乐歌曲或歌单链接", example="https://y.qq.com/n/ryqq/songDetail/003fA11G0Pdvnm")
    format: Optional[str] = Field(default="128mp3", description="音频格式: 128mp3/320mp3/flac/m4a/bestaudio", example="128mp3")


class SongInfo(BaseModel):
    """单个歌曲信息"""
    title: str = Field(..., description="歌曲标题")
    artist: Optional[str] = Field(None, description="艺术家")
    album: Optional[str] = Field(None, description="专辑名称")
    download_url: Optional[str] = Field(None, description="下载链接")
    duration: Optional[int] = Field(None, description="时长(秒)")
    filesize: Optional[int] = Field(None, description="文件大小(字节)")
    format: Optional[str] = Field(None, description="音频格式")
    error: Optional[str] = Field(None, description="错误信息(如果有)")


@router.post("/download", response_model=ResponseModel, summary="获取QQ音乐下载链接/Get QQ Music download links")
async def qqmusic_download(request: Request, req: QQMusicDownloadRequest = Body(...)):
    """
    # [中文]
    ### 用途:
    - 获取QQ音乐歌曲或歌单的下载链接
    ### 参数:
    - cookie: QQ音乐Cookie (Netscape格式)
    - url: QQ音乐歌曲或歌单链接
    - format: 音频格式 (可选: 128mp3, 320mp3, flac, m4a, bestaudio)
    ### 返回:
    - 歌曲列表,每个歌曲包含下载链接和元数据

    # [English]
    ### Purpose:
    - Get QQ Music song or playlist download links
    ### Parameters:
    - cookie: QQ Music Cookie (Netscape format)
    - url: QQ Music song or playlist URL
    - format: Audio format (options: 128mp3, 320mp3, flac, m4a, bestaudio)
    ### Return:
    - List of songs with download links and metadata

    # [示例/Example]
    ```json
    {
        "cookie": "# Netscape HTTP Cookie File\\n.qq.com\\tTRUE\\t/\\tFALSE\\t0\\tuin\\t179644359\\n.qq.com\\tTRUE\\t/\\tFALSE\\t0\\tqm_keyst\\txxx",
        "url": "https://y.qq.com/n/ryqq/playlist/8119523393",
        "format": "128mp3"
    }
    ```
    """

    # 创建临时cookie文件
    cookie_file = None
    try:
        # 将cookie字符串写入临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            cookie_file = f.name
            f.write(req.cookie)

        # 配置yt-dlp选项
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
            # 提取信息
            info = ydl.extract_info(req.url, download=False)

            # 判断是单个歌曲还是歌单
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
                # 单个歌曲
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

        return ResponseModel(
            code=200,
            router=request.url.path,
            data={
                "total": len(songs),
                "songs": songs
            }
        )

    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(
            code=status_code,
            router=request.url.path,
            params={"url": req.url, "format": req.format, "error": str(e)}
        )
        raise HTTPException(status_code=status_code, detail=detail.dict())

    finally:
        # 清理临时cookie文件
        if cookie_file and os.path.exists(cookie_file):
            try:
                os.unlink(cookie_file)
            except:
                pass
