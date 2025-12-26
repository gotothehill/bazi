#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import subprocess
import sys
import datetime
import os
import re

def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖...")
    try:
        import lunar_python
        print("✓ lunar_python 已安装")
        return True
    except ImportError:
        print("✗ lunar_python 未安装")
        print("请运行: pip install lunar-python")
        return False

def clean_ansi_codes(text):
    """清理ANSI颜色控制字符"""
    # 匹配ANSI转义序列的正则表达式
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

def save_bazi_result(result):
    """保存八字分析结果到MD文件"""
    try:
        # 创建输出目录
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成文件名
        birth_info = result['birth_info']
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bazi_analysis_{birth_info['date']}_{birth_info['time']}_{birth_info['gender']}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)
        
        # 清理分析结果中的ANSI颜色代码
        clean_analysis = clean_ansi_codes(result['analysis'])
        
        # 构建MD内容
        md_content = f"""# 八字分析报告

## 基本信息
- **出生日期**: {birth_info['date']}
- **出生时辰**: {birth_info['time']}点
- **性别**: {birth_info['gender']}
- **分析时间**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 详细分析

```
{clean_analysis}
```

---
*本报告由八字分析API生成*
"""
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✓ 八字分析结果已保存到: {filepath}")
        
    except Exception as e:
        print(f"✗ 保存八字分析结果失败: {e}")

def test_bazi_script():
    """直接测试bazi.py脚本"""
    print("\n直接测试 bazi.py 脚本:")
    try:
        import platform
        if platform.system() == "Windows":
            python_cmd = "python"
        else:
            python_cmd = "python3"
            
        # 使用与API服务相同的日期格式测试
        birth_date = "1990-01-01"
        year, month, day = birth_date.split('-')
        result = subprocess.run([python_cmd, "bazi.py", year, month, day, "8"], 
                               capture_output=True, text=True, encoding='gbk', errors='ignore')
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"输出长度: {len(result.stdout)} 字符")
            print(f"前100字符: {result.stdout[:100]}...")
        if result.stderr:
            print(f"错误: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_api():
    """测试API服务"""
    base_url = "http://localhost:5000"
    
    print("=" * 50)
    print("测试API服务")
    print("=" * 50)
    
    # 测试健康检查
    print("\n1. 测试健康检查:")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试首页
    print("\n2. 测试API首页:")
    try:
        response = requests.get(f"{base_url}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试生肖分析
    print("\n3. 测试生肖分析:")
    shengxiao_data = {"shengxiao": "鼠"}
    try:
        response = requests.post(
            f"{base_url}/api/shengxiao",
            json=shengxiao_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试八字分析
    print("\n4. 测试八字分析:")
    bazi_data = {
        "birth_date": "1990-01-01",
        "birth_time": "8",
        "gender": "男"
    }
    try:
        response = requests.post(
            f"{base_url}/api/bazi",
            json=bazi_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"出生信息: {json.dumps(result['birth_info'], ensure_ascii=False)}")
            print("分析结果:")
            if result['analysis'] and len(result['analysis']) > 0:
                print(result['analysis'][:500] + "..." if len(result['analysis']) > 500 else result['analysis'])
                
                # 保存完整的八字分析结果到MD文件
                save_bazi_result(result)
            else:
                print("分析结果为空")
        else:
            print(f"错误响应: {response.json()}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试错误输入
    print("\n5. 测试错误输入:")
    
    # 错误的生肖
    print("\n5.1 错误的生肖:")
    try:
        response = requests.post(
            f"{base_url}/api/shengxiao",
            json={"shengxiao": "无效生肖"},
            headers={'Content-Type': 'application/json'}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 错误的日期格式
    print("\n5.2 错误的日期格式:")
    try:
        response = requests.post(
            f"{base_url}/api/bazi",
            json={"birth_date": "1990/01/01"},
            headers={'Content-Type': 'application/json'}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    # 首先检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 测试脚本
    if not test_bazi_script():
        print("bazi.py 脚本测试失败，请检查依赖")
        sys.exit(1)
    
    print("\n请确保API服务已启动 (python api_server.py)")
    input("按回车键开始测试...")
    test_api()