#!/bin/bash

# CUHKstudy 一键部署脚本 - Ubuntu 22.04 阿里云ECS
# 使用方法: curl -s https://raw.githubusercontent.com/VincentJiang06/cuhkstudy/master/setup-server.sh | bash

set -e

echo "🚀 开始 CUHKstudy 一键部署..."
echo "📋 系统信息: $(lsb_release -d | cut -f2)"

# 检查root权限
if [[ $EUID -ne 0 ]]; then
   echo "❌ 此脚本需要root权限运行"
   echo "请使用: sudo bash setup-server.sh"
   exit 1
fi

# 更新系统
echo "🔄 更新系统包..."
apt update && apt upgrade -y

# 安装基础软件
echo "📦 安装基础软件..."
apt install -y wget curl git nginx ufw unzip

# 安装Hugo Extended
echo "🏗️ 安装 Hugo Extended..."
HUGO_VERSION="0.148.2"
HUGO_ARCHIVE="hugo_extended_${HUGO_VERSION}_linux-amd64.deb"

cd /tmp
wget -q "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/${HUGO_ARCHIVE}"
dpkg -i "${HUGO_ARCHIVE}"
rm "${HUGO_ARCHIVE}"

# 验证Hugo安装
hugo version
echo "✅ Hugo 安装完成"

# 创建项目目录
echo "📁 创建项目目录..."
mkdir -p /var/www
cd /var/www

# 克隆项目
echo "📥 克隆 CUHKstudy 项目..."
if [ -d "cuhkstudy" ]; then
    echo "⚠️ 项目目录已存在，删除旧版本..."
    rm -rf cuhkstudy
fi

git clone --recursive https://github.com/VincentJiang06/cuhkstudy.git
cd cuhkstudy

# 确保子模块正确加载
echo "🔄 初始化子模块..."
git submodule update --init --recursive

# 构建网站
echo "🔨 构建网站..."
hugo --minify

# 配置Nginx
echo "⚙️ 配置 Nginx..."
cat > /etc/nginx/sites-available/cuhkstudy << 'EOF'
server {
    listen 80;
    server_name _;
    root /var/www/cuhkstudy/public;
    index index.html;

    # 中文文件名支持
    charset utf-8;

    # 安全头部
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 静态文件缓存
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # PDF文件处理
    location /pdfs/ {
        add_header Content-Type 'application/pdf';
        add_header Content-Disposition 'inline';
    }

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # 默认路由
    location / {
        try_files $uri $uri/ =404;
    }

    # 404错误页面
    error_page 404 /404.html;
}
EOF

# 启用网站
ln -sf /etc/nginx/sites-available/cuhkstudy /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t

# 设置文件权限
echo "🔐 设置文件权限..."
chown -R www-data:www-data /var/www/cuhkstudy/public
find /var/www/cuhkstudy/public -type d -exec chmod 755 {} \;
find /var/www/cuhkstudy/public -type f -exec chmod 644 {} \;

# 配置防火墙
echo "🔥 配置防火墙..."
ufw --force enable
ufw allow 22
ufw allow 80
ufw allow 443

# 启动服务
echo "🚀 启动服务..."
systemctl enable nginx
systemctl restart nginx

# 创建更新脚本
echo "📝 创建更新脚本..."
chmod +x /var/www/cuhkstudy/deploy.sh

# 显示结果
echo ""
echo "🎉 部署完成！"
echo ""
echo "📊 网站信息："
echo "   项目路径: /var/www/cuhkstudy"
echo "   网站路径: /var/www/cuhkstudy/public"
echo "   总页面数: $(find /var/www/cuhkstudy/public -name "*.html" | wc -l)"
echo "   网站大小: $(du -sh /var/www/cuhkstudy/public | cut -f1)"
echo ""
echo "🌐 访问信息："
SERVER_IP=$(curl -s http://checkip.amazonaws.com || echo "获取IP失败")
echo "   IP地址: http://${SERVER_IP}/"
echo "   域名: http://您的域名/ (需要配置DNS)"
echo ""
echo "📚 常用命令："
echo "   更新网站: cd /var/www/cuhkstudy && ./deploy.sh"
echo "   查看日志: tail -f /var/log/nginx/access.log"
echo "   重启Nginx: systemctl restart nginx"
echo ""
echo "🔒 SSL证书配置："
echo "   1. 配置域名DNS指向本服务器"
echo "   2. 运行: apt install -y certbot python3-certbot-nginx"
echo "   3. 运行: certbot --nginx -d 您的域名.com"
echo ""
echo "✅ CUHKstudy 部署成功！"