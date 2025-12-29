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

def build_bazi_struct(birth_date, birth_time="8", calendar_type="农历"):
    """生成结构化的八字排盘数据，便于前端展示表格/图表"""
    try:
        year, month, day = [int(x) for x in birth_date.split('-')]
        hour = int(birth_time)

        if calendar_type == "公历":
            lunar = Solar.fromYmdHms(year, month, day, hour, 0, 0).getLunar()
        else:
            lunar = Lunar.fromYmdHms(year, month, day, hour, 0, 0)

        eight_char = lunar.getEightChar()
        gans = [
            eight_char.getYearGan(),
            eight_char.getMonthGan(),
            eight_char.getDayGan(),
            eight_char.getTimeGan()
        ]
        zhis = [
            eight_char.getYearZhi(),
            eight_char.getMonthZhi(),
            eight_char.getDayZhi(),
            eight_char.getTimeZhi()
        ]

        day_master = gans[2]
        pillars = []
        labels = ["年柱", "月柱", "日柱", "时柱"]

        for label, gan, zhi in zip(labels, gans, zhis):
            hidden_stems = list(zhi5[zhi].keys())
            main_hidden = hidden_stems[0] if hidden_stems else None
            pillars.append({
                "label": label,
                "gan": gan,
                "zhi": zhi,
                "gan_element": gan5.get(gan),
                "zhi_element": gan5.get(main_hidden) if main_hidden else None,
                "gan_ten_god": ten_deities[day_master][gan],
                "zhi_ten_god": ten_deities[day_master][main_hidden] if main_hidden else "",
                "hidden_stems": hidden_stems,
                "hidden_ten_gods": [ten_deities[day_master][h] for h in hidden_stems],
                "hidden_elements": [gan5.get(h) for h in hidden_stems]
            })

        # 五行计分：沿用原脚本的简化权重（干加5分，支藏干按权值累加）
        five_elements = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        for gan in gans:
            five_elements[gan5[gan]] += 5
        for zhi in zhis:
            for stem, score in zhi5[zhi].items():
                five_elements[gan5[stem]] += score

        advice = {}
        try:
            key = f"{day_master}{zhis[1]}"
            advice = {
                "tiao_hou": tiaohous.get(key),
                "jin_bu_huan": jinbuhuan.get(key),
                "ge_ju": ges.get(ten_deities[day_master]['本'], {}).get(zhis[1])
            }
        except Exception as e:
            print(f"结构化建议生成失败: {e}", file=sys.stderr)

        return {
            "pillars": pillars,
            "day_master": day_master,
            "day_master_element": gan5.get(day_master),
            "five_elements": five_elements,
            "advice": advice
        }
    except Exception as e:
        # 结构化信息失败不应中断主流程
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
