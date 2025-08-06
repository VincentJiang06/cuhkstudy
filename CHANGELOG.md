# CUHKstudy 更新日志

## [v1.1.0] - 2025-08-06

### 🎉 重大更新

#### ✨ 新功能
- **阅读量统计系统**: 自建轻量级、隐私友好的页面访问统计
  - 实时记录页面访问和卡片点击
  - 在页面卡片上显示阅读量标记
  - SQLite数据库存储，保护用户隐私
  - RESTful API支持(POST /api/track, GET /api/stats, GET /api/popular)

- **Markdown在线编辑器优化**:
  - 🌙 Tokyo Night Day 主题
  - 📁 智能文件分类系统(课程内容、基础文件、标签分类)
  - 🎨 CodeMirror语法高亮
  - 🇨🇳 完整中文支持
  - ⚙️ Hugo Front Matter渲染和语法高亮

#### 🚀 性能优化
- **CDN策略重构**:
  - 删除无用的PDF.js组件(节省20MB空间)
  - Inter字体本地化加载策略
  - 智能文件上传:仅上传大图片(PNG>1MB, JPG>500KB)和PDF文件
  - CDN文件数量从269个优化到20个(141.7MB)

- **服务架构改进**:
  - Nginx配置优化,精确的API路由
  - 系统服务自动启动和监控
  - BrokenPipe错误修复和日志优化

#### 🔧 系统改进
- **重复文件清理**: 删除deprecated资源目录和重复文件
- **系统健康检查**: 全面的服务状态、API、文件访问和CDN性能监控
- **错误处理增强**: 更好的异常处理和用户反馈

#### 📊 技术指标
- 系统健康评分: 84.6% (良好)
- 服务可用性: 100% (nginx, markdown-editor, reading-stats)
- API响应正常: 4/4 端点
- 文件访问正常: 3/4 路径

### 🛠️ 技术栈
- **后端**: Python 3, SQLite, systemd服务
- **前端**: JavaScript ES6+, CodeMirror, Hugo静态生成
- **基础设施**: Nginx, Cloudflare R2 CDN
- **监控**: 自定义健康检查系统

### 📝 已知问题
- Cloudflare R2直接连接偶有400错误(通过Nginx代理正常)
- Hugo主页重定向到/zh-cn/但该页面404(通过index.html正常访问)

### 🔄 升级说明
从v1.0升级到v1.1:
1. 运行系统健康检查: `python3 scripts/system_health_check.py`
2. 所有服务会自动启动
3. 新的阅读统计功能会自动生效
4. CDN文件已自动优化

---

## [v1.0.0] - 2025-08-01

### 初始版本
- Hugo静态网站生成
- Cloudflare R2 CDN集成
- 基础Nginx配置
- Markdown内容管理