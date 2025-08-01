# Hugo 播客网站管理手册

## 🎯 项目概述

这是一个基于 Hugo 的静态播客网站，支持：
- ✅ 中繁双语切换
- ✅ PDF 在线阅读和下载
- ✅ 音频播放器
- ✅ 响应式设计
- ✅ 高性能静态部署

## 🚀 快速开始

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

## 📁 目录结构

```
/home/mypodcast/
├── content/
│   ├── zh-cn/          # 简体中文内容
│   └── zh-tw/          # 繁体中文内容
├── static/
│   ├── pdfs/           # PDF 文件
│   ├── audio/          # 音频文件
│   └── pdfjs/          # PDF.js 阅读器
├── themes/PaperMod/    # 主题文件
├── hugo.toml           # 网站配置
├── deploy.sh           # 部署脚本
└── new-post.sh         # 新建文章脚本
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

### 4. SSL 证书配置

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