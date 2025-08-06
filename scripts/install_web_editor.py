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
        if self.path == '/' or self.path == '/editor':
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
<html>
<head>
    <meta charset="utf-8">
    <title>Markdown Editor</title>
    <style>
        body { margin: 0; font-family: Arial, sans-serif; }
        .container { display: flex; height: 100vh; }
        .sidebar { width: 300px; background: #f5f5f5; padding: 20px; overflow-y: auto; }
        .editor { flex: 1; display: flex; flex-direction: column; }
        .toolbar { background: #333; color: white; padding: 10px; }
        .content { flex: 1; display: flex; }
        .input { flex: 1; }
        .preview { flex: 1; background: white; padding: 20px; overflow-y: auto; }
        textarea { width: 100%; height: 100%; border: none; padding: 20px; font-family: 'Courier New', monospace; font-size: 14px; resize: none; outline: none; }
        .file-item { padding: 8px; cursor: pointer; border-radius: 4px; margin: 4px 0; }
        .file-item:hover { background: #e0e0e0; }
        .file-item.active { background: #007acc; color: white; }
        button { background: #007acc; color: white; border: none; padding: 8px 16px; margin: 0 4px; cursor: pointer; border-radius: 4px; }
        button:hover { background: #005a9e; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h3>📁 Markdown Files</h3>
            <div id="fileList"></div>
        </div>
        <div class="editor">
            <div class="toolbar">
                <span id="currentFile">Select a file to edit</span>
                <button onclick="saveFile()" id="saveBtn" disabled>💾 Save</button>
                <button onclick="refreshFiles()">🔄 Refresh</button>
            </div>
            <div class="content">
                <div class="input">
                    <textarea id="editor" placeholder="Select a markdown file to start editing..." disabled></textarea>
                </div>
                <div class="preview" id="preview">
                    <p>Preview will appear here...</p>
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
        
        function updatePreview() {
            const markdown = editor.value;
            preview.innerHTML = marked.parse(markdown);
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
                console.error('Error loading files:', error);
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
                alert('Error loading file: ' + error.message);
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
                    alert('✅ File saved successfully!');
                } else {
                    throw new Error('Save failed');
                }
            } catch (error) {
                alert('❌ Error saving file: ' + error.message);
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
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def list_files(self):
        """列出markdown文件"""
        md_files = []
        base_dir = Path('/root/cuhkstudy')
        
        for pattern in ['**/*.md', '**/*.markdown']:
            for file_path in base_dir.glob(pattern):
                rel_path = file_path.relative_to(base_dir)
                md_files.append(str(rel_path))
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(sorted(md_files)).encode())
    
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
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_editor(port)