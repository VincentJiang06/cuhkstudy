#!/bin/bash

# Hugo 博客开发调试脚本
# 启动本地开发服务器

set -e

echo "🚀 启动 Hugo 开发服务器..."
echo "📝 开发模式支持实时预览和自动刷新"
echo ""
echo "🌐 访问地址："
echo "   http://服务器IP:1313/"
echo ""
echo "💡 提示："
echo "   - 修改内容后会自动重新构建"
echo "   - 按 Ctrl+C 停止服务器"
echo ""

# 进入项目目录
cd /home/mypodcast

# 启动Hugo开发服务器
# --bind 0.0.0.0 允许外部访问
# --port 1313 指定端口
# --buildDrafts 包含草稿
# --buildFuture 包含未来日期的内容
hugo server --bind 0.0.0.0 --port 1313 --buildDrafts --buildFuture