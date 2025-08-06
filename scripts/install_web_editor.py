#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装简单的Web编辑器
基于Python的轻量级在线编辑器
"""

import os
import http.server
import socketserver
import urllib.parse
import json
from pathlib import Path

class MarkdownEditorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 处理nginx代理路径
        if self.path == '/' or self.path == '/editor' or self.path.startswith('/editor'):
            self.serve_editor()
        elif self.path.startswith('/api/files'):
            self.list_files()
        elif self.path.startswith('/api/read/'):
            self.read_file()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/save/'):
            self.save_file()
        else:
            self.send_error(404)
    
    def serve_editor(self):
        """提供编辑器界面"""
        html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📝 Markdown 编辑器 - CUHK Study</title>
    <style>
        * { 
            box-sizing: border-box; 
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        body { 
            margin: 0; 
            font-family: 
                -apple-system, BlinkMacSystemFont, 
                'Segoe UI', 'Roboto', 'Helvetica Neue', 
                'PingFang SC', 'Hiragino Sans GB', 
                'Microsoft YaHei UI', 'Microsoft YaHei', 
                'Source Han Sans SC', 'Noto Sans CJK SC', 
                'WenQuanYi Micro Hei', sans-serif;
            background: #f8f9fa;
            font-size: 14px;
            line-height: 1.6;
        }
        .container { display: flex; height: 100vh; }
        .sidebar { 
            width: 300px; 
            background: #fff; 
            padding: 20px; 
            overflow-y: auto; 
            border-right: 1px solid #e9ecef;
            box-shadow: 2px 0 4px rgba(0,0,0,0.1);
        }
        .editor { flex: 1; display: flex; flex-direction: column; }
        .toolbar { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 15px 20px; 
            display: flex; 
            align-items: center; 
            justify-content: space-between;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .content { flex: 1; display: flex; }
        .input { flex: 1; background: #fff; }
        .preview { 
            flex: 1; 
            background: white; 
            padding: 20px; 
            overflow-y: auto; 
            border-left: 1px solid #e9ecef;
            font-family: 
                -apple-system, BlinkMacSystemFont, 
                'Segoe UI', 'Roboto', 'Helvetica Neue',
                'PingFang SC', 'Hiragino Sans GB', 
                'Microsoft YaHei UI', 'Microsoft YaHei', 
                'Source Han Sans SC', 'Noto Sans CJK SC', 
                'WenQuanYi Micro Hei', sans-serif;
            font-size: 14px;
            line-height: 1.8;
            color: #2c3e50;
        }
        textarea { 
            width: 100%; 
            height: 100%; 
            border: none; 
            padding: 20px; 
            font-family: 
                'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono',
                'Source Code Pro', 'Menlo', 'Consolas', 
                'DejaVu Sans Mono', 'Ubuntu Mono', 'Courier New',
                'Microsoft YaHei UI', 'Microsoft YaHei', monospace;
            font-size: 14px; 
            line-height: 1.8;
            resize: none; 
            outline: none; 
            background: #fff;
            color: #2c3e50;
            font-feature-settings: "liga" 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        .file-item { 
            padding: 12px 16px; 
            cursor: pointer; 
            border-radius: 8px; 
            margin: 4px 0; 
            transition: all 0.2s ease;
            border: 1px solid transparent;
            font-size: 14px;
        }
        .file-item:hover { 
            background: #f8f9fa; 
            border-color: #dee2e6;
            transform: translateY(-1px);
        }
        .file-item.active { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        button { 
            background: rgba(255,255,255,0.2); 
            color: white; 
            border: 1px solid rgba(255,255,255,0.3); 
            padding: 8px 16px; 
            margin: 0 4px; 
            cursor: pointer; 
            border-radius: 6px; 
            font-size: 14px;
            transition: all 0.2s ease;
        }
        button:hover { 
            background: rgba(255,255,255,0.3); 
            transform: translateY(-1px);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .sidebar h3 {
            color: #495057;
            margin-top: 0;
            font-size: 16px;
            font-weight: 600;
        }
        .current-file {
            font-weight: 500;
            font-size: 16px;
        }
        .toolbar-right {
            display: flex;
            gap: 8px;
        }
        /* 中文字体和排版优化 */
        .preview h1, .preview h2, .preview h3, .preview h4, .preview h5, .preview h6 {
            font-family: 
                -apple-system, BlinkMacSystemFont, 
                'Segoe UI', 'Roboto', 'Helvetica Neue',
                'PingFang SC', 'Hiragino Sans GB', 
                'Microsoft YaHei UI', 'Microsoft YaHei', 
                'Source Han Sans SC', 'Noto Sans CJK SC', sans-serif;
            color: #2c3e50;
            font-weight: 600;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            line-height: 1.4;
        }
        .preview p, .preview li {
            line-height: 1.8;
            color: #34495e;
            margin: 0.8em 0;
            word-break: break-word;
            word-wrap: break-word;
        }
        .preview code {
            background: #f1f3f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 
                'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono',
                'Source Code Pro', 'Menlo', 'Consolas', 
                'Microsoft YaHei UI', monospace;
            font-size: 0.9em;
            color: #d73a49;
        }
        .preview pre {
            background: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid #e1e4e8;
            line-height: 1.6;
        }
        .preview pre code {
            background: none;
            padding: 0;
            color: #24292e;
        }
        .preview blockquote {
            border-left: 4px solid #dfe2e5;
            padding-left: 16px;
            margin: 16px 0;
            color: #6a737d;
            font-style: italic;
        }
        .preview table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        .preview th, .preview td {
            border: 1px solid #dfe2e5;
            padding: 8px 12px;
            text-align: left;
        }
        .preview th {
            background: #f6f8fa;
            font-weight: 600;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h3>📁 Markdown 文件</h3>
            <div id="fileList"></div>
        </div>
        <div class="editor">
            <div class="toolbar">
                <span class="current-file" id="currentFile">选择一个文件开始编辑</span>
                <div class="toolbar-right">
                    <button onclick="saveFile()" id="saveBtn" disabled>💾 保存</button>
                    <button onclick="refreshFiles()">🔄 刷新</button>
                </div>
            </div>
            <div class="content">
                <div class="input">
                    <textarea id="editor" placeholder="选择一个 Markdown 文件开始编辑...

支持中文字符输入，包括：
- 简体中文
- 繁体中文  
- 中文标点符号
- 混合中英文内容

快捷键：
Ctrl+S: 保存文件" disabled></textarea>
                </div>
                <div class="preview" id="preview">
                    <h3>📖 预览窗口</h3>
                    <p>Markdown 预览内容将在这里显示...</p>
                    <p>支持完整的中文字符渲染，包括中英文混排和中文标点。</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentFile = null;
        const editor = document.getElementById('editor');
        const preview = document.getElementById('preview');
        const currentFileSpan = document.getElementById('currentFile');
        const saveBtn = document.getElementById('saveBtn');
        
        editor.addEventListener('input', updatePreview);
        
        // 添加键盘快捷键支持
        document.addEventListener('keydown', function(e) {
            // Ctrl+S 保存文件
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                saveFile();
            }
            // Ctrl+R 刷新文件列表
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                refreshFiles();
            }
        });
        
        function updatePreview() {
            const markdown = editor.value;
            try {
                // 配置 marked 以更好地支持中文
                marked.setOptions({
                    breaks: true,  // 支持 GitHub 风格的换行
                    gfm: true,     // 启用 GitHub 风格的 Markdown
                });
                preview.innerHTML = marked.parse(markdown);
            } catch (error) {
                preview.innerHTML = '<p style="color: red;">预览解析错误: ' + error.message + '</p>';
            }
        }
        
        async function loadFiles() {
            try {
                const response = await fetch('/api/files');
                const files = await response.json();
                const fileList = document.getElementById('fileList');
                fileList.innerHTML = '';
                
                files.forEach(file => {
                    const div = document.createElement('div');
                    div.className = 'file-item';
                    div.textContent = file;
                    div.onclick = () => loadFile(file);
                    fileList.appendChild(div);
                });
            } catch (error) {
                console.error('加载文件列表时出错:', error);
                const fileList = document.getElementById('fileList');
                fileList.innerHTML = '<p style="color: red; padding: 8px;">❌ 无法加载文件列表</p>';
            }
        }
        
        async function loadFile(filename) {
            try {
                const response = await fetch(`/api/read/${encodeURIComponent(filename)}`);
                const content = await response.text();
                
                editor.value = content;
                editor.disabled = false;
                currentFile = filename;
                currentFileSpan.textContent = filename;
                saveBtn.disabled = false;
                
                // Update active file
                document.querySelectorAll('.file-item').forEach(item => {
                    item.classList.toggle('active', item.textContent === filename);
                });
                
                updatePreview();
            } catch (error) {
                alert('❌ 加载文件时出错：' + error.message);
            }
        }
        
        async function saveFile() {
            if (!currentFile) return;
            
            try {
                const response = await fetch(`/api/save/${encodeURIComponent(currentFile)}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: editor.value
                });
                
                if (response.ok) {
                    alert('✅ 文件保存成功！');
                } else {
                    throw new Error('保存失败');
                }
            } catch (error) {
                alert('❌ 保存文件时出错：' + error.message);
            }
        }
        
        function refreshFiles() {
            loadFiles();
        }
        
        // Load files on startup
        loadFiles();
    </script>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def list_files(self):
        """列出markdown文件"""
        md_files = []
        base_dir = Path('/root/cuhkstudy')
        
        for pattern in ['**/*.md', '**/*.markdown']:
            for file_path in base_dir.glob(pattern):
                rel_path = file_path.relative_to(base_dir)
                md_files.append(str(rel_path))
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(sorted(md_files), ensure_ascii=False).encode('utf-8'))
    
    def read_file(self):
        """读取文件内容"""
        file_path = urllib.parse.unquote(self.path[10:])  # Remove '/api/read/'
        full_path = Path('/root/cuhkstudy') / file_path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def save_file(self):
        """保存文件"""
        file_path = urllib.parse.unquote(self.path[10:])  # Remove '/api/save/'
        full_path = Path('/root/cuhkstudy') / file_path
        
        try:
            content_length = int(self.headers['Content-Length'])
            content = self.rfile.read(content_length).decode('utf-8')
            
            # 确保目录存在
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('保存成功'.encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))

def start_editor(port=8080):
    """启动编辑器服务"""
    os.chdir('/root/cuhkstudy')
    
    with socketserver.TCPServer(("", port), MarkdownEditorHandler) as httpd:
        print(f"🚀 Markdown Editor started at http://localhost:{port}")
        print(f"📝 You can now edit markdown files in your browser!")
        print(f"🔗 Open: http://your-server-ip:{port}")
        print(f"⭐ Press Ctrl+C to stop")
        httpd.serve_forever()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    start_editor(port)