const LAYOUT_VERSION = '7';
console.log('layout version', LAYOUT_VERSION);

document.getElementById('analysisForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const year = formData.get('birthYear');
    const month = formData.get('birthMonth').padStart(2, '0');
    const day = formData.get('birthDay').padStart(2, '0');

    const data = {
        birth_date: `${year}-${month}-${day}`,
        birth_time: formData.get('birthTime'),
        gender: formData.get('gender'),
        calendar_type: formData.get('calendarType')
    };

    // 显示加载状态
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('submitBtn').disabled = true;
    document.getElementById('submitBtn').textContent = '分析中...';

    // 调用API
    fetch('/api/complete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            document.getElementById('loading').style.display = 'none';

            if (result.success) {
                displayResults(result);
            } else {
                let errorMsg = result.error || '分析失败，请重试';
                if (result.debug_info) {
                    errorMsg += `\n\n调试信息:\n命令: ${result.debug_info.command}\n返回码: ${result.debug_info.return_code}\n错误: ${result.debug_info.stderr}`;
                }
                displayError(errorMsg);
            }
        })
        .catch(error => {
            document.getElementById('loading').style.display = 'none';
            displayError('网络错误：' + error.message);
        })
        .finally(() => {
            document.getElementById('submitBtn').disabled = false;
            document.getElementById('submitBtn').textContent = '开始分析';
        });
});

function displayResults(data) {
    // 保存数据到全局变量供复制功能使用
    currentAnalysisData = data;

    const resultsDiv = document.getElementById('results');
    const birthInfo = data.birth_info;
    const shengxiaoAnalysis = data.shengxiao_analysis;
    const baziAnalysis = data.bazi_analysis;

    resultsDiv.innerHTML = `
                <div class="basic-info">
                    <h4>📋 基本信息</h4>
                    <span class="info-item">📅 ${birthInfo.date} (${birthInfo.calendar_type})</span>
                    <span class="info-item">⏰ ${getTimeLabel(birthInfo.time)}</span>
                    <span class="info-item">👤 ${birthInfo.gender}</span>
                    <span class="info-item">🐲 ${birthInfo.shengxiao}</span>
                </div>
                
                ${renderShengxiaoCard(birthInfo, shengxiaoAnalysis)}
                
                ${renderProPanels(data.bazi_struct)}
                
                <div class="copy-actions">
                    <button class="copy-btn" onclick="copyShengxiaoInfo(this)">📋 复制生肖信息</button>
                    <button class="copy-btn" onclick="copyBaziInfo(this)">📋 复制八字排盘</button>
                    <button class="copy-btn" onclick="copyAllInfo(this)">📋 复制全部信息</button>
                </div>
                
                <div class="ai-config-section">
                    <h4>🤖 AI智能解读</h4>
                    <p>配置AI API信息，获得专业的命理解读</p>
                    <button class="ai-config-toggle" onclick="toggleAIConfig(this)">⚙️ 配置AI设置</button>
                    
                    <div class="ai-config-form" id="aiConfigForm">
                        <div class="form-group">
                            <label for="aiProvider">AI服务商</label>
                            <select id="aiProvider" onchange="updateAIConfig()">
                                <option value="openai">OpenAI (GPT)</option>
                                <option value="claude">Anthropic (Claude)</option>
                                <option value="deepseek">DeepSeek</option>
                                <option value="custom">自定义服务商</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="aiModel">AI模型</label>
                            <select id="aiModel">
                                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                <option value="gpt-4">GPT-4</option>
                                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="aiApiKey">API Key</label>
                            <input type="password" id="aiApiKey" placeholder="请输入您的API Key">
                        </div>
                        <div class="form-group">
                            <label for="aiApiUrl">API地址 (可选)</label>
                            <input type="text" id="aiApiUrl" placeholder="自定义API地址，留空使用默认">
                        </div>
                        
                        <div class="form-group custom-only" id="customModelGroup" style="display: none;">
                            <label for="customModel">自定义模型名</label>
                            <input type="text" id="customModel" placeholder="输入自定义模型名称">
                        </div>
                        
                        <div class="form-group custom-only" id="customHeaderGroup" style="display: none;">
                            <label for="customHeaders">自定义Headers (JSON格式，可选)</label>
                            <textarea id="customHeaders" placeholder='{"X-Custom-Header": "value"}' rows="3"></textarea>
                        </div>
                    </div>
                    
                    <button class="ai-interpret-btn" id="aiInterpretBtn" onclick="getAIInterpretation()">
                        🧠 AI智能解读
                    </button>
                    
                    <button class="destiny-track-btn" id="destinyTrackBtn" onclick="openDestinyTrack()" style="display: none;">
                        🎭 命运轨迹
                    </button>
                </div>
                
                <div id="aiInterpretationResult" style="display: none;"></div>
                
                <div class="result-card">
                    <h3>八字详细分析</h3>
                    <div class="bazi-content">${formatBaziContent(baziAnalysis)}</div>
                </div>
            `;

    // 隐藏 AI 解读与八字详细分析
    const aiSection = resultsDiv.querySelector('.ai-config-section');
    if (aiSection) aiSection.remove();
    const aiResult = resultsDiv.querySelector('#aiInterpretationResult');
    if (aiResult) aiResult.remove();
    const detailCard = Array.from(resultsDiv.querySelectorAll('.result-card')).find(c => c.querySelector('.bazi-content'));
    if (detailCard) detailCard.remove();

    resultsDiv.style.display = 'block';

    // 显示命运轨迹按钮
    const destinyTrackBtn = document.getElementById('destinyTrackBtn');
    if (destinyTrackBtn) {
        destinyTrackBtn.style.display = 'inline-block';
    }

    // 渲染图表
    renderCharts(data.bazi_struct);
}

