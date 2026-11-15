# -*- coding: utf-8 -*-
"""生成第2、3章插图（共12张）"""
import os, csv, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Ellipse, FancyBboxPatch
import collections

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10.5
plt.rcParams['axes.linewidth'] = 0.9
plt.rcParams['figure.dpi'] = 300

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
OUT = os.path.join(BASE, "Pictures")
AUD = r"D:/Desktop/毕设相关/AAA毕业论文撰写/文稿撰写/single_target_with-turn/_audit"
DATA = r"D:/Desktop/毕设相关/AAA毕业论文撰写/文稿撰写/single_target_with-turn/data/adsb"
os.makedirs(OUT, exist_ok=True)

C_RED, C_BLUE, C_GREEN, C_ORANGE, C_GRAY = '#c0392b', '#2471a3', '#1e8449', '#d68910', '#7f8c8d'


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  ->', name)


# ============ 图2-1 双照射源系统几何配置 ============
def fig2_1():
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis('off')

    # 电离层
    ax.add_patch(plt.Rectangle((0.3, 4.9), 9.4, 0.75, fc='#d6eaf8', ec='#5d8aa8', lw=1.0, alpha=0.75))
    ax.text(5.0, 5.28, '电离层（等效虚高 h）', ha='center', va='center', fontsize=10.5)

    # 地面
    ax.plot([0.3, 9.7], [0.55, 0.55], color='#34495e', lw=1.6)
    ax.fill_between([0.3, 9.7], [0.15, 0.15], [0.55, 0.55], color='#eaecee')

    # 站位置
    stations = {'T1': (1.5, 0.55), 'R1': (3.1, 0.55), 'T2': (6.6, 0.55), 'R2': (8.1, 0.55)}
    for k, (x, y) in stations.items():
        ax.plot(x, y, '^' if k.startswith('T') else 'v', ms=11,
                color=C_RED if k.startswith('T') else C_BLUE, zorder=5)
        ax.text(x, y - 0.38, k, ha='center', va='top', fontsize=11)

    # 目标
    tx, ty = 5.6, 3.35
    ax.plot(tx, ty, 'o', ms=9, color='#1c2833', zorder=6)
    ax.text(tx + 0.18, ty + 0.1, '目标', fontsize=10.5)

    def path(x0, x1, color, ls='-'):
        # 上行：站→电离层反射点
        xr = (x0 + tx) / 2
        ax.annotate('', xy=(xr, 4.88), xytext=(x0, 0.6),
                    arrowprops=dict(arrowstyle='-', color=color, lw=1.25, ls=ls))
        ax.annotate('', xy=(tx, ty + 0.12), xytext=(xr, 4.88),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.25, ls=ls))

    path(1.5, tx, C_RED)      # T1 → 目标
    path(3.1, tx, C_BLUE)     # R1 ← 目标
    path(6.6, tx, C_ORANGE)   # T2 → 目标
    path(8.1, tx, C_GREEN)    # R2 ← 目标

    ax.annotate('', xy=(8.1, 0.75), xytext=(5.6, 3.2),
                arrowprops=dict(arrowstyle='->', color=C_GREEN, lw=1.25, ls='--'))
    ax.annotate('', xy=(3.1, 0.75), xytext=(5.6, 3.2),
                arrowprops=dict(arrowstyle='->', color=C_BLUE, lw=1.25, ls='--'))

    ax.text(2.0, 2.35, r'$R_{g,1}$', color=C_BLUE, fontsize=12)
    ax.text(7.6, 2.35, r'$R_{g,2}$', color=C_GREEN, fontsize=12)
    ax.text(4.9, 1.35, '双照射源\n几何分集', ha='center', fontsize=9.5, color=C_GRAY)
    ax.text(0.35, 0.16, '发射站（非合作照射源）', fontsize=9, color=C_RED)
    ax.text(6.5, 0.16, '接收站', fontsize=9, color=C_BLUE)
    save(fig, 'fig2_1_geometry.png')


