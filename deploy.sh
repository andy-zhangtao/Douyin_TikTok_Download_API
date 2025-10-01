#!/bin/bash

# ==============================================================================
# Douyin TikTok Download API 部署脚本
# 支持分支更新、systemd服务配置、uvicorn启动
# ==============================================================================

set -e  # 遇到错误立即退出

# 配置变量
SERVICE_NAME="douyin-tiktok-api"
SERVICE_USER="www-data"
WORK_DIR="/opt/douyin-tiktok-api"
PYTHON_ENV="/opt/douyin-tiktok-api/venv"
SERVICE_PORT="9000"
DEFAULT_BRANCH="main"
VERSION=""  # 可选：指定 git tag 或 commit hash

# 外置配置文件目录
CONFIG_EXTERNAL_DIR="/opt/configs/douyin-tiktok-api"
# 需要保护的配置文件列表（相对于项目根目录）
CONFIG_FILES=(
    "config.yaml"
    "crawlers/douyin/web/config.yaml"
    "crawlers/tiktok/web/config.yaml"
    "crawlers/tiktok/app/config.yaml"
    "crawlers/bilibili/web/config.yaml"
)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# 显示帮助信息
show_help() {
    cat << EOF
使用方法: $0 [选项]

选项:
    -h, --help              显示此帮助信息
    -b, --branch BRANCH     指定要部署的分支 (默认: ${DEFAULT_BRANCH})
    -v, --version VERSION   指定版本 (git tag 或 commit hash)
    -u, --user USER         指定运行服务的用户 (默认: ${SERVICE_USER})
    -d, --dir DIR           指定安装目录 (默认: ${WORK_DIR})
    -p, --port PORT         指定服务端口 (默认: ${SERVICE_PORT})
    -c, --config-dir DIR    指定外置配置目录 (默认: ${CONFIG_EXTERNAL_DIR})
    --install               执行完整安装 (包括创建用户、安装依赖等)
    --update                仅更新代码和重启服务
    --service-only          仅生成systemd服务文件
    --init-config           初始化外置配置（首次部署时使用）

示例:
    # 首次部署（完整安装+初始化配置）
    $0 --install --init-config --branch main --port 9000

    # 更新代码（保护配置文件）
    $0 --update --version v1.2.3
    $0 --update --version abc123ef

    # 仅生成服务文件
    $0 --service-only --user myuser --port 8080
EOF
}

# 解析命令行参数
BRANCH="$DEFAULT_BRANCH"
INSTALL_MODE=false
UPDATE_MODE=false
SERVICE_ONLY=false
INIT_CONFIG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -u|--user)
            SERVICE_USER="$2"
            shift 2
            ;;
        -d|--dir)
            WORK_DIR="$2"
            PYTHON_ENV="$WORK_DIR/venv"
            shift 2
            ;;
        -p|--port)
            SERVICE_PORT="$2"
            shift 2
            ;;
        -c|--config-dir)
            CONFIG_EXTERNAL_DIR="$2"
            shift 2
            ;;
        --install)
            INSTALL_MODE=true
            shift
            ;;
        --update)
            UPDATE_MODE=true
            shift
            ;;
        --service-only)
            SERVICE_ONLY=true
            shift
            ;;
        --init-config)
            INIT_CONFIG=true
            shift
            ;;
        *)
            error "未知选项: $1. 使用 --help 查看帮助信息"
            ;;
    esac
done

# 检查root权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "此脚本需要root权限才能运行"
    fi
}

# 检查系统依赖
check_dependencies() {
    log "检查系统依赖..."

    local deps=("git" "python3" "python3-pip" "python3-venv")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            log "安装 $dep..."
            apt-get update && apt-get install -y "$dep"
        fi
    done
}

# 创建服务用户
create_user() {
    if id "$SERVICE_USER" &>/dev/null; then
        log "用户 $SERVICE_USER 已存在"
    else
        log "创建用户 $SERVICE_USER..."
        useradd --system --shell /bin/bash --home-dir "$WORK_DIR" --create-home "$SERVICE_USER"
    fi
}

