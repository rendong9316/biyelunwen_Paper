# -*- coding: utf-8 -*-
"""生成第4、5章插图（共10张）"""
import os, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10.5
plt.rcParams['axes.linewidth'] = 0.9
plt.rcParams['figure.dpi'] = 300

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
OUT = os.path.join(BASE, "Pictures")
AUD = r"D:/Desktop/毕设相关/AAA毕业论文撰写/文稿撰写/single_target_with-turn/_audit"
os.makedirs(OUT, exist_ok=True)

C_RED, C_BLUE, C_GREEN, C_ORANGE, C_GRAY, C_PURPLE = \
    '#c0392b', '#2471a3', '#1e8449', '#d68910', '#7f8c8d', '#7d3c98'


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  ->', name)


def load(fn):
    with open(os.path.join(AUD, fn), encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def agg(rows, key, fields):
    """按 key 分组求均值"""
    out = {}
    for r in rows:
        k = r[key]
        out.setdefault(k, {f: [] for f in fields})
        for f in fields:
            try:
                v = float(r[f])
                if v == v:
                    out[k][f].append(v)
            except Exception:
                pass
    return {k: {f: (np.mean(v) if v else np.nan) for f, v in d.items()} for k, d in out.items()}


# ============ 图4-1 候选对数随并发数增长 ============
def fig4_1():
    n = np.arange(2, 85)
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(n, n ** 2, '-', color=C_BLUE, lw=1.8, label=r'候选组合数 $N^2$')
    pts = [(6.2, 36, '稀疏场景\n（adsb_0002）', C_GREEN),
           (28.1, 784, '密集场景\n（adsb_0608）', C_ORANGE),
           (63.1, 3969, '高密集场景\n（adsb_0911）', C_RED)]
    for x, y, lab, c in pts:
        ax.plot(x, y, 'o', ms=9, color=c, mec='k', mew=0.6, zorder=5)
        ax.annotate(lab, xy=(x, y), xytext=(x + 5, y * 0.55),
                    fontsize=8.6, color=c,
                    arrowprops=dict(arrowstyle='->', color=c, lw=0.9))
    ax.set_xlabel('同时在场航迹数 N')
    ax.set_ylabel('候选配对组合数')
    ax.set_yscale('log')
    ax.legend(frameon=False, fontsize=9.5, loc='upper left')
    ax.grid(alpha=0.3, ls=':')
    ax.text(0.97, 0.06, '并发数从 6 增至 63，候选组合数增长约 110 倍\n'
                        '关联歧义随密度呈平方律恶化',
            transform=ax.transAxes, fontsize=8.8, ha='right',
            bbox=dict(fc='white', ec='#aeb6bf', lw=0.7, alpha=0.9))
    fig.tight_layout()
    save(fig, 'fig4_1_candidate_pairs.png')


# ============ 图4-2 M 扫描跷跷板 ============
def fig4_2():
    rows = load('m_sweep.csv')
    a = agg(rows, 'M', ['n_wrong', 'n_missed', 'precision', 'recall'])
    Ms = sorted(a, key=lambda x: int(x))
    wrong = [a[m]['n_wrong'] for m in Ms]
    missed = [a[m]['n_missed'] for m in Ms]
    prec = [a[m]['precision'] for m in Ms]
    rec = [a[m]['recall'] for m in Ms]

    fig, ax1 = plt.subplots(figsize=(7.8, 4.4))
    x = np.arange(len(Ms)); w = 0.36
    b1 = ax1.bar(x - w / 2, wrong, w, color=C_RED, edgecolor='k', lw=0.5, label='误配数')
    b2 = ax1.bar(x + w / 2, missed, w, color=C_BLUE, edgecolor='k', lw=0.5, label='漏配数')
    ax1.set_xticks(x); ax1.set_xticklabels([f'M={m}' for m in Ms])
    ax1.set_xlabel('连续确认帧数门限 M')
    ax1.set_ylabel('配对数（个）')
    ax1.grid(axis='y', alpha=0.3, ls=':')
    ax1.set_ylim(0, 65)

    ax2 = ax1.twinx()
    ax2.plot(x, prec, 'o--', color=C_GREEN, lw=1.5, ms=6, label='查准率 P')
    ax2.plot(x, rec, 's--', color=C_ORANGE, lw=1.5, ms=6, label='查全率 R')
    ax2.set_ylabel('查准率 / 查全率')
    ax2.set_ylim(0.78, 1.0)

    for i, (v1, v2) in enumerate(zip(wrong, missed)):
        ax1.text(i - w / 2, v1 + 1.2, f'{v1:.1f}', ha='center', fontsize=8.4)
        ax1.text(i + w / 2, v2 + 1.2, f'{v2:.1f}', ha='center', fontsize=8.4)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8.8, loc='upper center', ncol=2)
    ax1.text(0.5, -0.24, 'M 增大：误配单调下降，漏配单调上升，查全率随之跌落——不存在使两者同时最优的 M',
             transform=ax1.transAxes, fontsize=8.8, ha='center', color='#34495e')
    fig.tight_layout()
    save(fig, 'fig4_2_m_sweep.png')