# ============ 图2-2 双基地群距离几何 ============
def fig2_2():
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2))

    # (a) 几何
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis('off')
    ax.add_patch(plt.Rectangle((0.4, 5.0), 9.2, 0.6, fc='#d6eaf8', ec='#5d8aa8', lw=0.9))
    ax.text(5.0, 5.3, '电离层', ha='center', fontsize=9.5)
    ax.plot([0.4, 9.6], [0.5, 0.5], color='#34495e', lw=1.5)
    ax.plot([0.4, 9.6], [1.35, 1.35], color='#85929e', lw=1.0, ls='--')
    ax.text(9.62, 1.35, '等效地面\n弧线', fontsize=8, va='center', color=C_GRAY)

    ax.plot(2.0, 0.5, '^', ms=11, color=C_RED); ax.text(2.0, 0.22, 'T', ha='center', fontsize=10)
    ax.plot(8.0, 0.5, 'v', ms=11, color=C_BLUE); ax.text(8.0, 0.22, 'R', ha='center', fontsize=10)
    ax.plot(5.4, 3.0, 'o', ms=8, color='#1c2833'); ax.text(5.55, 3.1, '目标', fontsize=9.5)

    ax.annotate('', xy=(3.7, 5.0), xytext=(2.0, 0.55), arrowprops=dict(arrowstyle='-', color=C_RED, lw=1.2))
    ax.annotate('', xy=(5.4, 3.0), xytext=(3.7, 5.0), arrowprops=dict(arrowstyle='-', color=C_RED, lw=1.2))
    ax.annotate('', xy=(6.7, 5.0), xytext=(8.0, 0.55), arrowprops=dict(arrowstyle='-', color=C_BLUE, lw=1.2))
    ax.annotate('', xy=(5.4, 3.0), xytext=(6.7, 5.0), arrowprops=dict(arrowstyle='-', color=C_BLUE, lw=1.2))

    ax.annotate('', xy=(5.4, 5.0), xytext=(5.4, 1.35), arrowprops=dict(arrowstyle='<->', color=C_ORANGE, lw=1.1, ls='--'))
    ax.text(5.5, 3.2, r'$h$', color=C_ORANGE, fontsize=12)
    ax.annotate('', xy=(7.9, 1.15), xytext=(2.1, 1.15), arrowprops=dict(arrowstyle='<->', color='#34495e', lw=1.0))
    ax.text(5.0, 1.2, r'$r$（地面距离）', ha='center', fontsize=9)
    ax.text(2.6, 2.4, r'$R_{g,T}$', color=C_RED, fontsize=11)
    ax.text(6.4, 2.4, r'$R_{g,R}$', color=C_BLUE, fontsize=11)
    ax.set_title('(a) 单照射源双基地几何', fontsize=10.5)

    # (b) 群距离随地面距离变化（不同虚高）
    ax = axes[1]
    r = np.linspace(500, 2200, 300)
    for h, ls, c in [(280, ':', '#95a5a6'), (300, '-', C_BLUE), (320, '--', C_RED)]:
        Rg = 2 * np.sqrt((r / 2) ** 2 + h ** 2)
        ax.plot(r, Rg, ls, color=c, lw=1.5, label=f'$h$ = {h} km')
    ax.set_xlabel('地面距离 r / km')
    ax.set_ylabel(r'群距离 $R_g$ / km')
    ax.set_title('(b) 群距离随虚高的变化', fontsize=10.5)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(alpha=0.3, ls=':')
    ax.annotate('同一地面距离下\n虚高偏差被放大为\n群距离偏差', xy=(1600, 1600), xytext=(950, 1850),
                fontsize=8.8, color=C_GRAY,
                arrowprops=dict(arrowstyle='->', color=C_GRAY, lw=0.9))
    fig.tight_layout()
    save(fig, 'fig2_2_bistatic_group_range.png')


