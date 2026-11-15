# -*- coding: utf-8 -*-
"""数据口径一致性核对：检查关键数字与禁用表述"""
import os, re

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
CHS = ['ch1.md', 'ch2.md', 'ch3.md', 'ch4.md', 'ch5.md', 'ch6.md']

# 必须出现的权威数字（出现在对应章节即可）
MUST = {
    'ch2.md': ['82.53', '11.75', '320', '300', '13'],
    'ch3.md': ['12.105', '11.320', '10.522', '8.039', '0.416', '0.173',
               '4.28', '2.91', '12.24', '26.29', '2.20', '2.24'],
    'ch4.md': ['16.40', '7.40', '8.20', '6.20', '0.9768', '0.9354',
               '0.9432', '0.9745', '0.9667'],
    'ch5.md': ['26.29', '12.24', '10.522', '8.039'],
}

# 禁用表述（一旦出现即需人工确认）
BAN = [
    (r'Δgain\s*=\s*[-−]39', '禁用的确定性回归公式 Δgain=-39Δρ'),
    (r'[-−]39\.0\s*[×x]\s*Δ', '禁用的确定性回归公式'),
    (r'ρ\s*每降\s*0\.1', '禁用的"ρ每降0.1增益增3.9pp"表述'),
    (r'航迹.{0,6}提升\s*50\s*%', '开题承诺航迹长度+50%（本文未兑现）'),
    (r'航迹.{0,6}提升百分之五十', '开题承诺航迹长度+50%（本文未兑现）'),
    (r'全面优于', '绝对化表述'),
    (r'全面最优', '绝对化表述'),
    (r'CI\s*更鲁棒', '与实测相反（CI 均值与最坏情况均更差）'),
    (r'BC\s*与\s*SCC\s*并列', '伪结论（BC 已退化为 SCC）'),
]

# 融合增益的错误主结论：0.5% 只能作为"基线诊断"出现
FUSION_MAIN = r'(融合增益|增益).{0,12}(仅|只有|为)\s*0\.5\s*%'

rows = []
for ch in CHS:
    p = os.path.join(BASE, ch)
    if not os.path.exists(p):
        rows.append((ch, 'MISSING', '文件不存在'))
        continue
    txt = open(p, encoding='utf-8').read()

    # 必须出现的数字
    for num in MUST.get(ch, []):
        if num not in txt:
            rows.append((ch, 'MISS_NUM', f'缺少权威数字 {num}'))

    # 禁用表述
    for pat, why in BAN:
        for mt in re.finditer(pat, txt):
            i = mt.start()
            ctx = txt[max(0, i - 40):i + 50].replace('\n', ' ')
            rows.append((ch, 'BANNED', f'{why} | …{ctx}…'))

    # 0.5% 误用检查
    for mt in re.finditer(FUSION_MAIN, txt):
        i = mt.start()
        ctx = txt[max(0, i - 80):i + 80].replace('\n', ' ')
        # 若同句出现"基线"则视为合规
        seg = txt[max(0, i - 120):i + 120]
        if '基线' in seg:
            rows.append((ch, 'CHECK_OK', f'0.5% 已标注基线口径 | …{ctx}…'))
        else:
            rows.append((ch, 'RISK_05', f'0.5% 未标注基线 | …{ctx}…'))

    # 数值范围粗检：RMSE 不应出现明显离谱值
    for mt in re.finditer(r'(\d+\.\d{3})\s*km', txt):
        v = float(mt.group(1))
        if v > 100:
            rows.append((ch, 'RANGE', f'可疑 RMSE {v} km'))

print('=' * 76)
print('数据口径一致性核对')
print('=' * 76)
if not rows:
    print('✅ 全部通过')
else:
    for ch, k, d in rows:
        print(f'[{ch}][{k}] {d}')
print()
print(f'合计 {len(rows)} 条')
