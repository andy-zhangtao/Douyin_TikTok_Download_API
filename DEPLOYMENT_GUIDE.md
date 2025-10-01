# 🚀 部署指南

## 快速开始

### 首次部署

```bash
# 1. 克隆仓库
git clone https://github.com/andy-zhangtao/Douyin_TikTok_Download_API.git
cd Douyin_TikTok_Download_API

# 2. 执行部署脚本（带配置初始化）
sudo ./deploy.sh --install --init-config --branch main --port 9000

# 3. 编辑配置文件（添加Cookie等敏感信息）
sudo nano /opt/configs/douyin-tiktok-api/crawlers/douyin/web/config.yaml

# 4. 重启服务
sudo systemctl restart douyin-tiktok-api
```

### 更新部署

```bash
# 方法1: 使用部署脚本（推荐）
sudo ./deploy.sh --update

# 方法2: 指定版本更新
sudo ./deploy.sh --update --version v1.2.3
```

---

## 📋 配置文件保护机制

采用**外置配置方案**，确保每次更新代码时不会覆盖配置文件（尤其是包含Cookie的配置）。

### 工作原理

- **外置配置目录**：`/opt/configs/douyin-tiktok-api/`
- **项目配置目录**：`/opt/douyin-tiktok-api/`（通过软链接指向外置配置）
- **更新保护**：拉取新代码后自动重建软链接，保护外置配置不被覆盖

### 配置文件位置

| 配置类型 | 外置路径 |
|---------|---------|
| 主配置 | `/opt/configs/douyin-tiktok-api/config.yaml` |
| 抖音配置 | `/opt/configs/douyin-tiktok-api/crawlers/douyin/web/config.yaml` |
| TikTok Web | `/opt/configs/douyin-tiktok-api/crawlers/tiktok/web/config.yaml` |
| TikTok App | `/opt/configs/douyin-tiktok-api/crawlers/tiktok/app/config.yaml` |
| Bilibili | `/opt/configs/douyin-tiktok-api/crawlers/bilibili/web/config.yaml` |

详细文档：[CONFIG_MANAGEMENT.md](CONFIG_MANAGEMENT.md)

---

## 🛠️ 常用命令

### 服务管理

```bash
# 查看服务状态
sudo systemctl status douyin-tiktok-api

# 启动服务
sudo systemctl start douyin-tiktok-api

# 停止服务
sudo systemctl stop douyin-tiktok-api

# 重启服务
sudo systemctl restart douyin-tiktok-api

# 查看实时日志
sudo journalctl -u douyin-tiktok-api -f
```

### 配置管理

```bash
# 查看所有配置文件
ls -la /opt/configs/douyin-tiktok-api/

# 编辑抖音配置（最常用）
sudo nano /opt/configs/douyin-tiktok-api/crawlers/douyin/web/config.yaml

# 验证软链接
ls -la /opt/douyin-tiktok-api/config.yaml

# 备份配置
sudo tar -czf ~/config-backup-$(date +%Y%m%d).tar.gz /opt/configs/douyin-tiktok-api/
```

---

## 🔧 部署脚本参数

### 基础参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-b, --branch` | 指定部署分支 | main |
| `-v, --version` | 指定版本（tag或commit） | - |
| `-u, --user` | 运行服务的用户 | www-data |
| `-d, --dir` | 安装目录 | /opt/douyin-tiktok-api |
| `-p, --port` | 服务端口 | 9000 |
| `-c, --config-dir` | 外置配置目录 | /opt/configs/douyin-tiktok-api |

### 操作模式

| 参数 | 说明 |
|------|------|
| `--install` | 完整安装（创建用户、安装依赖、配置服务） |
| `--update` | 仅更新代码和重启服务 |
| `--service-only` | 仅生成systemd服务文件 |
| `--init-config` | 初始化外置配置（首次部署必须） |

---

## 📝 部署场景示例

### 场景1：全新服务器首次部署

