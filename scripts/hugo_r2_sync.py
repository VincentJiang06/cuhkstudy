#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hugo R2 同步脚本
在Hugo构建后，自动将静态资源同步到R2
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def run_command(cmd, cwd=None):
    """运行shell命令"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {cmd}")
        print(f"错误: {e.stderr}")
        return None

def sync_to_r2():
    """同步Hugo public目录到R2"""
    print("🚀 开始同步Hugo静态文件到R2...")
    
    # 检查环境变量
    endpoint = os.getenv('R2_ENDPOINT')
    bucket = os.getenv('R2_BUCKET')
    
    if not endpoint or not bucket:
        print("❌ 缺少R2环境变量")
        return False
    
    # 确保public目录存在
    public_dir = "/var/www/cuhkstudy/public"
    if not os.path.exists(public_dir):
        print(f"❌ Hugo public目录不存在: {public_dir}")
        return False
    
    # 只同步静态资源文件
    sync_patterns = [
        "*.pdf",
        "*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp", "*.svg", "*.ico",
        "*.woff", "*.woff2", "*.ttf", "*.eot",
        "*.mp3", "*.mp4", "*.wav", "*.ogg"
    ]
    
    success_count = 0
    total_count = 0
    
    for pattern in sync_patterns:
        print(f"🔄 同步 {pattern} 文件...")
        
        # 查找匹配的文件
        find_cmd = f"find {public_dir} -name '{pattern}' -type f"
        files = run_command(find_cmd)
        
        if not files:
            continue
            
        file_list = files.split('\n')
        total_count += len(file_list)
        
        # 使用AWS CLI批量上传
        for file_path in file_list:
            # 计算相对路径作为S3 key
            rel_path = os.path.relpath(file_path, "/var/www/cuhkstudy")
            
            upload_cmd = f"""aws s3 cp "{file_path}" "s3://{bucket}/{rel_path}" \
                --profile r2-cuhkstudy \
                --endpoint-url {endpoint} \
                --content-type "$(file -b --mime-type '{file_path}')" \
                --cache-control "public, max-age=2592000" \
                --acl public-read"""
            
            if run_command(upload_cmd):
                success_count += 1
                print(f"  ✅ {rel_path}")
            else:
                print(f"  ❌ {rel_path}")
    
    print(f"\n📊 同步完成: {success_count}/{total_count} 个文件")
    return success_count == total_count

def update_hugo_config():
    """更新Hugo配置以支持R2 CDN"""
    print("🔧 更新Hugo配置...")
    
    hugo_config = "/var/www/cuhkstudy/hugo.toml"
    
    # 读取现有配置
    if os.path.exists(hugo_config):
        with open(hugo_config, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # 添加R2 CDN配置
    r2_config = f"""
# Cloudflare R2 CDN配置
[params.cdn]
enabled = true
r2_endpoint = "{os.getenv('R2_ENDPOINT')}"
r2_bucket = "{os.getenv('R2_BUCKET')}"
r2_base_url = "{os.getenv('R2_ENDPOINT')}/{os.getenv('R2_BUCKET')}"

# 资源URL前缀
[params.assets]
image_prefix = "/img/"
pdf_prefix = "/pdfs/"
audio_prefix = "/audio/"
"""
    
    # 如果配置中没有CDN部分，则添加
    if "[params.cdn]" not in content:
        content += r2_config
        
        with open(hugo_config, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Hugo配置已更新")
    else:
        print("ℹ️  Hugo配置已包含CDN设置")
    
    return True

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--build":
        print("🏗️  构建Hugo站点...")
        os.chdir("/root/cuhkstudy")
        
        # 构建Hugo
        if not run_command("hugo --minify --cleanDestinationDir"):
            print("❌ Hugo构建失败")
            return 1
        
        print("✅ Hugo构建完成")
    
    # 更新配置
    if not update_hugo_config():
        return 1
    
    # 同步到R2
    if not sync_to_r2():
        return 1
    
    print("🎉 所有操作完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main())