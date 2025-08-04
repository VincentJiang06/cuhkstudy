# CUHKstudy - CUHK 课程资料分享网站

## 🎯 项目概述

CUHKstudy 是一个基于 Hugo 静态网站生成器的学术资料分享平台，专为中文大学（CUHK）学生设计。网站采用现代化的架构，提供高性能的内容访问体验。

### ✨ 核心特性

- 🌍 **多语言支持**：简体中文为主，支持多语言扩展
- 📚 **学术资料管理**：PDF 文档在线预览和下载
- 🏗️ **模块化架构**：按课程类型组织内容（UGFN、UGFH、Main等）
- 📱 **响应式设计**：完美适配桌面和移动设备
- ⚡ **高性能优化**：静态生成，CDN友好
- 🎨 **现代UI**：基于 Blowfish 主题，支持暗色模式

## 🏗️ 网站架构

### 技术栈
- **静态网站生成器**：[Hugo](https://gohugo.io/) v0.148.2
- **主题框架**：[Blowfish](https://blowfish.page/) v2.89.0
- **Web服务器**：Nginx 1.18.0
- **部署环境**：Ubuntu 22.04 LTS
- **版本控制**：Git + GitHub

### 目录结构

```
/var/www/cuhkstudy/
├── config/_default/           # Hugo 配置文件
│   ├── hugo.toml             # 主配置文件
│   ├── params.toml           # 主题参数配置
│   ├── menus.zh-cn.toml      # 中文菜单配置
│   └── languages.zh-cn.toml  # 语言配置
├── content/                  # 内容源文件
│   ├── main/                 # 主要内容版块
│   ├── ugfn/                 # 大学国文课程
│   ├── ugfh/                 # 大学中史课程
│   ├── mess/                 # 杂聊内容
│   └── info/                 # 网站信息
├── static/                   # 静态资源
│   ├── pdfs/                 # PDF 文档
│   ├── img/                  # 图片资源
│   └── fonts/                # 字体文件
├── layouts/                  # 自定义布局模板
│   ├── partials/home/        # 首页组件
│   └── partials/recent-articles/ # 文章列表组件
├── assets/css/               # 自定义样式
├── themes/blowfish/          # 主题文件
├── public/                   # 生成的静态网站
├── deploy.sh                 # 自动化部署脚本
└── new-post.sh              # 新建文章脚本
```

## 📚 内容架构

### 学术内容分类

1. **UGFN (大学国文)**
   - 经典文本阅读
   - 课程指导材料
   - AI 辅助学习指南

2. **UGFH (大学中史)**  
   - 历史文献资料
   - 研究方法指导

3. **Main (主要内容)**
   - 跨学科学习资源
   - 通识教育材料

4. **杂聊 (Mess)**
   - 学习心得分享
   - 校园生活话题

### 内容格式支持

- **Markdown 文章**：支持丰富的 Markdown 语法
- **PDF 文档**：在线预览，支持下载
- **图片媒体**：自动优化，支持多格式
- **外部链接**：智能标记，新窗口打开

## 🚀 开发与部署

### 本地开发环境

```bash
# 克隆项目
git clone git@github.com:VincentJiang06/cuhkstudy.git
cd cuhkstudy

# 初始化子模块（主题）
git submodule update --init --recursive

# 启动开发服务器
hugo server -D

# 访问 http://localhost:1313
```

### 生产环境部署

```bash
# 1. 构建网站
hugo --minify

# 2. 使用自动化部署脚本
./deploy.sh

# 3. 手动部署（如果需要）
cp -r public/* /var/www/cuhkstudy/public/
chown -R www-data:www-data /var/www/cuhkstudy/public/
systemctl reload nginx
```

### 配置管理

#### 网站基础配置 (`config/_default/hugo.toml`)
```toml
title = "CUHKstudy"
baseURL = "https://cuhkstudy.com/"  # 域名配置
defaultContentLanguage = "zh-cn"
theme = "blowfish"
```

#### 主题参数配置 (`config/_default/params.toml`)
```toml
# 首页布局
[homepage]
  layout = "background"
  showRecent = true
  showRecentItems = 6

# 列表显示
[list]
  showCards = false  # 简洁列表视图
  constrainItemsWidth = true
```

## 🔧 内容管理

### 创建新文章

```bash
# 使用脚本创建新文章
./new-post.sh "文章标题" [zh-cn|zh-tw|both]

# 手动创建
hugo new content/ugfn/new-article.md
```

### 文章Front Matter示例

```yaml
---
title: "文章标题"
description: "文章描述"
date: 2025-01-01T00:00:00+08:00
draft: false
categories: ["课程资料"]
tags: ["UGFN", "Guide"]
---

文章内容...

## PDF 下载
[点击下载 PDF](/pdfs/document.pdf)
```

### 上传资源文件

```bash
# PDF 文档
cp document.pdf static/pdfs/

# 图片文件  
cp image.jpg content/ugfn/

# 重新构建
hugo --minify
```

## 🎨 自定义与扩展

### 主题颜色定制

主品牌色：`#0EB185`

自定义CSS位置：`assets/css/custom.css`

### 布局组件

- **首页布局**：`layouts/partials/home/background.html`
- **文章列表**：`layouts/partials/recent-articles/list.html`
- **文章链接**：`layouts/partials/article-link/simple.html`

### 功能特性

- ✅ 图片自动优化（11MB → 371KB）
- ✅ 简洁列表视图（移除卡片边框）
- ✅ 禁用编辑链接（生产环境友好）
- ✅ 中文字体优化（Inter字体）
- ✅ 暗色模式支持

## 🌐 访问信息

### 域名配置
- **主域名**：cuhkstudy.com（备案中）
- **临时访问**：通过服务器IP + SSH端口转发

### 访问方式

```bash
# SSH 端口转发（开发调试）
ssh -L 8080:localhost:80 root@SERVER_IP

# 浏览器访问
http://localhost:8080
```

### 网站结构
- **首页**：`/` （自动重定向到中文版本）
- **主要内容**：`/main/`
- **大学国文**：`/ugfn/`
- **大学中史**：`/ugfh/`
- **杂聊**：`/mess/`
- **关于**：`/info/`