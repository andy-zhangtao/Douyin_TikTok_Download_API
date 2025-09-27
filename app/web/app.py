# PyWebIO组件/PyWebIO components
import os

import yaml
from pywebio import session, config as pywebio_config
from pywebio.input import *
from pywebio.output import *

from app.web.views.ParseVideo import parse_video
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
            # 设置标题/Set title
            title = self.utils.t("视频魔方 - 一键批量解析神器",
                                 "VideoCube - One-Click Batch Parser")
            put_html(f"""
                    <div align="center">
                    <a href="/" alt="logo" ><img src="{favicon_url}" width="100"/></a>
                    <h1 align="center">{title}</h1>
                    </div>
                    """)
            # 设置导航栏/Navbar (已移除所有导航按钮)
            # put_row([]) # 导航栏已被移除

            # 直接显示批量解析视频功能/Direct batch video parsing function
            put_markdown(f"## {self.utils.t('🔍批量解析视频', '🔍Batch Parse Video')}")
            # 直接运行批量解析视频功能
            parse_video()