# ============ 图4-3 四方法 P/R 对比 ============
def fig4_3():
    dense = load('mewf_compare.csv')
    sparse = load('mewf_sparse.csv')

    name_map = {'NN': 'NN', 'Sequential': 'Sequential',
                'DualGate_M8': '三判据M=8', 'MEWF_hungarian': 'MEWF'}
    dense_sel = [r for r in dense if r['method'] in name_map]
    ad = agg(dense_sel, 'method', ['precision', 'recall', 'n_wrong', 'n_missed'])

    sp_map = {'NN': 'NN', 'Sequential': 'Sequential',
              'DualGate_M8': '三判据M=8', 'MEWF': 'MEWF'}
    sparse_sel = [r for r in sparse if r['method'] in sp_map]
    asp = agg(sparse_sel, 'method', ['precision', 'recall'])

    order = ['NN', 'Sequential', 'DualGate_M8', 'MEWF_hungarian']
    labels = [name_map[k] for k in order]

    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.3))

    # (a) P-R 平面
    ax = axes[0]
    mk = {'NN': 'o', 'Sequential': 's', 'DualGate_M8': '^', 'MEWF_hungarian': 'D'}
    cl = {'NN': C_GRAY, 'Sequential': C_ORANGE, 'DualGate_M8': C_BLUE, 'MEWF_hungarian': C_RED}
    for k in order:
        if k not in ad:
            continue
        ax.scatter(ad[k]['recall'], ad[k]['precision'], s=130, marker=mk[k],
                   color=cl[k], edgecolor='k', lw=0.7, zorder=5, label=name_map[k])
        ax.annotate(name_map[k], xy=(ad[k]['recall'], ad[k]['precision']),
                    xytext=(6, -12), textcoords='offset points', fontsize=8.6, color=cl[k])
    ax.set_xlabel('查全率 R')
    ax.set_ylabel('查准率 P')
    ax.set_title('(a) 密集场景（5 组平均）', fontsize=10.5)
    ax.grid(alpha=0.3, ls=':')
    ax.set_xlim(0.83, 0.96)
    ax.set_ylim(0.935, 0.985)

    # (b) 误配/漏配
    ax = axes[1]
    x = np.arange(len(order)); w = 0.36
    wr = [ad[k]['n_wrong'] for k in order]
    ms = [ad[k]['n_missed'] for k in order]
    ax.bar(x - w / 2, wr, w, color=C_RED, edgecolor='k', lw=0.5, label='误配')
    ax.bar(x + w / 2, ms, w, color=C_BLUE, edgecolor='k', lw=0.5, label='漏配')
    for i, (a1, a2) in enumerate(zip(wr, ms)):
        ax.text(i - w / 2, a1 + 0.7, f'{a1:.1f}', ha='center', fontsize=8.4)
        ax.text(i + w / 2, a2 + 0.7, f'{a2:.1f}', ha='center', fontsize=8.4)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel('错误配对数（个）')
    ax.set_title('(b) 错误构成', fontsize=10.5)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.set_ylim(0, 56)
    fig.tight_layout()
    save(fig, 'fig4_3_method_compare.png')
    return ad, asp


