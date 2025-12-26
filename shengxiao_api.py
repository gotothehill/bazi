#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io
from contextlib import redirect_stdout
from datas import shengxiaos, zhi_atts

def get_shengxiao_info(shengxiao):
    """
    获取生肖信息
    
    Args:
        shengxiao (str): 生肖名称
    
    Returns:
        dict: 包含生肖信息的字典
    """
    if shengxiao not in shengxiaos.inverse:
        return {
            "error": "请输入正确的生肖",
            "valid_shengxiaos": list(shengxiaos.inverse.keys())
        }
    
    zhi = shengxiaos.inverse[shengxiao]
    
    # 构建结果字典
    result = {
        "shengxiao": shengxiao,
        "year_zhi": zhi,
        "compatible": {
            "sanhe": [shengxiaos[item] for item in zhi_atts[zhi]['合']],
            "liuhe": [shengxiaos[item] for item in zhi_atts[zhi]['六']],
            "sanhui": [shengxiaos[item] for item in zhi_atts[zhi]['会']]
        },
        "incompatible": {
            "chong": [shengxiaos[item] for item in zhi_atts[zhi]['冲']],
            "xing": [shengxiaos[item] for item in zhi_atts[zhi]['刑']],
            "beixing": [shengxiaos[item] for item in zhi_atts[zhi]['被刑']],
            "hai": [shengxiaos[item] for item in zhi_atts[zhi]['害']],
            "po": [shengxiaos[item] for item in zhi_atts[zhi]['破']]
        }
    }
    
    return result

def format_shengxiao_result(result):
    """
    格式化生肖信息输出
    
    Args:
        result (dict): 生肖信息字典
    
    Returns:
        str: 格式化的字符串
    """
    if "error" in result:
        return f"错误：{result['error']}\n有效的生肖：{', '.join(result['valid_shengxiaos'])}"
    
    output = []
    output.append(f"你的生肖是：{result['shengxiao']}")
    output.append(f"你的年支是：{result['year_zhi']}")
    output.append("=" * 80)
    output.append("合生肖是合八字的一小部分，有一定参考意义，但是不是全部。")
    output.append("合婚请以八字为准，技术支持：钉钉或微信pythontesting")
    output.append("以下为相合的生肖：")
    output.append("=" * 80)
    
    if result['compatible']['sanhe']:
        output.append(f"与你三合的生肖：{''.join(result['compatible']['sanhe'])}")
    if result['compatible']['liuhe']:
        output.append(f"与你六合的生肖：{''.join(result['compatible']['liuhe'])}")
    if result['compatible']['sanhui']:
        output.append(f"与你三会的生肖：{''.join(result['compatible']['sanhui'])}")
    
    output.append("")
    output.append("=" * 80)
    output.append("以下为不合的生肖：")
    output.append("=" * 80)
    
    if result['incompatible']['chong']:
        output.append(f"与你相冲的生肖：{''.join(result['incompatible']['chong'])}")
    if result['incompatible']['xing']:
        output.append(f"你刑的生肖：{''.join(result['incompatible']['xing'])}")
    if result['incompatible']['beixing']:
        output.append(f"被你刑的生肖：{''.join(result['incompatible']['beixing'])}")
    if result['incompatible']['hai']:
        output.append(f"与你相害的生肖：{''.join(result['incompatible']['hai'])}")
    if result['incompatible']['po']:
        output.append(f"与你相破的生肖：{''.join(result['incompatible']['po'])}")
    
    output.append("")
    output.append("=" * 80)
    output.append("如果生肖同时在你的合与不合中，则做加减即可。")
    output.append("比如猪对于虎，有一个相破，有一六合，抵消就为平性。")
    
    return "\n".join(output)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python shengxiao_api.py <生肖>")
        print("例如: python shengxiao_api.py 鼠")
        sys.exit(1)
    
    shengxiao = sys.argv[1]
    result = get_shengxiao_info(shengxiao)
    print(format_shengxiao_result(result))