# -*- coding: utf-8 -*-
"""第4章插图：五模型 IMM-UKF 结构、单站误差的逐目标分布。

数据来源
  - 结构图：无数据，按 single_target_with-turn/tracker/ 的 IMM 实现绘制
  - 逐目标误差：文稿撰写/_analysis/o4_per_target.csv
    （exp_o4_outliers.m 在 adsb_ns_all、注册配置、种子 42/43/44 上输出）

产出
  Pictures/fig4_1_imm_structure.png
  Pictures/fig4_2_error_tail.png

复现：
  cd 格式排版
  python _fig_ch4.py
"""
import os
import csv
import statistics as st

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
CSV = os.path.join(BASE, "文稿撰写", "_analysis", "o4_per_target.csv")
C_RED, C_BLUE, C_GREEN, C_GRAY = "#c0392b", "#2471a3", "#1e8449", "#7f8c8d"


def box(ax, x, y, w, h, txt, fc="#ebf5fb", ec="#2471a3", fs=9.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=fc, ec=ec, lw=1.0))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs)


def arrow(ax, p, q, style="-|>", color="#2c3e50", ls="-"):
    ax.annotate("", xy=q, xytext=p,
                arrowprops=dict(arrowstyle=style, color=color, lw=1.0, ls=ls))


def fig4_1():
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    box(ax, 0.15, 2.55, 1.5, 0.9, "量测\n$[R_g,\\phi_{az},v_d]$", fc="#fdf2e9", ec="#b9770e")
    models = [("匀速 CV", 4.15), ("转弯 CT$_1$", 3.30), ("转弯 CT$_2$", 2.45),
              ("转弯 CT$_3$", 1.60), ("转弯 CT$_4$", 0.75)]
    for txt, y in models:
        box(ax, 2.35, y, 1.75, 0.62, txt, fs=9)
        arrow(ax, (1.65, 3.0), (2.33, y + 0.31))

    box(ax, 4.55, 2.30, 1.75, 1.40, "模型概率更新\n（似然递推）", fc="#eafaf1", ec="#1e8449")
    for _, y in models:
        arrow(ax, (4.10, y + 0.31), (4.53, 3.00))

    box(ax, 6.70, 2.30, 1.55, 1.40, "加权融合\n$\\hat x=\\sum \\mu_i \\hat x_i$", fc="#f4ecf7", ec="#7d3c98")
    for _, y in models:
        arrow(ax, (6.30, 3.00), (6.68, 3.00), color="#1e8449", ls=":")

    arrow(ax, (8.25, 3.00), (9.35, 3.00), color="#7d3c98")
    ax.text(9.40, 3.00, "航迹输出", fontsize=9, va="center")

    # 反馈支路
    ax.plot([9.0, 9.0, 3.2, 3.2], [2.55, 0.30, 0.30, 0.72], color="#7f8c8d", lw=1.0, ls="--")
    arrow(ax, (3.2, 0.72), (3.2, 0.74), color="#7f8c8d")
    ax.text(6.0, 0.12, "状态与协方差反馈：按模型概率混合后重新初始化各滤波器", fontsize=8.5, color=C_GRAY, ha="center")

    ax.text(2.3, 5.55, "五模型：1 个匀速 + 4 个协同转弯（左右各两档）", fontsize=9.5)
    ax.text(2.3, 5.15, "转移概率由驻留时间生成：$\\pi_{ii}=e^{-dt/\\tau_i}$", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig4_1_imm_structure.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig4_1_imm_structure.png")


def fig4_2():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    meds = []
    for sta, col, lab in (("R1", C_BLUE, "R1"), ("R2", C_GREEN, "R2")):
        v = sorted(float(r["rmse_km"]) for r in rows
                   if r["cfg"] == "registered" and r["seed"] == "42" and r["station"] == sta)
        ax.semilogy(range(1, len(v) + 1), v, "-", color=col, lw=1.2, label="%s 逐目标 RMSE" % lab)
        ax.semilogy(range(1, len(v) + 1), v, ".", color=col, ms=2.4)
        med = st.median(v)
        ax.axhline(med, color=col, ls=":", lw=0.9)
        meds.append((lab, med))
    ax.text(2, 13.5, "逐目标 RMSE 中位：" + "，".join("%s %.1f km" % m for m in meds),
            fontsize=8.5, color="0.25")
    ax.axhline(2.24, color=C_RED, ls="--", lw=1.0)
    ax.text(2, 2.45, "匀速窗口下界 $\\sigma_R/\\sqrt{N}$ = 2.24 km", color=C_RED, fontsize=8.5)
    ax.set_xlabel("目标序号（按 RMSE 升序）")
    ax.set_ylabel("逐目标位置 RMSE / km")
    ax.set_title("单站误差的逐目标分布（63 段，种子 42）", fontsize=10.5)
    ax.grid(ls=":", color="0.9", which="both")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_ylim(1.5, 200)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig4_2_error_tail.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig4_2_error_tail.png")


if __name__ == "__main__":
    fig4_1()
    fig4_2()