function displayError(message) {
    const resultsDiv = document.getElementById('results');
    const formattedMessage = message.replace(/\n/g, '<br>');
    resultsDiv.innerHTML = `<div class="error">❌ ${formattedMessage}</div>`;
    resultsDiv.style.display = 'block';
}

function renderShengxiaoCard(birthInfo, analysis) {
    if (!analysis) return '';

    const renderTags = (label, list, type) => {
        if (!list || list.length === 0) return '';
        const badgeClass = type === 'good' ? 'z-badge-good' : 'z-badge-bad';
        return `
            <div class="z-row">
                <span class="z-label">${label}</span>
                <div class="z-tags">
                    ${list.map(z => `<span class="${badgeClass}">${z}</span>`).join('')}
                </div>
            </div>
        `;
    };

    return `
        <div class="result-card shengxiao-new-card">
            <div class="shengxiao-header">
                <div class="sx-icon-box">${birthInfo.shengxiao}</div>
                <div class="sx-title-box">
                    <h3 style="margin:0;border:none;padding:0;color:var(--text-main);font-size:1.3em;">生肖分析 · ${birthInfo.shengxiao}</h3>
                    <span class="sx-year-zhi">年支：${analysis.year_zhi}</span>
                </div>
            </div>

            <div class="shengxiao-grid">
                <div class="relation-group good">
                    <h4 class="rg-title"><span style="color:#ff5677;">💖</span> 缘分相合</h4>
                    ${renderTags('三合', analysis.compatible.sanhe, 'good') || '<div class="z-empty">无</div>'}
                    ${renderTags('六合', analysis.compatible.liuhe, 'good') || ''}
                    ${renderTags('三会', analysis.compatible.sanhui, 'good') || ''}
                </div>
                
                <div class="relation-group bad">
                    <h4 class="rg-title"><span style="color:#636e72;">⚠️</span> 需要注意</h4>
                    ${renderTags('相冲', analysis.incompatible.chong, 'bad') || '<div class="z-empty">无</div>'}
                    ${renderTags('相刑', analysis.incompatible.xing, 'bad') || ''}
                    ${renderTags('相害', analysis.incompatible.hai, 'bad') || ''}
                    ${renderTags('相破', analysis.incompatible.po, 'bad') || ''}
                </div>
            </div>
            
            <div class="shengxiao-note">
                 💡 <strong>提示：</strong>生肖相合仅供参考，人际交往更看重性格契合与沟通。
            </div>
        </div>
    `;
}

function renderZodiacTags(label, list, type) {
    // Helper used inside if needed, but included in closure above.
    // Keeping this if needed later or remove.
    return '';
}

function getTimeLabel(hour) {
    const timeLabels = {
        '0': '子时 (23:00-01:00)',
        '1': '丑时 (01:00-03:00)',
        '3': '寅时 (03:00-05:00)',
        '5': '卯时 (05:00-07:00)',
        '7': '辰时 (07:00-09:00)',
        '8': '巳时 (09:00-11:00)',
        '11': '午时 (11:00-13:00)',
        '13': '未时 (13:00-15:00)',
        '15': '申时 (15:00-17:00)',
        '17': '酉时 (17:00-19:00)',
        '19': '戌时 (19:00-21:00)',
        '21': '亥时 (21:00-23:00)'
    };
    return timeLabels[hour] || `${hour}点`;
}

