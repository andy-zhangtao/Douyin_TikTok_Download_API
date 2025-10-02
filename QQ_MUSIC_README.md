# QQ音乐下载功能说明

## 功能概述

本项目已集成QQ音乐下载功能,支持通过Cookie下载VIP歌曲和歌单。

## 后端API

### 接口地址
```
POST /api/qqmusic/download
```

### 请求参数
```json
{
  "cookie": "Netscape格式的Cookie字符串",
  "url": "QQ音乐歌曲或歌单链接",
  "format": "音频格式(可选: 128mp3/320mp3/flac/m4a/bestaudio)"
}
```

### 返回数据
```json
{
  "code": 200,
  "router": "/api/qqmusic/download",
  "data": {
    "total": 61,
    "songs": [
      {
        "title": "歌曲标题",
        "artist": "艺术家",
        "album": "专辑",
        "download_url": "下载链接",
        "duration": 180,
        "filesize": 3145728,
        "format": "m4a",
        "error": null
      }
    ]
  }
}
```

## 前端页面

### 访问方式
1. 启动服务后访问主页
2. 在功能选择下拉框中选择 "🎵 QQ音乐下载"
3. 输入以下信息:
   - Cookie (Netscape格式)
   - 歌曲或歌单链接
   - 选择音频格式

### 使用说明

#### 1. 获取Cookie
使用第三方Cookie导出工具(如EditThisCookie、Cookie-Editor)从QQ音乐网站导出Cookie,选择Netscape格式。

Cookie示例:
```
# Netscape HTTP Cookie File
.qq.com	TRUE	/	FALSE	0	uin	179644359
.qq.com	TRUE	/	FALSE	0	qm_keyst	xxxxx
.qq.com	TRUE	/	FALSE	0	qqmusic_key	xxxxx
```

#### 2. 输入歌曲链接
支持单曲和歌单链接:
- 单曲: `https://y.qq.com/n/ryqq/songDetail/003fA11G0Pdvnm`
- 歌单: `https://y.qq.com/n/ryqq/playlist/9482566232`

#### 3. 选择音频格式
- **128kbps MP3** (推荐): 文件小,音质较好
- **320kbps MP3**: 高品质MP3
- **FLAC无损**: 无损音质,文件较大
- **M4A**: Apple格式
- **最佳音质**: 自动选择最佳可用格式

### 功能特点

✅ 支持单曲和歌单批量解析
✅ 支持VIP歌曲下载(需要有效Cookie)
✅ 支持多种音频格式选择
✅ 显示歌曲详细信息(标题、艺术家、专辑、时长)
✅ 提供直接下载链接
✅ 美观的界面设计

## 技术实现

### 后端
- 框架: FastAPI
- 下载引擎: yt-dlp
- 文件: `app/api/endpoints/qqmusic_web.py`

### 前端
- 框架: PyWebIO
- 文件: `app/web/views/QQMusicParser.py`
- 主页: `app/web/app.py`

### 依赖
```
yt-dlp>=2024.0.0
```

## 注意事项

⚠️ **重要提示**:
1. Cookie中必须包含QQ登录的认证信息(uin, qm_keyst, qqmusic_key等)
2. Cookie必须是Netscape格式
3. VIP歌曲需要使用VIP账号的Cookie
4. Cookie有效期有限,失效后需要重新获取
5. 请遵守QQ音乐服务条款,仅用于个人学习用途

## 测试示例

已测试的歌单:
- MRM歌单: `https://y.qq.com/n/ryqq/playlist/9482566232` (61首歌)
- 越野跑歌单: `https://y.qq.com/n/ryqq/playlist/8119523393`

测试结果: ✅ 所有歌曲成功获取下载链接

## 故障排除

### 问题1: 无法获取下载链接
**原因**: Cookie无效或过期
**解决**: 重新从浏览器导出Cookie

### 问题2: VIP歌曲无法下载
**原因**: 使用的不是QQ登录的Cookie,或账号非VIP
**解决**: 确保使用QQ账号登录QQ音乐后导出Cookie

### 问题3: 服务启动失败
**原因**: Python版本过低(需要3.10+)或依赖未安装
**解决**:
```bash
pip install -r requirements.txt
```

## 更新日志

### v1.0.0 (2025-10-01)
- ✅ 添加QQ音乐下载后端API
- ✅ 添加前端QQ音乐解析界面
- ✅ 支持单曲和歌单解析
- ✅ 支持多种音频格式
- ✅ 集成到主页功能选择
