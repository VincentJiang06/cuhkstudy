#!/usr/bin/env python3
"""
CUHKstudy 阅读量统计服务
轻量级、隐私友好的阅读量统计系统
"""

import json
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading

class ReadingStatsServer:
    def __init__(self, db_path="/root/cuhkstudy/data/reading_stats.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
        
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建阅读统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reading_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_url TEXT NOT NULL,
                page_title TEXT,
                visitor_hash TEXT,
                timestamp INTEGER,
                user_agent TEXT,
                referrer TEXT
            )
        ''')
        
        # 创建页面统计视图
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS page_views AS
            SELECT 
                page_url,
                page_title,
                COUNT(*) as total_views,
                COUNT(DISTINCT visitor_hash) as unique_visitors,
                MAX(timestamp) as last_visit,
                MIN(timestamp) as first_visit
            FROM reading_stats 
            GROUP BY page_url
        ''')
        
        conn.commit()
        conn.close()
        
    def get_visitor_hash(self, ip, user_agent):
        """生成访客hash（隐私保护）"""
        # 使用IP+User-Agent生成hash，不存储原始信息
        data = f"{ip[:12]}{user_agent[:50]}"  # 只取部分信息
        return hashlib.md5(data.encode()).hexdigest()[:12]
        
    def record_view(self, page_url, page_title="", visitor_ip="", user_agent="", referrer=""):
        """记录页面访问"""
        visitor_hash = self.get_visitor_hash(visitor_ip, user_agent)
        timestamp = int(time.time())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reading_stats 
            (page_url, page_title, visitor_hash, timestamp, user_agent, referrer)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (page_url, page_title, visitor_hash, timestamp, user_agent, referrer))
        
        conn.commit()
        conn.close()
        
    def get_page_stats(self, page_url=None):
        """获取页面统计数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if page_url:
            cursor.execute('SELECT * FROM page_views WHERE page_url = ?', (page_url,))
            result = cursor.fetchone()
            if result:
                return {
                    'page_url': result[0],
                    'page_title': result[1],
                    'total_views': result[2],
                    'unique_visitors': result[3],
                    'last_visit': result[4],
                    'first_visit': result[5]
                }
        else:
            cursor.execute('SELECT * FROM page_views ORDER BY total_views DESC')
            results = cursor.fetchall()
            return [{
                'page_url': row[0],
                'page_title': row[1],
                'total_views': row[2],
                'unique_visitors': row[3],
                'last_visit': row[4],
                'first_visit': row[5]
            } for row in results]
            
        conn.close()
        return None
        
    def get_popular_pages(self, limit=10):
        """获取热门页面"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT page_url, page_title, total_views, unique_visitors
            FROM page_views 
            ORDER BY total_views DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'url': row[0],
            'title': row[1],
            'views': row[2],
            'unique': row[3]
        } for row in results]

class StatsHandler(BaseHTTPRequestHandler):
    def __init__(self, stats_server, *args, **kwargs):
        self.stats_server = stats_server
        super().__init__(*args, **kwargs)
        
    def log_message(self, format, *args):
        """禁用默认日志输出，避免BrokenPipe错误"""
        return
        
    def do_POST(self):
        """处理阅读量记录请求"""
        if self.path.startswith('/api/track'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # 记录访问
                self.stats_server.record_view(
                    page_url=data.get('url', ''),
                    page_title=data.get('title', ''),
                    visitor_ip=self.client_address[0],
                    user_agent=self.headers.get('User-Agent', ''),
                    referrer=self.headers.get('Referer', '')
                )
                
                # 返回成功响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                response = {'status': 'success', 'message': '阅读记录已保存'}
                try:
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except BrokenPipeError:
                    pass  # 客户端断开连接，忽略错误
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_GET(self):
        """处理统计数据查询"""
        if self.path.startswith('/api/stats'):
            # 解析查询参数
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            
            page_url = params.get('url', [None])[0]
            
            try:
                if page_url:
                    stats = self.stats_server.get_page_stats(page_url)
                else:
                    stats = self.stats_server.get_page_stats()
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                try:
                    self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
                except BrokenPipeError:
                    pass
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
        elif self.path.startswith('/api/popular'):
            try:
                popular = self.stats_server.get_popular_pages()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                try:
                    self.wfile.write(json.dumps(popular, ensure_ascii=False).encode('utf-8'))
                except BrokenPipeError:
                    pass
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_stats_server(port=8889):
    """启动统计服务"""
    stats_server = ReadingStatsServer()
    
    def handler(*args, **kwargs):
        StatsHandler(stats_server, *args, **kwargs)
    
    httpd = HTTPServer(('localhost', port), handler)
    print(f"📊 阅读统计服务启动在端口 {port}")
    print(f"📈 API端点:")
    print(f"   POST /api/track - 记录阅读")
    print(f"   GET /api/stats?url=xxx - 查询统计")
    print(f"   GET /api/popular - 热门页面")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n📊 统计服务已停止")
        httpd.shutdown()

if __name__ == "__main__":
    start_stats_server()