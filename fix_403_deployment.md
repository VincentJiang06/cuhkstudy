# 🔧 修复UGFN/UGFH 403 Forbidden问题

## 问题原因
Nginx配置中的`try_files`指令不正确，无法正确处理Hugo生成的静态页面。

## 修复内容
将nginx配置中的：
```nginx
try_files $uri $uri/ =404;
```

修改为：
```nginx  
try_files $uri $uri/ $uri/index.html =404;
```

## 部署步骤

### 1. 更新服务器上的nginx配置
```bash
# 备份当前配置
sudo cp /etc/nginx/sites-available/cuhkstudy /etc/nginx/sites-available/cuhkstudy.backup

# 上传修复后的配置文件
sudo cp nginx-r2-optimized.conf /etc/nginx/sites-available/cuhkstudy

# 测试配置语法
sudo nginx -t

# 重新加载nginx
sudo systemctl reload nginx
```

### 2. 验证修复
访问以下URL应该正常工作：
- https://cuhkstudy.com/ugfn/
- https://cuhkstudy.com/ugfh/

### 3. 清除缓存（如果需要）
```bash
# 清除nginx缓存（如果启用了缓存）
sudo rm -rf /var/cache/nginx/*

# 如果使用了CDN，需要清除CDN缓存
```

## 技术说明
- Hugo生成的是`/ugfn/index.html`文件
- 原配置只查找`/ugfn/`目录，找不到时返回404
- 新配置会依次查找：`/ugfn` → `/ugfn/` → `/ugfn/index.html` → 404
- 这样可以正确找到Hugo生成的index.html文件

