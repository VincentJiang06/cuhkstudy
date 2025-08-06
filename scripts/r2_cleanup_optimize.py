#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R2 CDN 清理和优化脚本
1. 清理冗余文件
2. 只保留真正需要CDN加速的大文件
3. 去重相同文件
4. 优化文件组织结构
"""

import os
import sys
import json
import subprocess
import hashlib
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

R2_ENDPOINT = os.getenv('R2_ENDPOINT')
R2_BUCKET = os.getenv('R2_BUCKET')

def run_aws_cmd(cmd):
    """执行AWS CLI命令"""
    full_cmd = f"{cmd} --profile r2-cuhkstudy --endpoint-url {R2_ENDPOINT}"
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令失败: {cmd}")
        print(f"错误: {e.stderr}")
        return None

def get_file_size(file_path):
    """获取文件大小(MB)"""
    try:
        return os.path.getsize(file_path) / 1024 / 1024
    except:
        return 0

def calculate_md5(file_path):
    """计算文件MD5"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def clean_r2_bucket():
    """清理R2存储桶中的冗余文件"""
    print("🧹 开始清理R2存储桶...")
    
    # 获取所有文件列表
    list_cmd = f"aws s3 ls s3://{R2_BUCKET}/ --recursive"
    files_output = run_aws_cmd(list_cmd)
    
    if not files_output:
        print("❌ 无法获取R2文件列表")
        return False
    
    # 需要删除的路径模式
    delete_patterns = [
        "resource/",      # 弃用目录
        "resources/",     # 弃用目录  
        "Uploads/",       # 用户上传目录，不需要CDN
        "themes/blowfish/exampleSite/",  # 示例文件
        "themes/blowfish/assets/",       # 主题资源
        "themes/blowfish/static/",       # 主题静态文件
        "content/",       # 内容源文件
    ]
    
    files_to_delete = []
    
    for line in files_output.split('\n'):
        if not line.strip():
            continue
        
        # 解析文件信息
        parts = line.split()
        if len(parts) < 4:
            continue
            
        file_key = parts[3]
        
        # 检查是否需要删除
        should_delete = False
        for pattern in delete_patterns:
            if file_key.startswith(pattern):
                should_delete = True
                break
        
        # 检查小文件 (< 100KB)
        if not should_delete:
            file_size_bytes = int(parts[2])
            if file_size_bytes < 100 * 1024:  # 小于100KB
                # 只保留PDF文件，删除小图标等
                if not file_key.endswith('.pdf'):
                    should_delete = True
        
        if should_delete:
            files_to_delete.append(file_key)
    
    print(f"📋 发现 {len(files_to_delete)} 个文件需要删除")
    
    # 批量删除
    if files_to_delete:
        print("🗑️  开始批量删除文件...")
        
        # 每次删除1000个文件
        batch_size = 1000
        for i in range(0, len(files_to_delete), batch_size):
            batch = files_to_delete[i:i+batch_size]
            
            # 创建删除清单文件
            delete_list = "delete-list.json"
            delete_objects = {
                "Objects": [{"Key": key} for key in batch],
                "Quiet": True
            }
            
            with open(delete_list, 'w') as f:
                json.dump(delete_objects, f)
            
            # 执行删除
            delete_cmd = f"aws s3api delete-objects --bucket {R2_BUCKET} --delete file://{delete_list}"
            if run_aws_cmd(delete_cmd):
                print(f"  ✅ 删除了 {len(batch)} 个文件")
            else:
                print(f"  ❌ 删除失败")
            
            # 清理临时文件
            os.remove(delete_list)
    
    print("✅ R2清理完成")
    return True

def find_large_files():
    """查找需要CDN的大文件"""
    print("🔍 分析需要CDN的大文件...")
    
    target_dirs = [
        "/var/www/cuhkstudy/static",
        "/var/www/cuhkstudy/assets", 
        "/var/www/cuhkstudy/public"
    ]
    
    large_files = []
    duplicates = defaultdict(list)
    
    for base_dir in target_dirs:
        if not os.path.exists(base_dir):
            continue
            
        print(f"📂 扫描 {base_dir}")
        
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = get_file_size(file_path)
                
                # 只处理大文件或PDF
                if file_size > 0.1 or file.endswith(('.pdf', '.PDF')):  # >100KB 或 PDF
                    file_md5 = calculate_md5(file_path)
                    if file_md5:
                        rel_path = os.path.relpath(file_path, "/var/www/cuhkstudy")
                        
                        large_files.append({
                            'path': file_path,
                            'rel_path': rel_path,
                            'size_mb': file_size,
                            'md5': file_md5,
                            'ext': Path(file).suffix.lower()
                        })
                        
                        duplicates[file_md5].append(rel_path)
    
    # 输出重复文件报告
    print("\n📊 重复文件分析:")
    for md5, paths in duplicates.items():
        if len(paths) > 1:
            print(f"  🔄 MD5: {md5[:8]}... 有 {len(paths)} 个副本:")
            for path in paths:
                print(f"    - {path}")
    
    return large_files, duplicates

