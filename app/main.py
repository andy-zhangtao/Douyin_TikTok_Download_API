# ==============================================================================
# Copyright (C) 2021 Evil0ctal
#
# This file is part of the Douyin_TikTok_Download_API project.
#
# This project is licensed under the Apache License 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# 　　　　 　　  ＿＿
# 　　　 　　 ／＞　　フ
# 　　　 　　| 　_　 _ l
# 　 　　 　／` ミ＿xノ
# 　　 　 /　　　 　 |       Feed me Stars ⭐ ️
# 　　　 /　 ヽ　　 ﾉ
# 　 　 │　　|　|　|
# 　／￣|　　 |　|　|
# 　| (￣ヽ＿_ヽ_)__)
# 　＼二つ
# ==============================================================================
#
# Contributor Link:
# - https://github.com/Evil0ctal
# - https://github.com/Johnserf-Seed
#
# ==============================================================================


# FastAPI APP
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from app.api.router import router as api_router
import markdown

# PyWebIO APP
from app.web.app import MainView
from pywebio.platform.fastapi import asgi_app

# OS
import os

# YAML
import yaml

# Load Config

# 读取上级再上级目录的配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)


Host_IP = config['API']['Host_IP']
Host_Port = config['API']['Host_Port']

# API Tags
tags_metadata = [
    {
        "name": "Hybrid-API",
        "description": "**(混合数据接口/Hybrid-API data endpoints)**",
    },
    {
        "name": "Douyin-Web-API",
        "description": "**(抖音Web数据接口/Douyin-Web-API data endpoints)**",
    },
    {
        "name": "TikTok-Web-API",
        "description": "**(TikTok-Web-API数据接口/TikTok-Web-API data endpoints)**",
    },
    {
        "name": "TikTok-App-API",
        "description": "**(TikTok-App-API数据接口/TikTok-App-API data endpoints)**",
    },
    {
        "name": "Bilibili-Web-API",
        "description": "**(Bilibili-Web-API数据接口/Bilibili-Web-API data endpoints)**",
    },
    {
        "name": "QQMusic-API",
        "description": "**(QQ音乐数据接口/QQMusic-API data endpoints)**",
    },
    {
        "name": "iOS-Shortcut",
        "description": "**(iOS快捷指令数据接口/iOS-Shortcut data endpoints)**",
    },
    {
        "name": "Download",
        "description": "**(下载数据接口/Download data endpoints)**",
    },
]

version = config['API']['Version']
update_time = config['API']['Update_Time']
environment = config['API']['Environment']

description = f"""
### [中文]

#### 关于
- **Github**: [Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API)
- **版本**: `{version}`
- **更新时间**: `{update_time}`
- **环境**: `{environment}`
- **文档**: [API Documentation](https://douyin.wtf/docs)
#### 备注
- 本项目仅供学习交流使用，不得用于违法用途，否则后果自负。
- 如果你不想自己部署，可以直接使用我们的在线API服务：[Douyin_TikTok_Download_API](https://douyin.wtf/docs)
- 如果你需要更稳定以及更多功能的API服务，可以使用付费API服务：[TikHub API](https://api.tikhub.io/)

### [English]

#### About
- **Github**: [Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API)
- **Version**: `{version}`
- **Last Updated**: `{update_time}`
- **Environment**: `{environment}`
- **Documentation**: [API Documentation](https://douyin.wtf/docs)
#### Note
- This project is for learning and communication only, and shall not be used for illegal purposes, otherwise the consequences shall be borne by yourself.
- If you do not want to deploy it yourself, you can directly use our online API service: [Douyin_TikTok_Download_API](https://douyin.wtf/docs)
- If you need a more stable and feature-rich API service, you can use the paid API service: [TikHub API](https://api.tikhub.io)
"""

docs_url = config['API']['Docs_URL']
redoc_url = config['API']['Redoc_URL']

app = FastAPI(
    title="Douyin TikTok Download API",
    description=description,
    version=version,
    openapi_tags=tags_metadata,
    docs_url=docs_url,  # 文档路径
    redoc_url=redoc_url,  # redoc文档路径
)

# API router
app.include_router(api_router, prefix="/api")

# 文档路由
@app.get("/help", response_class=HTMLResponse, include_in_schema=False)
async def help_page():
    """QQ音乐Cookie获取帮助文档"""
    doc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'qqmusic-cookie-guide.md')

    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 转换Markdown为HTML
        html_body = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'nl2br', 'toc']
        )

        # 包装成完整HTML页面
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>QQ音乐Cookie获取与使用教程 - VideoCube</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, sans-serif;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 30px 20px;
                    line-height: 1.8;
                    color: #333;
                    background: #f5f5f5;
                }}
                .content {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #667eea;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 15px;
                    margin-top: 30px;
                }}
                h2 {{
                    color: #764ba2;
                    margin-top: 35px;
                    margin-bottom: 15px;
                    border-left: 4px solid #667eea;
                    padding-left: 15px;
                }}
                h3 {{
                    color: #555;
                    margin-top: 25px;
                }}
                h4 {{
                    color: #666;
                    margin-top: 20px;
                }}
                code {{
                    background: #f4f4f4;
                    padding: 3px 6px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    color: #e03131;
                    font-size: 0.9em;
                }}
                pre {{
                    background: #2d2d2d;
                    color: #f8f8f2;
                    padding: 20px;
                    border-radius: 8px;
                    overflow-x: auto;
                    margin: 20px 0;
                }}
                pre code {{
                    background: transparent;
                    color: #f8f8f2;
                    padding: 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                tr:hover {{
                    background: #f9f9f9;
                }}
                blockquote {{
                    border-left: 4px solid #ffc107;
                    background: #fff3cd;
                    padding: 15px 20px;
                    margin: 20px 0;
                    color: #856404;
                }}
                a {{
                    color: #667eea;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                img {{
                    max-width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    margin: 20px 0;
                }}
                .back-btn {{
                    display: inline-block;
                    margin-bottom: 20px;
                    padding: 10px 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 20px;
                    text-decoration: none;
                    transition: all 0.3s;
                }}
                .back-btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
                    text-decoration: none;
                }}
                ul, ol {{
                    margin: 15px 0;
                    padding-left: 30px;
                }}
                li {{
                    margin: 8px 0;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                <a href="/" class="back-btn">← 返回首页</a>
                {html_body}
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>文档未找到</h1><p>请确保文档文件存在</p>",
            status_code=404
        )


# SEO文件路由
@app.get("/robots.txt", include_in_schema=False)
async def robots():
    """返回robots.txt文件"""
    robots_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'robots.txt')
    if os.path.exists(robots_path):
        return FileResponse(robots_path, media_type="text/plain")
    return FileResponse(path=robots_path, status_code=404)

@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    """返回sitemap.xml文件"""
    sitemap_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'sitemap.xml')
    if os.path.exists(sitemap_path):
        return FileResponse(sitemap_path, media_type="application/xml")
    return FileResponse(path=sitemap_path, status_code=404)

# PyWebIO APP
if config['Web']['PyWebIO_Enable']:
    webapp = asgi_app(lambda: MainView().main_view())
    app.mount("/", webapp)

if __name__ == '__main__':
    uvicorn.run(app, host=Host_IP, port=Host_Port)