# ============ 图4-4 MEWF 分层框图 ============
def fig4_4():
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    ax.set_xlim(0, 10.2); ax.set_ylim(0, 6.6); ax.axis('off')

    def box(x, y, w, h, txt, fc, ec, fs=8.8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.07', fc=fc, ec=ec, lw=1.0))
        ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs)

    # 输入
    box(0.15, 2.95, 1.42, 0.95, '对齐后的\n双站快照', '#fdf2e9', '#ca6f1e', 8.8)

    # 判定层
    ax.add_patch(FancyBboxPatch((2.02, 1.42), 4.05, 3.85, boxstyle='round,pad=0.10',
                                fc='#eaf4fb', ec='#2471a3', lw=1.2, ls='--'))
    ax.text(4.05, 4.98, '判定层：全共现区间四证据累积', ha='center', fontsize=9.4, color='#2471a3')

    feats = [('距离证据 $E_d$', r'$\mathrm{mean}_k\,e^{-d_k^2/2\sigma^2}$', 4.22),
             ('马氏证据 $E_m$', r'$\mathrm{mean}_k\,\mathbf{1}[D_k^2<\chi^2_{thr}]$', 3.62),
             ('速度证据 $E_v$', r'$\mathrm{mean}_k\,\mathbf{1}[\Delta v_k<\kappa\tau_k]$', 3.02),
             ('连续证据 $E_c$', r'最长合格段 / 共现帧数', 2.42)]
    for name, expr, y in feats:
        box(2.18, y, 1.72, 0.46, name, '#ffffff', '#5d8aa8', 8.2)
        ax.text(4.00, y + 0.23, expr, fontsize=7.6, va='center')

    # 综合得分（含判决）
    box(6.38, 3.95, 1.62, 1.05,
        '综合得分\n$S=\\sum w_iE_i/\\sum w_i$\n$S\\geq S_{thr}$ 判决',
        '#f4ecf7', '#7d3c98', 7.8)

    # 指派层
    ax.add_patch(FancyBboxPatch((6.30, 1.42), 3.55, 1.92, boxstyle='round,pad=0.10',
                                fc='#fdedec', ec='#c0392b', lw=1.2, ls='--'))
    ax.text(8.07, 3.12, '指派层：全局最优 1v1', ha='center', fontsize=9.4, color=C_RED)
    box(6.48, 2.35, 3.20, 0.58, '代价矩阵 $C_{ij}$ = 马氏距离均值', '#ffffff', '#c0392b', 8.2)
    box(6.48, 1.62, 3.20, 0.58, '匈牙利算法求全局最优指派', '#ffffff', '#c0392b', 8.2)

    # 输出
    box(8.45, 4.85, 1.55, 0.85, '配对输出\n+ 综合得分', '#eafaf1', '#1e8449', 8.4)

    # 箭头
    ax.annotate('', xy=(1.99, 3.42), xytext=(1.60, 3.42),
                arrowprops=dict(arrowstyle='->', color='#34495e', lw=1.2))
    ax.annotate('', xy=(6.35, 4.42), xytext=(6.10, 4.42),
                arrowprops=dict(arrowstyle='->', color='#34495e', lw=1.2))
    ax.annotate('', xy=(7.19, 3.40), xytext=(7.19, 3.92),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=1.1, ls='--'))
    ax.text(7.30, 3.60, '候选集', fontsize=7.6, color=C_RED)
    ax.annotate('', xy=(8.42, 5.15), xytext=(8.02, 4.55),
                arrowprops=dict(arrowstyle='->', color='#34495e', lw=1.2))
    ax.annotate('', xy=(8.42, 5.30), xytext=(9.60, 3.38),
                arrowprops=dict(arrowstyle='->', color='#34495e', lw=1.2,
                                connectionstyle='arc3,rad=-0.18'))

    ax.text(5.1, 0.82, '与三判据的本质差别：不再有"连续 M 帧"硬约束，连续性与速度判据由否决门槛降级为可加权的证据',
            ha='center', fontsize=8.6, color='#34495e')
    save(fig, 'fig4_4_mewf_framework.png')