function cleanAnsiCodes(text) {
    // 清理ANSI颜色代码
    return text.replace(/\x1b\[[0-9;]*m/g, '');
}

function formatBaziContent(text) {
    if (!text) return '暂无分析结果';

    // 清理ANSI代码但保持原始格式
    let cleanText = cleanAnsiCodes(text);

    // 过滤推广信息
    let lines = cleanText.split('\n');
    let filteredLines = [];

    for (let line of lines) {
        // 过滤推广信息
        if (line.includes('建议参见') || line.includes('t.cn') || line.includes('http')) {
            continue;
        }
        filteredLines.push(line);
    }

    return filteredLines.join('\n');
}

// 初始化日期选择器
function initializeDateSelectors() {
    const currentYear = new Date().getFullYear();
    const yearSelect = document.getElementById('birthYear');
    const monthSelect = document.getElementById('birthMonth');
    const daySelect = document.getElementById('birthDay');

    // 生成年份选项 (1900-当前年份)
    for (let year = currentYear; year >= 1900; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year + '年';
        if (year === 1990) option.selected = true; // 默认选择1990年
        yearSelect.appendChild(option);
    }

    // 生成月份选项
    for (let month = 1; month <= 12; month++) {
        const option = document.createElement('option');
        option.value = month;
        option.textContent = month + '月';
        if (month === 1) option.selected = true; // 默认选择1月
        monthSelect.appendChild(option);
    }

    // 生成日期选项
    function updateDays() {
        const selectedYear = parseInt(yearSelect.value);
        const selectedMonth = parseInt(monthSelect.value);
        const daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();

        daySelect.innerHTML = '';
        for (let day = 1; day <= daysInMonth; day++) {
            const option = document.createElement('option');
            option.value = day;
            option.textContent = day + '日';
            if (day === 1) option.selected = true; // 默认选择1日
            daySelect.appendChild(option);
        }
    }

    // 初始化日期
    updateDays();

    // 年份或月份改变时更新日期
    yearSelect.addEventListener('change', updateDays);
    monthSelect.addEventListener('change', updateDays);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initializeDateSelectors);

// 全局变量存储分析结果
let currentAnalysisData = null;

// Markdown 渲染（本地 marked 优先，失败则兜底纯文本换行）
function renderMarkdown(content) {
    const hasMarked = typeof window.marked !== 'undefined' && typeof window.marked.parse === 'function';
    if (hasMarked) {
        return window.marked.parse(content);
    }
    const safe = (content || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/\\n/g, '<br>');
    return `<p>${safe}</p>`;
}

function renderFiveElements(fiveElements) {
    if (!fiveElements) return '';
    const total = Object.values(fiveElements).reduce((a, b) => a + (b || 0), 0) || 1;
    const bars = Object.entries(fiveElements).map(([element, value]) => {
        const percent = Math.round((value / total) * 100);
        return `
                    <div class="fe-row">
                        <span class="fe-label">${element}</span>
                        <div class="fe-bar"><div style="width:${percent}%;"></div></div>
                        <span class="fe-value">${value}</span>
                    </div>
                `;
    }).join('');

    return `
                <div class="five-element-panel">
                    <div class="panel-title">五行分布</div>
                    ${bars}
                </div>
            `;
}

function renderPillarSection(struct) {
    if (!struct || !struct.pillars) return '';

    const cards = struct.pillars.map(pillar => {
        const hidden = (pillar.hidden_stems || []).map((stem, idx) => {
            const tg = pillar.hidden_ten_gods ? pillar.hidden_ten_gods[idx] : '';
            return `${stem}${tg ? `(${tg})` : ''}`;
        }).join('、') || '无';

        return `
                    <div class="pillar-card">
                        <div class="pillar-label">${pillar.label}</div>
                        <div class="pillar-gan">
                            ${pillar.gan}
                            <span class="tag">${pillar.gan_element || ''}</span>
                            <span class="tag subtle">${pillar.gan_ten_god || ''}</span>
                        </div>
                        <div class="pillar-zhi">
                            ${pillar.zhi}
                            <span class="tag">${pillar.zhi_element || ''}</span>
                            <span class="tag subtle">${pillar.zhi_ten_god || ''}</span>
                        </div>
                        <div class="pillar-hidden">藏干：${hidden}</div>
                    </div>
                `;
    }).join('');

    const dayMaster = struct.day_master ? `<div class="day-master">日主：${struct.day_master}${struct.day_master_element ? `（${struct.day_master_element}）` : ''}</div>` : '';

    return `
                <div class="bazi-structure">
                    <div class="structure-header">
                        <h4>八字排盘</h4>
                        ${dayMaster}
                    </div>
                    <div class="pillar-grid">
                        ${cards}
                    </div>
                </div>
            `;
}

function summarizeTenGods(struct) {
    const counts = {};
    if (!struct || !struct.pillars) return counts;
    struct.pillars.forEach(p => {
        if (p.gan_ten_god) counts[p.gan_ten_god] = (counts[p.gan_ten_god] || 0) + 1;
        (p.hidden_ten_gods || []).forEach(tg => {
            if (!tg) return;
            counts[tg] = (counts[tg] || 0) + 1;
        });
    });
    return counts;
}

function renderFiveElementSummary(struct) {
    if (!struct || !struct.five_elements) {
        return '<p style="color:#888;">暂无五行数据</p>';
    }

    // Map element names to CSS classes
    const elMap = {
        '金': 'jin',
        '木': 'mu',
        '水': 'shui',
        '火': 'huo',
        '土': 'tu'
    };

    const total = Object.values(struct.five_elements).reduce((a, b) => a + (b || 0), 0) || 1;
    // Unsorted to match standard sequence or maintain chart order? 
    // Usually Key Sequence is 金木水火土 or sorted by value. 
    // Chart uses keys(fiveEl), which is not guaranteed order but usually standard.
    // Let's sort by value descending for the summary to show dominant elements first.
    const rows = Object.entries(struct.five_elements)
        .sort((a, b) => b[1] - a[1])
        .map(([el, val]) => {
            const pct = Math.round((val / total) * 100);
            const elClass = elMap[el] || '';
            return `
                        <div style="display:flex;align-items:center;gap:15px;margin:12px 0;">
                            <span style="width:28px;font-weight:bold;font-size:1.1em;color:var(--text-main);">${el}</span>
                            <div class="fe-bar ${elClass}"><div style="width:${pct}%;"></div></div>
                            <span class="fe-value" style="font-weight:600;width:40px;">${val}</span>
                        </div>
                    `;
        })
        .join('');

    // Add a container with flex grow to distribute space if needed, though margins help
    return `<div style="padding:10px 0;display:flex;flex-direction:column;justify-content:center;height:100%;">${rows}</div>`;
}


function renderPillarTable(struct) {
    if (!struct || !struct.pillars) return '';
    const rows = struct.pillars.map(p => {
        const hidden = (p.hidden_stems || []).map((stem, idx) => {
            const tg = p.hidden_ten_gods ? p.hidden_ten_gods[idx] : '';
            return `<span style="display:inline-block; margin-right:4px;">${stem}<span style="font-size:0.8em;color:#999;">${tg}</span></span>`;
        }).join('');

        let shensha = '';
        if (p.shen_sha && p.shen_sha.length > 0) {
            shensha = p.shen_sha.map(s => `<span class="ss-badge">${s}</span>`).join(' ');
        }

        return `
                    <tr>
                        <td class="p-label">${p.label}</td>
                        <td class="p-gan" data-el="${p.gan_element}">
                            ${p.gan}
                            <div class="p-tg">${p.gan_ten_god || ''}</div>
                        </td>
                        <td class="p-zhi" data-el="${p.zhi_element}">
                            ${p.zhi}
                            <div class="p-tg">${p.zhi_ten_god || ''}</div>
                        </td>
                        <td class="p-nayin">${p.na_yin || '-'}</td>
                        <td class="p-hidden">${hidden}</td>
                        <td class="p-shensha">${shensha}</td>
                    </tr>
                `;
    }).join('');

    return `
                <div class="pro-card">
                    <h4>四柱排盘 (乾坤造化)</h4>
                    <div class="table-responsive">
                        <table class="pillar-table-pro">
                            <thead>
                                <tr><th>柱</th><th>天干</th><th>地支</th><th>纳音</th><th>藏干</th><th>神煞</th></tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table>
                    </div>
                </div>
            `;
}

function renderDaYunTable(struct) {
    if (!struct || !struct.da_yun) return '';
    const items = struct.da_yun.map(dy => {
        return `
            <div class="dy-item">
                <div class="dy-head">
                    <span class="dy-age">${dy.start_age}岁</span>
                    <span class="dy-year">${dy.start_year}</span>
                </div>
                <div class="dy-body">
                    <div class="dy-gz">
                        <span class="dy-gan" data-tg="${dy.ten_god}">${dy.gan}</span>
                        <span class="dy-zhi">${dy.zhi}</span>
                    </div>
                    <div class="dy-nayin">${dy.na_yin}</div>
                    <div class="dy-tg">${dy.ten_god}</div>
                </div>
            </div>
        `;
    }).join('');

    return `
        <div class="pro-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
                <h4>大运排盘</h4>
                <div style="font-size:0.9em;color:#666;">${struct.start_yun_desc || ''}</div>
            </div>
            <div class="dayun-scroll">
                ${items}
            </div>
        </div>
    `;
}

function renderShenShaInfo(struct) {
    if (!struct || !struct.extras) return '';
    const ex = struct.extras;
    const kw = ex.kong_wang || "无";
    const mg = ex.ming_gong || "无";
    const ty = ex.tai_yuan || "无";
    const tyNy = ex.tai_yuan_nayin || "";

    // Format Useful Gods with badges
    const formatGods = (gods) => {
        if (!gods || gods.length === 0) return '无';
        const mapColor = { '金': '#f39c12', '木': '#2ecc71', '水': '#3498db', '火': '#e74c3c', '土': '#a0522d' };
        return gods.map(g => `<span style="background:${mapColor[g] || '#eee'};color:#fff;padding:2px 6px;border-radius:4px;margin-right:4px;">${g}</span>`).join('');
    };

    return `
        <div class="pro-card">
            <h4>命理提示</h4>
            <div class="info-grid-2">
                <div class="ig-item">
                    <span class="ig-label">日柱旬空</span>
                    <span class="ig-val">${kw}</span>
                </div>
                <div class="ig-item">
                    <span class="ig-label">命宫</span>
                    <span class="ig-val">${mg}</span>
                </div>
                 <div class="ig-item">
                    <span class="ig-label">胎元</span>
                    <span class="ig-val">
                        ${ty} <span style="font-size:0.8em;font-weight:normal;color:#999;">${tyNy}</span>
                    </span>
                </div>
                 <div class="ig-item">
                    <span class="ig-label">身强身弱</span>
                    <span class="ig-val">${ex.strength || '未判'}</span>
                </div>
            </div>
            
            <div style="margin-top:15px;border-top:1px dashed #eee;padding-top:10px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span style="color:#666;">喜用神 (利)</span>
                    <div>${formatGods(ex.yong_shen)}</div>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:#666;">忌神 (弊)</span>
                    <div>${formatGods(ex.ji_shen)}</div>
                </div>
            </div>
            
            <p style="font-size:0.9em;color:#999;margin-top:10px;">* 以上喜用神基于五行平衡法简推，仅供参考。</p>
        </div>
    `;
}


function renderTenGodTable(tenGodCounts) {
    const entries = Object.entries(tenGodCounts);
    if (!entries.length) return '';
    const rows = entries
        .sort((a, b) => b[1] - a[1])
        .map(([god, count]) => `<tr><td>${god}</td><td>${count}</td></tr>`)
        .join('');
    return `
                <div class="pro-card">
                    <h4>十神分布</h4>
                    <table class="ten-god-table">
                        <thead><tr><th>十神</th><th>数量</th></tr></thead>
                        <tbody>${rows}</tbody>
                    </table>
                </div>
            `;
}

function renderGauge(struct) {
    if (!struct || !struct.five_elements || !struct.day_master_element) return '';
    const total = Object.values(struct.five_elements).reduce((a, b) => a + (b || 0), 0) || 1;
    const dmVal = struct.five_elements[struct.day_master_element] || 0;
    const percent = Math.min(100, Math.round((dmVal / total) * 100));
    return `
                <div class="gauge-panel">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <h4 style="margin:0;">日主强弱</h4>
                        <span>${struct.day_master} · ${struct.day_master_element || ''}</span>
                    </div>
                    <div class="gauge-bar"><div class="gauge-fill" style="width:${percent}%;"></div></div>
                    <div class="gauge-meta">
                        <span>弱</span>
                        <span>${percent}%</span>
                        <span>强</span>
                    </div>
                </div>
            `;
}

function renderAdvice(struct) {
    if (!struct || !struct.advice) return '';
    const advice = struct.advice;
    const item = (label, val) => `
        <div style="margin-bottom:8px;">
            <span style="display:inline-block;width:80px;color:#666;">${label}</span>
            <span style="font-weight:600;">${val || '暂无'}</span>
        </div>`;

    return `
        <div style="padding:10px 0;">
             ${item('格局', advice.ge_ju)}
             ${item('调候', advice.tiao_hou)}
             ${item('金不换', advice.jin_bu_huan)}
        </div>
    `;
}

function renderProPanels(struct) {
    if (!struct) return '';
    const tenGodCounts = summarizeTenGods(struct);

    // Check if we have new data to render new components
    const hasDaYun = struct.da_yun && struct.da_yun.length > 0;

    return `
                ${renderGauge(struct)}
                
                <div class="stack-row full">
                    <div class="pro-card">
                        ${renderPillarSection(struct)}
                    </div>
                </div>

                <div class="stack-row full">
                    ${renderPillarTable(struct)}
                </div>
                
                ${hasDaYun ? `
                <div class="stack-row full">
                    ${renderDaYunTable(struct)}
                </div>` : ''}

                <div class="stack-row">
                    ${renderTenGodTable(tenGodCounts)}
                    <div class="pro-card">
                        <h4>十神环形图</h4>
                        <div style="display: flex; flex-direction: column; flex: 1; min-height: 280px;">
                            <div style="flex: 1; position: relative; min-height: 0;">
                                <canvas id="tenGodDonut"></canvas>
                            </div>
                            <div id="tenGodLegend" style="overflow-y: auto; max-height: 100px; display: flex; flex-wrap: wrap; justify-content: center; align-content: flex-end; gap: 15px; padding-top: 10px;"></div>
                        </div>
                    </div>
                </div>
                
                <div class="stack-row">
                    <div class="pro-card">
                        <h4>五行摘要</h4>
                        ${renderFiveElementSummary(struct)}
                    </div>
                    <div class="pro-card">
                        <h4>五行雷达</h4>
                        <div style="position: relative; height: 260px; width: 100%;">
                            <canvas id="fiveElementChart"></canvas>
                        </div>
                        <div style="font-size:12px;color:#666;margin-top:6px;text-align:center;">*权重为天干5分+藏干权值</div>
                    </div>
                </div>
                
                <div class="stack-row full">
                    <div class="pro-card">
                        <h4>格局与调候</h4>
                        ${renderAdvice(struct)}
                    </div>
                </div>
                
                <div class="stack-row">
                    ${renderShenShaInfo(struct)}
                </div>
            `;
}

function renderCharts(struct) {
    if (!struct) return;
    const fiveEl = struct.five_elements || {};
    const tenGodCounts = summarizeTenGods(struct);

    const feCtx = document.getElementById('fiveElementChart');
    if (feCtx && window.Chart) {
        // Enforce standard generating cycle order: Wood -> Fire -> Earth -> Metal -> Water
        const order = ['木', '火', '土', '金', '水'];
        // Ensure all keys exist
        const labels = order;
        const data = order.map(k => fiveEl[k] || 0);

        // Destroy existing chart instance if exists? 
        // Simple implementation creates new, but might leak. 
        // In this simple app, we just create new. Ideally should check ID.
        // Assuming the container is cleared or page refreshed.

        new Chart(feCtx, {
            type: 'radar',
            data: {
                labels,
                datasets: [{
                    label: '五行分布',
                    data,
                    backgroundColor: 'rgba(145, 69, 182, 0.2)', // Secondary color from theme
                    borderColor: '#9145b6',
                    pointBackgroundColor: ['#2ecc71', '#e74c3c', '#f1c40f', '#bdc3c7', '#3498db'], // Match element colors
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#9145b6'
                }]
            },
            options: {
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: { display: false },
                        pointLabels: {
                            font: {
                                size: 14,
                                family: "'Noto Sans SC', sans-serif"
                            }
                        }
                    }
                },
                plugins: {
                    legend: { display: false }
                },
                maintainAspectRatio: false,
                responsive: true
            }
        });
    }

    const tgCtx = document.getElementById('tenGodDonut');
    if (tgCtx && window.Chart && Object.keys(tenGodCounts).length) {
        const labels = Object.keys(tenGodCounts);
        const data = labels.map(k => tenGodCounts[k]);
        const colors = ['#4ECDC4', '#667eea', '#f39c12', '#e74c3c', '#8e44ad', '#1abc9c', '#3498db', '#95a5a6', '#2ecc71', '#e67e22'];

        const chart = new Chart(tgCtx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                layout: {
                    padding: 0
                },
                plugins: {
                    legend: {
                        display: false // Disable default legend
                    }
                },
                maintainAspectRatio: false,
                responsive: true,
                cutout: '60%'
            }
        });

        // Generate Custom HTML Legend
        const legendContainer = document.getElementById('tenGodLegend');
        if (legendContainer) {
            legendContainer.innerHTML = labels.map((label, index) => {
                const color = colors[index % colors.length];
                return `
                    <div style="display: flex; align-items: center; margin-right: 15px; margin-bottom: 5px; cursor: pointer;" onclick="toggleDataset(event, ${index})">
                        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: ${color}; margin-right: 8px;"></span>
                        <span style="font-size: 14px; color: #333;">${label}</span>
                    </div>
                `;
            }).join('');
        }
    }
}