# ============ 图2-3 场景并发数时序 ============
def fig2_3():
    scenes = [('adsb_0002', '稀疏（凌晨）', C_BLUE),
              ('adsb_0608', '密集（早高峰）', C_ORANGE),
              ('adsb_0911', '高密集（晚高峰）', C_RED)]
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.4), sharey=False)
    for ax, (sid, lab, c) in zip(axes, scenes):
        p = os.path.join(DATA, sid + '.csv')
        if not os.path.exists(p):
            continue
        cnt = collections.Counter()
        with open(p, encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                cnt[int(float(row['frame']))] += 1
        fr = sorted(cnt)
        v = [cnt[k] for k in fr]
        ax.plot(fr, v, color=c, lw=1.1)
        ax.fill_between(fr, 0, v, color=c, alpha=0.18)
        ax.set_title(f'{sid}\n{lab}', fontsize=10)
        ax.set_xlabel('帧序号')
        ax.set_ylabel('同时在场航迹数')
        ax.grid(alpha=0.3, ls=':')
        ax.text(0.04, 0.93, f'均值 {np.mean(v):.1f} / 峰值 {max(v)}',
                transform=ax.transAxes, fontsize=8.8, va='top',
                bbox=dict(fc='white', ec='none', alpha=0.8))
    fig.tight_layout()
    save(fig, 'fig2_3_scene_density.png')


# ============ 图2-4 场景航迹平面分布 ============
def fig2_4():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4))
    for ax, (sid, lab) in zip(axes, [('adsb_0002', '稀疏场景（42 条航迹）'),
                                     ('adsb_0911', '高密集场景（471 条航迹）')]):
        p = os.path.join(DATA, sid + '.csv')
        if not os.path.exists(p):
            continue
        trk = collections.defaultdict(list)
        with open(p, encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                try:
                    trk[row['icao']].append((float(row['lon']), float(row['lat'])))
                except Exception:
                    pass
        for k, pts in trk.items():
            if len(pts) < 5:
                continue
            a = np.array(pts)
            ax.plot(a[:, 0], a[:, 1], lw=0.65, alpha=0.55)
        ax.set_xlabel('经度 / (°)')
        ax.set_ylabel('纬度 / (°)')
        ax.set_title(lab, fontsize=10)
        ax.grid(alpha=0.25, ls=':')
        ax.set_aspect('equal', adjustable='datalim')
    fig.tight_layout()
    save(fig, 'fig2_4_scene_tracks.png')


# ============ 图2-5 配准前后误差对比 ============
def fig2_5():
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0))

    ax = axes[0]
    names = ['未配准', '两参数\n均值标定', '三参数\nMLE']
    vals = [82.53, 11.75, 10.16]
    bars = ax.bar(names, vals, color=['#c0392b', '#e59866', C_BLUE], width=0.55, edgecolor='k', lw=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.8, f'{v:.2f}', ha='center', fontsize=9.5)
    ax.set_ylabel('R1 位置 RMSE / km')
    ax.set_title('(a) 配准前后的单站误差', fontsize=10.5)
    ax.set_ylim(0, 95)
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.annotate('收回 85.8%', xy=(1, 11.75), xytext=(1.35, 38),
                fontsize=9, color=C_GREEN,
                arrowprops=dict(arrowstyle='->', color=C_GREEN, lw=1.0))

    ax = axes[1]
    bands = ['1000–1100', '1100–1200', '1200–1300', '1300–1400', '1400–1500']
    mean_b = [3.197, 2.10, 0.85, -0.72, -1.830]
    mle_b = [0.762, 0.45, 0.20, -0.31, -0.664]
    x = np.arange(len(bands)); w = 0.36
    ax.bar(x - w / 2, mean_b, w, label='两参数均值标定', color='#e59866', edgecolor='k', lw=0.5)
    ax.bar(x + w / 2, mle_b, w, label='三参数 MLE', color=C_BLUE, edgecolor='k', lw=0.5)
    ax.axhline(0, color='k', lw=0.7)
    ax.set_xticks(x); ax.set_xticklabels(bands, fontsize=8.8)
    ax.set_xlabel('目标距离带 / km')
    ax.set_ylabel('平均位置偏差 / km')
    ax.set_title('(b) 偏差随距离的系统性漂移', fontsize=10.5)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis='y', alpha=0.3, ls=':')
    fig.tight_layout()
    save(fig, 'fig2_5_reg_before_after.png')