# 克隆或更新代码
update_code() {
    if [ -n "$VERSION" ]; then
        log "部署版本: $VERSION"
    else
        log "部署分支: $BRANCH"
    fi

    if [ ! -d "$WORK_DIR/.git" ]; then
        # 首次克隆
        log "克隆代码仓库..."
        rm -rf "$WORK_DIR"
        git clone https://github.com/andy-zhangtao/Douyin_TikTok_Download_API.git "$WORK_DIR"
        cd "$WORK_DIR"

        if [ -n "$VERSION" ]; then
            log "切换到版本: $VERSION"
            git checkout "$VERSION"
        else
            git checkout "$BRANCH"
        fi
    else
        # 更新现有仓库
        cd "$WORK_DIR"
        log "拉取最新代码..."
        git fetch --all --tags

        if [ -n "$VERSION" ]; then
            log "切换到版本: $VERSION"
            git checkout "$VERSION"
        else
            git checkout "$BRANCH"
            git pull origin "$BRANCH"
        fi
    fi

    # 显示当前版本信息
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    CURRENT_TAG=$(git describe --tags --exact-match 2>/dev/null || echo "无tag")
    log "当前代码版本: commit=$CURRENT_COMMIT, tag=$CURRENT_TAG"

    # 设置正确的所有权
    chown -R "$SERVICE_USER:$SERVICE_USER" "$WORK_DIR"
}

# 初始化外置配置目录
init_external_config() {
    log "初始化外置配置目录..."

    # 创建外置配置目录
    mkdir -p "$CONFIG_EXTERNAL_DIR"

    # 复制所有配置文件到外置目录（保留目录结构）
    for config_file in "${CONFIG_FILES[@]}"; do
        source_file="$WORK_DIR/$config_file"
        target_file="$CONFIG_EXTERNAL_DIR/$config_file"

        if [ -f "$source_file" ]; then
            # 创建目标目录
            target_dir=$(dirname "$target_file")
            mkdir -p "$target_dir"

            # 复制配置文件
            cp "$source_file" "$target_file"
            log "已复制配置文件: $config_file -> $target_file"
        else
            warn "配置文件不存在，跳过: $source_file"
        fi
    done

    # 设置正确的所有权
    chown -R "$SERVICE_USER:$SERVICE_USER" "$CONFIG_EXTERNAL_DIR"
    chmod -R 600 "$CONFIG_EXTERNAL_DIR"

    log "外置配置目录已初始化: $CONFIG_EXTERNAL_DIR"
    log "⚠️  请编辑外置配置文件，添加Cookie等敏感信息"
}

# 链接外置配置文件到项目目录
link_external_config() {
    log "链接外置配置文件..."

    # 检查外置配置目录是否存在
    if [ ! -d "$CONFIG_EXTERNAL_DIR" ]; then
        error "外置配置目录不存在: $CONFIG_EXTERNAL_DIR\n请先运行: $0 --init-config"
    fi

    # 为每个配置文件创建软链接
    for config_file in "${CONFIG_FILES[@]}"; do
        source_file="$CONFIG_EXTERNAL_DIR/$config_file"
        target_file="$WORK_DIR/$config_file"

        if [ -f "$source_file" ]; then
            # 删除项目中的配置文件（如果存在）
            if [ -f "$target_file" ] && [ ! -L "$target_file" ]; then
                log "备份项目中的配置文件: $target_file -> $target_file.bak"
                mv "$target_file" "$target_file.bak"
            fi

            # 删除旧的软链接
            rm -f "$target_file"

            # 创建软链接
            ln -sf "$source_file" "$target_file"
            log "已创建软链接: $target_file -> $source_file"
        else
            warn "外置配置文件不存在，跳过: $source_file"
        fi
    done

    log "配置文件链接完成"
}

# 设置Python环境
setup_python_env() {
    log "设置Python虚拟环境..."

    # 创建虚拟环境 (如果不存在)
    if [ ! -d "$PYTHON_ENV" ]; then
        sudo -u "$SERVICE_USER" python3 -m venv "$PYTHON_ENV"
    fi

    # 激活虚拟环境并安装依赖
    log "安装Python依赖..."
    sudo -u "$SERVICE_USER" bash -c "
        source '$PYTHON_ENV/bin/activate'
        pip install --upgrade pip
        cd '$WORK_DIR'
        pip install -r requirements.txt
    "
}