function renderAdvice(struct) {
    const advice = struct && struct.advice ? struct.advice : {};
    const items = [];
    if (advice.ge_ju) items.push(`<li><strong>格局：</strong>${advice.ge_ju}</li>`);
    if (advice.tiao_hou) items.push(`<li><strong>调候：</strong>${advice.tiao_hou}</li>`);
    if (advice.jin_bu_huan) items.push(`<li><strong>金不换：</strong>${advice.jin_bu_huan}</li>`);

    const fiveEl = struct && struct.five_elements ? struct.five_elements : {};
    const sortedEl = Object.entries(fiveEl).sort((a, b) => b[1] - a[1]);
    if (sortedEl.length) {
        const strong = sortedEl[0][0];
        const weak = sortedEl[sortedEl.length - 1][0];
        items.push(`<li><strong>五行相对强：</strong>${strong}</li>`);
        items.push(`<li><strong>五行相对弱：</strong>${weak}</li>`);
    }

    if (!items.length) {
        return `<p style="color:#888;">暂无结构化建议数据</p>`;
    }
    return `<ul style="padding-left:16px; margin:0; line-height:1.6;">${items.join('')}</ul>`;
}

// AI配置和解读功能
function toggleAIConfig(button) {
    const form = document.getElementById('aiConfigForm');
    form.classList.toggle('show');

    const targetBtn = button || document.querySelector('.ai-config-toggle');
    if (targetBtn) {
        targetBtn.textContent = form.classList.contains('show') ?
            '?? ??AI??' : '?? ??AI??';
    }
}

