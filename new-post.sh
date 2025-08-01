#!/bin/bash

# 创建新博客文章的脚本
# 使用方法: ./new-post.sh "文章标题" [语言]

set -e

if [ $# -lt 1 ]; then
    echo "使用方法: $0 \"文章标题\" [语言]"
    echo "语言选项: zh-cn (默认), zh-tw, both"
    exit 1
fi

TITLE="$1"
LANG="${2:-zh-cn}"
DATE=$(date +%Y-%m-%dT%H:%M:%S%z)
SLUG=$(echo "$TITLE" | sed -e 's/[^a-zA-Z0-9\u4e00-\u9fa5]/-/g' | tr A-Z a-z)

# 进入项目目录
cd /home/mypodcast

echo "📝 创建新文章: $TITLE"

create_post() {
    local lang=$1
    local title=$2
    local content_dir="content/$lang/posts"
    local filename="$content_dir/$SLUG.md"
    
    mkdir -p "$content_dir"
    
    cat > "$filename" << EOF
---
title: "$title"
date: $DATE
draft: true
tags: ["博客"]
categories: ["博客文章"]
summary: ""
translationKey: "$SLUG"
---

# $title

## 文章内容

在这里写您的博客内容...

## 相关资源

- [下载相关PDF资料](/pdfs/$SLUG.pdf)
- [在线阅读PDF](/pdfjs/web/viewer.html?file=/pdfs/$SLUG.pdf)

---

感谢阅读！
EOF

    echo "✅ 已创建 $lang 版本: $filename"
}

if [ "$LANG" = "both" ]; then
    create_post "zh-cn" "$TITLE"
    create_post "zh-tw" "$TITLE"
elif [ "$LANG" = "zh-tw" ]; then
    create_post "zh-tw" "$TITLE"
else
    create_post "zh-cn" "$TITLE"
fi

echo ""
echo "📁 如需添加相关文件，请上传到对应目录："
echo "   PDF文件:  static/pdfs/$SLUG.pdf"
echo ""
echo "📝 编辑完成后运行以下命令发布："
echo "   ./deploy.sh --draft  # 包含草稿"
echo "   ./deploy.sh         # 仅发布正式内容"