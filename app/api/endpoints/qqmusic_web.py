from typing import List, Optional
from fastapi import APIRouter, Body, Request, HTTPException
from pydantic import BaseModel, Field
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel
import yt_dlp
import tempfile
import os
import logging
import traceback

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


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
        logger.info(f"========== QQ音乐下载请求开始 ==========")
        logger.info(f"请求URL: {req.url}")
        logger.info(f"音频格式: {req.format}")
        logger.info(f"Cookie长度: {len(req.cookie)} 字符")
        logger.debug(f"Cookie内容预览: {req.cookie[:200]}...")

        # 将cookie字符串写入临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            cookie_file = f.name
            f.write(req.cookie)
            logger.info(f"临时Cookie文件已创建: {cookie_file}")

        # 配置yt-dlp选项
        ydl_opts = {
            'cookiefile': cookie_file,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'format': req.format if req.format != 'bestaudio' else 'bestaudio',
            'ignoreerrors': True,
            'proxy': '',  # 禁用代理
        }

        logger.info(f"yt-dlp配置: {ydl_opts}")

        songs = []
        failed_count = 0
        success_count = 0

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 提取信息
            logger.info("开始调用 yt-dlp 提取信息...")
            info = ydl.extract_info(req.url, download=False)
            logger.info(f"yt-dlp 提取完成，info类型: {type(info)}")
            logger.debug(f"info keys: {info.keys() if info else 'None'}")

            # 判断是单个歌曲还是歌单
            if 'entries' in info:
                # 歌单
                total_entries = len(info['entries'])
                logger.info(f"检测到歌单，共 {total_entries} 首歌曲")

                for idx, entry in enumerate(info['entries'], 1):
                    if entry is None:
                        logger.warning(f"歌曲 #{idx}: entry为None，跳过")
                        failed_count += 1
                        # 添加失败记录
                        songs.append({
                            "title": f"歌曲 #{idx}",
                            "artist": None,
                            "album": None,
                            "download_url": None,
                            "duration": None,
                            "filesize": None,
                            "format": None,
                            "error": "无法提取歌曲信息"
                        })
                        continue

                    try:
                        logger.info(f"处理歌曲 #{idx}: {entry.get('title', 'Unknown')}")
                        logger.debug(f"歌曲 #{idx} 详细信息: {entry}")

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

                        if not entry.get('url'):
                            logger.warning(f"歌曲 #{idx} 无下载链接")
                            failed_count += 1
                        else:
                            success_count += 1

                        songs.append(song.dict())

                    except Exception as song_error:
                        logger.error(f"处理歌曲 #{idx} 时出错: {str(song_error)}")
                        failed_count += 1
                        # 添加失败记录
                        songs.append({
                            "title": entry.get('title', f'歌曲 #{idx}'),
                            "artist": entry.get('artist') or entry.get('uploader'),
                            "album": entry.get('album'),
                            "download_url": None,
                            "duration": None,
                            "filesize": None,
                            "format": None,
                            "error": f"处理失败: {str(song_error)}"
                        })
            else:
                # 单个歌曲
                logger.info(f"检测到单个歌曲: {info.get('title', 'Unknown')}")
                logger.debug(f"歌曲详细信息: {info}")

                try:
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

                    if not info.get('url'):
                        logger.warning("单个歌曲无下载链接")
                        failed_count += 1
                    else:
                        success_count += 1

                    songs.append(song.dict())

                except Exception as song_error:
                    logger.error(f"处理单个歌曲时出错: {str(song_error)}")
                    failed_count += 1
                    songs.append({
                        "title": info.get('title', 'Unknown'),
                        "artist": info.get('artist') or info.get('uploader'),
                        "album": info.get('album'),
                        "download_url": None,
                        "duration": None,
                        "filesize": None,
                        "format": None,
                        "error": f"处理失败: {str(song_error)}"
                    })

        logger.info(f"========== 处理完成 ==========")
        logger.info(f"总计: {len(songs)} 首 | 成功: {success_count} 首 | 失败: {failed_count} 首")

        return ResponseModel(
            code=200,
            router=request.url.path,
            data={
                "total": len(songs),
                "success": success_count,
                "failed": failed_count,
                "songs": songs
            }
        )

    except Exception as e:
        logger.error(f"========== 处理失败 ==========")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error(f"完整堆栈跟踪:\n{traceback.format_exc()}")

        status_code = 400
        detail = ErrorResponseModel(
            code=status_code,
            router=request.url.path,
            params={
                "url": req.url,
                "format": req.format,
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )
        raise HTTPException(status_code=status_code, detail=detail.dict())

    finally:
        # 清理临时cookie文件
        if cookie_file and os.path.exists(cookie_file):
            try:
                os.unlink(cookie_file)
                logger.info(f"临时Cookie文件已删除: {cookie_file}")
            except Exception as cleanup_error:
                logger.warning(f"清理临时文件失败: {cleanup_error}")
