# QQ音乐Cookie获取与使用教程

> 使用Chrome插件轻松获取QQ音乐Cookie，一键下载歌曲和歌单

---

## 📋 目录

- [前置准备](#前置准备)
- [获取Cookie步骤](#获取cookie步骤)
- [完整使用流程](#完整使用流程)
- [常见问题](#常见问题)

---

## 🔧 前置准备

### 1. 浏览器要求
- **Chrome浏览器**（或基于Chromium的浏览器，如Edge、Brave等）
- 版本要求：Chrome 88+

### 2. QQ音乐账号
- 需要登录QQ音乐网页版
- 建议使用QQ音乐VIP账号（可下载高品质音乐）

### 3. 安装Chrome插件 - EditThisCookie

**安装方式：**

1. 访问Chrome应用商店
2. 搜索 **"EditThisCookie"**
3. 点击"添加至Chrome"

**下载地址：**
```
https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg
```

**特点：**
- ✅ 功能强大，可查看和编辑Cookie
- ✅ 支持多种导出格式
- ✅ 使用简单，一键导出

---

## 🍪 获取Cookie步骤

### 步骤1：登录QQ音乐

1. 打开浏览器，访问 [QQ音乐网页版](https://y.qq.com/)
2. 点击右上角登录按钮
3. 使用QQ或微信扫码登录


### 步骤2：打开EditThisCookie插件

1. **确保当前页面是 `y.qq.com` 域名下**
2. 点击浏览器右上角的 **EditThisCookie** 插件图标（🍪 饼干图标）

![](https://p.ipic.vip/55xcgb.png)

### 步骤3：导出Cookie

1. 点击插件弹窗右下角的 **"导出"** 按钮（📥 图标）

![](https://p.ipic.vip/ynqb56.png)



2. 在弹出的格式选择菜单中，选择 **"Netscape HTTP Cookie File"** 格式

![](https://p.ipic.vip/1n5tjh.png)

3. Cookie内容会自动复制到剪贴板 ✅

### 步骤4：查看Cookie内容

1. 打开**记事本**或任意文本编辑器
2. 粘贴刚才复制的内容 (Ctrl+V 或 Cmd+V)
3. 内容格式应类似：

```plaintext
# Netscape HTTP Cookie File
# This is a generated file! Do not edit.

.qq.com	TRUE	/	FALSE	1735689600	uin	o1234567890
.qq.com	TRUE	/	TRUE	1735689600	qm_keyst	Q_H_L_xxxxxxxxxxxxx
.qq.com	TRUE	/	FALSE	1735689600	psrf_qqaccess_token	xxxxxxxxxxxxxxx
y.qq.com	FALSE	/	FALSE	1735689600	wxuin	12345678
.qq.com	TRUE	/	FALSE	1735689600	wxrefresh_token	xxxxxxxxxxxx
```

4. **确认Cookie已正确复制**（包括第一行注释）

---

## 🚀 完整使用流程

### 第1步：获取Cookie
按照上述步骤获取并复制Cookie内容

### 第2步：访问下载页面
打开本站QQ音乐下载页面

### 第3步：填写表单

#### 1. 粘贴Cookie

在 **"QQ音乐Cookie"** 输入框中，粘贴刚才复制的Cookie内容：

```plaintext
# Netscape HTTP Cookie File
.qq.com	TRUE	/	FALSE	0	uin	o1234567890
.qq.com	TRUE	/	FALSE	0	qm_keyst	Q_H_L_xxxxx
...（完整内容）
```

![](https://p.ipic.vip/93qbxl.png)


#### 2. 填写歌曲或歌单链接

**单曲链接示例：**
```
https://y.qq.com/n/ryqq/songDetail/001234567
```

**歌单链接示例：**
```
https://y.qq.com/n/ryqq/playlist/7654321098
```

**如何获取链接：**
1. 在QQ音乐网页版找到你想下载的歌曲/歌单
2. 复制浏览器地址栏的URL

![](https://p.ipic.vip/riefec.png)

#### 3. 选择音频格式

| 格式 | 音质 | 文件大小 | 适用场景 |
|------|------|----------|----------|
| **128kbps MP3** | 标准音质 | ~4MB/首 | 日常听歌（推荐） |
| **320kbps MP3** | 高音质 | ~10MB/首 | 发烧友 |
| **FLAC** | 无损音质 | ~30-50MB/首 | 需要VIP账号 |
| **M4A** | 高音质 | ~8MB/首 | Apple设备 |
| **最佳音质** | 自动选择 | 不定 | 自动匹配最高可用音质 |

> 💡 **提示：** FLAC格式需要QQ音乐VIP账号，否则会返回错误

### 第4步：获取下载链接

1. 点击 **"🚀 获取下载链接"** 按钮
2. 等待解析（单曲约5-10秒，歌单可能需要1-5分钟）

**解析中提示：**
- 单曲：`正在获取歌曲信息，请稍候...`
- 歌单：`⏰ 正在解析歌单，请耐心等待...`

### 第5步：下载音乐

解析成功后会显示歌曲列表，每首歌都有 **"⬇️ 下载"** 按钮：

1. 点击下载按钮
2. 浏览器会自动开始下载
3. 下载的文件名格式：`歌曲名 - 歌手名.mp3`


---

## ❓ 常见问题

### Q1: Cookie多久会过期？

**A:** QQ音乐的Cookie通常有效期为：
- 短期Cookie：1-7天
- 长期Cookie：30-90天

**建议：** 如果出现"登录失效"错误，重新导出Cookie即可

---

### Q2: 提示"解析失败"怎么办？

**可能原因：**

1. **Cookie已过期**
   - 解决：重新登录QQ音乐，导出新Cookie

2. **Cookie格式错误**
   - 检查是否完整复制（包括 `# Netscape HTTP Cookie File` 这一行）
   - 确保没有多余的空格或换行

3. **歌曲需要VIP权限**
   - 部分高音质格式需要VIP
   - 切换为 `128kbps MP3` 尝试

4. **网络问题**
   - 检查服务器网络连接
   - 稍后重试

---

### Q3: 找不到"Netscape HTTP Cookie File"选项？

**A:** EditThisCookie导出步骤：

1. 点击插件图标（🍪）
2. 点击右下角 **导出按钮**（📥 图标）
3. 会弹出格式选择菜单
4. 选择 **"Netscape HTTP Cookie File"**

如果还是找不到，可以：
- 更新插件到最新版本
- 或者选择 **"Header String"** 格式（需要手动调整格式）

---

### Q4: 歌单解析太慢怎么办？

**A:** 歌单解析速度取决于：
- 歌单歌曲数量（100首约需2-3分钟）
- 服务器性能
- 网络速度

**建议：**
- 耐心等待，不要刷新页面
- 如果歌单很大（>100首），建议分批下载
- 使用单曲链接下载速度更快

---

### Q5: 无法下载FLAC格式？

**A:** FLAC无损格式需要：
1. QQ音乐VIP账号
2. 该歌曲支持无损音质

**解决方案：**
- 确认已用VIP账号登录
- 尝试切换为 `320kbps MP3`

---

### Q6: 下载的文件没有音乐信息标签？

**A:** 本工具提供的是直链下载，不包含ID3标签。

**解决方案：**
- 使用 [Mp3tag](https://www.mp3tag.de/) 等工具自动补全标签
- 或使用支持自动识别的播放器（如：网易云音乐、foobar2000）

---

### Q7: 浏览器拦截了下载怎么办？

**A:** 部分浏览器可能拦截批量下载。

**解决方案：**
1. 允许本站弹出窗口和下载
2. 在浏览器设置中添加本站为信任网站
3. 使用Chrome浏览器（兼容性最好）

---

### Q8: Cookie安全吗？会泄露吗？

**A:** 本站的Cookie处理机制：
- ✅ Cookie仅在服务器临时存储（处理完立即删除）
- ✅ 不会保存到数据库
- ✅ 不会用于其他用途
- ✅ 建议使用完后退出QQ音乐账号重新登录（使旧Cookie失效）

**额外建议：**
- 不要在公共电脑上导出Cookie
- 定期更换QQ密码

---

### Q9: 支持其他平台吗（网易云、酷狗等）？

**A:** 目前仅支持QQ音乐。

计划支持的平台：
- [ ] 网易云音乐
- [ ] 酷狗音乐
- [ ] 酷我音乐

---

## 📞 技术支持

### 遇到问题？

1. **查看本教程** - 大部分问题都能在FAQ中找到答案
2. **检查Cookie格式** - 90%的错误都是Cookie问题
3. **联系我们** - 如果仍无法解决

---

## 📄 附录

### A. Netscape Cookie格式说明

```plaintext
域名    子域名  路径  安全  过期时间    名称    值
.qq.com	TRUE   /    FALSE 1735689600  uin   o12345
```

**字段解释：**
1. **域名**：Cookie所属域名
2. **子域名**：是否包含子域名（TRUE/FALSE）
3. **路径**：Cookie作用路径
4. **安全**：是否仅HTTPS（TRUE/FALSE）
5. **过期时间**：Unix时间戳（0表示会话Cookie）
6. **名称**：Cookie键名
7. **值**：Cookie值

---

### B. 快捷键参考

| 操作 | Windows/Linux | macOS |
|------|--------------|-------|
| 打开开发者工具 | `F12` 或 `Ctrl+Shift+I` | `Cmd+Option+I` |
| 刷新页面 | `F5` 或 `Ctrl+R` | `Cmd+R` |
| 强制刷新 | `Ctrl+Shift+R` | `Cmd+Shift+R` |
| 查看源代码 | `Ctrl+U` | `Cmd+Option+U` |

---

## ⚖️ 免责声明

> ⚠️ **重要提示**

1. 本工具仅供**个人学习和研究**使用
2. 请尊重版权，**不要用于商业用途**
3. 下载的音乐仅限**个人欣赏**，请支持正版音乐
4. 如侵犯您的权益，请联系我们删除

**建议：**
- 优先使用音乐平台的官方下载功能
- 支持喜欢的音乐人购买正版专辑
- 本工具作为备用方案使用

---

## 📝 更新日志

### v1.0.1 (2025-01-02)
- ✅ 简化教程，只保留EditThisCookie插件
- ✅ 优化步骤说明，更加简洁明了
- ✅ 删除冗余选项，降低用户选择困扰

### v1.0.0 (2025-01-02)
- ✅ 初始版本
- ✅ 支持单曲和歌单下载
- ✅ 支持多种音质格式
- ✅ Cookie安全处理机制

---

**最后更新时间：** 2025-01-02
**文档版本：** v1.0.1

---

<div align="center">

**感谢使用本工具！**

</div>
