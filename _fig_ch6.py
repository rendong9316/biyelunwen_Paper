# -*- coding: utf-8 -*-
"""第6章插图：增益机理链、闭式有效域、负增益种子计数。

数据来源
  - 图6-1 结构示意 + 第4章模型集实验、§12.6.5 机理表（池化 rho、NEES）的数值
  - 图6-2 闭式：SCC 方差比 V/sigma1^2 = k^2/(1+k^2) + 2*rho*k^3/(1+k^2)^2
  - 图6-3 _analysis/mc_online_chain.csv（47 对，基线/优化）负增益计数

产出
  Pictures/fig6_1_gain_region.png
  Pictures/fig6_2_mechanism.png
  Pictures/fig6_3_negative_gain.png

复现：
  cd 格式排版
  python _fig_ch6.py
"""
import os
import csv

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
AUD = os.path.join(BASE, "文稿撰写", "_analysis")
C_RED, C_BLUE, C_GREEN, C_ORANGE, C_GRAY, C_PURPLE = (
    "#c0392b", "#2471a3", "#1e8449", "#d68910", "#7f8c8d", "#7d3c98")


def box(ax, x, y, w, h, txt, fc="#ebf5fb", ec="#2471a3", fs=8.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=fc, ec=ec, lw=1.0))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs)


def arrow(ax, p, q, color="#2c3e50"):
    ax.annotate("", xy=q, xytext=p,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.0,
                                shrinkA=0, shrinkB=0))


