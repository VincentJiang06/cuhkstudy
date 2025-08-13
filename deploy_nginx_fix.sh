#!/bin/bash

# 🔧 部署UGFN/UGFH 403修复

echo "🔧 开始部署nginx配置修复..."

# 1. 备份当前配置
sudo cp /etc/nginx/sites-available/cuhkstudy /etc/nginx/sites-available/cuhkstudy.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "备份失败，可能是首次配置"

# 2. 复制修复后的配置
sudo cp nginx-r2-optimized.conf /etc/nginx/sites-available/cuhkstudy

# 3. 创建软链接（如果不存在）
sudo ln -sf /etc/nginx/sites-available/cuhkstudy /etc/nginx/sites-enabled/cuhkstudy 2>/dev/null || echo "软链接已存在"

# 4. 测试nginx配置
echo "📋 测试nginx配置语法..."
if sudo nginx -t; then
    echo "✅ nginx配置语法正确"
    
    # 5. 重新加载nginx
    echo "🔄 重新加载nginx..."
    sudo systemctl reload nginx
    
    echo "✅ nginx配置已更新！"
    echo ""
    echo "🌐 现在可以测试访问："
    echo "   https://cuhkstudy.com/ugfn/"
    echo "   https://cuhkstudy.com/ugfh/"
    
else
    echo "❌ nginx配置语法错误，请检查配置文件"
    exit 1
fi

