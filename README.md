# CUHKstudy - 香港中文大学课程资料分享平台 v1.1

[![版本](https://img.shields.io/badge/版本-v1.1.0-blue)](./VERSION)
[![系统状态](https://img.shields.io/badge/系统状态-良好_84.6%25-green)](./system_health_report.json)
[![Hugo](https://img.shields.io/badge/Hugo-0.148.2-ff4088)](https://gohugo.io/)
[![Python](https://img.shields.io/badge/Python-3.x-3776ab)](https://python.org/)

## 🎯 项目概述

这是一个现代化的香港中文大学课程资料分享平台，基于 Hugo 构建，集成了：
- ✅ **阅读量统计系统** - 自建轻量级页面访问跟踪
- ✅ **智能CDN加速** - Cloudflare R2 优化大文件加载
- ✅ **在线Markdown编辑器** - 支持语法高亮和文件分类
- ✅ **中文优化** - 完整的中文字体和编码支持
- ✅ **现代化设计** - 响应式布局和Tokyo Night主题
- ✅ **系统监控** - 自动健康检查和性能监控
- ✅ Cloudflare R2 CDN 加速

## 🚀 快速开始

### 📊 v1.1 新功能

#### 阅读量统计系统
- **自动跟踪**: 页面访问和卡片点击自动记录
- **实时显示**: 在页面卡片上显示👁️阅读量标记
- **隐私保护**: 仅存储hash化访客信息，不记录IP地址
- **API接口**: 支持编程访问统计数据

```bash
# 查看热门页面
curl http://localhost/api/popular

# 查看特定页面统计
curl "http://localhost/api/stats?url=/ugfn/"
```

#### 在线Markdown编辑器 (端口8888)
- **访问地址**: http://localhost:8888/editor
- **文件分类**: 智能分类课程内容、基础文件、标签分类
- **语法高亮**: CodeMirror支持Markdown语法高亮
- **Hugo支持**: 自动识别和渲染Hugo Front Matter
- **快捷键**: Ctrl+S保存, Ctrl+R刷新

#### 系统健康监控
```bash
# 运行系统健康检查
cd /root/cuhkstudy
python3 scripts/system_health_check.py
```

### 创建新播客文章
```bash
# 创建简体中文文章
./new-post.sh "第二期播客：技术分享"

# 创建繁体中文文章  
./new-post.sh "第二期播客：技术分享" zh-tw

# 同时创建中繁两个版本
./new-post.sh "第二期播客：技术分享" both
```

### 部署网站
```bash
# 部署包含草稿的版本（用于预览）
./deploy.sh --draft

# 部署正式版本
./deploy.sh
```

## 🌐 CDN 架构

本网站采用**智能混合CDN架构**，结合nginx本地服务和Cloudflare R2全球CDN：

```
用户请求 → nginx → [本地文件存在?] → 是 → 直接返回 (小文件)
                ↓ 否
                → Cloudflare R2 CDN → 返回文件 (大文件)
```

### 🎯 文件分层策略

| 文件类型 | 存储位置 | 说明 |
|---------|---------|------|
| HTML/CSS/JS | nginx本地 | 小文件，快速响应 |
| 大PDF/图片 | Cloudflare R2 | >100KB文件，全球CDN加速 |
| 字体文件 | Cloudflare R2 | woff2字体，缓存30天 |

### 📊 优化成果

- 🗂️ **文件去重**: 从269个文件优化到48个核心文件  
- 📦 **存储优化**: 103.49MB CDN存储，节省带宽成本
- ⚡ **加载提升**: 大文件全球CDN分发，显著提升访问速度
- 🛡️ **智能回退**: nginx自动在本地和CDN间选择最优路径

## 📁 目录结构

```
/root/cuhkstudy/
├── content/
│   ├── zh-cn/          # 简体中文内容
│   └── zh-tw/          # 繁体中文内容
├── static/
│   ├── pdfs/           # PDF 文件 (CDN同步)
│   ├── img/            # 图片文件 (CDN同步)
│   ├── fonts/          # 字体文件 (CDN同步)
│   └── pdfjs/          # PDF.js 阅读器
├── assets/             # 静态资源 (CDN同步)
├── public/             # Hugo生成文件
├── scripts/            # 自动化脚本
│   ├── upload_to_r2.py        # R2批量上传
│   ├── hugo_r2_sync.py        # Hugo构建后同步
│   └── r2_cleanup_optimize.py # CDN优化清理
├── nginx-r2-optimized.conf    # nginx CDN配置
├── .env.example               # 环境变量模板
├── hugo.toml                  # 网站配置
└── README.md                  # 本文档
```

## 🔧 常用操作

### 1. 上传文件

**音频文件：**
```bash
# 将音频文件上传到
/home/mypodcast/static/audio/文件名.mp3
```

**PDF文件：**
```bash
# 将PDF文件上传到
/home/mypodcast/static/pdfs/文件名.pdf
```

### 2. 编辑文章

```bash
# 编辑简体中文文章
vim content/zh-cn/posts/文章名.md

# 编辑繁体中文文章
vim content/zh-tw/posts/文章名.md
```

### 3. 网站配置

主要配置文件：`hugo.toml`

**修改域名：**
```toml
baseURL = 'https://您的域名/'
```

**修改网站标题：**
```toml
title = '您的播客站名称'
```

### 4. CDN 管理

**同步文件到CDN：**
```bash
# Hugo构建后自动同步静态资源到R2
python3 scripts/hugo_r2_sync.py --build

# 只同步现有文件（不重新构建）
python3 scripts/hugo_r2_sync.py
```

**清理和优化CDN：**
```bash
# 清理冗余文件，优化存储
python3 scripts/r2_cleanup_optimize.py
```

**检查CDN状态：**
```bash
# 查看nginx CDN状态
curl http://localhost/api/r2-status

# 测试文件CDN回退
curl -I http://localhost/static/pdfs/UGFN中文版ver2.1.pdf
```

### 5. SSL 证书配置

```bash
# 安装SSL证书（需要先配置域名DNS）
certbot --nginx -d 您的域名
```

## 🎨 自定义

### 修改主题颜色

主品牌色已配置为 `#0EB185`，如需修改可编辑：
- CSS 文件: `assets/css/custom.css`
- 主题配置: `hugo.toml` 中的 `params` 部分

### 添加菜单项

在 `hugo.toml` 中修改 `[menu]` 部分：

```toml
[[menu.main]]
    identifier = "new-page"
    name = "新页面"
    url = "/new-page/"
    weight = 50
```

## 📊 网站监控

### 查看访问日志
```bash
tail -f /var/log/nginx/mypodcast_access.log
```

### 查看错误日志
```bash
tail -f /var/log/nginx/mypodcast_error.log
```

### 检查网站状态
```bash
systemctl status nginx
```

## 🔍 故障排除

### Hugo 构建失败
```bash
# 检查语法错误
hugo --verbose

# 清理缓存
rm -rf public/
hugo
```

### Nginx 配置问题
```bash
# 测试配置
nginx -t

# 重新加载配置
systemctl reload nginx
```

### 权限问题
```bash
# 重设文件权限
chown -R www-data:www-data /var/www/mypodcast
```

## 🌐 访问地址

- **简体中文**: http://您的域名/zh-cn/
- **繁体中文**: http://您的域名/zh-tw/
- **自动重定向**: http://您的域名/ (根据浏览器语言)

## 🛡️ 安全建议

1. 定期更新系统和软件包
2. 配置 SSL 证书启用 HTTPS
3. 定期备份内容文件
4. 监控访问日志

## 📚 更多资源

- [Hugo 官方文档](https://gohugo.io/documentation/)
- [PaperMod 主题文档](https://github.com/adityatelange/hugo-PaperMod)
- [PDF.js 文档](https://mozilla.github.io/pdf.js/)
- [Nginx 配置指南](https://nginx.org/en/docs/)

---

**技术支持**: 如有问题，请查看相关日志文件或重新运行部署脚本。