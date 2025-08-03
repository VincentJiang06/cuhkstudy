# CUHKstudy - Ubuntu 22.04 阿里云ECS部署指南

## 🚀 部署概述

本项目是基于Hugo的静态网站，使用Blowfish主题。可以完美部署在Ubuntu 22.04阿里云ECS服务器上。

## 📋 系统要求

- **操作系统**: Ubuntu 22.04 LTS
- **内存**: 最少1GB（推荐2GB+）
- **存储**: 最少10GB可用空间
- **网络**: 公网IP（阿里云ECS默认提供）

## 🛠️ 安装步骤

### 1. 连接到服务器

```bash
ssh root@你的服务器IP
```

### 2. 更新系统

```bash
apt update && apt upgrade -y
```

### 3. 安装必要软件

```bash
# 安装基础工具
apt install -y wget curl git nginx ufw

# 安装Hugo Extended版本
wget https://github.com/gohugoio/hugo/releases/download/v0.148.2/hugo_extended_0.148.2_linux-amd64.deb
dpkg -i hugo_extended_0.148.2_linux-amd64.deb

# 验证安装
hugo version
```

### 4. 克隆项目

```bash
# 进入网站目录
cd /var/www

# 克隆项目（包含子模块）
git clone --recursive https://github.com/VincentJiang06/cuhkstudy.git
cd cuhkstudy

# 如果子模块没有正确加载
git submodule update --init --recursive
```

### 5. 配置域名

编辑配置文件：

```bash
nano config/_default/hugo.toml
```

修改：
```toml
baseURL = "https://你的域名.com/"  # 替换为实际域名
```

### 6. 构建网站

```bash
# 构建生产版本
hugo --minify

# 检查构建结果
ls -la public/
```

### 7. 配置Nginx

创建Nginx配置：

```bash
nano /etc/nginx/sites-available/cuhkstudy
```

添加配置：
```nginx
server {
    listen 80;
    server_name 你的域名.com www.你的域名.com;
    root /var/www/cuhkstudy/public;
    index index.html;

    # 中文文件名支持
    charset utf-8;

    # 静态文件缓存
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # PDF文件直接下载
    location /pdfs/ {
        add_header Content-Disposition 'attachment';
        add_header Content-Type 'application/pdf';
    }

    # 默认路由
    location / {
        try_files $uri $uri/ =404;
    }

    # 404错误页面
    error_page 404 /404.html;
}
```

启用网站：
```bash
ln -s /etc/nginx/sites-available/cuhkstudy /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 8. 配置防火墙

```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### 9. 设置自动更新脚本

创建更新脚本：

```bash
nano /var/www/cuhkstudy/update.sh
chmod +x /var/www/cuhkstudy/update.sh
```

## 🔄 自动更新部署

### 设置定时任务（可选）

```bash
crontab -e
```

添加：
```bash
# 每天凌晨2点自动更新
0 2 * * * /var/www/cuhkstudy/update.sh >> /var/log/cuhkstudy-update.log 2>&1
```

## 🔒 SSL证书配置

### 使用Let's Encrypt（推荐）

```bash
# 安装Certbot
apt install -y certbot python3-certbot-nginx

# 获取SSL证书
certbot --nginx -d 你的域名.com -d www.你的域名.com

# 设置自动续期
crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 性能优化

### 1. 启用Gzip压缩

在Nginx配置中添加：
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### 2. 设置合适的worker进程数

```bash
# 检查CPU核心数
nproc

# 编辑Nginx配置
nano /etc/nginx/nginx.conf
# 设置worker_processes为CPU核心数
```

## 🔍 故障排除

### 常见问题

1. **Hugo版本错误**
   ```bash
   hugo version  # 确认使用extended版本
   ```

2. **子模块未加载**
   ```bash
   git submodule update --init --recursive
   ```

3. **权限问题**
   ```bash
   chown -R www-data:www-data /var/www/cuhkstudy/public
   ```

4. **中文显示问题**
   确保Nginx配置中有 `charset utf-8;`

### 日志位置

- Nginx访问日志: `/var/log/nginx/access.log`
- Nginx错误日志: `/var/log/nginx/error.log`
- 更新日志: `/var/log/cuhkstudy-update.log`

## 📈 监控和维护

### 基本监控

```bash
# 检查服务状态
systemctl status nginx

# 检查磁盘空间
df -h

# 检查内存使用
free -h

# 查看最近的访问
tail -f /var/log/nginx/access.log
```

## 🎯 总结

这个Hugo项目完全兼容Ubuntu 22.04阿里云ECS，主要特点：

- ✅ 纯静态网站，性能优秀
- ✅ 支持中文内容和文件名
- ✅ 响应式设计，移动端友好
- ✅ SEO优化配置完整
- ✅ 自动化部署脚本
- ✅ SSL证书支持

部署后网站将完全可用，支持PDF下载、多语言显示等所有功能。