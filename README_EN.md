# Hugo Podcast Website Management Guide

## 🎯 Project Overview

This is a Hugo-based static podcast website that supports:
- ✅ Chinese Simplified/Traditional language switching
- ✅ Online PDF reading and downloading  
- ✅ Audio player
- ✅ Responsive design
- ✅ High-performance static deployment
- ✅ Cloudflare R2 CDN acceleration

## 🌐 CDN Architecture

This website uses a **smart hybrid CDN architecture**, combining nginx local service with Cloudflare R2 global CDN:

```
User Request → nginx → [Local file exists?] → Yes → Direct return (small files)
                ↓ No
                → Cloudflare R2 CDN → Return file (large files)
```

### 🎯 File Layering Strategy

| File Type | Storage Location | Description |
|---------|---------|------|
| HTML/CSS/JS | nginx local | Small files, fast response |
| Large PDF/Images | Cloudflare R2 | >100KB files, global CDN acceleration |
| Font files | Cloudflare R2 | woff2 fonts, 30-day cache |

### 📊 Optimization Results

- 🗂️ **File deduplication**: Optimized from 269 files to 48 core files  
- 📦 **Storage optimization**: 103.49MB CDN storage, saving bandwidth costs
- ⚡ **Loading improvement**: Large files distributed via global CDN, significantly improving access speed
- 🛡️ **Smart fallback**: nginx automatically selects optimal path between local and CDN

## 📁 Directory Structure

```
/root/cuhkstudy/
├── content/
│   ├── zh-cn/          # Simplified Chinese content
│   └── zh-tw/          # Traditional Chinese content
├── static/
│   ├── pdfs/           # PDF files (CDN synced)
│   ├── img/            # Image files (CDN synced)
│   ├── fonts/          # Font files (CDN synced)
│   └── pdfjs/          # PDF.js reader
├── assets/             # Static resources (CDN synced)
├── public/             # Hugo generated files
├── scripts/            # Automation scripts
│   ├── upload_to_r2.py        # R2 batch upload
│   ├── hugo_r2_sync.py        # Post-Hugo build sync
│   └── r2_cleanup_optimize.py # CDN optimization cleanup
├── nginx-r2-optimized.conf    # nginx CDN configuration
├── .env.example               # Environment variable template
├── hugo.toml                  # Website configuration
└── README.md                  # This documentation
```

## 🚀 Quick Start

### Create New Podcast Article
```bash
# Create Simplified Chinese article
./new-post.sh "Episode 2: Tech Sharing"

# Create Traditional Chinese article  
./new-post.sh "Episode 2: Tech Sharing" zh-tw

# Create both Chinese versions simultaneously
./new-post.sh "Episode 2: Tech Sharing" both
```

### Deploy Website
```bash
# Deploy version with drafts (for preview)
./deploy.sh --draft

# Deploy production version
./deploy.sh
```

## 🔧 Common Operations

### 1. File Upload

**Audio files:**
```bash
# Upload audio files to
/root/cuhkstudy/static/audio/filename.mp3
```

**PDF files:**
```bash
# Upload PDF files to
/root/cuhkstudy/static/pdfs/filename.pdf
```

### 2. Edit Articles

```bash
# Edit Simplified Chinese article
vim content/zh-cn/posts/article-name.md

# Edit Traditional Chinese article
vim content/zh-tw/posts/article-name.md
```

### 3. Website Configuration

Main configuration file: `hugo.toml`

**Modify domain:**
```toml
baseURL = 'https://yourdomain.com/'
```

**Modify website title:**
```toml
title = 'Your Podcast Site Name'
```

### 4. CDN Management

**Sync files to CDN:**
```bash
# Auto-sync static resources to R2 after Hugo build
python3 scripts/hugo_r2_sync.py --build

# Sync existing files only (no rebuild)
python3 scripts/hugo_r2_sync.py
```

**Clean and optimize CDN:**
```bash
# Clean redundant files, optimize storage
python3 scripts/r2_cleanup_optimize.py
```

**Check CDN status:**
```bash
# Check nginx CDN status
curl http://localhost/api/r2-status

# Test file CDN fallback
curl -I http://localhost/static/pdfs/UGFN中文版ver2.1.pdf
```

### 5. SSL Certificate Configuration

```bash
# Install SSL certificate (DNS must be configured first)
certbot --nginx -d yourdomain.com
```

## 🎨 Customization

### Modify Theme Colors

The main brand color is configured as `#0EB185`. To modify, edit:
- CSS file: `assets/css/custom.css`
- Theme configuration: `params` section in `hugo.toml`

### Add Menu Items

Modify the `[menu]` section in `hugo.toml`:

```toml
[[menu.main]]
    identifier = "new-page"
    name = "New Page"
    url = "/new-page/"
    weight = 50
```

## 📊 Website Monitoring

### View Access Logs
```bash
tail -f /var/log/nginx/cuhkstudy_access.log
```

### View Error Logs
```bash
tail -f /var/log/nginx/cuhkstudy_error.log
```

### Check Website Status
```bash
systemctl status nginx
```

## 🔍 Troubleshooting

### Hugo Build Failure
```bash
# Check syntax errors
hugo --verbose

# Clear cache
rm -rf public/
hugo
```

### Nginx Configuration Issues
```bash
# Test configuration
nginx -t

# Reload configuration
systemctl reload nginx
```

### Permission Issues
```bash
# Reset file permissions
chown -R www-data:www-data /var/www/cuhkstudy
```

## 🌐 Access URLs

- **Simplified Chinese**: http://yourdomain.com/zh-cn/
- **Traditional Chinese**: http://yourdomain.com/zh-tw/
- **Auto redirect**: http://yourdomain.com/ (based on browser language)

## 🛡️ Security Recommendations

1. Regularly update system and software packages
2. Configure SSL certificates to enable HTTPS
3. Regularly backup content files
4. Monitor access logs

## 📚 Additional Resources

- [Hugo Official Documentation](https://gohugo.io/documentation/)
- [Blowfish Theme Documentation](https://blowfish.page/)
- [PDF.js Documentation](https://mozilla.github.io/pdf.js/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)

---

**Technical Support**: If you encounter issues, please check relevant log files or re-run deployment scripts.