function updateAIConfig() {
    const provider = document.getElementById('aiProvider').value;
    const modelSelect = document.getElementById('aiModel');
    const apiUrlInput = document.getElementById('aiApiUrl');
    const customModelGroup = document.getElementById('customModelGroup');
    const customHeaderGroup = document.getElementById('customHeaderGroup');

    // 隐藏所有自定义字段
    customModelGroup.style.display = 'none';
    customHeaderGroup.style.display = 'none';

    // 根据服务商更新模型选项和API地址提示
    if (provider === 'openai') {
        modelSelect.innerHTML = `
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    <option value="gpt-4o">GPT-4o</option>
                `;
        apiUrlInput.placeholder = "自定义API地址，留空使用默认 (https://api.openai.com/v1/chat/completions)";
        apiUrlInput.style.borderColor = "#ddd";
    } else if (provider === 'claude') {
        modelSelect.innerHTML = `
                    <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                    <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                    <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                    <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                `;
        apiUrlInput.placeholder = "自定义API地址，留空使用默认 (https://api.anthropic.com/v1/messages)";
        apiUrlInput.style.borderColor = "#ddd";
    } else if (provider === 'deepseek') {
        modelSelect.innerHTML = `
                    <option value="deepseek-chat">DeepSeek Chat</option>
                    <option value="deepseek-coder">DeepSeek Coder</option>
                `;
        apiUrlInput.placeholder = "自定义API地址，留空使用默认 (https://api.deepseek.com/v1/chat/completions)";
        apiUrlInput.style.borderColor = "#ddd";
    } else if (provider === 'custom') {
        modelSelect.innerHTML = `
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (OpenAI兼容)</option>
                    <option value="gpt-4">GPT-4 (OpenAI兼容)</option>
                    <option value="claude-3-sonnet">Claude-3-Sonnet (Claude兼容)</option>
                    <option value="custom-model">使用下方自定义模型名</option>
                `;
        apiUrlInput.placeholder = "必填：自定义API地址 (如: https://your-api.com/v1/chat/completions)";
        apiUrlInput.style.borderColor = "#ff6b6b";

        // 显示自定义字段
        customModelGroup.style.display = 'block';
        customHeaderGroup.style.display = 'block';
    }
}