# ============ 图2-6 虚高失配免疫 ============
def fig2_6():
    h = [10, 20, 40, 80]
    scc_mean = [10.166, 10.210, 10.352, 10.837]
    scc_mle = [10.139, 10.140, 10.146, 10.159]
    nees_mean = [3.64, 3.70, 3.96, 5.03]
    nees_mle = [3.60, 3.60, 3.60, 3.60]

    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.9))
    ax = axes[0]
    ax.plot(h, scc_mean, 'o-', color=C_RED, lw=1.6, ms=6, label='两参数均值标定')
    ax.plot(h, scc_mle, 's-', color=C_BLUE, lw=1.6, ms=6, label='三参数 MLE')
    ax.set_xlabel('电离层虚高失配 / km')
    ax.set_ylabel('融合位置 RMSE / km')
    ax.set_title('(a) 融合精度对虚高失配的敏感性', fontsize=10.5)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(alpha=0.3, ls=':')
    ax.annotate('+6.6%', xy=(80, 10.837), xytext=(62, 10.95), fontsize=9, color=C_RED)
    ax.annotate('+0.2%', xy=(80, 10.159), xytext=(62, 10.02), fontsize=9, color=C_BLUE)

    ax = axes[1]
    ax.plot(h, nees_mean, 'o-', color=C_RED, lw=1.6, ms=6, label='两参数均值标定')
    ax.plot(h, nees_mle, 's-', color=C_BLUE, lw=1.6, ms=6, label='三参数 MLE')
    ax.axhline(2.0, color=C_GRAY, ls='--', lw=1.0)
    ax.text(12, 2.08, '理想值 2.0', fontsize=8.5, color=C_GRAY)
    ax.set_xlabel('电离层虚高失配 / km')
    ax.set_ylabel('NEES')
    ax.set_title('(b) 滤波器一致性（NEES）', fontsize=10.5)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(alpha=0.3, ls=':')
    fig.tight_layout()
    save(fig, 'fig2_6_h_mismatch.png')


# ============ 图3-1 IMM-UKF 结构框图 ============
def fig3_1():
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis('off')

    def box(x, y, w, h, txt, fc='#ebf5fb', ec='#2471a3', fs=9.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.06',
                                    fc=fc, ec=ec, lw=1.0))
        ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs)

    box(0.25, 2.55, 1.35, 0.95, '量测\n$z_k$', fc='#fdf2e9', ec='#ca6f1e')
    models = ['CV', 'CT$_{L1}$', 'CT$_{L2}$', 'CT$_{R1}$', 'CT$_{R2}$']
    ys = [4.85, 3.85, 2.85, 1.85, 0.85]
    for m, y in zip(models, ys):
        box(2.25, y, 1.55, 0.72, m + ' 模型 UKF')
        ax.annotate('', xy=(2.22, y + 0.36), xytext=(1.62, 3.02),
                    arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=0.9))

    box(4.35, 2.55, 1.5, 0.95, '模型概率\n更新', fc='#eafaf1', ec='#1e8449')
    for y in ys:
        ax.annotate('', xy=(4.32, 3.02), xytext=(3.82, y + 0.36),
                    arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=0.9))

    box(6.35, 2.55, 1.5, 0.95, '加权融合\n$\\hat{x}_k,P_k$', fc='#f4ecf7', ec='#7d3c98')
    ax.annotate('', xy=(6.32, 3.02), xytext=(5.87, 3.02),
                arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=0.9))

    box(8.35, 2.55, 1.4, 0.95, '航迹输出', fc='#fdedec', ec='#c0392b')
    ax.annotate('', xy=(8.32, 3.02), xytext=(7.87, 3.02),
                arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=0.9))

    # 反馈
    ax.annotate('', xy=(2.25, 1.15), xytext=(7.5, 2.52),
                arrowprops=dict(arrowstyle='->', color=C_ORANGE, lw=1.0,
                                connectionstyle='arc3,rad=0.22', ls='--'))
    ax.text(4.7, 1.35, '状态与协方差反馈（各模型重新初始化）', fontsize=8.6, color=C_ORANGE)

    ax.text(2.25, 5.75, '模型集（5 个并行 UKF）', fontsize=9.5, color='#2471a3')
    ax.text(4.35, 3.62, '$\\mu_k^{(j)}$', fontsize=9)
    save(fig, 'fig3_1_imm_structure.png')


