import asyncio
import os
import time

import yaml
from pywebio.input import *
from pywebio.output import *
from pywebio_battery import put_video

from app.web.views.ViewsUtils import ViewsUtils

from crawlers.hybrid.hybrid_crawler import HybridCrawler

HybridCrawler = HybridCrawler()

# 读取上级再上级目录的配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)


# 校验输入值/Validate input value
def valid_check(input_data: str):
    # 检索出所有链接并返回列表/Retrieve all links and return a list
    url_list = ViewsUtils.find_url(input_data)
    # 总共找到的链接数量/Total number of links found
    total_urls = len(url_list)
    if total_urls == 0:
        # 统一更清晰的校验文案
        warn_info = ViewsUtils.t('未检测到有效链接，请检查输入内容是否正确。',
                                 'No valid links detected. Please check your input.')
        return warn_info
    else:
        # 最大接受提交URL的数量/Maximum number of URLs accepted
        max_urls = config['Web']['Max_Take_URLs']
        if total_urls > int(max_urls):
            warn_info = ViewsUtils.t(
                f'输入链接过多，当前仅处理前 {max_urls} 条。',
                f'Too many links; only the first {max_urls} will be processed.'
            )
            return warn_info


# 错误处理/Error handling
def error_do(reason: str, value: str) -> None:
    # 输出分隔线
    put_html("<hr>")
    # 自定义可读性更好的错误提示（深色文字以适配浅色背景）
    put_html(
        f"""
        <div class=\"vc-alert\">
            <div class=\"vc-alert-title\">⚠ {ViewsUtils.t('解析出错', 'Error occurred')}</div>
            <div class=\"vc-alert-desc\">{ViewsUtils.t('已跳过该条，继续处理下一条。', 'Skipping this entry and continuing.')}</div>
        </div>
        """
    )
    put_html(f"<h3>⚠{ViewsUtils.t('详情', 'Details')}</h3>")
    put_table([
        [
            ViewsUtils.t('原因', 'reason'),
            ViewsUtils.t('输入值', 'input value')
        ],
        [
            reason,
            value
        ]
    ])
    # 精简错误提示，不再输出额外的引导与链接
    put_html("<hr>")