# ============ 图4-5 优势来源拆解 ============
def fig4_5():
    cfg = ['Seq r=0.80\ngreedy\n（原基线）', 'Seq r=0.80\nhungarian\n（换指派）',
           'Seq r=0.50\nhungarian\n（再松门限）', 'MEWF\nS=0.40\n（软融合）']
    cost = [67.20, 56.00, 51.40, 49.40]

    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    colors = [C_GRAY, C_BLUE, C_ORANGE, C_GREEN]
    bars = ax.bar(cfg, cost, color=colors, width=0.58, edgecolor='k', lw=0.6)
    for b, v in zip(bars, cost):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.2, f'{v:.2f}', ha='center', fontsize=9.5)

    deltas = [('-11.20\n(63%)', 0), ('-5.00\n(28%)', 1), ('-2.00\n(11%)', 2)]
    for txt, i in deltas:
        ax.annotate('', xy=(i + 1, cost[i + 1] + 0.5), xytext=(i + 1, cost[i] + 0.5),
                    arrowprops=dict(arrowstyle='->', color=C_RED, lw=1.6))
        ax.text(i + 1.02, (cost[i] + cost[i + 1]) / 2, txt, fontsize=8.4, color=C_RED, va='center')

    ax.set_ylabel('加权代价（5×误配 + 漏配）')
    ax.set_ylim(0, 78)
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.text(0.5, -0.26, '全局最优指派贡献最大（63%），门限软化次之（28%），距离证据的连续加权贡献最小（11%）',
            transform=ax.transAxes, fontsize=8.8, ha='center', color='#34495e')
    fig.tight_layout()
    save(fig, 'fig4_5_decompose.png')


# ============ 图4-6 特征消融 P-R 曲线 ============
def fig4_6():
    rows = load('mewf_pr_curve.csv')
    cmap = {'full': ('完整四特征', C_RED, 'o'),
            'no_dist': ('去距离证据', C_BLUE, 's'),
            'no_maha': ('去马氏证据', C_GREEN, '^'),
            'no_vel': ('去速度证据', C_ORANGE, 'v'),
            'no_cont': ('去连续性证据', C_PURPLE, 'D')}

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.3))
    ax = axes[0]
    for k, (lab, c, m) in cmap.items():
        sel = sorted([r for r in rows if r['config'] == k], key=lambda r: float(r['s_thr']))
        if not sel:
            continue
        xs = [float(r['avg_recall']) for r in sel]
        ys = [float(r['avg_precision']) for r in sel]
        ax.plot(xs, ys, m + '-', color=c, lw=1.4, ms=5, label=lab, alpha=0.85)
    ax.set_xlabel('查全率 R')
    ax.set_ylabel('查准率 P')
    ax.set_title('(a) 各配置的 P-R 曲线', fontsize=10.5)
    ax.legend(frameon=False, fontsize=8.2)
    ax.grid(alpha=0.3, ls=':')

    ax = axes[1]
    sthr = sorted({float(r['s_thr']) for r in rows})
    for k, (lab, c, m) in cmap.items():
        sel = {float(r['s_thr']): r for r in rows if r['config'] == k}
        ys = [float(sel[s]['avg_cost']) if s in sel else np.nan for s in sthr]
        ax.plot(sthr, ys, m + '-', color=c, lw=1.4, ms=5, label=lab, alpha=0.85)
    ax.set_xlabel('综合得分门限 $S_{thr}$')
    ax.set_ylabel('加权代价（5×误配 + 漏配）')
    ax.set_title('(b) 加权代价随门限的变化', fontsize=10.5)
    ax.grid(alpha=0.3, ls=':')
    ax.axvspan(0.38, 0.42, color='#d6eaf8', alpha=0.45)
    ax.text(0.40, ax.get_ylim()[1] * 0.93, '最优工作点\n（宽松端）', ha='center', fontsize=8.2, color='#2471a3')
    fig.tight_layout()
    save(fig, 'fig4_6_ablation.png')