async function getAIInterpretation() {
    if (!currentAnalysisData) {
        alert('请先完成八字分析');
        return;
    }

    // 获取AI配置
    const provider = document.getElementById('aiProvider').value;
    const model = document.getElementById('aiModel').value;
    const apiKey = document.getElementById('aiApiKey').value;
    const apiUrl = document.getElementById('aiApiUrl').value;

    if (!apiKey.trim()) {
        alert('请输入API Key');
        return;
    }

    // 自定义服务商必须填写API地址
    if (provider === 'custom' && !apiUrl.trim()) {
        alert('自定义服务商必须填写API地址');
        return;
    }

    let finalModel = model;
    let aiConfig = {
        provider: provider,
        model: finalModel,
        api_key: apiKey.trim()
    };

    // 处理自定义配置
    if (provider === 'custom') {
        const customModel = document.getElementById('customModel').value;
        const customHeaders = document.getElementById('customHeaders').value;

        // 如果选择了自定义模型且填写了模型名，使用自定义模型名
        if (model === 'custom-model' && customModel.trim()) {
            finalModel = customModel.trim();
            aiConfig.model = finalModel;
        }

        // 自定义服务商必须有API地址
        aiConfig.api_url = apiUrl.trim();

        // 添加自定义headers
        if (customHeaders.trim()) {
            try {
                aiConfig.custom_headers = JSON.parse(customHeaders.trim());
            } catch (e) {
                alert('自定义Headers格式错误，请检查JSON格式');
                return;
            }
        }
    } else {
        // 其他服务商的API地址是可选的
        if (apiUrl.trim()) {
            aiConfig.api_url = apiUrl.trim();
        }
    }

    // 显示加载状态和可折叠界面
    const resultDiv = document.getElementById('aiInterpretationResult');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = `
                <div class="ai-interpretation">
                    <div class="ai-interpretation-header">
                        <h3>🧠 AI智能解读</h3>
                        <button class="ai-collapse-btn" onclick="toggleAIResult()">▼</button>
                    </div>
                    <div class="ai-interpretation-content" id="aiContentArea">
                        <div class="ai-loading">🤖 AI正在分析中，请稍候...<span class="streaming-cursor">|</span></div>
                    </div>
                </div>
            `;

    const interpretBtn = document.getElementById('aiInterpretBtn');
    interpretBtn.disabled = true;
    interpretBtn.textContent = '🤖 AI分析中...';

    try {
        // 使用流式API端点
        const response = await fetch('/api/ai-interpretation-stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                birth_info: currentAnalysisData.birth_info,
                shengxiao_analysis: currentAnalysisData.shengxiao_analysis,
                bazi_analysis: currentAnalysisData.bazi_analysis,
                ai_config: aiConfig
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const contentArea = document.getElementById('aiContentArea');
        let fullContent = '';

        // 清空加载状态
        contentArea.innerHTML = '<div class="content"></div>';
        const contentDiv = contentArea.querySelector('.content');

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                break;
            }

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data.trim() === '') continue;

                    try {
                        const parsed = JSON.parse(data);

                        if (parsed.error) {
                            contentDiv.innerHTML = `
                                        <div class="error">
                                            ❌ AI解读失败: ${parsed.error}
                                        </div>
                                    `;
                            return;
                        }

                        if (parsed.content) {
                            fullContent += parsed.content;
                            // 实时渲染Markdown内容
                            contentDiv.innerHTML = renderMarkdown(fullContent) + '<span class="streaming-cursor">|</span>';
                        }

                        if (parsed.done) {
                            // 完成时移除光标并添加时间戳
                            contentDiv.innerHTML = renderMarkdown(fullContent) + `
                                        <div style="text-align: right; margin-top: 15px; opacity: 0.8; font-size: 0.9em;">
                                            解读时间: ${new Date().toLocaleString()}
                                        </div>
                                    `;
                            break;
                        }
                    } catch (e) {
                        console.error('解析JSON错误:', e);
                        continue;
                    }
                }
            }
        }

    } catch (error) {
        document.getElementById('aiContentArea').innerHTML = `
                    <div class="error">
                        ❌ 网络错误: ${error.message}
                    </div>
                `;
    } finally {
        interpretBtn.disabled = false;
        interpretBtn.textContent = '🧠 AI智能解读';
    }
}

