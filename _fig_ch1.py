# -*- coding: utf-8 -*-
"""生成第1章插图：全文研究框架"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10.5
plt.rcParams['figure.dpi'] = 300

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
OUT = os.path.join(BASE, "Pictures")
C_BLUE, C_RED, C_GREEN, C_ORANGE, C_PURPLE, C_GRAY = \
    '#2471a3', '#c0392b', '#1e8449', '#d68910', '#7d3c98', '#7f8c8d'


def fig1_1():
    fig, ax = plt.subplots(figsize=(10.0, 5.6))
    ax.set_xlim(0, 10.4); ax.set_ylim(0, 6.2); ax.axis('off')

    def box(x, y, w, h, txt, fc, ec, fs=8.6, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.06',
                                    fc=fc, ec=ec, lw=1.0))
        ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center',
                fontsize=fs, fontweight='bold' if bold else 'normal')

    # 顶行：观测条件
    box(3.35, 5.35, 3.7, 0.62, '短波双照射源观测条件\n（低精度 · 低数据率 · 强相关）',
        '#fdf2e9', '#ca6f1e', 8.8)

    # 四个痛点
    pains = [('电离层虚高失配\n空间配准', 0.30, C_BLUE),
             ('低检测概率\n航迹断续', 2.95, C_GREEN),
             ('密集空域\n关联歧义', 5.60, C_ORANGE),
             ('双站误差相关\n融合失效', 8.25, C_RED)]
    for txt, x, c in pains:
        box(x, 3.95, 1.85, 0.86, txt, '#ffffff', c, 8.4)
        ax.annotate('', xy=(x + 0.92, 4.91), xytext=(5.2, 5.32),
                    arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=0.9))

    # 章节
    chs = [('第2章\n量测建模与\n时空配准', 0.30, C_BLUE),
           ('第3章\n单站滤波与\n性能边界', 2.95, C_GREEN),
           ('第4章\n跨照射源\n航迹关联', 5.60, C_ORANGE),
           ('第5章\n双照射源\n航迹融合', 8.25, C_RED)]
    for txt, x, c in chs:
        box(x, 2.30, 1.85, 1.00, txt, '#eaf4fb', c, 8.4)
        ax.annotate('', xy=(x + 0.92, 3.34), xytext=(x + 0.92, 3.92),
                    arrowprops=dict(arrowstyle='->', color=c, lw=1.1))

    # 章节间横向传导
    for x in [2.17, 4.82, 7.47]:
        ax.annotate('', xy=(x + 0.76, 2.80), xytext=(x, 2.80),
                    arrowprops=dict(arrowstyle='->', color='#34495e', lw=1.2))

    # 核心结论
    box(1.55, 0.72, 7.3, 0.95,
        '核心论点：融合增益由两站误差相关性决定，\n'
        '而相关性由前端模型与真实机动的匹配程度决定',
        '#f4ecf7', C_PURPLE, 9.2, bold=True)
    for x, c in [(1.22, C_BLUE), (3.87, C_GREEN), (6.52, C_ORANGE), (9.17, C_RED)]:
        ax.annotate('', xy=(x, 1.70), xytext=(x, 2.27),
                    arrowprops=dict(arrowstyle='->', color=c, lw=1.0, ls='--'))

    ax.text(0.30, 1.98, '沿处理链逐级传导', fontsize=8.6, color='#34495e')
    ax.text(0.30, 0.30, '注：四个问题并非彼此孤立，前一环节的残差会成为后一环节的输入扰动',
            fontsize=8.2, color=C_GRAY)

    p = os.path.join(OUT, 'fig1_1_framework.png')
    fig.savefig(p, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  ->', p)


if __name__ == '__main__':
    fig1_1()