# 生成systemd服务文件
create_systemd_service() {
    log "创建systemd服务文件..."

    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=Douyin TikTok Download API Service
After=network.target

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$WORK_DIR
Environment="PATH=$PYTHON_ENV/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$PYTHON_ENV/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port $SERVICE_PORT --workers 4 --log-level info
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=5

# 安全设置
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$WORK_DIR

# 资源限制
LimitNOFILE=65535
LimitNPROC=32768

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载systemd配置
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"

    log "systemd服务文件已创建: /etc/systemd/system/$SERVICE_NAME.service"
}

# 启动服务
start_service() {
    log "启动服务..."

    systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    systemctl start "$SERVICE_NAME"

    # 等待服务启动
    sleep 3

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "服务启动成功！"
        log "服务状态: $(systemctl is-active $SERVICE_NAME)"
        log "访问地址: http://localhost:$SERVICE_PORT"
    else
        error "服务启动失败！请检查日志: journalctl -u $SERVICE_NAME -f"
    fi
}

# 显示服务信息
show_service_info() {
    cat << EOF

${GREEN}=== 部署完成 ===${NC}

服务名称: $SERVICE_NAME
运行用户: $SERVICE_USER
工作目录: $WORK_DIR
外置配置: $CONFIG_EXTERNAL_DIR
监听端口: $SERVICE_PORT
部署分支: $BRANCH

常用命令:
  查看状态: systemctl status $SERVICE_NAME
  启动服务: systemctl start $SERVICE_NAME
  停止服务: systemctl stop $SERVICE_NAME
  重启服务: systemctl restart $SERVICE_NAME
  查看日志: journalctl -u $SERVICE_NAME -f

配置文件管理:
  编辑配置: 修改 $CONFIG_EXTERNAL_DIR 下的配置文件
  配置列表: ls -la $CONFIG_EXTERNAL_DIR

  ${YELLOW}⚠️  配置文件通过软链接管理，更新代码不会覆盖配置${NC}

访问地址: http://localhost:$SERVICE_PORT

EOF
}

# 主执行逻辑
main() {
    log "开始部署 Douyin TikTok Download API..."
    if [ -n "$VERSION" ]; then
        log "版本: $VERSION, 端口: $SERVICE_PORT, 用户: $SERVICE_USER"
    else
        log "分支: $BRANCH, 端口: $SERVICE_PORT, 用户: $SERVICE_USER"
    fi

    check_root

    if [[ "$SERVICE_ONLY" == true ]]; then
        # 仅生成服务文件
        create_systemd_service
        log "systemd服务文件已生成"
        exit 0
    fi

    if [[ "$INSTALL_MODE" == true ]]; then
        # 完整安装
        check_dependencies
        create_user
        update_code

        # 如果指定了初始化配置，则执行配置初始化和链接
        if [[ "$INIT_CONFIG" == true ]]; then
            init_external_config
            link_external_config
        else
            # 否则只链接已存在的外置配置
            if [ -d "$CONFIG_EXTERNAL_DIR" ]; then
                link_external_config
            else
                warn "未找到外置配置目录: $CONFIG_EXTERNAL_DIR"
                warn "如需使用外置配置，请运行: $0 --init-config"
            fi
        fi

        setup_python_env
        create_systemd_service
        start_service
        show_service_info

    elif [[ "$UPDATE_MODE" == true ]]; then
        # 仅更新
        update_code

        # 更新后重新链接外置配置（保护配置不被覆盖）
        if [ -d "$CONFIG_EXTERNAL_DIR" ]; then
            link_external_config
        else
            warn "未找到外置配置目录: $CONFIG_EXTERNAL_DIR"
            warn "配置文件可能已被覆盖，建议运行: $0 --init-config"
        fi

        setup_python_env  # 可能有新的依赖
        systemctl restart "$SERVICE_NAME"
        log "代码更新完成，服务已重启"

    else
        # 默认: 完整安装
        warn "未指定模式，执行完整安装。使用 --help 查看选项"
        check_dependencies
        create_user
        update_code

        # 如果指定了初始化配置，则执行配置初始化和链接
        if [[ "$INIT_CONFIG" == true ]]; then
            init_external_config
            link_external_config
        else
            # 否则只链接已存在的外置配置
            if [ -d "$CONFIG_EXTERNAL_DIR" ]; then
                link_external_config
            else
                warn "未找到外置配置目录: $CONFIG_EXTERNAL_DIR"
                warn "如需使用外置配置，请运行: $0 --init-config"
            fi
        fi

        setup_python_env
        create_systemd_service
        start_service
        show_service_info
    fi
}

# 执行主函数
main "$@"