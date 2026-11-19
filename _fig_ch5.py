# -*- coding: utf-8 -*-
"""第5章插图：MEWF 判定—指派分层结构、四方法对比、优势拆解。

数据来源
  - single_target_with-turn/_audit/mewf_compare.csv（密集场景 adsb_0608 / adsb_0911，种子 301–303 / 401–402）
  - single_target_with-turn/_audit/mewf_decompose.csv（同上场景，正交对照）

产出
  Pictures/fig5_1_mewf_framework.png
  Pictures/fig5_2_method_compare.png
  Pictures/fig5_3_decompose.png

复现：
  cd 格式排版
  python _fig_ch5.py
"""
import os
import csv
import collections

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch

_c = ["SimHei", "Microsoft YaHei", "SimSun"]
_a = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in _c if f in _a), "DejaVu Sans")
plt.rcParams["font.sans-serif"] = [FONT]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写"
OUT = os.path.join(BASE, "格式排版", "Pictures")
AUD = os.path.join(BASE, "文稿撰写", "single_target_with-turn", "_audit")
C_RED, C_BLUE, C_GREEN, C_ORANGE, C_GRAY = "#c0392b", "#2471a3", "#1e8449", "#d68910", "#7f8c8d"


def box(ax, x, y, w, h, txt, fc="#ebf5fb", ec="#2471a3", fs=9.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fc, ec=ec, lw=1.0))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs)


def arrow(ax, p, q, color="#2c3e50"):
    ax.annotate("", xy=q, xytext=p,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.0))


def fig5_1():
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.6)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch((0.15, 2.35), 5.55, 3.55, boxstyle="round,pad=0.03",
                                fc="#fcfcfc", ec="#95a5a6", lw=1.0, ls="--"))
    ax.text(0.32, 5.55, '判定层：在全部共现区间上累积证据，回答“是否值得配对”',
            fontsize=9.5, color="0.25")

    for txt, y in [("距离 $E_d$", 4.55), ("马氏 $E_m$", 3.90),
                   ("速度 $E_v$", 3.25), ("连续 $E_c$", 2.60)]:
        box(ax, 0.35, y, 1.30, 0.52, txt, fs=8.8)
        arrow(ax, (1.67, y + 0.26), (1.98, 3.95))
    box(ax, 2.00, 3.35, 1.50, 1.20, "加权融合\n$S\\geq S_{thr}$", fc="#eafaf1", ec="#1e8449", fs=8.8)
    box(ax, 3.90, 3.45, 1.30, 1.00, "候选集\n（带分数）", fc="#fdf2e9", ec="#b9770e", fs=8.8)
    arrow(ax, (3.52, 3.95), (3.88, 3.95))

    ax.add_patch(FancyBboxPatch((6.05, 2.35), 5.80, 3.55, boxstyle="round,pad=0.03",
                                fc="#fcfcfc", ec="#95a5a6", lw=1.0, ls="--"))
    ax.text(6.22, 5.55, '指派层：在候选集上求全局最优，回答“配给哪一条”', fontsize=9.5, color="0.25")
    box(ax, 6.25, 3.45, 2.10, 1.00, "匈牙利算法\n代价 = 马氏距离", fc="#f4ecf7", ec="#7d3c98", fs=8.8)
    box(ax, 8.85, 3.45, 1.95, 1.00, "一对一配对\n（互斥）", fc="#fdf2e9", ec="#b9770e", fs=8.8)
    arrow(ax, (5.22, 3.95), (6.23, 3.95))
    arrow(ax, (8.37, 3.95), (8.83, 3.95))

    ax.text(6.0, 1.75, "分层的理由：判定与指派混在同一个综合分里时，", fontsize=9.2, ha="center", color="0.2")
    ax.text(6.0, 1.28, "两对分数接近的候选会被随机对调（成对交换）。", fontsize=9.2, ha="center", color="0.2")
    ax.text(6.0, 0.62, "判定层只回答是否值得配对，具体配给谁交由指派层统一求解。", fontsize=9.2, ha="center", color="0.2")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig5_1_mewf_framework.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig5_1_mewf_framework.png")