def fig6_2():
    fig, ax = plt.subplots(figsize=(10.4, 4.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    box(ax, 0.25, 2.55, 2.55, 1.30,
        "真实机动分布\n中位 0.012 °/s\np90 0.229、p99 0.660 °/s", fs=8.4)
    box(ax, 3.35, 2.55, 2.35, 1.30,
        "模型集设计\nCT 0.7/1.5 →\n0.05/0.2°/s", fc="#fef9e7", ec="#b9770e", fs=8.4)
    arrow(ax, (2.82, 3.20), (3.33, 3.20))

    ys = [4.55, 3.20, 1.85]
    labels = [
        ("单站残差减小\nR1 -13.8%、R2 -8.1%（不显著）", "#eafaf1", "#1e8449"),
        ("共同模型误差减小\n池化 ρ 0.520 → 0.224", "#fdedec", "#c0392b"),
        ("协方差更可信\nNEES 4.49→2.87、2.94→1.53", "#f4ecf7", "#7d3c98"),
    ]
    for y, (t, fc, ec) in zip(ys, labels):
        box(ax, 6.35, y, 3.05, 1.00, t, fc=fc, ec=ec, fs=8.2)
        arrow(ax, (5.72, 3.20), (6.33, y + 0.50))

    box(ax, 9.95, 2.20, 1.85, 2.00,
        "融合增益\nRMSE 1.7→17.4%\n中位 7.3→15.6%\np90 -2.6→14.8%",
        fc="#ebf5fb", ec="#2471a3", fs=8.2)
    for y in ys:
        arrow(ax, (9.42, y + 0.50), (9.93, 3.20))

    ax.text(6.0, 1.30,
            "三条通道同时改善，但决定增益大小的是中间一条：两站误差的相关系数。",
            fontsize=9.0, ha="center", color="0.2")
    ax.text(6.0, 0.85,
            "逆方差加权下，融合增益可由 $\\rho$ 与两源方差比 $k$ 的闭式（6.2 节）直接给出。",
            fontsize=9.0, ha="center", color="0.2")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig6_2_mechanism.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig6_2_mechanism.png")


def v_scc(rho, k):
    """SCC（逆方差加权）在相关系数 rho 下的方差比 V/sigma1^2。"""
    return k ** 2 / (1 + k ** 2) + 2 * rho * k ** 3 / (1 + k ** 2) ** 2


def fig6_1():
    rho = np.linspace(0, 1, 401)
    ks = [1.0, 1.4, 2.0, 3.0]
    colors = [C_BLUE, C_GREEN, C_ORANGE, C_RED]

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    for k, c in zip(ks, colors):
        ax.plot(rho, v_scc(rho, k), color=c, lw=1.6, label="$k=%.1f$" % k)
        # 与 V=1 的交点
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if v_scc(mid, k) < 1.0:
                lo = mid
            else:
                hi = mid
        ax.plot([lo], [1.0], "o", ms=4.5, color=c)
        if lo < 0.99:
            ax.annotate("%.2f" % lo, (lo, 1.0), textcoords="offset points",
                        xytext=(3, -12), fontsize=8, color=c, va="top")

    ax.axhline(1.0, color="0.45", ls="--", lw=1.0)
    ax.text(0.02, 1.03, "无增益界线 $V=\\sigma_1^2$", fontsize=8.5, color="0.35")

    # 工作点：63 段基线（k≈1.4，池化 rho=0.172）
    ax.plot([0.172], [v_scc(0.172, 1.4)], "s", ms=7, mfc="white",
            mec=C_GREEN, mew=1.6)
    ax.annotate("63 段工作点\n$\\rho$=0.172, $k$=1.4", (0.172, v_scc(0.172, 1.4)),
                textcoords="offset points", xytext=(10, -26), fontsize=8.5)
    ax.text(0.42, 0.575,
            "10 对实验按其自身方差比的有效上界：\n$k$=1.18 时 0.73，$k$=1.26 时 0.64",
            fontsize=8.4, color="0.25")

    ax.set_xlabel("两站误差相关系数 $\\rho$")
    ax.set_ylabel("融合方差比 $\\sigma_f^2/\\sigma_1^2$")
    ax.set_xlim(0, 1)
    ax.set_ylim(0.55, 1.45)
    ax.grid(ls=":", color="0.9")
    ax.legend(frameon=False, loc="upper left", fontsize=9,
              title="方差比 $k=\\sigma_2/\\sigma_1$", title_fontsize=8.5)
    ax.set_title("逆方差加权融合的方差随相关系数上升；曲线与虚线之交点即该方差比下的有效上界", fontsize=9.6)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig6_1_gain_region.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig6_1_gain_region.png")


def fig6_3():
    # 负增益种子计数直接由 47 对结果文件复算（§12.6.4）
    rows = list(csv.DictReader(open(os.path.join(AUD, "mc_online_chain.csv"), encoding="utf-8")))
    by = {}
    for r in rows:
        by.setdefault(r["cfg"], {})[int(r["seed"])] = r
    base_cfg, opt_cfg = "base_07_15", "opt_005_02"
    common = sorted(set(by[base_cfg]) & set(by[opt_cfg]))
    keys = ["gain_rmse_pct", "gain_med_pct", "gain_p90_pct"]
    cats = ["RMSE", "中位", "p90"]
    base = [sum(1 for s in common if float(by[base_cfg][s][k]) < 0) for k in keys]
    opt = [sum(1 for s in common if float(by[opt_cfg][s][k]) < 0) for k in keys]
    print("    负增益计数 base=%s opt=%s (n=%d)" % (base, opt, len(common)))

    x = np.arange(len(cats))
    w = 0.34
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.bar(x - w / 2, base, w, color=C_RED, label="模型集 0.7 / 1.5")
    ax.bar(x + w / 2, opt, w, color=C_GREEN, label="模型集 0.05 / 0.2")
    for i in range(len(cats)):
        ax.text(x[i] - w / 2, base[i] + 0.5, "%d" % base[i], ha="center",
                fontsize=9, color=C_RED)
        ax.text(x[i] + w / 2, opt[i] + 0.5, "%d" % opt[i], ha="center",
                fontsize=9, color=C_GREEN)
    ax.set_xticks(x)
    ax.set_xticklabels(cats)
    ax.set_ylabel("融合劣于最优单站的种子数（共 47 对）")
    ax.set_ylim(0, 31)
    ax.set_title("融合劣于最优单站的种子数（47 对配对，按三个统计口径）", fontsize=9.8)
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", ls=":", color="0.9")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig6_3_negative_gain.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig6_3_negative_gain.png")


if __name__ == "__main__":
    fig6_1()
    fig6_2()
    fig6_3()
