#!/usr/bin/env python3
"""
CUHKstudy 系统健康检查脚本 v1.1
检查所有服务、功能和配置的状态
"""

import requests
import subprocess
import json
import os
import sqlite3
import time
from pathlib import Path

class SystemHealthChecker:
    def __init__(self):
        self.base_url = "http://localhost"
        self.results = {
            'services': {},
            'apis': {},
            'files': {},
            'cdn': {},
            'database': {},
            'overall_health': 'unknown'
        }
        
    def check_service_status(self, service_name):
        """检查systemd服务状态"""
        try:
            result = subprocess.run([
                'systemctl', 'is-active', service_name
            ], capture_output=True, text=True, timeout=10)
            
            return result.stdout.strip() == 'active'
        except:
            return False
            
    def check_service_health(self):
        """检查所有关键服务"""
        services = {
            'nginx': '网页服务器',
            'markdown-editor': 'Markdown编辑器',
            'reading-stats': '阅读统计服务'
        }
        
        print("🔍 检查系统服务状态...")
        for service, desc in services.items():
            status = self.check_service_status(service)
            self.results['services'][service] = {
                'status': 'running' if status else 'stopped',
                'description': desc,
                'healthy': status
            }
            print(f"  {'✅' if status else '❌'} {desc}: {'运行中' if status else '已停止'}")
            
    def check_api_endpoints(self):
        """检查所有API端点"""
        endpoints = {
            '/api/track': {'method': 'POST', 'data': {'url': '/test/', 'title': '健康检查'}},
            '/api/stats': {'method': 'GET'},
            '/api/popular': {'method': 'GET'},
            '/api/files': {'method': 'GET'}
        }
        
        print("\n🌐 检查API端点...")
        for endpoint, config in endpoints.items():
            try:
                if config['method'] == 'POST':
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=config.get('data', {}),
                        timeout=5
                    )
                else:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    
                healthy = response.status_code == 200
                self.results['apis'][endpoint] = {
                    'status_code': response.status_code,
                    'healthy': healthy,
                    'response_time': response.elapsed.total_seconds()
                }
                print(f"  {'✅' if healthy else '❌'} {endpoint}: {response.status_code}")
                
            except Exception as e:
                self.results['apis'][endpoint] = {
                    'status_code': 0,
                    'healthy': False,
                    'error': str(e)
                }
                print(f"  ❌ {endpoint}: 连接失败 - {e}")
                
    def check_file_access(self):
        """检查关键文件访问"""
        files = {
            '/js/reading-tracker.js': '阅读统计脚本',
            '/img/background-hd.png': '高清背景图',
            '/ugfn/': 'UGFN课程页面',
            '/zh-cn/': '中文主页'
        }
        
        print("\n📁 检查文件访问...")
        for file_path, desc in files.items():
            try:
                response = requests.get(f"{self.base_url}{file_path}", timeout=5)
                healthy = response.status_code == 200
                served_from = response.headers.get('X-Served-From', 'unknown')
                
                self.results['files'][file_path] = {
                    'status_code': response.status_code,
                    'healthy': healthy,
                    'served_from': served_from,
                    'size': len(response.content) if healthy else 0
                }
                print(f"  {'✅' if healthy else '❌'} {desc}: {response.status_code} ({served_from})")
                
            except Exception as e:
                self.results['files'][file_path] = {
                    'status_code': 0,
                    'healthy': False,
                    'error': str(e)
                }
                print(f"  ❌ {desc}: 连接失败")
                
    def check_database_health(self):
        """检查数据库状态"""
        db_path = "/root/cuhkstudy/data/reading_stats.db"
        
        print("\n🗄️ 检查数据库状态...")
        try:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 检查表结构
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # 检查数据量
                cursor.execute("SELECT COUNT(*) FROM reading_stats")
                record_count = cursor.fetchone()[0]
                
                conn.close()
                
                self.results['database'] = {
                    'exists': True,
                    'tables': tables,
                    'record_count': record_count,
                    'healthy': True
                }
                print(f"  ✅ 数据库正常: {record_count} 条记录")
            else:
                self.results['database'] = {
                    'exists': False,
                    'healthy': False
                }
                print("  ❌ 数据库文件不存在")
                
        except Exception as e:
            self.results['database'] = {
                'exists': False,
                'healthy': False,
                'error': str(e)
            }
            print(f"  ❌ 数据库检查失败: {e}")
            
    def check_cdn_performance(self):
        """检查CDN性能"""
        print("\n🚀 检查CDN性能...")
        
        # 检查R2连接
        try:
            response = requests.get(
                "https://447991a9c9d7dad31c67040315d483b2.r2.cloudflarestorage.com/cuhkstudy/",
                timeout=10
            )
            r2_healthy = response.status_code in [200, 403]  # 403是正常的，因为没有列表权限
            print(f"  {'✅' if r2_healthy else '❌'} Cloudflare R2连接: {response.status_code}")
            
            self.results['cdn']['r2_connection'] = {
                'healthy': r2_healthy,
                'status_code': response.status_code
            }
        except Exception as e:
            print(f"  ❌ R2连接失败: {e}")
            self.results['cdn']['r2_connection'] = {
                'healthy': False,
                'error': str(e)
            }
            
    def calculate_overall_health(self):
        """计算系统整体健康状态"""
        total_checks = 0
        passed_checks = 0
        
        # 统计各项检查结果
        for category in ['services', 'apis', 'files']:
            for item, result in self.results[category].items():
                total_checks += 1
                if result.get('healthy', False):
                    passed_checks += 1
                    
        # 数据库检查
        total_checks += 1
        if self.results['database'].get('healthy', False):
            passed_checks += 1
            
        # CDN检查
        if 'r2_connection' in self.results['cdn']:
            total_checks += 1
            if self.results['cdn']['r2_connection'].get('healthy', False):
                passed_checks += 1
                
        health_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        if health_score >= 90:
            overall_health = 'excellent'
            status_emoji = '🟢'
            status_text = '优秀'
        elif health_score >= 75:
            overall_health = 'good'
            status_emoji = '🟡'
            status_text = '良好'
        elif health_score >= 50:
            overall_health = 'warning'
            status_emoji = '🟠'
            status_text = '警告'
        else:
            overall_health = 'critical'
            status_emoji = '🔴'
            status_text = '严重'
            
        self.results['overall_health'] = overall_health
        self.results['health_score'] = health_score
        self.results['checks_passed'] = passed_checks
        self.results['total_checks'] = total_checks
        
        print(f"\n{status_emoji} 系统整体健康状态: {status_text} ({health_score:.1f}%)")
        print(f"   通过检查: {passed_checks}/{total_checks}")
        
    def generate_report(self):
        """生成详细报告"""
        report_path = "/root/cuhkstudy/system_health_report.json"
        
        report = {
            'timestamp': time.time(),
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': 'v1.1',
            'results': self.results
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print(f"\n📊 详细报告已保存到: {report_path}")
        return report_path
        
    def run_full_check(self):
        """运行完整的健康检查"""
        print("🏥 CUHKstudy 系统健康检查 v1.1")
        print("=" * 50)
        
        self.check_service_health()
        self.check_api_endpoints()
        self.check_file_access()
        self.check_database_health()
        self.check_cdn_performance()
        self.calculate_overall_health()
        
        report_path = self.generate_report()
        
        print("\n" + "=" * 50)
        print("✅ 健康检查完成！")
        
        return self.results['overall_health'], report_path

if __name__ == "__main__":
    checker = SystemHealthChecker()
    health_status, report_path = checker.run_full_check()
    
    # 根据健康状态设置退出码
    exit_codes = {
        'excellent': 0,
        'good': 0,
        'warning': 1,
        'critical': 2
    }
    
    exit(exit_codes.get(health_status, 1))