# ============ 图5-1 四融合算法对比 ============
def fig5_1():
    algos = ['SCC', 'BC', 'CI', 'FCI']
    base = [0.890, 0.890, 0.922, 0.913]
    opt = [0.736, 0.736, 0.848, 0.764]
    worst_b = [1.008, 1.007, 1.016, 1.036]
    worst_o = [0.806, 0.805, 0.967, 0.844]

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2))
    ax = axes[0]
    x = np.arange(len(algos)); w = 0.36
    ax.bar(x - w / 2, base, w, color='#f5b7b1', edgecolor='k', lw=0.5, label='模型集 0.7/1.5')
    ax.bar(x + w / 2, opt, w, color=C_BLUE, edgecolor='k', lw=0.5, label='模型集 0.05/0.2')
    ax.axhline(1.0, color=C_GRAY, ls='--', lw=1.0)
    ax.text(3.35, 1.008, '与最优单站持平', fontsize=8.2, color=C_GRAY, ha='right')
    ax.set_xticks(x); ax.set_xticklabels(algos)
    ax.set_ylabel('融合 RMSE / 最优单站 RMSE')
    ax.set_title('(a) 平均比值（小于 1 表示优于单站）', fontsize=10.5)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.set_ylim(0.6, 1.18)

    ax = axes[1]
    ax.bar(x - w / 2, worst_b, w, color='#f5b7b1', edgecolor='k', lw=0.5, label='模型集 0.7/1.5')
    ax.bar(x + w / 2, worst_o, w, color=C_BLUE, edgecolor='k', lw=0.5, label='模型集 0.05/0.2')
    ax.axhline(1.0, color=C_GRAY, ls='--', lw=1.0)
    ax.set_xticks(x); ax.set_xticklabels(algos)
    ax.set_ylabel('最坏情况比值')
    ax.set_title('(b) 50 个种子中的最坏情况', fontsize=10.5)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.set_ylim(0.6, 1.18)
    ax.annotate('CI 最坏情况\n仍劣于单站', xy=(2.36, 0.967), xytext=(2.4, 0.72),
                fontsize=8.4, color=C_RED,
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=0.9))
    fig.tight_layout()
    save(fig, 'fig5_1_fusion_4algo.png')


# ============ 图5-2 增益与 ρ 的闭式关系 ============
def fig5_2():
    rho = np.linspace(0, 0.95, 200)
    s1, s2 = 12.06, 13.07
    sf = np.sqrt(s1 ** 2 * s2 ** 2 * (1 - rho ** 2) /
                 (s1 ** 2 + s2 ** 2 - 2 * rho * s1 * s2))
    best_single = min(s1, s2)
    gain = 100 * (best_single - sf) / best_single

    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    ax.plot(rho, gain, '-', color=C_BLUE, lw=2.0, label='理论增益上界')

    marks = [(0.416, '基线实测\n$\\rho$=0.416', C_RED),
             (0.173, '优化后实测\n$\\rho$=0.173', C_GREEN)]
    for r, lab, c in marks:
        sf0 = np.sqrt(s1 ** 2 * s2 ** 2 * (1 - r ** 2) /
                      (s1 ** 2 + s2 ** 2 - 2 * r * s1 * s2))
        g0 = 100 * (best_single - sf0) / best_single
        ax.plot(r, g0, 'o', ms=10, color=c, mec='k', mew=0.7, zorder=6)
        ax.annotate(f'{lab}\n上界 {g0:.1f}%', xy=(r, g0), xytext=(r + 0.06, g0 - 6),
                    fontsize=8.6, color=c,
                    arrowprops=dict(arrowstyle='->', color=c, lw=0.9))

    ax.axhline(0, color=C_GRAY, lw=0.8, ls=':')
    ax.set_xlabel(r'两站误差相关系数 $\rho$')
    ax.set_ylabel('融合增益上界 / %')
    ax.set_xlim(0, 0.95); ax.set_ylim(-5, 32)
    ax.legend(frameon=False, fontsize=9.5)
    ax.grid(alpha=0.3, ls=':')
    ax.text(0.60, 6.0, r'$\rho\to1$ 时增益趋于 0：' + '\n两站犯同样的错，融合无法消除',
            fontsize=8.8, color='#34495e',
            bbox=dict(fc='white', ec='#aeb6bf', lw=0.7, alpha=0.9))
    fig.tight_layout()
    save(fig, 'fig5_2_gain_rho_relation.png')


