# PyWebIO组件/PyWebIO components
import os

import yaml
from pywebio import session, config as pywebio_config
from pywebio.input import *
from pywebio.output import *

from app.web.views.ParseVideo import parse_video
from app.web.views.QQMusicParser import qqmusic_parser
# PyWebIO的各个视图/Views of PyWebIO
from app.web.views.ViewsUtils import ViewsUtils

# 读取上级再上级目录的配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    _config = yaml.safe_load(file)

pywebio_config(theme=_config['Web']['PyWebIO_Theme'],
               title=_config['Web']['Tab_Title'],
               description=_config['Web']['Description'],
               js_file=[
                   # 整一个看板娘，二次元浓度++
                   _config['Web']['Live2D_JS'] if _config['Web']['Live2D_Enable'] else None,
               ])


class MainView:
    def __init__(self):
        self.utils = ViewsUtils()

    # 主界面/Main view
    def main_view(self):
        # 左侧导航栏/Left navbar
        with use_scope('main'):
            # 设置favicon/Set favicon
            favicon_url = _config['Web']['Favicon']
            session.run_js(f"""
                            $('head').append('<link rel="icon" type="image/png" href="{favicon_url}">')
                            """)
            # 修改footer/Remove footer
            session.run_js("""$('footer').remove()""")
            # 设置不允许referrer/Set no referrer
            session.run_js("""$('head').append('<meta name=referrer content=no-referrer>');""")

            # SEO优化 - 基础Meta标签
            session.run_js("""
                // 设置语言
                $('html').attr('lang', 'zh-CN');

                // 添加关键词 - 优化后的精准关键词列表
                $('head').append('<meta name="keywords" content="VideoCube,视频魔方,抖音无水印下载,TikTok视频解析,QQ音乐下载工具,在线视频批量下载,免费视频解析器">');

                // 添加作者
                $('head').append('<meta name="author" content="VideoCube Team">');

                // 添加viewport（如果没有）
                if (!$('meta[name="viewport"]').length) {
                    $('head').append('<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">');
                }

                // 添加charset（如果没有）
                if (!$('meta[charset]').length) {
                    $('head').prepend('<meta charset="UTF-8">');
                }
            """)

            # SEO优化 - Open Graph标签（社交媒体分享优化）
            domain = _config['Web']['Domain']
            title = _config['Web']['Tab_Title']
            description = _config['Web']['Description']
            session.run_js(f"""
                // Open Graph标签
                $('head').append('<meta property="og:type" content="website">');
                $('head').append('<meta property="og:site_name" content="VideoCube">');
                $('head').append('<meta property="og:title" content="{title}">');
                $('head').append('<meta property="og:description" content="{description}">');
                $('head').append('<meta property="og:url" content="{domain}">');
                $('head').append('<meta property="og:image" content="{favicon_url}">');
                $('head').append('<meta property="og:locale" content="zh_CN">');

                // Twitter Card标签
                $('head').append('<meta name="twitter:card" content="summary_large_image">');
                $('head').append('<meta name="twitter:title" content="{title}">');
                $('head').append('<meta name="twitter:description" content="{description}">');
                $('head').append('<meta name="twitter:image" content="{favicon_url}">');

                // Canonical URL
                $('head').append('<link rel="canonical" href="{domain}">');
            """)

            # SEO优化 - 结构化数据（JSON-LD）
            session.run_js(f"""
                var structuredData = {{
                    "@context": "https://schema.org",
                    "@type": "WebApplication",
                    "name": "VideoCube",
                    "alternateName": "视频魔方",
                    "description": "{description}",
                    "url": "{domain}",
                    "applicationCategory": "MultimediaApplication",
                    "operatingSystem": "Web Browser",
                    "offers": {{
                        "@type": "Offer",
                        "price": "0",
                        "priceCurrency": "CNY"
                    }},
                    "featureList": [
                        "抖音视频无水印下载",
                        "TikTok视频批量解析",
                        "QQ音乐高品质下载",
                        "在线视频批量处理",
                        "免费视频解析工具"
                    ],
                    "screenshot": "{favicon_url}",
                    "aggregateRating": {{
                        "@type": "AggregateRating",
                        "ratingValue": "4.8",
                        "ratingCount": "1000",
                        "bestRating": "5",
                        "worstRating": "1"
                    }}
                }};

                var script = document.createElement('script');
                script.type = 'application/ld+json';
                script.text = JSON.stringify(structuredData);
                $('head').append(script);
            """)

            # 设置背景颜色/Set background color
            session.run_js("""
                $('head').append('<style>body { background-color: #faf5cf !important; } .pywebio-content { background-color: #faf5cf !important; } .container, .container-fluid { background-color: #faf5cf !important; } #pywebio-scope-ROOT { background-color: #faf5cf !important; } div { background-color: inherit !important; }</style>');
            """)
            # 设置标题/Set title
            title = self.utils.t("视频魔方 - 一键批量解析神器",
                                 "VideoCube - One-Click Batch Parser")
            put_html(f"""
                    <div style="text-align: center; padding: 20px 0; background: transparent; margin-bottom: 20px;">
                        <div style="display: inline-flex; align-items: center; justify-content: center; gap: 20px; flex-wrap: wrap;">
                            <a href="/" alt="logo">
                                <img src="{favicon_url}"
                                     style="width: 80px; height: 80px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); transition: transform 0.3s ease;"
                                     onmouseover="this.style.transform='scale(1.1)'"
                                     onmouseout="this.style.transform='scale(1)'"/>
                            </a>
                            <div style="text-align: left;">
                                <h1 style="color: #2c3e50; margin: 0; font-size: 2.2em; font-weight: bold; text-shadow: none; font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;">
                                    {title}
                                </h1>
                                <p style="color: #34495e; margin: 8px 0 0 0; font-size: 1.1em; font-weight: 400;">
                                    {self.utils.t("简单快速 · 批量高效 · 完全免费", "Simple & Fast · Batch Processing · Completely Free")}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div style="text-align: center; margin: 20px 0 30px 0; padding: 20px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%); border-radius: 12px; border: 2px solid #667eea;">
                        <a href="/help" target="_blank" style="display: inline-block; font-size: 1.1em; font-weight: 600; color: #667eea; text-decoration: none; padding: 12px 25px; background: white; border-radius: 25px; transition: all 0.3s; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);"
                           onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 20px rgba(102, 126, 234, 0.4)'; this.style.color='#764ba2';"
                           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(102, 126, 234, 0.2)'; this.style.color='#667eea';">
                            📖 {self.utils.t("如何获取QQ音乐Cookie？查看完整使用教程", "How to get QQ Music Cookie? View complete tutorial")} →
                        </a>
                    </div>
                    """)
            # 添加功能选择按钮
            put_html("""
            <style>
            .function-selector {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin: 20px 0 30px 0;
                flex-wrap: wrap;
            }
            .function-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                color: white;
                font-weight: 600;
                font-size: 16px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .function-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            .function-btn.active {
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.8);
            }
            </style>
            """)

            # 功能选择
            function_choice = select(
                ViewsUtils.t("选择功能", "Select Function"),
                options=[
                    (ViewsUtils.t("📹 视频解析下载", "📹 Video Parser"), "video"),
                    (ViewsUtils.t("🎵 QQ音乐下载", "🎵 QQ Music Download"), "qqmusic")
                ],
                value="video"
            )

            # 根据选择显示不同功能
            if function_choice == "video":
                parse_video()
            elif function_choice == "qqmusic":
                qqmusic_parser()