def create_optimized_upload_list(large_files, duplicates):
    """创建优化的上传列表"""
    print("📝 创建优化上传策略...")
    
    upload_list = []
    processed_md5 = set()
    
    # 优先级规则
    priority_order = [
        'static/',      # 最高优先级
        'assets/',      # 次优先级  
        'public/',      # 最低优先级
    ]
    
    for file_info in large_files:
        md5 = file_info['md5']
        
        # 跳过已处理的重复文件
        if md5 in processed_md5:
            continue
        
        # 对于重复文件，选择最优路径
        if len(duplicates[md5]) > 1:
            best_path = None
            best_priority = 999
            
            for dup_path in duplicates[md5]:
                for i, prefix in enumerate(priority_order):
                    if dup_path.startswith(prefix):
                        if i < best_priority:
                            best_priority = i
                            best_path = dup_path
                        break
            
            if best_path:
                # 找到对应的file_info
                for f in large_files:
                    if f['rel_path'] == best_path:
                        upload_list.append(f)
                        processed_md5.add(md5)
                        break
        else:
            upload_list.append(file_info)
            processed_md5.add(md5)
    
    return upload_list

def upload_optimized_files(upload_list):
    """上传优化后的文件列表"""
    print(f"📤 开始上传 {len(upload_list)} 个优化文件...")
    
    success_count = 0
    total_size = 0
    
    for file_info in upload_list:
        file_path = file_info['path']
        rel_path = file_info['rel_path']
        size_mb = file_info['size_mb']
        
        # 优化S3 key路径
        s3_key = rel_path
        if s3_key.startswith('public/'):
            s3_key = s3_key[7:]  # 去掉 public/ 前缀
        
        print(f"📤 {file_path} -> s3://{R2_BUCKET}/{s3_key} ({size_mb:.2f}MB)")
        
        upload_cmd = f"""aws s3 cp "{file_path}" "s3://{R2_BUCKET}/{s3_key}" \
            --content-type "$(file -b --mime-type '{file_path}')" \
            --cache-control "public, max-age=31536000" \
            --acl public-read"""
        
        if run_aws_cmd(upload_cmd):
            success_count += 1
            total_size += size_mb
        else:
            print(f"  ❌ 上传失败: {rel_path}")
    
    print(f"\n📊 上传统计:")
    print(f"  ✅ 成功: {success_count}/{len(upload_list)} 个文件")
    print(f"  📦 总大小: {total_size:.2f} MB")
    
    return success_count == len(upload_list)

def clean_deprecated_dirs():
    """清理本地弃用目录"""
    print("🗂️  清理本地弃用目录...")
    
    deprecated_dirs = [
        "/var/www/cuhkstudy/resource",
        "/var/www/cuhkstudy/resources", 
        "/root/cuhkstudy/resource",
        "/root/cuhkstudy/resources"
    ]
    
    for dir_path in deprecated_dirs:
        if os.path.exists(dir_path):
            print(f"🗑️  删除目录: {dir_path}")
            # 先移动到临时位置，确认后再删除
            backup_path = f"{dir_path}.backup"
            os.rename(dir_path, backup_path)
            print(f"  📁 已移动到: {backup_path}")
            print(f"  ⚠️  请确认无问题后手动删除: rm -rf {backup_path}")

def main():
    """主函数"""
    print("🚀 开始R2 CDN优化...")
    
    # 1. 清理R2存储桶
    if not clean_r2_bucket():
        return 1
    
    # 2. 分析本地大文件
    large_files, duplicates = find_large_files()
    
    # 3. 创建优化上传列表
    upload_list = create_optimized_upload_list(large_files, duplicates)
    
    # 4. 上传优化文件
    if not upload_optimized_files(upload_list):
        return 1
    
    # 5. 清理弃用目录
    clean_deprecated_dirs()
    
    # 6. 生成最终报告
    print("\n🎉 优化完成!")
    print("📋 下一步建议:")
    print("  1. 测试网站功能是否正常")
    print("  2. 确认弃用目录备份后删除")
    print("  3. 更新nginx配置以匹配新的文件结构")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())