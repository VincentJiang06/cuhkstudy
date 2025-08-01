#!/bin/bash

# Hugo 博客网站部署脚本
# 使用方法: ./deploy.sh [选项]
# 选项: --draft 包含草稿内容

set -e

echo "🚀 开始部署 Hugo 博客网站..."

# 进入项目目录
cd /home/mypodcast

# 检查是否包含草稿
DRAFT_FLAG=""
if [[ "$1" == "--draft" ]]; then
    DRAFT_FLAG="-D"
    echo "📝 包含草稿内容"
fi

# 构建网站
echo "🔨 构建 Hugo 网站..."
hugo $DRAFT_FLAG

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo "✅ Hugo 构建成功"
else
    echo "❌ Hugo 构建失败"
    exit 1
fi

# 清理旧文件
echo "🧹 清理旧的网站文件..."
rm -rf /var/www/mypodcast/*

# 复制新文件
echo "📁 复制新的网站文件..."
cp -r public/* /var/www/mypodcast/

# 设置正确的权限
echo "🔐 设置文件权限..."
chown -R www-data:www-data /var/www/mypodcast
find /var/www/mypodcast -type d -exec chmod 755 {} \;
find /var/www/mypodcast -type f -exec chmod 644 {} \;

# 测试 Nginx 配置
echo "🔍 测试 Nginx 配置..."
nginx -t

if [ $? -eq 0 ]; then
    # 重新加载 Nginx
    echo "🔄 重新加载 Nginx..."
    systemctl reload nginx
    echo "✅ Nginx 重新加载成功"
else
    echo "❌ Nginx 配置测试失败"
    exit 1
fi

echo "🎉 网站部署完成！"
echo "📊 网站统计："
hugo $DRAFT_FLAG --quiet | tail -5

echo ""
echo "🌐 访问地址："
echo "   简体中文: http://您的域名/zh-cn/"
echo "   繁体中文: http://您的域名/zh-tw/"
echo ""
echo "🔧 如需配置SSL证书，请运行: certbot --nginx -d 您的域名"