# 配置文件管理指南

## 📋 问题描述

每次在远程服务器更新代码时，配置文件（如包含Cookie的 `config.yaml`）会被Git仓库中的文件覆盖，导致需要重新配置。

## ✅ 解决方案：外置配置文件

通过将配置文件存储在项目目录外，使用软链接的方式关联，确保更新代码时不会覆盖配置。

---

## 🚀 使用方法

### 1. 首次部署（带配置初始化）

```bash
sudo ./deploy.sh --install --init-config --branch main --port 9000
```

**这个命令会：**
- 完整安装项目
- 创建外置配置目录：`/opt/configs/douyin-tiktok-api/`
- 复制所有配置文件到外置目录
- 在项目中创建软链接指向外置配置

### 2. 编辑配置文件

配置文件存储在：`/opt/configs/douyin-tiktok-api/`

```bash
# 编辑主配置文件
sudo nano /opt/configs/douyin-tiktok-api/config.yaml

# 编辑抖音配置（添加Cookie）
sudo nano /opt/configs/douyin-tiktok-api/crawlers/douyin/web/config.yaml

# 编辑TikTok配置
sudo nano /opt/configs/douyin-tiktok-api/crawlers/tiktok/web/config.yaml

# 查看所有配置文件
ls -la /opt/configs/douyin-tiktok-api/
```

### 3. 更新代码（保护配置）

```bash
# 更新到最新main分支
sudo ./deploy.sh --update

# 更新到指定版本
sudo ./deploy.sh --update --version v1.2.3

# 更新到指定commit
sudo ./deploy.sh --update --version abc123ef
```

**更新时会自动：**
- 拉取最新代码
- 重新创建软链接（保护外置配置不被覆盖）
- 重启服务

---

## 🔧 工作原理

### 配置文件结构

```
项目目录 (/opt/douyin-tiktok-api/)
├── config.yaml                          -> 软链接 -> /opt/configs/douyin-tiktok-api/config.yaml
├── crawlers/
│   ├── douyin/web/config.yaml          -> 软链接
│   ├── tiktok/web/config.yaml          -> 软链接
│   ├── tiktok/app/config.yaml          -> 软链接
│   └── bilibili/web/config.yaml        -> 软链接

外置配置目录 (/opt/configs/douyin-tiktok-api/)
├── config.yaml                          ← 真实文件
├── crawlers/
│   ├── douyin/web/config.yaml          ← 真实文件
│   ├── tiktok/web/config.yaml          ← 真实文件
│   ├── tiktok/app/config.yaml          ← 真实文件
│   └── bilibili/web/config.yaml        ← 真实文件
```

### 软链接验证

```bash
# 查看软链接状态
ls -la /opt/douyin-tiktok-api/config.yaml
# 输出示例：lrwxrwxrwx 1 www-data www-data 47 Jan 10 10:00 config.yaml -> /opt/configs/douyin-tiktok-api/config.yaml

# 验证文件内容
cat /opt/douyin-tiktok-api/config.yaml
cat /opt/configs/douyin-tiktok-api/config.yaml
# 两个命令输出相同内容
```

---

## 📝 受保护的配置文件列表

以下配置文件会被自动外置和保护：

1. `config.yaml` - 主配置文件
2. `crawlers/douyin/web/config.yaml` - 抖音配置（包含Cookie）
3. `crawlers/tiktok/web/config.yaml` - TikTok Web配置
4. `crawlers/tiktok/app/config.yaml` - TikTok App配置
5. `crawlers/bilibili/web/config.yaml` - Bilibili配置

---

## 🛠️ 高级用法

### 自定义外置配置目录

```bash
sudo ./deploy.sh --install --init-config --config-dir /data/configs/my-api
```

### 仅初始化配置（不安装服务）

```bash
# 1. 先拉取代码
cd /opt/douyin-tiktok-api
git pull

# 2. 手动初始化配置
sudo ./deploy.sh --init-config
```

### 备份配置文件

