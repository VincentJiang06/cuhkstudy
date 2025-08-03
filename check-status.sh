#!/bin/bash

# CUHKstudy 系统状态检查脚本

echo "🔍 CUHKstudy 系统状态检查"
echo "=========================="

# 基本信息
echo ""
echo "📋 系统信息:"
echo "   系统版本: $(lsb_release -d | cut -f2)"
echo "   内核版本: $(uname -r)"
echo "   运行时间: $(uptime -p)"

# 服务状态
echo ""
echo "🔧 服务状态:"
if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx: 运行中"
else
    echo "   ❌ Nginx: 已停止"
fi

# Hugo版本
echo ""
echo "🏗️ Hugo信息:"
if command -v hugo &> /dev/null; then
    echo "   版本: $(hugo version | cut -d' ' -f1-2)"
    echo "   ✅ Hugo Extended: 已安装"
else
    echo "   ❌ Hugo: 未安装"
fi

# 项目状态
echo ""
echo "📁 项目信息:"
if [ -d "/var/www/cuhkstudy" ]; then
    cd /var/www/cuhkstudy
    echo "   ✅ 项目目录: 存在"
    echo "   分支: $(git branch --show-current)"
    echo "   最后提交: $(git log -1 --format='%h %s' --oneline)"
    echo "   最后更新: $(stat -c %y public/ 2>/dev/null | cut -d. -f1 || echo '未构建')"
    
    if [ -d "public" ]; then
        echo "   网站大小: $(du -sh public | cut -f1)"
        echo "   页面数量: $(find public -name "*.html" | wc -l)"
        echo "   图片数量: $(find public -name "*.png" -o -name "*.jpg" -o -name "*.svg" | wc -l)"
        echo "   PDF数量: $(find public -name "*.pdf" | wc -l)"
    else
        echo "   ❌ public目录: 不存在"
    fi
else
    echo "   ❌ 项目目录: 不存在"
fi

# 磁盘空间
echo ""
echo "💾 磁盘空间:"
df -h | grep -E "(Filesystem|/dev/)" | head -2 | while read output; do
    echo "   $output"
done

# 内存使用
echo ""
echo "🧠 内存使用:"
free -h | head -2 | while read output; do
    echo "   $output"
done

# 网络连接
echo ""
echo "🌐 网络状态:"
if curl -s --connect-timeout 5 http://localhost/ > /dev/null; then
    echo "   ✅ 本地连接: 正常"
else
    echo "   ❌ 本地连接: 失败"
fi

# 获取公网IP
PUBLIC_IP=$(curl -s --connect-timeout 5 http://checkip.amazonaws.com 2>/dev/null || echo "获取失败")
echo "   公网IP: $PUBLIC_IP"

# 端口检查
echo ""
echo "🔌 端口状态:"
for port in 22 80 443; do
    if ss -tuln | grep -q ":$port "; then
        echo "   ✅ 端口 $port: 开放"
    else
        echo "   ❌ 端口 $port: 关闭"
    fi
done

# 最近的访问日志
echo ""
echo "📊 最近访问 (最后5条):"
if [ -f "/var/log/nginx/access.log" ]; then
    tail -5 /var/log/nginx/access.log | while read line; do
        echo "   $line"
    done
else
    echo "   ❌ 访问日志不存在"
fi

# 错误日志
echo ""
echo "⚠️ 最近错误 (最后3条):"
if [ -f "/var/log/nginx/error.log" ]; then
    ERRORS=$(tail -3 /var/log/nginx/error.log 2>/dev/null)
    if [ -z "$ERRORS" ]; then
        echo "   ✅ 无错误记录"
    else
        echo "$ERRORS" | while read line; do
            echo "   $line"
        done
    fi
else
    echo "   ❌ 错误日志不存在"
fi

echo ""
echo "=========================="
echo "✅ 状态检查完成"

# 提供快速操作建议
echo ""
echo "🔧 快速操作:"
echo "   更新网站: cd /var/www/cuhkstudy && ./deploy.sh"
echo "   重启Nginx: systemctl restart nginx"
echo "   查看日志: tail -f /var/log/nginx/access.log"
echo "   检查配置: nginx -t"