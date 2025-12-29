#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, send_from_directory, Response
import subprocess
import os
import sys
import requests
import json
from lunar_python import Solar, Lunar
from datas import shengxiaos, zhi_atts, tiaohous, jinbuhuan, ges
from ganzhi import gan5, zhi5, ten_deities

app = Flask(__name__, template_folder='templates')

class AIAnalysisAPI:
    @staticmethod
    def get_ai_interpretation(birth_info, shengxiao_analysis, bazi_analysis, ai_config):
        """使用AI解读八字和生肖信息"""
        try:
            # 构建AI解读的提示词
            prompt = f"""你是一位专业的命理学专家，请基于以下传统八字和生肖分析结果，为用户提供全面、专业且易懂的命理解读。

## 基本信息：
- 出生日期：{birth_info['date']} ({birth_info['calendar_type']})
- 出生时辰：{birth_info['time']}点
- 性别：{birth_info['gender']}
- 生肖：{birth_info['shengxiao']}

## 生肖分析结果：
年支：{shengxiao_analysis['year_zhi']}

相合生肖：
- 三合：{', '.join(shengxiao_analysis['compatible']['sanhe']) if shengxiao_analysis['compatible']['sanhe'] else '无'}
- 六合：{', '.join(shengxiao_analysis['compatible']['liuhe']) if shengxiao_analysis['compatible']['liuhe'] else '无'}
- 三会：{', '.join(shengxiao_analysis['compatible']['sanhui']) if shengxiao_analysis['compatible']['sanhui'] else '无'}

不合生肖：
- 相冲：{', '.join(shengxiao_analysis['incompatible']['chong']) if shengxiao_analysis['incompatible']['chong'] else '无'}
- 相刑：{', '.join(shengxiao_analysis['incompatible']['xing']) if shengxiao_analysis['incompatible']['xing'] else '无'}
- 相害：{', '.join(shengxiao_analysis['incompatible']['hai']) if shengxiao_analysis['incompatible']['hai'] else '无'}
- 相破：{', '.join(shengxiao_analysis['incompatible']['po']) if shengxiao_analysis['incompatible']['po'] else '无'}

## 八字排盘分析：
{bazi_analysis}

请基于以上信息，从以下几个方面为用户提供专业解读：

1. **性格特点分析**：根据八字五行和生肖特性，分析此人的性格特点、优缺点
2. **事业运势**：分析事业发展方向、适合的职业类型、成功的关键因素
3. **财运分析**：财富积累能力、理财建议、财运周期
4. **感情婚姻**：感情模式、婚姻运势、与什么类型的人相配
5. **健康建议**：根据五行分析可能的健康注意事项
6. **人生建议**：基于命理特点给出的人生发展建议

要求：
- 语言通俗易懂，避免过于专业的术语
- 结合现代生活实际，给出实用的建议
- 保持客观中性，既不过分乐观也不悲观
- 重点突出个人努力的重要性
- 字数控制在800-1200字左右
- 使用温和、积极的语调"""

            # 根据配置的AI服务发送请求
            if ai_config['provider'] == 'openai':
                return AIAnalysisAPI._call_openai(prompt, ai_config)
            elif ai_config['provider'] == 'claude':
                return AIAnalysisAPI._call_claude(prompt, ai_config)
            elif ai_config['provider'] == 'deepseek':
                return AIAnalysisAPI._call_deepseek(prompt, ai_config)
            elif ai_config['provider'] == 'qianfan':
                return AIAnalysisAPI._call_qianfan(prompt, ai_config)
            elif ai_config['provider'] == 'custom':
                return AIAnalysisAPI._call_custom(prompt, ai_config)
            else:
                return {"error": "不支持的AI服务提供商"}
                
        except Exception as e:
            return {"error": f"AI解读失败: {str(e)}"}
    
    @staticmethod
    def _call_openai(prompt, config, stream=False):
        """调用OpenAI API"""
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config.get('model', 'gpt-3.5-turbo'),
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': config.get('max_tokens', 2000),
            'temperature': config.get('temperature', 0.7),
            'stream': stream
        }
        
        api_url = config.get('api_url', 'https://api.openai.com/v1/chat/completions')
        
        if stream:
            response = requests.post(api_url, headers=headers, json=data, timeout=60, stream=True)
            return response
        else:
            response = requests.post(api_url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "content": result['choices'][0]['message']['content']}
            else:
                return {"error": f"OpenAI API错误: {response.status_code} - {response.text}"}
    
    @staticmethod
    def _call_claude(prompt, config):
        """调用Claude API"""
        headers = {
            'x-api-key': config["api_key"],
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': config.get('model', 'claude-3-sonnet-20240229'),
            'max_tokens': config.get('max_tokens', 2000),
            'messages': [{'role': 'user', 'content': prompt}]
        }
        
        api_url = config.get('api_url', 'https://api.anthropic.com/v1/messages')
        
        response = requests.post(api_url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return {"success": True, "content": result['content'][0]['text']}
        else:
            return {"error": f"Claude API错误: {response.status_code} - {response.text}"}
    
    @staticmethod
    def _call_deepseek(prompt, config, stream=False):
        """调用DeepSeek API"""
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config.get('model', 'deepseek-chat'),
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': config.get('max_tokens', 2000),
            'temperature': config.get('temperature', 0.7),
            'stream': stream
        }
        
        api_url = config.get('api_url', 'https://api.deepseek.com/v1/chat/completions')
        
        if stream:
            response = requests.post(api_url, headers=headers, json=data, timeout=60, stream=True)
            return response
        else:
            response = requests.post(api_url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "content": result['choices'][0]['message']['content']}
            else:
                return {"error": f"DeepSeek API错误: {response.status_code} - {response.text}"}
    
    @staticmethod
    def _call_qianfan(prompt, config):
        """调用百度千帆API"""
        # 这里可以根据需要实现千帆API调用
        return {"error": "千帆API暂未实现"}
    
    @staticmethod
    def _call_custom(prompt, config):
        """调用自定义API"""
        try:
            # 验证必需的配置项
            required_fields = ['api_url', 'api_key']
            for field in required_fields:
                if field not in config or not config[field]:
                    return {"error": f"自定义API配置缺少必需字段: {field}"}
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            # 添加自定义headers
            if 'custom_headers' in config and config['custom_headers']:
                headers.update(config['custom_headers'])
            
            # 构建请求数据
            data = {
                'model': config.get('model', 'gpt-3.5-turbo'),
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': config.get('max_tokens', 2000),
                'temperature': config.get('temperature', 0.7)
            }
            
            # 添加自定义参数
            if 'custom_params' in config and config['custom_params']:
                data.update(config['custom_params'])
            
            response = requests.post(config['api_url'], headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # 支持不同的响应格式
                content = ""
                if 'choices' in result and result['choices']:
                    # OpenAI格式
                    content = result['choices'][0]['message']['content']
                elif 'content' in result:
                    # Claude格式
                    if isinstance(result['content'], list):
                        content = result['content'][0]['text']
                    else:
                        content = result['content']
                elif 'response' in result:
                    # 通用格式
                    content = result['response']
                else:
                    return {"error": "自定义API返回格式无法解析"}
                
                return {"success": True, "content": content}
            else:
                return {"error": f"自定义API错误: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": f"自定义API调用失败: {str(e)}"}
    
    @staticmethod
    def _call_custom_stream(prompt, config):
        """调用自定义API流式"""
        try:
            # 验证必需的配置项
            required_fields = ['api_url', 'api_key']
            for field in required_fields:
                if field not in config or not config[field]:
                    raise Exception(f"自定义API配置缺少必需字段: {field}")
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            # 添加自定义headers
            if 'custom_headers' in config and config['custom_headers']:
                headers.update(config['custom_headers'])
            
            # 构建请求数据
            data = {
                'model': config.get('model', 'gpt-3.5-turbo'),
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': config.get('max_tokens', 2000),
                'temperature': config.get('temperature', 0.7),
                'stream': True
            }
            
            # 添加自定义参数
            if 'custom_params' in config and config['custom_params']:
                data.update(config['custom_params'])
            
            response = requests.post(config['api_url'], headers=headers, json=data, timeout=60, stream=True)
            return response
                
        except Exception as e:
            raise Exception(f"自定义API流式调用失败: {str(e)}")

class ShengxiaoAPI:
    @staticmethod
    def get_shengxiao_by_year(year):
        """根据年份获取生肖"""
        # 计算生肖的基础年份（1900年为鼠年）
        base_year = 1900
        zodiac_animals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
        
        # 计算生肖索引
        zodiac_index = (year - base_year) % 12
        return zodiac_animals[zodiac_index]
    
    @staticmethod
    def get_shengxiao_info(shengxiao):
        """获取生肖信息"""
        if shengxiao not in shengxiaos.inverse:
            return {
                "error": "请输入正确的生肖",
                "valid_shengxiaos": list(shengxiaos.inverse.keys())
            }
        
        zhi = shengxiaos.inverse[shengxiao]
        
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


def calculate_shensha(eight_char, lunar):
    """计算核心神煞"""
    day_gan = eight_char.getDayGan()
    day_zhi = eight_char.getDayZhi()
    year_zhi = eight_char.getYearZhi()
    
    shensha_map = { "year": [], "month": [], "day": [], "time": [] }
    zhis = [eight_char.getYearZhi(), eight_char.getMonthZhi(), eight_char.getDayZhi(), eight_char.getTimeZhi()]
    labels = ["year", "month", "day", "time"]
    
    # 1. 天乙贵人
    tianyi_rules = {
        "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
        "乙": ["子", "申"], "己": ["子", "申"],
        "丙": ["亥", "酉"], "丁": ["亥", "酉"],
        "壬": ["卯", "巳"], "癸": ["卯", "巳"],
        "辛": ["午", "寅"]
    }
    target_zhis = tianyi_rules.get(day_gan, [])
    for i, zhi in enumerate(zhis):
        if zhi in target_zhis: shensha_map[labels[i]].append("天乙贵人")
            
    # 2. 桃花
    taohua_rules = {
        "申": "酉", "子": "酉", "辰": "酉", "寅": "卯", "午": "卯", "戌": "卯",
        "巳": "午", "酉": "午", "丑": "午", "亥": "子", "卯": "子", "未": "子"
    }
    targets = {taohua_rules.get(year_zhi), taohua_rules.get(day_zhi)}
    for i, zhi in enumerate(zhis):
        if zhi in targets: shensha_map[labels[i]].append("桃花")
            
    # 3. 驿马
    yima_rules = {
        "申": "寅", "子": "寅", "辰": "寅", "寅": "申", "午": "申", "戌": "申",
        "巳": "亥", "酉": "亥", "丑": "亥", "亥": "巳", "卯": "巳", "未": "巳"
    }
    targets = {yima_rules.get(year_zhi), yima_rules.get(day_zhi)}
    for i, zhi in enumerate(zhis):
        if zhi in targets: shensha_map[labels[i]].append("驿马")
            
    # 4. 空亡
    xun_kong = eight_char.getDayXunKong()
    for i, zhi in enumerate(zhis):
        if zhi in xun_kong: shensha_map[labels[i]].append("空亡")
            
    # 5. 羊刃
    yangren_rules = {"甲": "卯", "乙": "辰", "丙": "午", "戊": "午", "庚": "酉", "壬": "子"}
    if day_gan in yangren_rules:
        target = yangren_rules[day_gan]
        for i, zhi in enumerate(zhis):
            if zhi == target: shensha_map[labels[i]].append("羊刃")
            
    # 6. 文昌
    wenchang_rules = {
        "甲": "巳", "乙": "午", "丙": "申", "戊": "申", "丁": "酉", "己": "酉",
        "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯"
    }
    target = wenchang_rules.get(day_gan)
    for i, zhi in enumerate(zhis):
        if zhi == target: shensha_map[labels[i]].append("文昌")
            
    return shensha_map

# 纳音查找表
NAYIN = {
    '甲子': '海中金', '乙丑': '海中金', '丙寅': '炉中火', '丁卯': '炉中火',
    '戊辰': '大林木', '己巳': '大林木', '庚午': '路旁土', '辛未': '路旁土',
    '壬申': '剑锋金', '癸酉': '剑锋金', '甲戌': '山头火', '乙亥': '山头火',
    '丙子': '涧下水', '丁丑': '涧下水', '戊寅': '城头土', '己卯': '城头土',
    '庚辰': '白蜡金', '辛巳': '白蜡金', '壬午': '杨柳木', '癸未': '杨柳木',
    '甲申': '泉中水', '乙酉': '泉中水', '丙戌': '屋上土', '丁亥': '屋上土',
    '戊子': '霹雳火', '己丑': '霹雳火', '庚寅': '松柏木', '辛卯': '松柏木',
    '壬辰': '长流水', '癸巳': '长流水', '甲午': '沙中金', '乙未': '沙中金',
    '丙申': '山下火', '丁酉': '山下火', '戊戌': '平地木', '己亥': '平地木',
    '庚子': '壁上土', '辛丑': '壁上土', '壬寅': '金箔金', '癸卯': '金箔金',
    '甲辰': '覆灯火', '乙巳': '覆灯火', '丙午': '天河水', '丁未': '天河水',
    '戊申': '大驿土', '己酉': '大驿土', '庚戌': '钗钏金', '辛亥': '钗钏金',
    '壬子': '桑柘木', '癸丑': '桑柘木', '甲寅': '大溪水', '乙卯': '大溪水',
    '丙辰': '沙中土', '丁巳': '沙中土', '戊午': '天上火', '己未': '天上火',
    '庚申': '石榴木', '辛酉': '石榴木', '壬戌': '大海水', '癸亥': '大海水'
}

def build_bazi_struct(birth_date, birth_time="8", calendar_type="农历", gender="男"):
    """生成结构化的八字排盘数据，专业版"""
    try:
        year, month, day = [int(x) for x in birth_date.split('-')]
        hour = int(birth_time)
        if calendar_type == "公历":
            lunar = Solar.fromYmdHms(year, month, day, hour, 0, 0).getLunar()
        else:
            lunar = Lunar.fromYmdHms(year, month, day, hour, 0, 0)

        eight_char = lunar.getEightChar()
        gans = [eight_char.getYearGan(), eight_char.getMonthGan(), eight_char.getDayGan(), eight_char.getTimeGan()]
        zhis = [eight_char.getYearZhi(), eight_char.getMonthZhi(), eight_char.getDayZhi(), eight_char.getTimeZhi()]
        na_yins = [eight_char.getYearNaYin(), eight_char.getMonthNaYin(), eight_char.getDayNaYin(), eight_char.getTimeNaYin()]
        
        day_master = gans[2]
        shenshas = calculate_shensha(eight_char, lunar)
        
        pillars = []
        labels = ["年柱", "月柱", "日柱", "时柱"]
        keys = ["year", "month", "day", "time"]

        for i, (label, gan, zhi) in enumerate(zip(labels, gans, zhis)):
            hidden_stems = list(zhi5.get(zhi, {}).keys())
            main_hidden = hidden_stems[0] if hidden_stems else None
            pillars.append({
                "label": label, "gan": gan, "zhi": zhi,
                "na_yin": na_yins[i], "shen_sha": shenshas[keys[i]],
                "gan_element": gan5.get(gan),
                "zhi_element": gan5.get(main_hidden) if main_hidden else None,
                "gan_ten_god": ten_deities[day_master][gan],
                "zhi_ten_god": ten_deities[day_master][main_hidden] if main_hidden else "",
                "hidden_stems": hidden_stems,
                "hidden_ten_gods": [ten_deities[day_master][h] for h in hidden_stems],
                "hidden_elements": [gan5.get(h) for h in hidden_stems]
            })

        five_elements = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        for gan in gans: five_elements[gan5[gan]] += 5
        for zhi in zhis:
            if zhi in zhi5:
                for stem, score in zhi5[zhi].items(): five_elements[gan5[stem]] += score
                    
        # 大运计算
        gender_num = 1 if gender == "男" else 0
        yun = eight_char.getYun(gender_num)
        da_yun_list = []
        da_yuns = yun.getDaYun()
        for i in range(10):
            if i >= len(da_yuns): break
            dy = da_yuns[i]
            gan_zhi = dy.getGanZhi()
            start_year = dy.getStartYear()
            if len(gan_zhi) >= 2:
                dg, dz = gan_zhi[0], gan_zhi[1]
                tg_val = ten_deities[day_master].get(dg, '')
            else:
                dg, dz = '', ''
                tg_val = ''
                
            da_yun_list.append({
                "index": i, "gan_zhi": gan_zhi, "gan": dg, "zhi": dz,
                "start_year": start_year, "start_age": dy.getStartAge(), "end_age": dy.getEndAge(),
                "ten_god": tg_val,
                "ten_god": tg_val,
                "na_yin": NAYIN.get(gan_zhi, '') # Use manual lookup
            })


        # --- 新增专业计算 logic ---
        
        # 1. 计算胎元 (Tai Yuan)
        # 规则: 月干后一位, 月支后三位
        def get_tai_yuan(month_gan, month_zhi):
            stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
            branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
            
            try:
                g_idx = stems.index(month_gan)
                z_idx = branches.index(month_zhi)
                new_g = stems[(g_idx + 1) % 10]
                new_z = branches[(z_idx + 3) % 12]
                return f"{new_g}{new_z}"
            except:
                return "未知"

        tai_yuan = get_tai_yuan(gans[1], zhis[1])
        tai_yuan_nayin = NAYIN.get(tai_yuan, '')

        # 2. 计算身强身弱与喜用神 (Basic Balancing Method)
        # 此算法基于五行得分对比 (V1.0)
        
        # 定义五行生克关系
        elements_order = ["木", "火", "土", "金", "水"] # 0,1,2,3,4
        dm_el = gan5.get(day_master) # 日主五行
        
        # 计算同党 (帮我) 与 异党 (耗我)
        # 同党: 日主五行 (比劫) + 生日主五行 (印枭)
        # 异党: 克日主 (官杀) + 日主生 (食伤) + 日主克 (财才)
        
        idx = elements_order.index(dm_el)
        resource_el = elements_order[(idx - 1) % 5]    # 印
        output_el = elements_order[(idx + 1) % 5]      # 食
        wealth_el = elements_order[(idx + 2) % 5]      # 财
        power_el = elements_order[(idx + 3) % 5]       # 官
        
        score_same = (five_elements.get(dm_el, 0) + five_elements.get(resource_el, 0))
        score_diff = (five_elements.get(output_el, 0) + five_elements.get(wealth_el, 0) + five_elements.get(power_el, 0))
        
        total_score = score_same + score_diff
        weak_strength = "中和"
        xi_yong = [] # 喜用
        ji_shen = [] # 忌神
        
        # 简化判定标准 (45% - 55% 视为中和，实际应用可能更复杂)
        # 这里采用倾向性判定
        if score_same >= total_score * 0.55:
            weak_strength = "身强"
            xi_yong = [output_el, wealth_el, power_el] # 喜克泄耗
            ji_shen = [dm_el, resource_el]
        elif score_same <= total_score * 0.45:
            weak_strength = "身弱"
            xi_yong = [dm_el, resource_el] # 喜生扶
            ji_shen = [output_el, wealth_el, power_el]
        else:
            weak_strength = "中和偏" + ("强" if score_same > score_diff else "弱")
            # 中和者通常喜平衡，视具体过旺过弱项微调，此处简化为取通关
            if score_same > score_diff:
                xi_yong = [output_el, wealth_el, power_el]
                ji_shen = [dm_el, resource_el]
            else:
                 xi_yong = [dm_el, resource_el]
                 ji_shen = [output_el, wealth_el, power_el]

        advice = {}
        try:
            key = f"{day_master}{zhis[1]}"
            advice = {
                "tiao_hou": tiaohous.get(key),
                "jin_bu_huan": jinbuhuan.get(key),
                "ge_ju": ges.get(ten_deities[day_master]['本'], {}).get(zhis[1])
            }
        except: pass

        return {
            "pillars": pillars,
            "day_master": day_master,
            "day_master_element": gan5.get(day_master),
            "five_elements": five_elements,
            "advice": advice,
            "da_yun": da_yun_list,
            "start_yun_desc": f"{yun.getStartYear()}年{yun.getStartMonth()}月起运",
            "extras": { 
                "kong_wang": eight_char.getDayXunKong(), 
                "ming_gong": eight_char.getMingGong(),
                "tai_yuan": tai_yuan,
                "tai_yuan_nayin": tai_yuan_nayin,
                "strength": weak_strength,
                "yong_shen": xi_yong,
                "ji_shen": ji_shen
            }
        }
    except Exception as e:
        print(f"结构化八字生成失败: {e}", file=sys.stderr)
        return None

class BaziAPI:
    @staticmethod
    def run_bazi_analysis(birth_date, birth_time="8", gender="男", calendar_type="农历"):
        """运行八字分析"""
        try:
            # 兼容不同操作系统的Python命令
            import platform
            if platform.system() == "Windows":
                python_cmd = "python"
            else:
                python_cmd = "python3"
            
            # 解析日期格式 YYYY-MM-DD
            year, month, day = birth_date.split('-')
            
            # 构建命令参数
            cmd = [python_cmd, "bazi.py", year, month, day, str(birth_time)]
            
            # 如果是公历，添加 -g 参数
            if calendar_type == "公历":
                cmd.append("-g")
            
            # 如果是女性，添加 -n 参数
            if gender == "女":
                cmd.append("-n")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='gbk',  # Windows中文编码
                errors='ignore',  # 忽略编码错误
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # 调试输出
            print(f"命令执行: {' '.join(cmd)}")
            print(f"返回码: {result.returncode}")
            print(f"stdout长度: {len(result.stdout) if result.stdout else 0}")
            print(f"stderr: {result.stderr if result.stderr else 'None'}")
            
            return {
                "success": result.returncode == 0,
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
    
    @staticmethod
    def validate_date_format(date_str):
        """验证日期格式"""
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
    
    @staticmethod
    def validate_time(time_str):
        """验证时间格式"""
        try:
            time_int = int(time_str)
            return 0 <= time_int <= 23
        except:
            return False

# 页面路由
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/destiny-track')
def destiny_track():
    """命运轨迹游戏页面"""
    return render_template('destiny_track.html')

@app.route('/api')
def api_info():
    """API首页"""
    return jsonify({
        "message": "八字生肖分析API服务",
        "endpoints": {
            "/api/shengxiao": "生肖分析 (POST)",
            "/api/bazi": "八字分析 (POST)",
            "/api/complete": "完整分析 (POST)",
            "/health": "健康检查 (GET)"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "healthy"})

@app.route('/api/shengxiao', methods=['POST'])
def shengxiao_analysis():
    """生肖分析接口"""
    try:
        data = request.get_json()
        
        if not data or 'shengxiao' not in data:
            return jsonify({
                "error": "缺少参数",
                "required": ["shengxiao"],
                "example": {"shengxiao": "鼠"}
            }), 400
        
        shengxiao = data['shengxiao']
        result = ShengxiaoAPI.get_shengxiao_info(shengxiao)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/api/bazi', methods=['POST'])
def bazi_analysis():
    """八字分析接口"""
    try:
        data = request.get_json()
        
        if not data or 'birth_date' not in data:
            return jsonify({
                "error": "缺少参数",
                "required": ["birth_date"],
                "optional": ["birth_time", "gender"],
                "example": {
                    "birth_date": "1990-01-01",
                    "birth_time": "8",
                    "gender": "男"
                }
            }), 400
        
        birth_date = data['birth_date']
        birth_time = data.get('birth_time', '8')
        gender = data.get('gender', '男')
        calendar_type = data.get('calendar_type', '农历')
        
        # 验证输入
        if not BaziAPI.validate_date_format(birth_date):
            return jsonify({"error": "日期格式不正确，请使用 YYYY-MM-DD 格式"}), 400
        
        if not BaziAPI.validate_time(str(birth_time)):
            return jsonify({"error": "时辰格式不正确，请使用 0-23 的整数"}), 400
        
        if gender not in ["男", "女"]:
            return jsonify({"error": "性别必须是 '男' 或 '女'"}), 400
        
        if calendar_type not in ["公历", "农历"]:
            return jsonify({"error": "历法类型必须是 '公历' 或 '农历'"}), 400
        
        # 运行分析
        result = BaziAPI.run_bazi_analysis(birth_date, str(birth_time), gender, calendar_type)
        
        if not result["success"]:
            return jsonify({
                "error": result["error"],
                "birth_info": {
                    "date": birth_date,
                    "time": birth_time,
                    "gender": gender
                }
            }), 500
        
        # 清理分析结果
        cleaned_output = result["output"] or "八字分析暂无结果"
        if cleaned_output != "八字分析暂无结果":
            lines = cleaned_output.split('\n')
            filtered_lines = []
            for line in lines:
                if not any(keyword in line for keyword in ['t.cn', 'http', '建议参见', 'pythontesting']):
                    filtered_lines.append(line)
            cleaned_output = '\n'.join(filtered_lines)
        
        return jsonify({
            "birth_info": {
                "date": birth_date,
                "time": birth_time,
                "gender": gender
            },
            "analysis": cleaned_output,
            "success": True
        })
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/api/complete', methods=['POST'])
def complete_analysis():
    """完整分析接口：同时返回八字和生肖信息"""
    try:
        data = request.get_json()
        
        if not data or 'birth_date' not in data:
            return jsonify({
                "error": "缺少参数",
                "required": ["birth_date"],
                "optional": ["birth_time", "gender"]
            }), 400
        
        birth_date = data['birth_date']
        birth_time = data.get('birth_time', '8')
        gender = data.get('gender', '男')
        calendar_type = data.get('calendar_type', '农历')
        
        # 验证输入
        if not BaziAPI.validate_date_format(birth_date):
            return jsonify({"error": "日期格式不正确，请使用 YYYY-MM-DD 格式"}), 400
        
        if not BaziAPI.validate_time(str(birth_time)):
            return jsonify({"error": "时辰格式不正确，请使用 0-23 的整数"}), 400
        
        if gender not in ["男", "女"]:
            return jsonify({"error": "性别必须是 '男' 或 '女'"}), 400
        
        if calendar_type not in ["公历", "农历"]:
            return jsonify({"error": "历法类型必须是 '公历' 或 '农历'"}), 400
        
        # 获取年份并计算生肖
        year = int(birth_date.split('-')[0])
        shengxiao = ShengxiaoAPI.get_shengxiao_by_year(year)
        
        # 获取生肖详细信息
        shengxiao_info = ShengxiaoAPI.get_shengxiao_info(shengxiao)
        
        # 运行八字分析
        bazi_result = BaziAPI.run_bazi_analysis(birth_date, str(birth_time), gender, calendar_type)
        
        if not bazi_result["success"]:
            return jsonify({
                "error": f"八字分析失败: {bazi_result['error']}",
                "debug_info": {
                    "command": f"python bazi.py {birth_date.replace('-', ' ')} {birth_time}",
                    "return_code": bazi_result.get('return_code'),
                    "stderr": bazi_result.get('error')
                },
                "birth_info": {
                    "date": birth_date,
                    "time": birth_time,
                    "gender": gender
                }
            }), 500
        
        # 调试输出
        print(f"八字分析结果长度: {len(bazi_result['output']) if bazi_result['output'] else 0}")
        print(f"八字分析前100字符: {bazi_result['output'][:100] if bazi_result['output'] else 'None'}")
        
        # 清理八字分析结果中的推广链接
        cleaned_output = bazi_result["output"] or "八字分析暂无结果"
        if cleaned_output != "八字分析暂无结果":
            # 删除推广链接行
            lines = cleaned_output.split('\n')
            filtered_lines = []
            for line in lines:
                # 过滤掉包含网址和推广信息的行
                if not any(keyword in line for keyword in ['t.cn', 'http', '建议参见', 'pythontesting']):
                    filtered_lines.append(line)
            cleaned_output = '\n'.join(filtered_lines)

        # 结构化八字排盘（用于前端表格/图表）
        bazi_struct = build_bazi_struct(birth_date, birth_time, calendar_type)
        
        return jsonify({
            "birth_info": {
                "date": birth_date,
                "time": birth_time,
                "gender": gender,
                "calendar_type": calendar_type,
                "shengxiao": shengxiao
            },
            "bazi_analysis": cleaned_output,
            "shengxiao_analysis": shengxiao_info,
            "bazi_struct": bazi_struct,
            "success": True
        })
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/api/ai-interpretation', methods=['POST'])
def ai_interpretation():
    """AI解读接口"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['birth_info', 'shengxiao_analysis', 'bazi_analysis', 'ai_config']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必需参数: {field}"}), 400
        
        # 验证AI配置
        ai_config = data['ai_config']
        if 'provider' not in ai_config or 'api_key' not in ai_config:
            return jsonify({"error": "AI配置不完整，需要provider和api_key"}), 400
        
        # 调用AI解读
        result = AIAnalysisAPI.get_ai_interpretation(
            data['birth_info'],
            data['shengxiao_analysis'], 
            data['bazi_analysis'],
            ai_config
        )
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify({
            "success": True,
            "interpretation": result["content"],
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/api/ai-interpretation-stream', methods=['POST'])
def ai_interpretation_stream():
    """AI解读流式接口"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['birth_info', 'shengxiao_analysis', 'bazi_analysis', 'ai_config']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必需参数: {field}"}), 400
        
        # 验证AI配置
        ai_config = data['ai_config']
        if 'provider' not in ai_config or 'api_key' not in ai_config:
            return jsonify({"error": "AI配置不完整，需要provider和api_key"}), 400
        
        # 构建AI解读的提示词
        birth_info = data['birth_info']
        shengxiao_analysis = data['shengxiao_analysis']
        bazi_analysis = data['bazi_analysis']
        
        prompt = f"""你是一位专业的命理学专家，请基于以下传统八字和生肖分析结果，为用户提供全面、专业且易懂的命理解读。

## 基本信息：
- 出生日期：{birth_info['date']} ({birth_info['calendar_type']})
- 出生时辰：{birth_info['time']}点
- 性别：{birth_info['gender']}
- 生肖：{birth_info['shengxiao']}

## 生肖分析结果：
年支：{shengxiao_analysis['year_zhi']}

相合生肖：
- 三合：{', '.join(shengxiao_analysis['compatible']['sanhe']) if shengxiao_analysis['compatible']['sanhe'] else '无'}
- 六合：{', '.join(shengxiao_analysis['compatible']['liuhe']) if shengxiao_analysis['compatible']['liuhe'] else '无'}
- 三会：{', '.join(shengxiao_analysis['compatible']['sanhui']) if shengxiao_analysis['compatible']['sanhui'] else '无'}

不合生肖：
- 相冲：{', '.join(shengxiao_analysis['incompatible']['chong']) if shengxiao_analysis['incompatible']['chong'] else '无'}
- 相刑：{', '.join(shengxiao_analysis['incompatible']['xing']) if shengxiao_analysis['incompatible']['xing'] else '无'}
- 相害：{', '.join(shengxiao_analysis['incompatible']['hai']) if shengxiao_analysis['incompatible']['hai'] else '无'}
- 相破：{', '.join(shengxiao_analysis['incompatible']['po']) if shengxiao_analysis['incompatible']['po'] else '无'}

## 八字排盘分析：
{bazi_analysis}

请基于以上信息，从以下几个方面为用户提供专业解读：

1. **性格特点分析**：根据八字五行和生肖特性，分析此人的性格特点、优缺点
2. **事业运势**：分析事业发展方向、适合的职业类型、成功的关键因素
3. **财运分析**：财富积累能力、理财建议、财运周期
4. **感情婚姻**：感情模式、婚姻运势、与什么类型的人相配
5. **健康建议**：根据五行分析可能的健康注意事项
6. **人生建议**：基于命理特点给出的人生发展建议

要求：
- 语言通俗易懂，避免过于专业的术语
- 结合现代生活实际，给出实用的建议
- 保持客观中性，既不过分乐观也不悲观
- 重点突出个人努力的重要性
- 字数控制在800-1200字左右
- 使用温和、积极的语调"""
        
        def generate_stream():
            try:
                provider = ai_config['provider']
                
                if provider == 'openai':
                    response = AIAnalysisAPI._call_openai(prompt, ai_config, stream=True)
                elif provider == 'deepseek':
                    response = AIAnalysisAPI._call_deepseek(prompt, ai_config, stream=True)
                elif provider == 'custom':
                    response = AIAnalysisAPI._call_custom_stream(prompt, ai_config)
                else:
                    yield f"data: {json.dumps({'error': '不支持的AI服务提供商流式输出'})}\n\n"
                    return
                
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': f'API错误: {response.status_code}'})}\n\n"
                    return
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data_obj = json.loads(data_str)
                                if 'choices' in data_obj and data_obj['choices']:
                                    delta = data_obj['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        yield f"data: {json.dumps({'content': content})}\n\n"
                            except json.JSONDecodeError:
                                continue
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': f'流式处理错误: {str(e)}'})}\n\n"
        
        return Response(generate_stream(), mimetype='text/event-stream')
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/api/destiny-story', methods=['POST'])
def destiny_story():
    """命运轨迹故事生成接口"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['prompt', 'ai_config', 'game_state']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必需参数: {field}"}), 400
        
        # 验证AI配置
        ai_config = data['ai_config']
        if 'api_key' not in ai_config or not ai_config['api_key']:
            return jsonify({"error": "AI配置不完整，需要api_key"}), 400
        
        prompt = data['prompt']
        
        # 调用AI生成故事
        try:
            if ai_config['provider'] == 'openai':
                result = AIAnalysisAPI._call_openai(prompt, ai_config)
            elif ai_config['provider'] == 'claude':
                result = AIAnalysisAPI._call_claude(prompt, ai_config)
            elif ai_config['provider'] == 'deepseek':
                result = AIAnalysisAPI._call_deepseek(prompt, ai_config)
            elif ai_config['provider'] == 'custom':
                result = AIAnalysisAPI._call_custom(prompt, ai_config)
            else:
                return jsonify({"error": "不支持的AI服务提供商"}), 400
            
            if "error" in result:
                return jsonify({"success": False, "error": result["error"]}), 500
            
            # 解析AI返回的JSON格式故事
            try:
                content = result["content"]
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    story_json = json_match.group(1)
                else:
                    # 如果没有代码块，尝试直接解析
                    story_json = content.strip()
                
                story_data = json.loads(story_json)
                
                # 验证故事数据格式
                required_story_fields = ['title', 'story', 'choices']
                for field in required_story_fields:
                    if field not in story_data:
                        raise ValueError(f"故事数据缺少字段: {field}")
                
                if not isinstance(story_data['choices'], list) or len(story_data['choices']) < 2:
                    raise ValueError("choices必须是包含至少2个元素的数组")
                
                return jsonify({
                    "success": True,
                    "story": story_data,
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                })
                
            except (json.JSONDecodeError, ValueError) as e:
                return jsonify({
                    "success": False,
                    "error": f"AI返回格式错误: {str(e)}",
                    "raw_content": result["content"]
                }), 500
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"AI调用失败: {str(e)}"
            }), 500
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/api/destiny-story-stream', methods=['POST'])
def destiny_story_stream():
    """命运轨迹故事生成流式接口"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['prompt', 'ai_config', 'game_state']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必需参数: {field}"}), 400
        
        # 验证AI配置
        ai_config = data['ai_config']
        if 'api_key' not in ai_config or not ai_config['api_key']:
            return jsonify({"error": "AI配置不完整，需要api_key"}), 400
        
        prompt = data['prompt']
        
        def generate_stream():
            try:
                provider = ai_config['provider']
                
                if provider == 'openai':
                    response = AIAnalysisAPI._call_openai(prompt, ai_config, stream=True)
                elif provider == 'deepseek':
                    response = AIAnalysisAPI._call_deepseek(prompt, ai_config, stream=True)
                elif provider == 'custom':
                    response = AIAnalysisAPI._call_custom_stream(prompt, ai_config)
                else:
                    yield f"data: {json.dumps({'error': '不支持的AI服务提供商流式输出'})}\n\n"
                    return
                
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': f'API错误: {response.status_code}'})}\n\n"
                    return
                
                full_content = ""
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data_obj = json.loads(data_str)
                                if 'choices' in data_obj and data_obj['choices']:
                                    delta = data_obj['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        full_content += content
                                        yield f"data: {json.dumps({'content': content})}\n\n"
                            except json.JSONDecodeError:
                                continue
                
                # 流式传输完成后，解析完整内容
                try:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', full_content, re.DOTALL)
                    if json_match:
                        story_json = json_match.group(1)
                    else:
                        story_json = full_content.strip()
                    
                    story_data = json.loads(story_json)
                    
                    # 验证故事数据格式
                    required_story_fields = ['title', 'story', 'choices']
                    for field in required_story_fields:
                        if field not in story_data:
                            raise ValueError(f"故事数据缺少字段: {field}")
                    
                    if not isinstance(story_data['choices'], list) or len(story_data['choices']) < 2:
                        raise ValueError("choices必须是包含至少2个元素的数组")
                    
                    yield f"data: {json.dumps({'story_data': story_data, 'done': True})}\n\n"
                    
                except (json.JSONDecodeError, ValueError) as e:
                    yield f"data: {json.dumps({'error': f'故事解析错误: {str(e)}', 'raw_content': full_content})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': f'流式处理错误: {str(e)}'})}\n\n"
        
        return Response(generate_stream(), mimetype='text/event-stream')
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

if __name__ == '__main__':
    print("启动八字生肖分析API服务...")
    print("Web界面: http://localhost:5000")
    print("命运轨迹游戏: http://localhost:5000/destiny-track")
    print("API端点:")
    print("  POST /api/shengxiao - 生肖分析")
    print("  POST /api/bazi - 八字分析")
    print("  POST /api/complete - 完整分析")
    print("  POST /api/ai-interpretation - AI解读")
    print("  POST /api/ai-interpretation-stream - AI解读流式")
    print("  POST /api/destiny-story - 命运轨迹故事生成")
    print("  POST /api/destiny-story-stream - 命运轨迹故事生成流式")
    print("  GET /health - 健康检查")
    print("  GET /api - API文档")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