```bash
# 安装系统依赖
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv

# 克隆项目
git clone https://github.com/andy-zhangtao/Douyin_TikTok_Download_API.git /opt/douyin-tiktok-api

# 部署（带配置初始化）
cd /opt/douyin-tiktok-api
sudo ./deploy.sh --install --init-config

# 编辑配置
sudo nano /opt/configs/douyin-tiktok-api/crawlers/douyin/web/config.yaml

# 重启服务
sudo systemctl restart douyin-tiktok-api
```

### 场景2：已有项目，迁移到外置配置

```bash
# 备份现有配置
sudo cp -r /opt/douyin-tiktok-api/*.yaml ~/config-backup/

# 初始化外置配置
cd /opt/douyin-tiktok-api
sudo ./deploy.sh --init-config

# 验证配置已复制
ls -la /opt/configs/douyin-tiktok-api/

# 重启服务
sudo systemctl restart douyin-tiktok-api
```

### 场景3：定期更新代码

```bash
cd /opt/douyin-tiktok-api

# 更新到最新main分支
sudo ./deploy.sh --update

# 或更新到指定版本
sudo ./deploy.sh --update --version v1.2.3
```

### 场景4：自定义配置目录

```bash
# 使用自定义配置目录
sudo ./deploy.sh --install --init-config --config-dir /data/my-configs
```

### 场景5：更换端口

```bash
# 重新生成服务文件（更换端口为8080）
sudo ./deploy.sh --service-only --port 8080

# 重启服务
sudo systemctl restart douyin-tiktok-api
```

---

## ⚠️ 重要注意事项

### 1. 首次部署必须使用 `--init-config`

```bash
# ✅ 正确：首次部署
sudo ./deploy.sh --install --init-config

# ❌ 错误：首次部署忘记初始化配置
sudo ./deploy.sh --install
```

### 2. 更新代码会自动保护配置

```bash
# 更新代码时，脚本会：
# 1. 拉取最新代码
# 2. 自动重建软链接
# 3. 保护 /opt/configs/ 下的配置不被覆盖
sudo ./deploy.sh --update
```

### 3. 所有配置修改在外置目录进行

```bash
# ✅ 正确：编辑外置配置
sudo nano /opt/configs/douyin-tiktok-api/config.yaml

# ⚠️ 也可以（但容易混淆）：编辑项目中的软链接
sudo nano /opt/douyin-tiktok-api/config.yaml  # 实际修改的还是外置配置
```

### 4. 配置修改后需要重启服务

```bash
sudo systemctl restart douyin-tiktok-api
```

---

## 🔍 故障排查

### 问题：服务启动失败

```bash
# 查看详细日志
sudo journalctl -u douyin-tiktok-api -n 50 --no-pager

# 检查配置文件
ls -la /opt/configs/douyin-tiktok-api/

# 检查软链接
ls -la /opt/douyin-tiktok-api/config.yaml
```

### 问题：更新后配置丢失

```bash
# 检查外置配置是否存在
ls -la /opt/configs/douyin-tiktok-api/

# 重新创建软链接
cd /opt/douyin-tiktok-api
sudo ./deploy.sh --update
```

### 问题：权限错误

```bash
# 修复权限
sudo chown -R www-data:www-data /opt/douyin-tiktok-api/
sudo chown -R www-data:www-data /opt/configs/douyin-tiktok-api/
sudo chmod -R 600 /opt/configs/douyin-tiktok-api/
```

---

## 📚 相关文档

- [配置文件管理详细文档](CONFIG_MANAGEMENT.md)
- [项目README](README.md)

---

## 💡 最佳实践

1. ✅ 首次部署使用 `--init-config`
2. ✅ 定期备份 `/opt/configs/` 目录
3. ✅ 所有配置修改在外置目录进行
4. ✅ 修改配置后重启服务
5. ✅ 更新代码前确认外置配置完整
6. ❌ 不要删除软链接
7. ❌ 不要将敏感信息提交到Git

---

**如有问题，请查阅 [CONFIG_MANAGEMENT.md](CONFIG_MANAGEMENT.md) 或提交Issue。**