// 切换AI结果显示/隐藏
function toggleAIResult() {
    const content = document.querySelector('.ai-interpretation-content');
    const btn = document.querySelector('.ai-collapse-btn');

    if (content.style.display === 'none') {
        content.style.display = 'block';
        btn.textContent = '▼';
    } else {
        content.style.display = 'none';
        btn.textContent = '▶';
    }
}

// 打开命运轨迹页面
function openDestinyTrack() {
    if (!currentAnalysisData) {
        alert('请先完成八字分析');
        return;
    }

    // 获取当前的AI配置
    const provider = document.getElementById('aiProvider').value;
    const model = document.getElementById('aiModel').value;
    const apiKey = document.getElementById('aiApiKey').value;
    const apiUrl = document.getElementById('aiApiUrl').value;
    const customModel = document.getElementById('customModel') ? document.getElementById('customModel').value : '';
    const customHeaders = document.getElementById('customHeaders') ? document.getElementById('customHeaders').value : '';

    let aiConfig = null;
    if (apiKey.trim()) {
        aiConfig = {
            provider: provider,
            model: model,
            api_key: apiKey.trim()
        };

        if (provider === 'custom') {
            if (model === 'custom-model' && customModel.trim()) {
                aiConfig.model = customModel.trim();
            }
            if (apiUrl.trim()) {
                aiConfig.api_url = apiUrl.trim();
            }
            if (customHeaders.trim()) {
                try {
                    aiConfig.custom_headers = JSON.parse(customHeaders.trim());
                } catch (e) {
                    // 忽略JSON解析错误
                }
            }
        } else if (apiUrl.trim()) {
            aiConfig.api_url = apiUrl.trim();
        }
    }

    // 将八字数据和AI配置存储到localStorage
    localStorage.setItem('baziData', JSON.stringify(currentAnalysisData));
    if (aiConfig) {
        localStorage.setItem('destinyAiConfig', JSON.stringify(aiConfig));
    } else {
        localStorage.removeItem('destinyAiConfig');
    }

    // 跳转到命运轨迹页面
    window.open('/destiny-track', '_blank');
}

// ???? - ??????
async function copyToClipboard(text, button) {
    const targetButton = button || null;
    const originalText = targetButton ? targetButton.textContent : "";

    try {
        // ??1: ?????????API
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            showCopySuccess(targetButton, originalText);
            return;
        }

        // ??2: ?????execCommand??????????
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        const successful = document.execCommand("copy");
        document.body.removeChild(textArea);

        if (successful) {
            showCopySuccess(targetButton, originalText);
        } else {
            throw new Error("execCommand failed");
        }
    } catch (err) {
        // ??3: ???????????
        showTextModal(text, targetButton, originalText);
    }
}

