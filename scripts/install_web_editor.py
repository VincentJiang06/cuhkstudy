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
            background: #f9fafb;
            font-size: 14px;
            line-height: 1.6;
            color: #1a1b23;
        }
        .container { display: flex; height: 100vh; }
        .sidebar { 
            width: 300px; 
            background: #ffffff; 
            padding: 20px; 
            overflow-y: auto; 
            border-right: 1px solid #e1e4e8;
            box-shadow: 0 0 0 1px rgba(27, 31, 36, 0.08);
        }
        .editor { flex: 1; display: flex; flex-direction: column; }
        .toolbar { 
            background: linear-gradient(135deg, #7aa2f7 0%, #9d7cd8 100%); 
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
            font-size: 16px;
            line-height: 1.8;
            color: #000;
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
            font-size: 16px; 
            line-height: 1.8;
            resize: none; 
            outline: none; 
            background: #fff;
            color: #000;
            font-feature-settings: "liga" 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        /* CodeMirror 编辑器样式修复 */
        .CodeMirror {
            width: 100%;
            height: 100% !important;
            border: none;
            font-family: 
                'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono',
                'Source Code Pro', 'Menlo', 'Consolas', 
                'DejaVu Sans Mono', 'Ubuntu Mono', 'Courier New',
                'Microsoft YaHei UI', 'Microsoft YaHei', monospace;
            font-size: 16px;
            line-height: 1.8;
            background: #f7f7f7 !important;
        }
        
        .CodeMirror-scroll {
            height: 100% !important;
            overflow: auto !important;
            padding: 20px;
        }
        
        .CodeMirror-sizer {
            min-height: 100% !important;
        }
        /* 文件夹样式 */
        .folder-main {
            margin-bottom: 16px;
        }
        
        .folder-header {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            background: linear-gradient(135deg, #7aa2f7 0%, #9d7cd8 100%);
            color: white;
            cursor: pointer;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 8px;
            transition: all 0.2s ease;
            user-select: none;
        }
        
        .folder-header:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(122, 162, 247, 0.3);
        }
        
        .folder-icon {
            margin-right: 8px;
            font-size: 18px;
        }
        
        .folder-title {
            flex: 1;
        }
        
        .folder-toggle {
            transition: transform 0.2s ease;
            margin-left: 8px;
        }
        
        .folder-content {
            padding-left: 16px;
        }
        
        .folder-sub {
            margin-bottom: 8px;
        }
        
        .subfolder-header {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            background: #f6f8fa;
            border: 1px solid #e1e4e8;
            cursor: pointer;
            border-radius: 6px;
            font-weight: 500;
            font-size: 14px;
            margin-bottom: 4px;
            transition: all 0.2s ease;
            user-select: none;
        }
        
        .subfolder-header:hover {
            background: #e1e4e8;
        }
        
        .subfolder-icon {
            margin-right: 6px;
        }
        
        .subfolder-title {
            flex: 1;
        }
        
        .file-count {
            color: #6c757d;
            font-size: 12px;
            margin-left: 4px;
        }
        
        .subfolder-toggle {
            transition: transform 0.2s ease;
            margin-left: 8px;
            font-size: 12px;
        }
        
        .subfolder-content {
            padding-left: 16px;
            margin-top: 4px;
        }
        
        .file-item { 
            padding: 8px 12px; 
            cursor: pointer; 
            border-radius: 6px; 
            margin: 2px 0; 
            transition: all 0.2s ease;
            border: 1px solid transparent;
            font-size: 14px;
            background: #fff;
            color: #000;
            position: relative;
            overflow: hidden;
        }
        .file-item:hover { 
            background: #f8f9fa;
            border-color: #e9ecef;
        }
        .file-item.active { 
            background: #7aa2f7;
            color: white; 
            box-shadow: 0 2px 8px rgba(122, 162, 247, 0.3);
            font-weight: 500;
        }
        

        
        /* 文件类型图标 */
        .file-item::before {
            content: "";
            font-size: 16px;
            margin-right: 8px;
            font-weight: bold;
        }
        .file-item.readme::before { content: "📖 "; }
        .file-item.basic-page::before { content: "🏠 "; }
        .file-item.main-content::before { content: "📝 "; }
        .file-item.ugfn::before { content: "🔬 "; }
        .file-item.ugfh::before { content: "🎨 "; }
        .file-item.misc::before { content: "🗂️ "; }
        .file-item.docs::before { content: "📋 "; }
        .file-item.uploads::before { content: "📁 "; }
        .file-item.backup::before { content: "🗄️ "; }
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
            color: #000;
            font-weight: 600;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            line-height: 1.4;
        }
        .preview p, .preview li {
            line-height: 1.8;
            color: #000;
            margin: 0.8em 0;
            word-break: break-word;
            word-wrap: break-word;
            font-size: 16px;
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
        
        /* Hugo Front Matter 样式 - 温和版本 */
        .preview .hugo-front-matter {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            padding: 12px 16px;
            margin: 16px 0;
            color: #495057;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
            font-size: 12px;
            line-height: 1.4;
            position: relative;
        }
        
        .preview .hugo-front-matter::before {
            content: "⚙️ Hugo配置";
            position: absolute;
            top: -8px;
            left: 12px;
            background: #f8f9fa;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            color: #667eea;
            border: 1px solid #e9ecef;
        }
        
        .preview .hugo-front-matter .fm-field {
            display: flex;
            margin: 4px 0;
            align-items: flex-start;
        }
        
        .preview .hugo-front-matter .fm-key {
            color: #495057;
            font-weight: 600;
            min-width: 80px;
            margin-right: 8px;
        }
        
        .preview .hugo-front-matter .fm-value {
            color: #6c757d;
            flex: 1;
        }
        
        .preview .hugo-front-matter .fm-array {
            color: #28a745;
        }
        
        .preview .hugo-front-matter .fm-string {
            color: #6f42c1;
        }
        
        .preview .hugo-front-matter .fm-boolean {
            color: #e83e8c;
        }
        
        .preview .hugo-front-matter .fm-date {
            color: #17a2b8;
        }
        .preview blockquote {
            border-left: 4px solid #dfe2e5;
            padding-left: 16px;
            margin: 16px 0;
            color: #333;
            font-style: italic;
            font-size: 16px;
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
    <!-- CodeMirror for markdown syntax highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/base16-light.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/markdown/markdown.min.js"></script>
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
        let codeMirrorEditor = null;
        
        // 初始化 CodeMirror
        window.addEventListener('load', function() {
            codeMirrorEditor = CodeMirror.fromTextArea(editor, {
                mode: 'markdown',
                lineNumbers: false,
                lineWrapping: true,
                theme: 'base16-light',
                styleActiveLine: true,
                matchBrackets: true,
                autoCloseBrackets: true,
                styleSelectedText: true,
                fontSize: 16,
                extraKeys: {
                    "Ctrl-S": function() { saveFile(); },
                    "Ctrl-R": function() { refreshFiles(); }
                }
            });
            
            codeMirrorEditor.on('change', function() {
                updatePreview();
            });
            
            // 设置编辑器字体大小
            codeMirrorEditor.getWrapperElement().style.fontSize = '16px';
            codeMirrorEditor.refresh();
        });
        
        // 文件分类函数
        function getFileCategory(filePath) {
            const file = filePath.toLowerCase();
            
            // README文件
            if (file.includes('readme')) {
                return 'readme';
            }
            
            // 基础页面
            if (file.includes('content/authors/') || 
                file.includes('content/info.md') || 
                file.includes('content/_index.md') || 
                file.includes('info.md') || 
                file.includes('archetypes/')) {
                return 'basic-page';
            }
            
            // 主要内容
            if (file.includes('content/main/')) {
                return 'main-content';
            }
            
            // UGFN课程
            if (file.includes('content/ugfn/') || file.includes('ugfn')) {
                return 'ugfn';
            }
            
            // UGFH课程
            if (file.includes('content/ugfh/') || file.includes('ugfh')) {
                return 'ugfh';
            }
            
            // 杂项内容
            if (file.includes('content/mess/') || file.includes('mess')) {
                return 'misc';
            }
            
            // 文档资料
            if (file.includes('docs/') || 
                file.includes('deployment') || 
                file.includes('test-')) {
                return 'docs';
            }
            
            // 上传文件
            if (file.includes('uploads/')) {
                return 'uploads';
            }
            
            // 备份文件
            if (file.includes('.backup/') || 
                file.includes('backup') || 
                file.includes('resource')) {
                return 'backup';
            }
            
            // 默认为文档类型
            return 'docs';
        }
        
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
            const markdown = codeMirrorEditor ? codeMirrorEditor.getValue() : editor.value;
            try {
                // 处理 Hugo Front Matter
                const processedMarkdown = processHugoFrontMatter(markdown);
                
                // 配置 marked 以更好地支持中文
                marked.setOptions({
                    breaks: true,  // 支持 GitHub 风格的换行
                    gfm: true,     // 启用 GitHub 风格的 Markdown
                });
                preview.innerHTML = marked.parse(processedMarkdown);
            } catch (error) {
                preview.innerHTML = '<p style="color: red;">预览解析错误: ' + error.message + '</p>';
            }
        }
        
        // 处理 Hugo Front Matter
        function processHugoFrontMatter(content) {
            // 检测 YAML Front Matter (---)
            const yamlMatch = content.match(/^---\\s*\\n([\\s\\S]*?)\\n---\\s*\\n([\\s\\S]*)$/);
            if (yamlMatch) {
                const frontMatter = yamlMatch[1];
                const markdownContent = yamlMatch[2];
                return renderFrontMatter(frontMatter, 'yaml') + '\\n\\n' + markdownContent;
            }
            
            // 检测 TOML Front Matter (+++)
            const tomlMatch = content.match(/^\\+\\+\\+\\s*\\n([\\s\\S]*?)\\n\\+\\+\\+\\s*\\n([\\s\\S]*)$/);
            if (tomlMatch) {
                const frontMatter = tomlMatch[1];
                const markdownContent = tomlMatch[2];
                return renderFrontMatter(frontMatter, 'toml') + '\\n\\n' + markdownContent;
            }
            
            // 检测 JSON Front Matter
            const jsonMatch = content.match(/^{([\\s\\S]*?)}\\s*\\n([\\s\\S]*)$/);
            if (jsonMatch) {
                const frontMatter = '{' + jsonMatch[1] + '}';
                const markdownContent = jsonMatch[2];
                return renderFrontMatter(frontMatter, 'json') + '\\n\\n' + markdownContent;
            }
            
            return content;
        }
        
        // 渲染 Front Matter
        function renderFrontMatter(frontMatter, type) {
            let html = '<div class="hugo-front-matter">';
            
            try {
                if (type === 'yaml') {
                    html += parseYamlFrontMatter(frontMatter);
                } else if (type === 'toml') {
                    html += '<pre>' + escapeHtml(frontMatter) + '</pre>';
                } else if (type === 'json') {
                    const parsed = JSON.parse(frontMatter);
                    html += formatJsonFrontMatter(parsed);
                }
            } catch (error) {
                html += '<pre>' + escapeHtml(frontMatter) + '</pre>';
            }
            
            html += '</div>';
            return html;
        }
        
        // 解析 YAML Front Matter
        function parseYamlFrontMatter(yaml) {
            const lines = yaml.split('\\n');
            let html = '';
            
            for (let line of lines) {
                line = line.trim();
                if (!line || line.startsWith('#')) continue;
                
                if (line.includes(':')) {
                    const [key, ...valueParts] = line.split(':');
                    const value = valueParts.join(':').trim();
                    
                    html += '<div class="fm-field">';
                    html += '<span class="fm-key">' + escapeHtml(key.trim()) + ':</span>';
                    html += '<span class="fm-value ' + getValueClass(value) + '">' + escapeHtml(value) + '</span>';
                    html += '</div>';
                } else if (line.startsWith('-')) {
                    html += '<div class="fm-field">';
                    html += '<span class="fm-key"></span>';
                    html += '<span class="fm-value fm-array">' + escapeHtml(line) + '</span>';
                    html += '</div>';
                } else {
                    html += '<div class="fm-field">';
                    html += '<span class="fm-value">' + escapeHtml(line) + '</span>';
                    html += '</div>';
                }
            }
            
            return html;
        }
        
        // 格式化 JSON Front Matter
        function formatJsonFrontMatter(obj, indent = 0) {
            let html = '';
            const spaces = '&nbsp;'.repeat(indent * 2);
            
            for (const [key, value] of Object.entries(obj)) {
                html += '<div class="fm-field">';
                html += '<span class="fm-key">' + spaces + escapeHtml(key) + ':</span>';
                
                if (Array.isArray(value)) {
                    html += '<span class="fm-value fm-array">[' + value.map(v => '"' + escapeHtml(String(v)) + '"').join(', ') + ']</span>';
                } else if (typeof value === 'object') {
                    html += '<span class="fm-value">{...}</span>';
                } else {
                    html += '<span class="fm-value ' + getValueClass(String(value)) + '">' + escapeHtml(String(value)) + '</span>';
                }
                html += '</div>';
            }
            
            return html;
        }
        
        // 获取值的CSS类
        function getValueClass(value) {
            if (!value) return '';
            
            const trimmed = value.trim().replace(/["']/g, '');
            
            if (trimmed === 'true' || trimmed === 'false') return 'fm-boolean';
            if (trimmed.match(/^\\d{4}-\\d{2}-\\d{2}/)) return 'fm-date';
            if (value.includes('"') || value.includes("'")) return 'fm-string';
            
            return '';
        }
        
        // HTML转义
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function loadFiles() {
            try {
                const response = await fetch('/api/files');
                const categorizedFiles = await response.json();
                const fileList = document.getElementById('fileList');
                fileList.innerHTML = '';
                
                // 渲染分类文件夹结构
                Object.entries(categorizedFiles).forEach(([mainCategory, subCategories]) => {
                    // 主分类标题
                    const mainCategoryDiv = document.createElement('div');
                    mainCategoryDiv.className = 'folder-main';
                    mainCategoryDiv.innerHTML = `
                        <div class="folder-header" onclick="toggleFolder(this)">
                            <span class="folder-icon">📂</span>
                            <span class="folder-title">${mainCategory}</span>
                            <span class="folder-toggle">▼</span>
                        </div>
                        <div class="folder-content">
                        </div>
                    `;
                    
                    const folderContent = mainCategoryDiv.querySelector('.folder-content');
                    
                    // 子分类
                    Object.entries(subCategories).forEach(([subCategory, files]) => {
                        if (files.length > 0) {
                            const subCategoryDiv = document.createElement('div');
                            subCategoryDiv.className = 'folder-sub';
                            subCategoryDiv.innerHTML = `
                                <div class="subfolder-header" onclick="toggleSubfolder(this)">
                                    <span class="subfolder-icon">📁</span>
                                    <span class="subfolder-title">${subCategory}</span>
                                    <span class="file-count">(${files.length})</span>
                                    <span class="subfolder-toggle">▼</span>
                                </div>
                                <div class="subfolder-content">
                                </div>
                            `;
                            
                            const subfolderContent = subCategoryDiv.querySelector('.subfolder-content');
                            
                            // 文件列表
                            files.forEach(filename => {
                                const fileItem = document.createElement('div');
                                fileItem.className = 'file-item';
                                fileItem.textContent = filename;
                                fileItem.onclick = () => loadFile(filename);
                                subfolderContent.appendChild(fileItem);
                            });
                            
                            folderContent.appendChild(subCategoryDiv);
                        }
                    });
                    
                    fileList.appendChild(mainCategoryDiv);
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
                
                if (codeMirrorEditor) {
                    codeMirrorEditor.setValue(content);
                } else {
                    editor.value = content;
                    editor.disabled = false;
                }
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
                const content = codeMirrorEditor ? codeMirrorEditor.getValue() : editor.value;
                const response = await fetch(`/api/save/${encodeURIComponent(currentFile)}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: content
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
        
        // 文件夹折叠展开功能
        function toggleFolder(header) {
            const folderMain = header.closest('.folder-main');
            const content = folderMain.querySelector('.folder-content');
            const toggle = header.querySelector('.folder-toggle');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                toggle.textContent = '▼';
            } else {
                content.style.display = 'none';
                toggle.textContent = '▶';
            }
        }
        
        function toggleSubfolder(header) {
            const folderSub = header.closest('.folder-sub');
            const content = folderSub.querySelector('.subfolder-content');
            const toggle = header.querySelector('.subfolder-toggle');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                toggle.textContent = '▼';
            } else {
                content.style.display = 'none';
                toggle.textContent = '▶';
            }
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
        """列出markdown文件并按文件夹分类"""
        md_files = []
        base_dir = Path('/root/cuhkstudy')
        
        for pattern in ['**/*.md', '**/*.markdown']:
            for file_path in base_dir.glob(pattern):
                rel_path = file_path.relative_to(base_dir)
                md_files.append(str(rel_path))
        
        # 创建分类结构
        categorized = {
            "📚 课程内容": {
                "🔬 UGFN课程": [],
                "🎨 UGFH课程": [],
                "🗂️ 杂项内容": []
            },
            "📂 基础文件": {
                "📖 README": [],
                "🏠 基础页面": []
            },
            "🏷️ 标签分类": {
                "🎯 主要内容 (Main)": [],
                "📚 UGFN标签": [],
                "🎨 UGFH标签": []
            }
        }
        
        # 分类文件
        for file_path in md_files:
            file_lower = file_path.lower()
            
            # 1. README 文件
            if 'readme' in file_lower:
                categorized["📂 基础文件"]["📖 README"].append(file_path)
                continue
                
            # 2. 基础页面 (authors, info等)
            if any(keyword in file_lower for keyword in ['author', 'info', '_index', 'about']):
                categorized["📂 基础文件"]["🏠 基础页面"].append(file_path)
                continue
            
            # 3. 读取文件内容检查标签
            try:
                full_path = base_dir / file_path
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查 Front Matter 中的标签
                if 'tags:' in content or 'categories:' in content:
                    # 主要内容标签
                    if '"Main"' in content or "'Main'" in content or '- Main' in content:
                        categorized["🏷️ 标签分类"]["🎯 主要内容 (Main)"].append(file_path)
                        continue
                    # UGFN标签
                    elif any(tag in content for tag in ['"UGFN"', "'UGFN'", '- UGFN', 'ugfn']):
                        categorized["🏷️ 标签分类"]["📚 UGFN标签"].append(file_path)
                        continue
                    # UGFH标签  
                    elif any(tag in content for tag in ['"UGFH"', "'UGFH'", '- UGFH', 'ugfh']):
                        categorized["🏷️ 标签分类"]["🎨 UGFH标签"].append(file_path)
                        continue
            except:
                pass
            
            # 4. 按路径分类课程内容
            if 'ugfn' in file_lower:
                categorized["📚 课程内容"]["🔬 UGFN课程"].append(file_path)
            elif 'ugfh' in file_lower:
                categorized["📚 课程内容"]["🎨 UGFH课程"].append(file_path)
            else:
                categorized["📚 课程内容"]["🗂️ 杂项内容"].append(file_path)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(categorized, ensure_ascii=False).encode('utf-8'))
    
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