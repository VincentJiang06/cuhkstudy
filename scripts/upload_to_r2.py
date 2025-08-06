#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare R2 批量上传脚本
上传现有的PDF和图片文件到R2存储桶
"""

import os
import sys
import json
import mimetypes
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import hashlib

# 加载环境变量
load_dotenv()

# R2配置
R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID')
R2_ENDPOINT = os.getenv('R2_ENDPOINT')
R2_BUCKET = os.getenv('R2_BUCKET')
R2_ADMIN_ACCESS_KEY = os.getenv('R2_ADMIN_ACCESS_KEY')
R2_ADMIN_SECRET_KEY = os.getenv('R2_ADMIN_SECRET_KEY')

def get_r2_client():
    """创建R2 S3客户端"""
    return boto3.client(
        's3',
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ADMIN_ACCESS_KEY,
        aws_secret_access_key=R2_ADMIN_SECRET_KEY,
        region_name='auto'
    )

def calculate_md5(file_path):
    """计算文件MD5"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_relative_key(file_path, base_path="/var/www/cuhkstudy"):
    """获取相对路径作为R2对象键"""
    return str(Path(file_path).relative_to(base_path))

def upload_single_file(args):
    """上传单个文件"""
    file_path, s3_client = args
    
    try:
        # 获取文件信息
        key = get_relative_key(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        file_size = os.path.getsize(file_path)
        
        print(f"上传: {file_path} -> s3://{R2_BUCKET}/{key}")
        
        # 上传文件
        with open(file_path, 'rb') as f:
            s3_client.put_object(
                Bucket=R2_BUCKET,
                Key=key,
                Body=f,
                ContentType=content_type,
                ACL='public-read'  # 设置为公共可读
            )
        
        # 生成公共URL
        public_url = f"{R2_ENDPOINT}/{R2_BUCKET}/{key}"
        
        return {
            'success': True,
            'local_path': file_path,
            'r2_key': key,
            'public_url': public_url,
            'size': file_size,
            'content_type': content_type
        }
        
    except Exception as e:
        return {
            'success': False,
            'local_path': file_path,
            'error': str(e)
        }

def main():
    print("🚀 开始批量上传文件到 Cloudflare R2...")
    
    # 检查环境变量
    if not all([R2_ACCOUNT_ID, R2_ENDPOINT, R2_BUCKET, R2_ADMIN_ACCESS_KEY, R2_ADMIN_SECRET_KEY]):
        print("❌ 缺少必要的环境变量，请检查 .env 文件")
        sys.exit(1)
    
    # 读取文件列表
    files_list_path = 'files_to_upload.txt'
    if not os.path.exists(files_list_path):
        print(f"❌ 找不到文件列表: {files_list_path}")
        sys.exit(1)
    
    with open(files_list_path, 'r') as f:
        files_to_upload = [line.strip() for line in f if line.strip()]
    
    print(f"📁 找到 {len(files_to_upload)} 个文件需要上传")
    
    # 创建S3客户端
    s3_client = get_r2_client()
    
    # 测试连接
    try:
        s3_client.head_bucket(Bucket=R2_BUCKET)
        print(f"✅ 成功连接到 R2 存储桶: {R2_BUCKET}")
    except ClientError as e:
        print(f"❌ 无法连接到 R2: {e}")
        sys.exit(1)
    
    # 并发上传
    upload_results = []
    failed_uploads = []
    
    print(f"🔄 开始上传，使用 10 个并发线程...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 为每个文件创建参数元组
        upload_args = [(file_path, get_r2_client()) for file_path in files_to_upload]
        
        # 提交所有任务
        future_to_file = {executor.submit(upload_single_file, args): args[0] for args in upload_args}
        
        # 处理结果
        for future in concurrent.futures.as_completed(future_to_file):
            result = future.result()
            upload_results.append(result)
            
            if result['success']:
                print(f"✅ {result['local_path']} -> {result['public_url']}")
            else:
                print(f"❌ {result['local_path']}: {result['error']}")
                failed_uploads.append(result)
    
    # 生成上传映射表
    successful_uploads = [r for r in upload_results if r['success']]
    
    mapping = {}
    for result in successful_uploads:
        mapping[result['local_path']] = {
            'r2_key': result['r2_key'],
            'public_url': result['public_url'],
            'size': result['size'],
            'content_type': result['content_type']
        }
    
    # 保存结果
    with open('upload_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    # 保存失败列表
    if failed_uploads:
        with open('failed_uploads.json', 'w', encoding='utf-8') as f:
            json.dump(failed_uploads, f, indent=2, ensure_ascii=False)
    
    # 输出统计
    print(f"\n📊 上传完成统计:")
    print(f"   ✅ 成功: {len(successful_uploads)} 个文件")
    print(f"   ❌ 失败: {len(failed_uploads)} 个文件")
    print(f"   📝 映射表已保存到: upload_mapping.json")
    
    if failed_uploads:
        print(f"   ⚠️  失败列表已保存到: failed_uploads.json")
    
    # 计算总大小
    total_size = sum(r['size'] for r in successful_uploads)
    print(f"   📦 总上传大小: {total_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()