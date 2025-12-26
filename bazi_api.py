#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import tempfile
import os
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

def run_bazi_analysis(birth_date, birth_time="8", gender="男"):
    """
    运行八字分析
    
    Args:
        birth_date (str): 出生日期，格式：YYYY-MM-DD
        birth_time (str): 出生时辰，默认为8点
        gender (str): 性别，'男' 或 '女'，默认为'男'
    
    Returns:
        dict: 包含分析结果和可能的错误信息
    """
    try:
        # 构建命令
        cmd = ["python", "bazi.py", birth_date, birth_time, gender]
        
        # 运行命令并捕获输出
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        return {
            "success": True,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None,
            "return_code": result.returncode
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output": None,
            "return_code": -1
        }

def get_bazi_info(birth_date, birth_time="8", gender="男"):
    """
    获取八字信息（结构化返回）
    
    Args:
        birth_date (str): 出生日期，格式：YYYY-MM-DD
        birth_time (str): 出生时辰，默认为8点
        gender (str): 性别，'男' 或 '女'，默认为'男'
    
    Returns:
        dict: 八字分析结果
    """
    result = run_bazi_analysis(birth_date, birth_time, gender)
    
    if not result["success"]:
        return {
            "error": result["error"],
            "birth_info": {
                "date": birth_date,
                "time": birth_time,
                "gender": gender
            }
        }
    
    # 解析输出（这里可以根据需要进一步结构化输出）
    return {
        "birth_info": {
            "date": birth_date,
            "time": birth_time,
            "gender": gender
        },
        "analysis": result["output"],
        "raw_output": result["output"]
    }

def validate_date_format(date_str):
    """
    验证日期格式
    
    Args:
        date_str (str): 日期字符串
    
    Returns:
        bool: 是否为有效格式
    """
    try:
        year, month, day = date_str.split('-')
        year = int(year)
        month = int(month)
        day = int(day)
        
        if year < 1900 or year > 2100:
            return False
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
            
        return True
    except:
        return False

def validate_time(time_str):
    """
    验证时间格式
    
    Args:
        time_str (str): 时间字符串
    
    Returns:
        bool: 是否为有效格式
    """
    try:
        time_int = int(time_str)
        return 0 <= time_int <= 23
    except:
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python bazi_api.py <出生日期> [出生时辰] [性别]")
        print("例如: python bazi_api.py 1990-01-01 8 男")
        print("参数说明：")
        print("  出生日期: YYYY-MM-DD 格式")
        print("  出生时辰: 0-23的整数，默认为8")
        print("  性别: '男' 或 '女'，默认为'男'")
        sys.exit(1)
    
    birth_date = sys.argv[1]
    birth_time = sys.argv[2] if len(sys.argv) > 2 else "8"
    gender = sys.argv[3] if len(sys.argv) > 3 else "男"
    
    # 验证输入
    if not validate_date_format(birth_date):
        print("错误：日期格式不正确，请使用 YYYY-MM-DD 格式")
        sys.exit(1)
    
    if not validate_time(birth_time):
        print("错误：时辰格式不正确，请使用 0-23 的整数")
        sys.exit(1)
    
    if gender not in ["男", "女"]:
        print("错误：性别必须是 '男' 或 '女'")
        sys.exit(1)
    
    # 运行分析
    result = get_bazi_info(birth_date, birth_time, gender)
    
    if "error" in result:
        print(f"错误：{result['error']}")
    else:
        print(result["analysis"])