# ============ 图5-3 距离分层增益 ============
def fig5_3():
    bands = ['1200–1300', '1300–1400', '1400–1500', '1500–1700']
    gain = [11.2, 20.8, -2.3, -22.3]
    n = [150, 325, 548, 196]

    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    colors = [C_GREEN if g > 0 else C_RED for g in gain]
    bars = ax.bar(bands, gain, color=colors, width=0.55, edgecolor='k', lw=0.6, alpha=0.85)
    for b, g, nn in zip(bars, gain, n):
        off = 1.4 if g > 0 else -2.6
        ax.text(b.get_x() + b.get_width() / 2, g + off, f'{g:+.1f}%', ha='center', fontsize=9.5)
        ax.text(b.get_x() + b.get_width() / 2, 1.2 if g > 0 else -1.2,
                f'n={nn}', ha='center', fontsize=7.8, color='#34495e')
    ax.axhline(0, color='k', lw=0.9)
    ax.set_xlabel('目标地面距离 / km')
    ax.set_ylabel('融合相对最优单站的增益 / %')
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.set_ylim(-30, 27)
    ax.text(0.5, -0.27, '近距段融合有效，远距段融合有害；整体增益是"好段与坏段相互抵消"的结果',
            transform=ax.transAxes, fontsize=8.8, ha='center', color='#34495e')
    fig.tight_layout()
    save(fig, 'fig5_3_distance_band.png')


# ============ 图5-4 密度鲁棒性 ============
def fig5_4():
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.6))
    dens = ['6.2 架\n（adsb_0002）', '28.1 架\n（adsb_0608）']

    ax = axes[0]
    g = [26.1, 28.0]
    bars = ax.bar(dens, g, color=[C_BLUE, C_ORANGE], width=0.5, edgecolor='k', lw=0.6)
    for b, v in zip(bars, g):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.5, f'{v:.1f}%', ha='center', fontsize=9.5)
    ax.set_ylabel('融合增益 / %')
    ax.set_title('(a) 增益', fontsize=10)
    ax.set_ylim(0, 33)
    ax.grid(axis='y', alpha=0.3, ls=':')

    ax = axes[1]
    r = [0.174, 0.156]
    bars = ax.bar(dens, r, color=[C_BLUE, C_ORANGE], width=0.5, edgecolor='k', lw=0.6)
    for b, v in zip(bars, r):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.004, f'{v:.3f}', ha='center', fontsize=9.5)
    ax.set_ylabel(r'两站误差相关系数 $\rho$')
    ax.set_title('(b) 误差相关性', fontsize=10)
    ax.set_ylim(0, 0.21)
    ax.grid(axis='y', alpha=0.3, ls=':')

    ax = axes[2]
    sd = [1.01, 0.33]
    bars = ax.bar(dens, sd, color=[C_BLUE, C_ORANGE], width=0.5, edgecolor='k', lw=0.6)
    for b, v in zip(bars, sd):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.03, f'±{v:.2f}', ha='center', fontsize=9.5)
    ax.set_ylabel('R1 RMSE 的标准差 / km')
    ax.set_title('(c) 种子间方差', fontsize=10)
    ax.set_ylim(0, 1.2)
    ax.grid(axis='y', alpha=0.3, ls=':')
    ax.annotate('目标越多，\n统计方差越小', xy=(1, 0.33), xytext=(0.45, 0.75),
                fontsize=8.4, color=C_GREEN,
                arrowprops=dict(arrowstyle='->', color=C_GREEN, lw=0.9))
    fig.tight_layout()
    save(fig, 'fig5_4_density_robust.png')


if __name__ == '__main__':
    print('生成第4、5章插图 ...')
    for fn in [fig4_1, fig4_2, fig4_3, fig4_4, fig4_5, fig4_6,
               fig5_1, fig5_2, fig5_3, fig5_4]:
        try:
            fn()
        except Exception as e:
            import traceback
            print('  [失败]', fn.__name__, e)
            traceback.print_exc()
    print('完成')
