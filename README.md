# CUHKstudy 网站

一个基于 Hugo 的静态网站，用于分享香港中文大学（深圳）课程资料。

- 线上地址：`https://cuhkstudy.com`
- 主题：`blowfish`
- 开发方式：使用 Cursor 辅助进行开发与运维

## 架构概览
- **Hugo** 构建静态页面，源码位于 `content/`、`layouts/`、`assets/`、`static/`
- **Nginx** 作为 Web 服务器，直接服务 `public/` 构建产物
- **Cloudflare R2** 用作 PDF 的公共 CDN（浏览器地址栏直接显示 R2 公网地址）
- **Certbot/Let’s Encrypt** 自动签发与续期证书，实现全站 HTTPS + HSTS
- **部署脚本**：`deploy.sh` 统一执行图片优化与生产构建
- **图片优化**：`optimize-images.sh` 将大图压缩为 WebP 并剥离元数据
- **ICP备案号**：通过生产环境参数注入并在页脚稳定展示

目录速览：
- `config/_default/params.toml`：公共站点参数（含 `fileCDN`）
- `config/production/params.toml`：生产环境参数（注入 `icp`，不纳入 Git）
- `layouts/partials/footer.html`：全局页脚，固定展示备案号
- `layouts/_default/_markup/render-link.html`：Markdown 链接重写（将 `https://cdn.cuhkstudy.com/pdfs/` 改写到 R2）
- `layouts/partials/article-link/_external-link.html`：卡片/外链的 PDF 链接重写
- `themes/blowfish/layouts/_default/single.html`：禁用文章底部“上一页/下一页”导航
- `server-config/nginx/`：Nginx 样例与说明（生产在 `/etc/nginx/`）

## 快速开始（开发）
1. 安装依赖
   - Hugo Extended ≥ 0.148
   - Node（如需 Tailwind/PostCSS 处理）
2. 启动本地预览
   ```bash
   hugo server -D
   # 浏览器打开 http://localhost:1313
   ```
3. 重要：开发时无需 ICP 值；生产注入由 `--environment production` 控制。

## 构建与部署（生产）
推荐使用 `deploy.sh`，它会先优化图片再进行生产构建：
```bash
bash deploy.sh
```
等价于：
```bash
bash optimize-images.sh
hugo --environment production --minify
```
构建产物在 `public/`，Nginx `root` 指向该目录即可。

### 生产参数注入（ICP）
- 文件：`config/production/params.toml`
- 内容：
  ```toml
  icp = "浙ICP备2025176709号-3"
  ```
- 说明：该文件被 `.gitignore` 排除，避免备案号进仓库。构建时需加 `--environment production`。

### PDF 加速与链接改写（R2）
- `config/_default/params.toml` 中配置统一前缀：
  ```toml
  [params]
  fileCDN = "https://cdn.cuhkstudy.com"
  ```
- Hugo 渲染阶段自动改写：
  - Markdown：`layouts/_default/_markup/render-link.html`
  - 卡片/外链：`layouts/partials/article-link/_external-link.html`
- Nginx 层：对以 `.pdf` 结尾的请求做 302 重定向到 R2 公网（地址栏直接显示 R2 域名）。

### Nginx 配置要点（示例）
```nginx
server {
    listen 80;
    server_name cuhkstudy.com www.cuhkstudy.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name cuhkstudy.com www.cuhkstudy.com;

    root /var/www/cuhkstudy/public;
    index index.html index.htm;

    # R2 公网地址
    set $r2_endpoint "https://cdn.cuhkstudy.com";

    location ~* \.pdf$ {
        add_header Cache-Control "public, max-age=300";
        add_header Access-Control-Allow-Origin "*";
        return 302 $r2_endpoint$uri;
    }

    # 图片/字体 本地直出 + 强缓存
    location ~* \.(png|jpg|jpeg|webp)$ {
        try_files $uri =404;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    location ~* \.(woff|woff2|ttf)$ {
        try_files $uri =404;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location / {
        try_files $uri $uri/ /index.html;
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    }

    # Certbot（示例，实际以 certbot 注入为准）
    ssl_certificate /etc/letsencrypt/live/cuhkstudy.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cuhkstudy.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
```

### 启用 HTTPS（Certbot）
```bash
sudo apt update && sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d cuhkstudy.com -d www.cuhkstudy.com
# 验证并重载
sudo nginx -t && sudo systemctl reload nginx --no-pager
```
证书续期由 Certbot 自动安装的定时任务处理，可用 `sudo certbot renew --dry-run` 验证。

### 服务器资源优化
- 图片在构建前使用 `optimize-images.sh` 统一压缩到 WebP、限制最大宽度并剥离元数据
- Nginx 对图片/字体关闭 `access_log`，降低 I/O
- Hugo 构建使用 `--minify`，产物更小

## 页脚与备案号（极其重要）
- 模板：`layouts/partials/footer.html`
- 逻辑：优先读取 `.Site.Params.icp`（生产注入），次要兜底读取 `HUGO_PARAMS_ICP`
- 要求：页脚始终渲染备案号，链接 `https://beian.miit.gov.cn/`

## 其他定制
- 文章页底部“上一页/下一页”分页导航已禁用，避免误跳到 PDF 卡片
- 首页背景恢复为 SVG（按需可自定义 `assetshttps://cdn.cuhkstudy.com/img/`）

## 常见问题
- Hugo 读取环境变量报 `access denied ... security.funcs.getenv`：请改为通过 `config/production/params.toml` 注入 `.Site.Params` 来读取
- R2 中文 PDF 文件名 400：已改为 302 跳转模式，浏览器直接访问 R2 公网地址，规避代理编码问题

## 发布与版本
- 正常工作流：
  ```bash
  git add -A
  git commit -m "feat/fix: ..."
  git tag vX.Y
  ```
- 本次版本：`v1.2`

## 开发说明
本项目使用 Cursor 进行开发、调试与文档编写，提升了协作效率与交付质量。

