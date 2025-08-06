#!/usr/bin/env python3
"""
设置Cloudflare R2公共访问权限
"""

import boto3
import json
from botocore.exceptions import ClientError

def setup_r2_public_access():
    """设置R2 bucket的公共读取权限"""
    
    # R2配置
    endpoint_url = "https://447991a9c9d7dad31c67040315d483b2.r2.cloudflarestorage.com"
    bucket_name = "cuhkstudy"
    
    # 从环境变量或配置文件读取凭据
    try:
        with open('/root/cuhkstudy/.env', 'r') as f:
            env_content = f.read()
            
        # 解析环境变量
        env_vars = {}
        for line in env_content.split('\n'):
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key] = value
                
        access_key = env_vars.get('R2_ADMIN_ACCESS_KEY')
        secret_key = env_vars.get('R2_ADMIN_SECRET_KEY')
        
        if not access_key or not secret_key:
            print("❌ 无法找到R2管理员凭据")
            return False
            
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False
    
    # 创建S3客户端
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'
        )
        
        print("✅ S3客户端创建成功")
        
    except Exception as e:
        print(f"❌ 创建S3客户端失败: {e}")
        return False
    
    # 设置bucket策略以允许公共读取
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    
    try:
        # 应用bucket策略
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("✅ R2 bucket公共访问策略设置成功")
        
        # 验证策略
        response = s3_client.get_bucket_policy(Bucket=bucket_name)
        print("📋 当前bucket策略:")
        policy = json.loads(response['Policy'])
        print(json.dumps(policy, indent=2, ensure_ascii=False))
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NotImplemented':
            print("⚠️  Cloudflare R2可能不支持bucket策略")
            print("💡 请在Cloudflare控制台中手动设置公共访问权限")
            return False
        else:
            print(f"❌ 设置bucket策略失败: {e}")
            return False
    
    except Exception as e:
        print(f"❌ 设置过程中出现错误: {e}")
        return False

def test_public_access():
    """测试公共访问"""
    import requests
    
    test_urls = [
        "https://447991a9c9d7dad31c67040315d483b2.r2.cloudflarestorage.com/cuhkstudy/pdfs/UGFN AI GUIDE V2.1.pdf",
        "https://447991a9c9d7dad31c67040315d483b2.r2.cloudflarestorage.com/cuhkstudy/img/CU_pic.png"
    ]
    
    print("\n🧪 测试公共访问:")
    for url in test_urls:
        try:
            response = requests.head(url, timeout=10)
            print(f"  {'✅' if response.status_code == 200 else '❌'} {url.split('/')[-1]}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {url.split('/')[-1]}: 连接失败 - {e}")

if __name__ == "__main__":
    print("🔧 设置Cloudflare R2公共访问权限")
    print("=" * 50)
    
    if setup_r2_public_access():
        test_public_access()
        print("\n💡 如果仍然无法访问，请：")
        print("1. 在Cloudflare控制台中设置R2 bucket为公共访问")
        print("2. 或设置自定义域名")
    else:
        print("\n📖 手动设置指南:")
        print("1. 登录Cloudflare控制台")
        print("2. 进入R2存储 > cuhkstudy bucket")
        print("3. 设置 > 公共访问 > 启用")
        print("4. 或配置自定义域名映射")