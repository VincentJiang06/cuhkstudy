#!/usr/bin/env python3
"""
优化的CDN上传脚本 - 只上传大文件，排除字体和PDF.js
"""
import os
import boto3
from pathlib import Path

def upload_large_files_only():
    """只上传大图片和PDF文件到CDN"""
    
    # 配置
    s3_client = boto3.client(
        's3',
        endpoint_url='https://447991a9c9d7dad31c67040315d483b2.r2.cloudflarestorage.com',
        aws_access_key_id='15f81283b1e9092dc433661173e17caa',
        aws_secret_access_key='0a92b00e366dcd0923743da7c8e5b4680d83af1b45cfa114160a77309aafeb79',
        region_name='auto'
    )
    
    bucket_name = 'cuhkstudy'
    base_path = Path('/var/www/cuhkstudy/public')
    
    # 要上传的文件类型和大小限制
    upload_rules = [
        {'pattern': '*.png', 'min_size': 1024*1024},  # PNG > 1MB
        {'pattern': '*.jpg', 'min_size': 500*1024},   # JPG > 500KB  
        {'pattern': '*.jpeg', 'min_size': 500*1024},  # JPEG > 500KB
        {'pattern': '*.pdf', 'min_size': 0},          # 所有PDF
    ]
    
    uploaded_files = []
    
    for rule in upload_rules:
        pattern = rule['pattern']
        min_size = rule['min_size']
        
        for file_path in base_path.rglob(pattern):
            # 跳过PDF.js相关文件
            if 'pdfjs' in str(file_path):
                continue
                
            file_size = file_path.stat().st_size
            if file_size >= min_size:
                relative_path = file_path.relative_to(base_path)
                s3_key = str(relative_path)
                
                try:
                    s3_client.upload_file(
                        str(file_path), 
                        bucket_name, 
                        s3_key,
                        ExtraArgs={'ContentType': get_content_type(file_path)}
                    )
                    uploaded_files.append({
                        'file': s3_key,
                        'size': f"{file_size/1024/1024:.1f}MB"
                    })
                    print(f"✅ 已上传: {s3_key} ({file_size/1024/1024:.1f}MB)")
                except Exception as e:
                    print(f"❌ 上传失败: {s3_key} - {e}")
    
    print(f"\n📊 上传总结: 共上传 {len(uploaded_files)} 个大文件")
    total_size = sum(float(f['size'].replace('MB', '')) for f in uploaded_files)
    print(f"📁 总大小: {total_size:.1f}MB")
    
    return uploaded_files

def get_content_type(file_path):
    """获取文件MIME类型"""
    suffix = file_path.suffix.lower()
    content_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg', 
        '.jpeg': 'image/jpeg',
        '.pdf': 'application/pdf'
    }
    return content_types.get(suffix, 'application/octet-stream')

if __name__ == "__main__":
    upload_large_files_only()