def parse_video():
    # 添加自定义CSS样式来美化按钮和背景
    put_html("""
    <style>
    :root {
        /* 主题与颜色变量 */
        --vc-bg: #faf5cf;
        --vc-primary: #667eea;          /* 与按钮渐变主色一致 */
        --vc-primary-2: #764ba2;        /* 渐变副色 */
        --vc-info-text: #163a5f;
        --vc-info-bg: #e7f3ff;
        --vc-info-border: #b6daff;
        --vc-info-accent: #1c7ed6;
        --vc-error-text: #5c2b29;
        --vc-error-bg: #fdecea;
        --vc-error-border: #f5c2c7;
        --vc-error-accent: #e03131;
        --vc-neutral-text: #1d1d1f;
        --vc-neutral-bg: #f6f6f7;
        --vc-neutral-border: #e5e5ea;
        --vc-success-text: #1e4620;      /* 成功提示文字色 */
        --vc-success-bg: #e6f4ea;        /* 成功提示背景色 */
        --vc-success-border: #b7e2c1;    /* 成功提示边框色 */
        --vc-success-accent: #2f9e44;    /* 成功提示左侧色条 */
    }
    /* 设置页面背景颜色 */
    body {
        background-color: var(--vc-bg) !important;
    }
    .pywebio-content {
        background-color: var(--vc-bg) !important;
    }
    /* 设置所有容器的背景颜色 */
    .container, .container-fluid {
        background-color: var(--vc-bg) !important;
    }
    /* 设置表单区域的背景颜色 */
    .form-group, .form-control {
        background-color: var(--vc-bg) !important;
    }
    /* 设置PyWebIO的主要内容区域 */
    #pywebio-scope-ROOT {
        background-color: var(--vc-bg) !important;
    }
    /* 设置所有div容器的背景 */
    div {
        background-color: inherit !important;
    }
    /* 专门针对输入框和按钮区域 */
    .pywebio-input-group {
        background-color: var(--vc-bg) !important;
    }
    .form-submit-btn {
        background: linear-gradient(135deg, var(--vc-primary) 0%, var(--vc-primary-2) 100%) !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
        margin-right: 10px !important;
    }
    .form-submit-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    .form-reset-btn {
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
    .form-reset-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    /* 为表单按钮容器添加样式 */
    .form-buttons {
        text-align: center !important;
        margin-top: 20px !important;
    }
    /* 修改PyWebIO默认按钮样式 */
    .btn-primary {
        background: linear-gradient(135deg, var(--vc-primary) 0%, var(--vc-primary-2) 100%) !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .btn-secondary {
        background: linear-gradient(135deg, var(--vc-primary) 0%, var(--vc-primary-2) 100%) !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .btn-secondary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    /* 专门针对重置按钮的样式 */
    button[type="reset"], input[type="reset"] {
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
    button[type="reset"]:hover, input[type="reset"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    .btn:hover {
        transform: translateY(-2px) !important;
    }
    /* 自定义错误提示样式（深色文字+浅色背景） */
    .vc-alert {
        color: var(--vc-error-text) !important;
        background: var(--vc-error-bg) !important;
        border: 1px solid var(--vc-error-border) !important;
        border-left: 4px solid var(--vc-error-accent) !important;
        padding: 12px 14px !important;
        border-radius: 8px !important;
        margin: 10px 0 !important;
    }
    .vc-alert-title { font-weight: 700 !important; margin-bottom: 4px !important; }
    .vc-alert-desc  { font-weight: 400 !important; }
    /* 成功提示样式 */
    .vc-success {
        color: var(--vc-success-text) !important;
        background: var(--vc-success-bg) !important;
        border: 1px solid var(--vc-success-border) !important;
        border-left: 4px solid var(--vc-success-accent) !important;
        padding: 12px 14px !important;
        border-radius: 8px !important;
        margin: 10px 0 !important;
    }
    .vc-success-title { font-weight: 700 !important; }
    /* 兜底：覆盖 PyWebIO/Bootstrap 内置警告颜色，防止白字不辨识 */
    .alert-danger, .alert-warning, .alert-info {
        color: var(--vc-neutral-text) !important;
        background-color: var(--vc-neutral-bg) !important;
        border-color: var(--vc-neutral-border) !important;
    }
    /* 信息提示（深蓝文字+浅蓝背景） */
    .vc-info {
        color: var(--vc-info-text) !important;
        background: var(--vc-info-bg) !important;
        border: 1px solid var(--vc-info-border) !important;
        border-left: 4px solid var(--vc-info-accent) !important;
        padding: 12px 14px !important;
        border-radius: 8px !important;
        margin: 10px 0 !important;
        white-space: pre-line !important;       /* 处理 \n 换行 */
    }
    .vc-info-title { font-weight: 700 !important; margin-bottom: 4px !important; }
    .vc-info-desc  { font-weight: 400 !important; }
    </style>
    """)

    placeholder = ViewsUtils.t(
        "支持抖音、TikTok视频链接批量解析。可直接粘贴多个链接，无需分隔符。",
        "Support batch parsing of Douyin and TikTok video links. Paste multiple links directly without separators.")
    input_data = textarea(
        ViewsUtils.t('粘贴视频链接或分享口令',
                     "Paste video links or share codes here"),
        type=TEXT,
        validate=valid_check,
        required=True,
        placeholder=placeholder,
        position=0)
    url_lists = ViewsUtils.find_url(input_data)
    # 解析开始时间
    start = time.time()
    # 成功/失败统计
    success_count = 0
    failed_count = 0
    # 链接总数
    url_count = len(url_lists)
    # 解析成功的url
    success_list = []
    # 解析失败的url
    failed_list = []
    # 输出一个提示条
    with use_scope('loading_text'):
        # 输出一个分行符
        put_row([put_html('<br>')])
        title = ViewsUtils.t('已收到链接，正在处理',
                             'Links received, processing')
        desc  = ViewsUtils.t('请稍候…',
                             'Please wait…')
        put_html(
            f"""
            <div class=\"vc-info\">
                <div class=\"vc-info-title\">{title}</div>
                <div class=\"vc-info-desc\">{desc}</div>
            </div>
            """
        )
    # 结果页标题
    put_scope('result_title')
    # 遍历链接列表
    for url in url_lists:
        # 链接编号
        url_index = url_lists.index(url) + 1
        # 解析
        try:
            data = asyncio.run(HybridCrawler.hybrid_parsing_single_video(url, minimal=True))
        except Exception as e:
            error_msg = str(e)
            with use_scope(str(url_index)):
                error_do(reason=error_msg, value=url)
            failed_count += 1
            failed_list.append(url)
            continue

        # 创建一个视频/图集的公有变量
        url_type = ViewsUtils.t('视频', 'Video') if data.get('type') == 'video' else ViewsUtils.t('图片', 'Image')
        platform = data.get('platform')
        table_list = [
            [ViewsUtils.t('类型', 'type'), ViewsUtils.t('内容', 'content')],
            [ViewsUtils.t('解析类型', 'Type'), url_type],
            [ViewsUtils.t('平台', 'Platform'), platform],
            [f'{url_type} ID', data.get('aweme_id')],
            [ViewsUtils.t(f'{url_type}描述', 'Description'), data.get('desc')],
            [ViewsUtils.t('作者昵称', 'Author nickname'), data.get('author').get('nickname')],
            [ViewsUtils.t('作者ID', 'Author ID'), data.get('author').get('unique_id')],
            [ViewsUtils.t('API链接', 'API URL'),
             put_link(
                 ViewsUtils.t('点击查看', 'Click to view'),
                 f"/api/hybrid/video_data?url={url}&minimal=false",
                 new_window=True)],
            [ViewsUtils.t('API链接-精简', 'API URL-Minimal'),
             put_link(ViewsUtils.t('点击查看', 'Click to view'),
                      f"/api/hybrid/video_data?url={url}&minimal=true",
                      new_window=True)]

        ]
        # 如果是视频/If it's video
        if url_type == ViewsUtils.t('视频', 'Video'):
            # 添加视频信息
            wm_video_url_HQ = data.get('video_data').get('wm_video_url_HQ')
            nwm_video_url_HQ = data.get('video_data').get('nwm_video_url_HQ')
            if wm_video_url_HQ and nwm_video_url_HQ:
                table_list.insert(4, [ViewsUtils.t('视频链接-水印', 'Video URL-Watermark'),
                                      put_link(ViewsUtils.t('点击查看', 'Click to view'),
                                               wm_video_url_HQ, new_window=True)])
                table_list.insert(5, [ViewsUtils.t('视频链接-无水印', 'Video URL-No Watermark'),
                                      put_link(ViewsUtils.t('点击查看', 'Click to view'),
                                               nwm_video_url_HQ, new_window=True)])
            table_list.insert(6, [ViewsUtils.t('视频下载-水印', 'Video Download-Watermark'),
                                  put_link(ViewsUtils.t('点击下载', 'Click to download'),
                                           f"/api/download?url={url}&prefix=true&with_watermark=true",
                                           new_window=True)])
            table_list.insert(7, [ViewsUtils.t('视频下载-无水印', 'Video Download-No-Watermark'),
                                  put_link(ViewsUtils.t('点击下载', 'Click to download'),
                                           f"/api/download?url={url}&prefix=true&with_watermark=false",
                                           new_window=True)])
            # 添加视频信息
            table_list.insert(0, [
                put_video(data.get('video_data').get('nwm_video_url_HQ'), poster=None, loop=True, width='50%')])
        # 如果是图片/If it's image
        elif url_type == ViewsUtils.t('图片', 'Image'):
            # 添加图片下载链接
            table_list.insert(4, [ViewsUtils.t('图片打包下载-水印', 'Download images ZIP-Watermark'),
                                  put_link(ViewsUtils.t('点击下载', 'Click to download'),
                                           f"/api/download?url={url}&prefix=true&with_watermark=true",
                                           new_window=True)])
            table_list.insert(5, [ViewsUtils.t('图片打包下载-无水印', 'Download images ZIP-No-Watermark'),
                                  put_link(ViewsUtils.t('点击下载', 'Click to download'),
                                           f"/api/download?url={url}&prefix=true&with_watermark=false",
                                           new_window=True)])
            # 添加图片信息
            no_watermark_image_list = data.get('image_data').get('no_watermark_image_list')
            for image in no_watermark_image_list:
                table_list.append(
                    [ViewsUtils.t('图片预览(如格式可显示): ', 'Image preview (if the format can be displayed):'),
                     put_image(image, width='50%')])
                table_list.append([ViewsUtils.t('图片直链: ', 'Image URL:'),
                                   put_link(ViewsUtils.t('⬆️点击打开图片⬆️', '⬆️Click to open image⬆️'), image,
                                            new_window=True)])
        # 向网页输出表格/Put table on web page
        with use_scope(str(url_index)):
            # 显示进度
            put_info(
                ViewsUtils.t(f'正在解析第{url_index}/{url_count}个链接: ',
                             f'Parsing the {url_index}/{url_count}th link: '),
                put_link(url, url, new_window=True), closable=True)
            put_table(table_list)
            put_html('<hr>')
        scroll_to(str(url_index))
        success_count += 1
        success_list.append(url)
        # print(success_count: {success_count}, success_list: {success_list}')
    # 全部解析完成跳出for循环/All parsing completed, break out of for loop
    with use_scope('result_title'):
        put_row([put_html('<br>')])
        put_markdown(ViewsUtils.t('## 📝结果概览:', '## 📝Results Overview:'))
        put_row([put_html('<br>')])
    with use_scope('result'):
        # 清除进度条
        clear('loading_text')
        # 滚动至result
        scroll_to('result')
        # for循环结束，向网页输出成功提醒（使用主题色的成功提示样式）
        success_title = ViewsUtils.t('解析完成', 'Parsing completed')
        put_html(f"""
            <div class=\"vc-success\">
                <div class=\"vc-success-title\">{success_title}</div>
            </div>
        """)
        # 以表格展示最终结果概览
        put_table([
            [ViewsUtils.t('指标', 'Metric'), ViewsUtils.t('数值', 'Value')],
            [ViewsUtils.t('成功', 'Success'), str(success_count)],
            [ViewsUtils.t('失败', 'Failed'), str(failed_count)],
            [ViewsUtils.t('总数量', 'Total'), str(success_count + failed_count)],
        ])
        # 成功列表（以表格展示）
        if len(success_list) > 0:
            rows = [[ViewsUtils.t('序号', '#'), ViewsUtils.t('链接', 'URL')]]
            for i, u in enumerate(success_list, start=1):
                rows.append([str(i), put_link(u, u, new_window=True)])
            put_html('<br>')
            put_markdown(f'**{ViewsUtils.t("成功列表", "Success list")}:**')
            put_table(rows)
        # 失败列表（以表格展示）
        if failed_count > 0:
            rows = [[ViewsUtils.t('序号', '#'), ViewsUtils.t('链接', 'URL')]]
            for i, u in enumerate(failed_list, start=1):
                rows.append([str(i), put_link(u, u, new_window=True)])
            put_html('<br>')
            put_markdown(f'**{ViewsUtils.t("失败列表", "Failed list")}:**')
            put_table(rows)
        # 所有输入链接（以表格展示）
        all_rows = [[ViewsUtils.t('序号', '#'), ViewsUtils.t('链接', 'URL')]]
        for i, u in enumerate(url_lists, start=1):
            all_rows.append([str(i), put_link(u, u, new_window=True)])
        put_html('<br>')
        put_markdown(ViewsUtils.t('**以下是您输入的所有链接：**', '**The following are all the links you entered:**'))
        put_table(all_rows)
        # 解析结束时间
        end = time.time()
        # 计算耗时,保留两位小数
        time_consuming = round(end - start, 2)
        # 显示耗时
        put_table([
            [ViewsUtils.t('指标', 'Metric'), ViewsUtils.t('数值', 'Value')],
            [ViewsUtils.t('耗时', 'Time'), f'{time_consuming}s']
        ])
        # 放置一个按钮，点击后跳转到顶部
        put_button(ViewsUtils.t('回到顶部', 'Back to top'), onclick=lambda: scroll_to('1'), color='success',
                   outline=True)
        # 返回主页链接（替换文案）
        put_link(ViewsUtils.t('返回首页', 'Back to home'), '/')