def agg(fn, key):
    rows = list(csv.DictReader(open(os.path.join(AUD, fn), encoding="utf-8")))
    a = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0, 0])
    for r in rows:
        k = r[key]
        a[k][0] += float(r["n_wrong"])
        a[k][1] += float(r["n_missed"])
        a[k][2] += float(r["n_correct"])
        a[k][3] += float(r["n_true_both"])
        a[k][4] += 1
    out = {}
    for k, v in a.items():
        n = v[4]
        out[k] = dict(wrong=v[0] / n, missed=v[1] / n,
                      P=v[2] / (v[2] + v[0]), R=v[2] / v[3],
                      cost=5 * v[0] / n + v[1] / n)
    return out


def fig5_2():
    d = agg("mewf_compare.csv", "method")
    order = [("NN", "最近邻"), ("Sequential", "序贯最近邻"),
             ("DualGate_M8", "三判据 M=8"), ("MEWF_hungarian", "多证据加权")]
    x = np.arange(len(order))
    w = 0.36
    fig, ax = plt.subplots(figsize=(7.6, 4.3))
    wr = [d[k]["wrong"] for k, _ in order]
    ms = [d[k]["missed"] for k, _ in order]
    ax.bar(x - w / 2, wr, w, color=C_RED, label="误配数")
    ax.bar(x + w / 2, ms, w, color=C_ORANGE, label="漏配数")
    for i, (k, _) in enumerate(order):
        ax.text(x[i] - w / 2, wr[i] + 0.7, "%.1f" % wr[i], ha="center", fontsize=8.5, color=C_RED)
        ax.text(x[i] + w / 2, ms[i] + 0.7, "%.1f" % ms[i], ha="center", fontsize=8.5, color=C_ORANGE)
        ax.text(x[i], -4.4, "P=%.3f\nR=%.3f" % (d[k]["P"], d[k]["R"]), ha="center", fontsize=8.2, color="0.3")
    ax.set_xticks(x)
    ax.set_xticklabels([n for _, n in order])
    ax.set_ylabel("每场景平均目标数")
    ax.set_ylim(-6.5, 52)
    ax.set_title("密集场景下四种方法的错误构成（5 组场景-种子平均，每组 200 个共现真目标）", fontsize=9.6)
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", ls=":", color="0.9")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig5_2_method_compare.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig5_2_method_compare.png")


def fig5_3():
    d = agg("mewf_decompose.csv", "config")
    steps = ["Seq_r0.80_greedy", "Seq_r0.80_hung", "Seq_r0.50_hung", "MEWF_S0.40"]
    labels = ["原方案\n硬门限+贪心", "+全局指派", "+放宽门限", "+证据软融合"]
    vals = [d[s]["cost"] for s in steps]

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for i, v in enumerate(vals):
        color = C_GRAY if i == 0 else (C_BLUE if i == 1 else (C_GREEN if i == 2 else "#8e44ad"))
        if i == 0:
            ax.bar(i, v, 0.55, color=color)
        else:
            ax.bar(i, vals[i - 1] - v, 0.55, bottom=v, color=color)
        ax.text(i, v - 1.7, "%.1f" % v, ha="center", fontsize=9.5)
        if i > 0:
            hgt = vals[i - 1] - v
            if hgt >= 4:
                ax.text(i, (v + vals[i - 1]) / 2, "-%.1f" % hgt,
                        ha="center", va="center", fontsize=8.5, color="white")
            else:
                dx, ha = (-0.33, "right") if i == len(vals) - 1 else (0.33, "left")
                ax.text(i + dx, (v + vals[i - 1]) / 2, "-%.1f" % hgt,
                        ha=ha, va="center", fontsize=8.5)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("加权代价 $C=5N_{wrong}+N_{missed}$（纵轴自 40 起）")
    ax.set_ylim(40, 75)
    tot = vals[0] - vals[-1]
    parts = [(vals[i - 1] - vals[i]) / tot for i in (1, 2, 3)]
    ax.set_title("优势来源的逐步拆解：指派 %.0f%%、门限 %.0f%%、软融合 %.0f%%"
                 % tuple(100 * p for p in parts), fontsize=10)
    ax.grid(axis="y", ls=":", color="0.9")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig5_3_decompose.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig5_3_decompose.png")


if __name__ == "__main__":
    fig5_1()
    fig5_2()
    fig5_3()
