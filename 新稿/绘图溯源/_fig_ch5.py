# -*- coding: utf-8 -*-
"""第五章在线配对流程、在线方法对照与6/8确认判据。"""
from pathlib import Path
import json
import hashlib

import numpy as np
import pandas as pd
from scipy.stats import chi2, ncx2, binom
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
DATA = HERE/'数据/第五章'
OUT = HERE.parent/'Pictures'
plt.rcParams.update({'font.family': ['Times New Roman', 'SimSun'],
                     'axes.unicode_minus': False, 'font.size': 10})


def box(ax, x, y, w, h, label, lw=1.0, fs=9):
    ax.add_patch(Rectangle((x, y), w, h, facecolor='white', edgecolor='black', linewidth=lw))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=fs, color='black')


def arrow(ax, start, end):
    ax.annotate('', xy=end, xytext=start,
                arrowprops={'arrowstyle': '->', 'color': 'black', 'lw': 1.0})


def fig5_1():
    fig, ax = plt.subplots(figsize=(10.2, 5.1))
    ax.set(xlim=(0, 12), ylim=(0, 6))
    ax.axis('off')
    ax.text(6, 5.75, '逐帧在线跨照射源配对与系统航迹管理', ha='center', fontsize=12)
    box(ax, .25, 3.95, 2.0, 1.0, '两站当前局部航迹\n状态、协方差与航迹龄')
    box(ax, 2.8, 3.75, 2.3, 1.4,
        '在线候选策略\n双门限（主配置）\n最近邻／序贯／MEWF（对照）')
    box(ax, 5.65, 3.95, 2.0, 1.0, '得分排序与逐帧\n贪心一对一指派')
    box(ax, 8.2, 3.95, 1.65, 1.0, '6/8 窗口确认\n同一候选累计命中')
    box(ax, 10.35, 3.95, 1.4, 1.0, '接入第二源\n或保持单源')
    arrow(ax, (2.27, 4.45), (2.77, 4.45))
    arrow(ax, (5.12, 4.45), (5.62, 4.45))
    arrow(ax, (7.67, 4.45), (8.17, 4.45))
    arrow(ax, (9.87, 4.45), (10.32, 4.45))
    box(ax, 8.15, 1.95, 1.75, .85, '不满足确认\n继续累计或撤销候选')
    arrow(ax, (9.0, 3.92), (9.0, 2.83))
    arrow(ax, (8.15, 2.35), (6.9, 3.92))
    box(ax, 10.35, 1.95, 1.4, .85, '重复系统航迹\n连续3帧则合并')
    arrow(ax, (11.05, 3.92), (11.05, 2.83))
    ax.text(6, .78,
            '关联与确认均按帧递推，只使用当前及历史信息；主链路默认双门限，其他候选策略在同一在线框架中作对照。',
            ha='center', va='center', fontsize=9.2)
    fig.tight_layout()
    fig.savefig(OUT/'fig5_1_mewf_framework.png', dpi=220, facecolor='white', bbox_inches='tight')
    plt.close(fig)


def read_online():
    a = pd.read_csv(DATA/'online_assoc_compare_A.csv').set_index('method')
    b = pd.read_csv(DATA/'online_assoc_compare_B.csv').set_index('method')
    methods = ['nn', 'sequential', 'dualgate', 'mewf']
    assert set(methods).issubset(a.index) and set(methods).issubset(b.index)
    for table in [a, b]:
        assert (table.n_correct <= table.n_pairs).all()
        assert (table.n_wrong == table.n_pairs-table.n_correct).all()
    return methods, a.loc[methods], b.loc[methods]


def fig5_2():
    methods, a, b = read_online()
    labels = ['最近邻', '序贯', '双门限', '多证据加权']
    x = np.arange(len(methods))
    fig, ax = plt.subplots(1, 2, figsize=(9.4, 4.2), layout='constrained')
    width = .34
    for axis, metric, title, ylabel in [
        (ax[0], 'n_wrong', '（a）误配数', '误配数 / 对'),
        (ax[1], 'n_correct', '（b）正确配对数', '正确配对数 / 对')]:
        axis.bar(x-width/2, a[metric], width, facecolor='white', edgecolor='black',
                 linewidth=1.0, hatch='///', label='在线对照 A')
        axis.bar(x+width/2, b[metric], width, facecolor='.65', edgecolor='black',
                 linewidth=1.0, label='在线对照 B')
        axis.set_xticks(x, labels)
        axis.set_title(title)
        axis.set_ylabel(ylabel)
        axis.grid(axis='y', linestyle=':', color='.82')
        axis.legend(frameon=False, fontsize=8.5)
    fig.suptitle('两组在线策略对照：带门限方法结果接近，最近邻出现误配', fontsize=11)
    fig.savefig(OUT/'fig5_2_method_compare.png', dpi=220, facecolor='white', bbox_inches='tight')
    plt.close(fig)


def confirmation_stats():
    gate = chi2.ppf(.95, 2)
    p1 = chi2.cdf(gate, 2)
    rows = []
    for m in range(4, 9):
        p0star = brentq(lambda p: binom.sf(m-1, 8, p)-.05, 1e-8, 1-1e-8)
        lam = brentq(lambda z: ncx2.cdf(gate, 2, z)-p0star, 1e-9, 1e3)
        rows.append({'M': m, 'N': 8, 'beta': binom.sf(m-1, 8, p1),
                     'p0_star': p0star, 'delta_min_sigma': np.sqrt(lam)})
    return pd.DataFrame(rows)


def fig5_3():
    table = confirmation_stats()
    table.to_csv(DATA/'confirmation_sweep.csv', index=False)
    fig, ax1 = plt.subplots(figsize=(7.5, 4.2), layout='constrained')
    x = table.M.to_numpy()
    ax1.plot(x, table.beta, color='black', marker='o', lw=1.3,
             label='同源检出概率 β')
    ax1.set_xlabel('8帧窗口内的确认帧数 M')
    ax1.set_ylabel('同源检出概率 β')
    ax1.set_ylim(.55, 1.03)
    ax1.set_xticks(x)
    ax1.grid(ls=':', color='.82')
    ax2 = ax1.twinx()
    ax2.plot(x, table.delta_min_sigma, color='.4', marker='s', ls='--', lw=1.2,
             label='5%假确认约束下的最小可分辨偏移')
    ax2.set_ylabel('最小可分辨偏移 / σ')
    ax1.axvline(6, color='.2', ls=':', lw=1)
    ax1.scatter([6], [table.loc[table.M == 6, 'beta'].iloc[0]],
                facecolors='white', edgecolors='black', s=58, zorder=4)
    lines = ax1.get_lines()[:1] + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], loc='center left',
               frameon=False, fontsize=8.5)
    ax1.set_title('6/8确认规则的检出率与判别力折中')
    fig.savefig(OUT/'fig5_3_decompose.png', dpi=220, facecolor='white', bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    fig5_1()
    fig5_2()
    fig5_3()
    print('PASS: generated three figures from online result snapshots and confirmation model')