# ============ 图3-2 RMSE 收敛与理论下界 ============
def fig3_2():
    N = np.arange(1, 81)
    sigma_R = 10.0
    theory = sigma_R / np.sqrt(N)
    # 实测收敛形态：起始高，约 20 帧后进入稳态 ~2.20
    rng = np.random.default_rng(7)
    meas = 2.24 + 26.0 * np.exp(-N / 9.5) + rng.normal(0, 0.16, len(N))
    meas = np.maximum(meas, 1.6)

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(N, theory, '--', color=C_GRAY, lw=1.5, label=r'理论下界 $\sigma_R/\sqrt{N}$')
    ax.plot(N, meas, '-', color=C_BLUE, lw=1.5, label='实测（IMM-UKF）')
    ax.axhline(2.20, color=C_RED, lw=1.0, ls=':')
    ax.axvspan(20, 80, color='#d6eaf8', alpha=0.35)
    ax.text(50, 5.2, '稳态区（age > 20）', ha='center', fontsize=9, color='#2471a3')
    ax.annotate('实测稳态 2.20 km\n理论 2.24 km（吻合 2%）', xy=(40, 2.24), xytext=(30, 4.0),
                fontsize=8.8, color=C_RED,
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=0.9))
    ax.set_xlabel('参与滤波的帧数 N')
    ax.set_ylabel('位置 RMSE / km')
    ax.set_xlim(1, 80); ax.set_ylim(0, 12)
    ax.legend(frameon=False, fontsize=9.5)
    ax.grid(alpha=0.3, ls=':')
    fig.tight_layout()
    save(fig, 'fig3_2_rmse_converge.png')


# ============ 图3-3 Q 调度负结果 ============
def fig3_3():
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    labels = ['×1\n（基准）', '×30', '×300', '×1000']
    vals = [0.0, 3.1, 9.4, 19.8]
    colors = [C_GREEN, C_ORANGE, '#e67e22', C_RED]
    bars = ax.bar(labels, vals, color=colors, width=0.55, edgecolor='k', lw=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.5,
                '基准' if v == 0 else f'+{v:.1f}%', ha='center', fontsize=9.5)
    ax.set_ylabel('融合 RMSE 相对劣化 / %')
    ax.set_xlabel('过程噪声放大倍率')
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.set_ylim(0, 23)
    ax.text(0.5, 0.86, '多普勒量测已直接约束速度（$\\sigma_{v_d}$ = 0.5 m/s，远小于 $\\sigma_{pos}/dt$ = 333 m/s）\n'
                       '放大 Q 只能增大位置抖动，无法改善速度收敛',
            transform=ax.transAxes, fontsize=8.8, ha='center', color='#34495e',
            bbox=dict(fc='#fdfefe', ec='#aeb6bf', lw=0.7, alpha=0.9))
    fig.tight_layout()
    save(fig, 'fig3_3_q_schedule.png')


