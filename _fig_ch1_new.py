# -*- coding: utf-8 -*-
"""第1章插图：全文研究框架（七章版）。

与旧稿 `_fig_ch1.py` 的区别：旧图按六章绘制（第2章含配准），本图按七章绘制，
把量测建模与时空配准拆为第2、3章，并在每个环节下方标出该环节的决定性量。

产出
  Pictures/fig1_1_framework.png

复现：
  cd 格式排版
  python _fig_ch1_new.py
"""
import os

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

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
OUT = os.path.join(BASE, "Pictures")
C_BLUE, C_RED, C_GREEN, C_ORANGE, C_PURPLE, C_GRAY = \
    "#2471a3", "#c0392b", "#1e8449", "#d68910", "#7d3c98", "#7f8c8d"


def box(ax, x, y, w, h, txt, fc, ec, fs=8.4, lw=1.0, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03",
                                fc=fc, ec=ec, lw=lw, ls=ls))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs)


def fig1_1():
    fig, ax = plt.subplots(figsize=(11.2, 5.0))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.05)
    ax.axis("off")

    W, GAP, X0, Y = 1.90, 0.30, 0.15, 3.30
    cxs = [X0 + i * (W + GAP) + W / 2 for i in range(5)]
    colors = [C_BLUE, C_GREEN, C_ORANGE, C_RED, C_PURPLE]

    box(ax, 1.05, 4.45, 8.90, 0.52,
        "短波双照射源观测条件：低精度 10 km · 低数据率 30 s · 双站误差相关",
        "#fdf2e9", "#ca6f1e", fs=9.4)

    chs = ["第2章\n量测模型与\n两种布设", "第3章\n双照射源\n时空配准",
           "第4章\n单站航迹\n滤波", "第5章\n跨照射源\n在线配对",
           "第6章\n航迹融合\n与增益"]
    qty = ["群距离与\n虚高灵敏度", "$\\sigma_{\\Delta R}=\\alpha\\sigma_R/\\sqrt{N}$",
           "$\\sigma_{pos}\\geq\\sigma_R/\\sqrt{N}$", "判别力 $\\delta/\\sigma$\n与共视长度",
           "$\\rho\\leq(1+k^2)/(2k^3)$"]

    for i, cx in enumerate(cxs):
        box(ax, X0 + i * (W + GAP), Y, W, 0.95, chs[i], "#eaf4fb", colors[i], fs=8.6)
        ax.annotate("", xy=(cx, 4.24), xytext=(cx, 4.43),
                    arrowprops=dict(arrowstyle="-|>", color="#7f8c8d", lw=0.9))
        if i < 4:
            ax.annotate("", xy=(cxs[i + 1] - W / 2 - 0.01, Y + 0.475),
                        xytext=(cx + W / 2 + 0.01, Y + 0.475),
                        arrowprops=dict(arrowstyle="-|>", color="#34495e", lw=1.1))
        box(ax, X0 + i * (W + GAP), 2.45, W, 0.52, qty[i], "#ffffff", colors[i],
            fs=8.0, lw=0.9, ls="--")
        ax.annotate("", xy=(cx, 3.01), xytext=(cx, 3.28),
                    arrowprops=dict(arrowstyle="-|>", color=colors[i], lw=0.9))

    box(ax, 0.95, 1.02, 9.10, 0.86,
        "融合增益由两站误差相关性决定，相关性由模型集与真实机动的匹配程度决定；\n"
        "航迹长度由覆盖并集决定，与融合算法无关",
        "#f4ecf7", C_PURPLE, fs=9.2)
    for i, cx in enumerate(cxs):
        ax.annotate("", xy=(cx, 1.90), xytext=(cx, 2.43),
                    arrowprops=dict(arrowstyle="-|>", color="#7d3c98", lw=0.9, ls=":"))

    ax.text(0.15, 0.42, "沿处理链逐级传导：前一环节的残差是后一环节的输入扰动，因此章节顺序即传导顺序",
            fontsize=8.4, color="#34495e")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_1_framework.png"), dpi=250, facecolor="white")
    plt.close(fig)
    print("  -> fig1_1_framework.png")


if __name__ == "__main__":
    fig1_1()
