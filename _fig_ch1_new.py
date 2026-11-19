# -*- coding: utf-8 -*-
"""第1章插图：七章论文的研究任务和两类评价目标。

图中只交代研究范围和处理关系，不预先宣告尚需后文证明的结论。
字体、字号和黑色样式先定义为常量，中文宋体、西文 Times New Roman。

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

FONT_WEST = "Times New Roman"
FONT_CN = "SimSun"
SIZE_BODY = 12
SIZE_SMALL = 10.5
COLOR_BLACK = "000000"
COLOR_WHITE = "FFFFFF"
INK = "#" + COLOR_BLACK
PAPER = "#" + COLOR_WHITE
_available_fonts = {f.name for f in fm.fontManager.ttflist}
for _required_font in (FONT_WEST, FONT_CN):
    if _required_font not in _available_fonts:
        raise RuntimeError(f"缺少指定字体：{_required_font}")
plt.rcParams["font.family"] = [FONT_WEST, FONT_CN]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = SIZE_BODY
plt.rcParams["text.color"] = INK

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
OUT = os.path.join(BASE, "Pictures")
def box(ax, x, y, w, h, txt, fs=SIZE_BODY, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03",
                                fc=PAPER, ec=INK, lw=0.9, ls=ls))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
            fontsize=fs, linespacing=1.25, color=INK)


def arrow(ax, start, end, style="-"):
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=INK,
                                lw=0.9, linestyle=style))


def fig1_1():
    fig, ax = plt.subplots(figsize=(11.2, 5.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    W, GAP, X0, Y = 1.90, 0.30, 0.15, 3.70
    cxs = [X0 + i * (W + GAP) + W / 2 for i in range(5)]
    box(ax, 1.05, 5.05, 8.90, 0.55,
        "研究条件：低精度量测、30 s 更新周期、检测概率 0.6、双照射源观测")

    chs = ["第2章\n量测模型与\n两种布设", "第3章\n双照射源\n时空配准",
           "第4章\n单站航迹\n滤波", "第5章\n跨照射源\n在线配对",
           "第6章\n航迹融合\n与增益"]
    qty = ["传播几何与量测\n两种覆盖布设",
           "虚高与量测偏差\n可辨识性与残差",
           "起始与缺测处理\n运动模型与误差",
           "多帧证据与门限\n全局一对一指派",
           "相关性与权重\n融合收益与边界"]

    for i, cx in enumerate(cxs):
        box(ax, X0 + i * (W + GAP), Y, W, 1.05, chs[i])
        arrow(ax, (cx, 5.01), (cx, Y + 1.10))
        if i < 4:
            arrow(ax, (cx + W / 2 + 0.04, Y + 0.525),
                  (cxs[i + 1] - W / 2 - 0.04, Y + 0.525))
        box(ax, X0 + i * (W + GAP), 2.60, W, 0.72, qty[i],
            fs=SIZE_SMALL, ls="--")
        arrow(ax, (cx, Y - 0.04), (cx, 3.37))

    box(ax, 0.70, 0.95, 4.50, 0.85,
        "精度评价（公共覆盖段）\n位置误差、误差相关性、协方差一致性", fs=SIZE_SMALL)
    box(ax, 5.80, 0.95, 4.50, 0.85,
        "持续跟踪评价（联合覆盖范围）\n配对可靠性、航迹长度、覆盖互补", fs=SIZE_SMALL)
    for i, cx in enumerate(cxs):
        ax.plot([cx, cx], [2.55, 2.15], color=INK, lw=0.8)
    ax.plot([cxs[0], cxs[-1]], [2.15, 2.15], color=INK, lw=0.8)
    arrow(ax, (2.95, 2.15), (2.95, 1.85))
    arrow(ax, (8.05, 2.15), (8.05, 1.85))

    ax.text(5.5, 0.38,
            "验证范围：可控模型实验与真实 ADS-B 航迹驱动的仿真",
            ha="center", fontsize=SIZE_SMALL, color=INK)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_1_framework.png"), dpi=250, facecolor=PAPER)
    plt.close(fig)
    print("  -> fig1_1_framework.png")


if __name__ == "__main__":
    fig1_1()