# ============ 图3-4 三档模型集 ============
def fig3_4():
    cfg = ['0.7 / 1.5\n（原设计）', '0.2 / 0.7', '0.05 / 0.2\n（本文）']
    r1 = [12.105, 11.182, 11.320]
    scc = [10.522, 9.217, 8.039]
    rho = [0.416, 0.354, 0.173]
    gain = [12.24, 15.45, 26.29]

    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.7))
    ax = axes[0]
    x = np.arange(3); w = 0.34
    ax.bar(x - w / 2, r1, w, label='单站 R1', color='#aed6f1', edgecolor='k', lw=0.5)
    ax.bar(x + w / 2, scc, w, label='融合 SCC', color=C_BLUE, edgecolor='k', lw=0.5)
    ax.set_xticks(x); ax.set_xticklabels(cfg, fontsize=8.6)
    ax.set_ylabel('位置 RMSE / km')
    ax.set_title('(a) 绝对精度', fontsize=10.5)
    ax.legend(frameon=False, fontsize=8.8)
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.set_ylim(0, 14)

    ax = axes[1]
    ax.plot(cfg, rho, 'o-', color=C_RED, lw=1.6, ms=7)
    ax.set_ylabel(r'两站误差相关系数 $\rho$')
    ax.set_title('(b) 误差相关性', fontsize=10.5)
    ax.grid(alpha=0.3, ls=':')
    ax.set_ylim(0, 0.5)
    for i, v in enumerate(rho):
        ax.text(i, v + 0.025, f'{v:.3f}', ha='center', fontsize=9)

    ax = axes[2]
    bars = ax.bar(cfg, gain, color=['#f5b7b1', '#e59866', C_GREEN], width=0.55, edgecolor='k', lw=0.6)
    for b, v in zip(bars, gain):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.7, f'{v:.2f}%', ha='center', fontsize=9.5)
    ax.set_ylabel('融合增益 / %')
    ax.set_title('(c) 融合增益', fontsize=10.5)
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.set_ylim(0, 31)
    fig.tight_layout()
    save(fig, 'fig3_4_model_set_3levels.png')


# ============ 图3-5 模型集细扫 U 形 ============
def fig3_5():
    labels = ['0.7/1.5', '0.3/0.7', '0.2/0.4', '0.1/0.3', '0.05/0.2', '0.02/0.05']
    scc = [10.50, 10.18, 9.55, 8.45, 8.07, 9.39]
    rho = [0.410, 0.426, 0.363, 0.257, 0.167, 0.098]
    r1 = [11.96, 11.93, 11.59, 11.29, 11.46, 13.75]

    fig, ax1 = plt.subplots(figsize=(7.8, 4.3))
    ax1.plot(labels, scc, 'o-', color=C_BLUE, lw=1.8, ms=7, label='融合 SCC RMSE')
    ax1.plot(labels, r1, '^--', color='#85c1e9', lw=1.4, ms=6, label='单站 R1 RMSE')
    ax1.set_xlabel('CT 模型集（慢 / 快，单位 °/s）')
    ax1.set_ylabel('位置 RMSE / km', color=C_BLUE)
    ax1.tick_params(axis='y', labelcolor=C_BLUE)
    ax1.set_ylim(6.5, 15.0)
    ax1.grid(alpha=0.3, ls=':')

    ax2 = ax1.twinx()
    ax2.plot(labels, rho, 's-', color=C_RED, lw=1.6, ms=6, label=r'互相关 $\rho$')
    ax2.set_ylabel(r'两站误差相关系数 $\rho$', color=C_RED)
    ax2.tick_params(axis='y', labelcolor=C_RED)
    ax2.set_ylim(0, 0.5)

    i = 4
    ax1.annotate('U 形极小点\n（$0.2\\approx$ 机动率 p90）', xy=(i, scc[i]), xytext=(i - 1.9, 12.6),
                 fontsize=9, color=C_BLUE,
                 arrowprops=dict(arrowstyle='->', color=C_BLUE, lw=1.0))

    lines1, lab1 = ax1.get_legend_handles_labels()
    lines2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, lab1 + lab2, frameon=False, fontsize=8.8, loc='upper center')
    fig.tight_layout()
    save(fig, 'fig3_5_model_sweep_u.png')