```bash
# 备份所有配置
sudo tar -czf ~/config-backup-$(date +%Y%m%d).tar.gz /opt/configs/douyin-tiktok-api/

# 恢复配置
sudo tar -xzf ~/config-backup-20250101.tar.gz -C /
```

### 迁移到新服务器

```bash
# 旧服务器
sudo tar -czf ~/config-export.tar.gz /opt/configs/douyin-tiktok-api/
scp ~/config-export.tar.gz new-server:/tmp/

# 新服务器
sudo mkdir -p /opt/configs/
sudo tar -xzf /tmp/config-export.tar.gz -C /
sudo ./deploy.sh --install
```

---

## ⚠️ 注意事项

### 1. 权限设置

外置配置目录权限默认为 `600`（仅所有者可读写），确保安全性：

```bash
# 检查权限
ls -la /opt/configs/douyin-tiktok-api/

# 修复权限（如需要）
sudo chown -R www-data:www-data /opt/configs/douyin-tiktok-api/
sudo chmod -R 600 /opt/configs/douyin-tiktok-api/
```

### 2. Git忽略提醒

**不要将包含敏感信息的配置文件提交到Git仓库！**

如果你修改了项目中的配置模板，确保：
- 移除所有敏感信息（Cookie、密钥等）
- 仅保留示例值

### 3. 配置文件不存在的处理

如果外置配置目录损坏或丢失：

```bash
# 重新初始化（会从项目中复制默认配置）
sudo ./deploy.sh --init-config
```

### 4. 更新配置后重启服务

修改配置文件后需要重启服务生效：

```bash
sudo systemctl restart douyin-tiktok-api
```

---

## 🔍 故障排查

### 问题1：更新后配置还是被覆盖了

**原因**：可能没有正确执行软链接

**解决**：
```bash
# 检查软链接是否存在
ls -la /opt/douyin-tiktok-api/config.yaml

# 重新创建软链接
sudo ./deploy.sh --update
```

### 问题2：服务启动失败，提示找不到配置文件

**原因**：外置配置目录不存在或权限错误

**解决**：
```bash
# 检查外置配置是否存在
ls -la /opt/configs/douyin-tiktok-api/

# 如果不存在，重新初始化
sudo ./deploy.sh --init-config

# 检查权限
sudo chown -R www-data:www-data /opt/configs/douyin-tiktok-api/
```

### 问题3：修改配置后不生效

**原因**：修改了项目中的文件，而不是外置配置

**解决**：
```bash
# 确认你编辑的是外置配置文件
sudo nano /opt/configs/douyin-tiktok-api/config.yaml  # ✅ 正确

# 而不是项目中的文件
sudo nano /opt/douyin-tiktok-api/config.yaml  # ❌ 这是软链接，编辑会生效但容易混淆
```

---

## 📚 参考命令速查表

| 操作 | 命令 |
|------|------|
| 首次部署 | `sudo ./deploy.sh --install --init-config` |
| 更新代码 | `sudo ./deploy.sh --update` |
| 编辑配置 | `sudo nano /opt/configs/douyin-tiktok-api/config.yaml` |
| 查看配置 | `ls -la /opt/configs/douyin-tiktok-api/` |
| 重启服务 | `sudo systemctl restart douyin-tiktok-api` |
| 查看日志 | `sudo journalctl -u douyin-tiktok-api -f` |
| 备份配置 | `sudo tar -czf ~/backup.tar.gz /opt/configs/` |
| 检查链接 | `ls -la /opt/douyin-tiktok-api/config.yaml` |

---

## 💡 最佳实践

1. **首次部署必须使用 `--init-config`**
2. **所有配置修改都在 `/opt/configs/` 目录下进行**
3. **定期备份配置文件**
4. **不要删除软链接**
5. **更新代码前确认外置配置目录完整**

---

## 🎯 总结

采用外置配置方案后：

✅ **更新代码永远不会覆盖配置**
✅ **配置文件集中管理，易于备份**
✅ **支持多环境部署（开发/测试/生产）**
✅ **符合安全最佳实践**

如有问题，请参考故障排查章节或提交Issue。