function showCopySuccess(button, originalText) {
    if (!button) return;
    button.textContent = "? ???";
    button.classList.add("copy-success");
    setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove("copy-success");
    }, 2000);
}
function showTextModal(text, button, originalText) {
    // 创建模态框显示文本供用户手动复制
    const modal = document.createElement('div');
    modal.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.8); z-index: 10000;
                display: flex; align-items: center; justify-content: center;
                padding: 20px;
            `;

    const content = document.createElement('div');
    content.style.cssText = `
                background: white; border-radius: 15px; padding: 30px;
                max-width: 90%; max-height: 80%; overflow-y: auto;
                position: relative;
            `;

    content.innerHTML = `
                <h3 style="margin-bottom: 20px; color: #333;">📋 请手动复制以下内容</h3>
                <textarea readonly style="width: 100%; min-height: 300px; padding: 15px; 
                    border: 2px solid #ddd; border-radius: 8px; font-family: monospace;
                    resize: vertical; font-size: 14px; line-height: 1.4;">${text}</textarea>
                <div style="text-align: center; margin-top: 20px;">
                    <button onclick="selectAllText(this)" style="background: #4ECDC4; color: white; 
                        border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;
                        margin-right: 10px;">全选文本</button>
                    <button onclick="closeModal(this)" style="background: #6c5ce7; color: white; 
                        border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">关闭</button>
                </div>
            `;

    modal.appendChild(content);
    document.body.appendChild(modal);

    // 自动选中文本
    const textarea = content.querySelector('textarea');
    textarea.focus();
    textarea.select();

    // 点击背景关闭
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });

    // 全局函数：全选文本
    window.selectAllText = function (btn) {
        const textarea = btn.parentElement.parentElement.querySelector('textarea');
        textarea.focus();
        textarea.select();
        btn.textContent = '✅ 已选中';
        setTimeout(() => {
            btn.textContent = '全选文本';
        }, 1000);
    };

    // 全局函数：关闭模态框
    window.closeModal = function (btn) {
        const modal = btn.closest('div[style*="position: fixed"]');
        if (modal) {
            document.body.removeChild(modal);
        }
    };
}

function copyShengxiaoInfo(button) {
    if (!currentAnalysisData) return;

    const birthInfo = currentAnalysisData.birth_info;
    const shengxiao = currentAnalysisData.shengxiao_analysis;

    const text = `生肖分析 - ${birthInfo.shengxiao}
            
基本信息：
出生日期：${birthInfo.date} (${birthInfo.calendar_type})
出生时辰：${getTimeLabel(birthInfo.time)}
性别：${birthInfo.gender}
生肖：${birthInfo.shengxiao}
年支：${shengxiao.year_zhi}

相合生肖：
三合：${shengxiao.compatible.sanhe.join('、') || '无'}
六合：${shengxiao.compatible.liuhe.join('、') || '无'}
三会：${shengxiao.compatible.sanhui.join('、') || '无'}

不合生肖：
相冲：${shengxiao.incompatible.chong.join('、') || '无'}
相刑：${shengxiao.incompatible.xing.join('、') || '无'}
被刑：${shengxiao.incompatible.beixing.join('、') || '无'}
相害：${shengxiao.incompatible.hai.join('、') || '无'}
相破：${shengxiao.incompatible.po.join('、') || '无'}

说明：合生肖是合八字的一小部分，有一定参考意义，但不是全部。合婚请以八字为准。`;

    copyToClipboard(text, button);
}

function copyBaziInfo(button) {
    if (!currentAnalysisData) return;

    const birthInfo = currentAnalysisData.birth_info;
    const baziText = formatBaziContent(currentAnalysisData.bazi_analysis);

    const text = `八字排盘
            
基本信息：
出生日期：${birthInfo.date} (${birthInfo.calendar_type})
出生时辰：${getTimeLabel(birthInfo.time)}
性别：${birthInfo.gender}
生肖：${birthInfo.shengxiao}

八字详细分析：
${baziText}`;

    copyToClipboard(text, button);
}

function copyAllInfo(button) {
    if (!currentAnalysisData) return;

    const birthInfo = currentAnalysisData.birth_info;
    const shengxiao = currentAnalysisData.shengxiao_analysis;
    const baziText = formatBaziContent(currentAnalysisData.bazi_analysis);

    const text = `八字生肖分析报告
            
基本信息：
出生日期：${birthInfo.date} (${birthInfo.calendar_type})
出生时辰：${getTimeLabel(birthInfo.time)}
性别：${birthInfo.gender}
生肖：${birthInfo.shengxiao}
年支：${shengxiao.year_zhi}

=== 生肖分析 ===
相合生肖：
三合：${shengxiao.compatible.sanhe.join('、') || '无'}
六合：${shengxiao.compatible.liuhe.join('、') || '无'}
三会：${shengxiao.compatible.sanhui.join('、') || '无'}

不合生肖：
相冲：${shengxiao.incompatible.chong.join('、') || '无'}
相刑：${shengxiao.incompatible.xing.join('、') || '无'}
被刑：${shengxiao.incompatible.beixing.join('、') || '无'}
相害：${shengxiao.incompatible.hai.join('、') || '无'}
相破：${shengxiao.incompatible.po.join('、') || '无'}

=== 八字详细分析 ===
${baziText}

说明：合生肖是合八字的一小部分，有一定参考意义，但不是全部。合婚请以八字为准。`;

    copyToClipboard(text, button);
}