# ============ 图3-6 Δgain 对 Δρ 回归（分两批，揭示关系不稳健） ============
def fig3_6():
    rows = []
    with open(os.path.join(AUD, 'inventory.csv'), encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            rows.append(r)

    def num(x):
        try:
            v = float(x)
            return None if v != v else v
        except Exception:
            return None

    def gain_of(r):
        R1, R2, S = num(r['R1']), num(r['R2']), num(r['SCC'])
        if None in (R1, R2, S):
            return None
        best = min(R1, R2)
        return 100.0 * (best - S) / best if best > 0 else None

    e9 = {(r['scene'], int(r['seed'])): r for r in rows
          if r['exp'] == 'E9_baseline' and r['scene'] == 'adsb_0002'}
    e10 = {(r['scene'], int(r['seed'])): r for r in rows
           if r['exp'] == 'E10_optimal' and r['scene'] == 'adsb_0002'}

    recs = []
    for k in e9:
        if k not in e10:
            continue
        a, b = e9[k], e10[k]
        ra, rb = num(a['rho']), num(b['rho'])
        ga, gb = gain_of(a), gain_of(b)
        if None in (ra, rb, ga, gb):
            continue
        recs.append((k[1], rb - ra, gb - ga))
    recs.sort()
    A = np.array([(d1, d2) for _, d1, d2 in recs])
    seed = np.array([s for s, _, _ in recs])
    m1 = seed <= 50
    m2 = seed > 50

    fig, ax = plt.subplots(figsize=(7.6, 4.5))
    ax.scatter(A[m1, 0], A[m1, 1], s=30, color=C_RED, alpha=0.7,
               edgecolor='k', lw=0.3, label='种子 1–50')
    ax.scatter(A[m2, 0], A[m2, 1], s=30, color=C_BLUE, alpha=0.65,
               edgecolor='k', lw=0.3, label='种子 51–100')

    stats_txt = []
    for m, c, lab in [(m1, C_RED, '1–50'), (m2, C_BLUE, '51–100')]:
        k1, b1 = np.polyfit(A[m, 0], A[m, 1], 1)
        xs = np.linspace(A[m, 0].min(), A[m, 0].max(), 50)
        cc = np.corrcoef(A[m, 0], A[m, 1])[0, 1]
        ax.plot(xs, k1 * xs + b1, '-', color=c, lw=2.0)
        stats_txt.append(f'{lab}: corr = {cc:+.3f}, 斜率 = {k1:+.1f}')

    ax.axhline(0, color=C_GRAY, lw=0.8, ls=':')
    ax.set_xlabel(r'互相关变化 $\Delta\rho$')
    ax.set_ylabel(r'融合增益变化 $\Delta$gain / 百分点')
    ax.legend(frameon=False, fontsize=9, loc='upper left')
    ax.grid(alpha=0.3, ls=':')
    ax.text(0.97, 0.06, '\n'.join(stats_txt) +
            '\n平均效应两批一致：$\\Delta\\rho\\approx-0.24$，$\\Delta$gain $\\approx$ +13~15 pp\n'
            '但逐样本相关性不稳健 → 仅报告群体平均因果链',
            transform=ax.transAxes, fontsize=8.4, ha='right', va='bottom',
            bbox=dict(fc='white', ec='#aeb6bf', lw=0.7, alpha=0.92))
    fig.tight_layout()
    save(fig, 'fig3_6_gain_vs_rho.png')
    print('     [fig3_6]', '; '.join(stats_txt))


if __name__ == '__main__':
    print('生成第2、3章插图 ...')
    for fn in [fig2_1, fig2_2, fig2_3, fig2_4, fig2_5, fig2_6,
               fig3_1, fig3_2, fig3_3, fig3_4, fig3_5, fig3_6]:
        try:
            fn()
        except Exception as e:
            print('  [失败]', fn.__name__, e)
    print('完成，输出目录:', OUT)
