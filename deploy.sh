#!/bin/bash

# CUHKstudy Hugo 网站部署脚本
# 使用方法: ./deploy.sh [选项]
# 选项: --draft 包含草稿内容

set -e

echo "🚀 开始部署 CUHKstudy 网站..."

# 进入项目目录
PROJECT_DIR="/var/www/cuhkstudy"
WEB_DIR="/var/www/cuhkstudy/public"

cd $PROJECT_DIR

# 检查是否包含草稿
DRAFT_FLAG=""
if [[ "$1" == "--draft" ]]; then
    DRAFT_FLAG="-D"
    echo "📝 包含草稿内容"
fi

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin master

# 更新子模块
echo "🔄 更新主题子模块..."
git submodule update --remote --recursive

# 压缩图片（常态化优化）
echo "🗜️  优化图片资源(生成 WebP、限制宽度、剥离元数据)..."
bash ./optimize-images.sh || true

# 构建网站（使用 production 环境配置，稳定输出备案号）
echo "🔨 构建 Hugo 网站..."
hugo --environment production $DRAFT_FLAG --minify

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo "✅ Hugo 构建成功"
else
    echo "❌ Hugo 构建失败"
    exit 1
fi

# 设置正确的权限
echo "🔐 设置文件权限..."
chown -R www-data:www-data $WEB_DIR
find $WEB_DIR -type d -exec chmod 755 {} \;
find $WEB_DIR -type f -exec chmod 644 {} \;

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

echo "🎉 CUHKstudy 网站部署完成！"
echo "📊 网站统计："
echo "   总页面数: $(find $WEB_DIR -name "*.html" | wc -l)"
echo "   图片文件: $(find $WEB_DIR -name "*.png" -o -name "*.jpg" -o -name "*.svg" | wc -l)"
echo "   PDF文件: $(find $WEB_DIR -name "*.pdf" | wc -l)"
echo "   总大小: $(du -sh $WEB_DIR | cut -f1)"

echo ""
echo "🌐 访问地址："
echo "   主页: http://您的域名/"
echo "   关于: http://您的域名/info/"
echo "   作者: http://您的域名/authors/"
echo ""
echo "🔧 如需配置SSL证书，请运行: certbot --nginx -d 您的域名"