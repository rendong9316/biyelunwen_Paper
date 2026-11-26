# -*- coding: utf-8 -*-
"""第1章研究内容与总体技术路线框图（黑白矢量规范风格）。

复现：在格式排版目录执行 python 新稿/绘图溯源/_fig_ch1_new.py。
原理图由 _extract_ch1_assets.py 从用户材料逐字节提取。
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, FancyArrowPatch

FONT_WEST = "Times New Roman"
FONT_CN = "SimSun"
SIZE_TITLE = 12
SIZE_BODY = 10.8
SIZE_SMALL = 10.0
INK = "#000000"
PAPER = "#FFFFFF"
LINE_SPACING = 1.28
DPI = 250
BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "新稿" / "Pictures"

available = {font.name for font in fm.fontManager.ttflist}
for required in (FONT_WEST, FONT_CN):
    if required not in available:
        raise RuntimeError(f"缺少指定字体：{required}")
plt.rcParams.update({
    "font.family": [FONT_WEST, FONT_CN],
    "font.size": SIZE_BODY,
    "text.color": INK,
    "axes.unicode_minus": False,
})


def canvas(width, height):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, height * 12.0 / width)
    ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    return fig, ax


def label(ax, x, y, text, size=SIZE_BODY, **kwargs):
    return ax.text(x, y, text, ha="center", va="center", fontsize=size,
                   color=INK, linespacing=LINE_SPACING, **kwargs)


def box(ax, x, y, width, height, text, dashed=False, size=SIZE_BODY, lw=0.95):
    ax.add_patch(Rectangle((x, y), width, height, facecolor=PAPER,
                           edgecolor=INK, linewidth=lw,
                           linestyle="--" if dashed else "-"))
    rendered = label(ax, x + width / 2, y + height / 2, text, size)
    rendered._owner_box = (x, y, width, height)
    return rendered


def edge(ax, points, dashed=False, lw=0.9):
    for start, end in zip(points[:-2], points[1:-1]):
        ax.plot([start[0], end[0]], [start[1], end[1]], color=INK,
                linewidth=lw, linestyle="--" if dashed else "-")
    ax.add_patch(FancyArrowPatch(points[-2], points[-1],
                                 arrowstyle="-|>", mutation_scale=11.5,
                                 linewidth=lw, color=INK,
                                 linestyle="--" if dashed else "-"))


def save(fig, filename):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    page = fig.bbox
    for text in fig.axes[0].texts:
        bounds = text.get_window_extent(renderer)
        if not (page.x0 <= bounds.x0 <= bounds.x1 <= page.x1 and
                page.y0 <= bounds.y0 <= bounds.y1 <= page.y1):
            raise RuntimeError(f"文字超出画布：{text.get_text()}")
        if hasattr(text, "_owner_box"):
            x, y, width, height = text._owner_box
            left, bottom = fig.axes[0].transData.transform((x, y))
            right, top = fig.axes[0].transData.transform((x + width, y + height))
            if not (left + 3 <= bounds.x0 and bounds.x1 <= right - 3 and
                    bottom + 3 <= bounds.y0 and bounds.y1 <= top - 3):
                raise RuntimeError(f"文字超出框内留白：{text.get_text()}")
    target = OUT / filename
    fig.savefig(target, dpi=DPI, facecolor=PAPER)
    plt.close(fig)
    print(f"Generated {target.name}")


def tech_route():
    # 画布宽 8.2 in、高 6.5 in -> 2050 x 1625 px，适配论文版心
    fig, ax = canvas(8.2, 6.5)
    # y 轴范围 0 .. 9.51
    # 顶部总框
    box(ax, 0.35, 8.70, 11.30, 0.60,
        "核心问题：低精度、断续观测条件下的短波双照射源航迹关联与融合",
        size=SIZE_TITLE, lw=1.05)

    x_mod, w_mod = 0.35, 1.60
    x_core, w_core = 2.25, 5.70
    x_val, w_val = 8.25, 3.40
    cx_mod = x_mod + w_mod / 2
    cx_core = x_core + w_core / 2
    cx_val = x_val + w_val / 2

    # 顶框下方分流至三栏列标题，避免线条穿透文字
    ax.plot([6.00, 6.00], [8.70, 8.48], color=INK, linewidth=0.9)
    ax.plot([cx_mod, cx_val], [8.48, 8.48], color=INK, linewidth=0.9)
    edge(ax, [(cx_mod, 8.48), (cx_mod, 8.22)])
    edge(ax, [(cx_core, 8.48), (cx_core, 8.22)])
    edge(ax, [(cx_val, 8.48), (cx_val, 8.22)], dashed=True)

    # 三栏列标题框
    box(ax, x_mod, 7.80, w_mod, 0.40, "研究模块", size=SIZE_SMALL, lw=0.8)
    box(ax, x_core, 7.80, w_core, 0.40, "核心处理链路与关键方法", size=SIZE_SMALL, lw=0.8)
    box(ax, x_val, 7.80, w_val, 0.40, "机理分析与实验验证", dashed=True, size=SIZE_SMALL, lw=0.8)

    rows = [
        (
            6.52,
            "第2章\n建模与场景",
            "天波双基地量测与目标运动建模\n等效虚高双基地量测模型；近共视与覆盖互补布设",
            "ADS-B 实测航迹数据驱动\n按时段分离标校集与评估集",
        ),
        (
            5.22,
            "第3章\n时空配准",
            "三参数联合时空配准与位置反演\n虚高、同步距离与方位偏置加权最大似然标定",
            "参数可辨识性与失配检验\nFisher 信息下界与失配对照",
        ),
        (
            3.92,
            "第4章\n单站滤波",
            "断续观测下双链路独立 IMM-UKF 滤波\n滑窗起始确认、五模型交互与漏检预测维持",
            "精度与协方差一致性评估\n过程噪声扫参及 NIS/NEES 检验",
        ),
        (
            2.62,
            "第5章\n跨源配对",
            "异步时间对齐与跨照射源在线配对\n因果外推对齐、候选筛选、一对一指派与 6/8 确认",
            "判别力界与同链路策略对照\n非中心卡方分析与误漏配统计",
        ),
        (
            1.32,
            "第6章\n融合与延续",
            "相关误差状态融合与覆盖互补航迹延续\n共视段 SCC 信息矩阵加权、单源接力与航迹管理",
            "精度收益与持续跟踪核定\n静态有效边界与覆盖实现率",
        ),
    ]

    h = 0.96
    # 列标题指向首行
    edge(ax, [(cx_core, 7.80), (cx_core, rows[0][0] + h + 0.02)])

    for idx, (y, mod_txt, core_txt, val_txt) in enumerate(rows):
        box(ax, x_mod, y, w_mod, h, mod_txt, size=SIZE_SMALL)
        box(ax, x_core, y, w_core, h, core_txt, size=SIZE_SMALL)
        box(ax, x_val, y, w_val, h, val_txt, dashed=True, size=SIZE_SMALL)
        yc = y + h / 2
        edge(ax, [(x_mod + w_mod + 0.02, yc), (x_core - 0.02, yc)])
        edge(ax, [(x_core + w_core + 0.02, yc), (x_val - 0.02, yc)], dashed=True)
        if idx < len(rows) - 1:
            y_next_top = rows[idx + 1][0] + h
            edge(ax, [(cx_core, y - 0.02), (cx_core, y_next_top + 0.02)])

    # 底部汇总框
    edge(ax, [(cx_core, rows[-1][0] - 0.02), (cx_core, 0.90)])
    edge(ax, [(cx_val, rows[-1][0] - 0.02), (cx_val, 0.90)], dashed=True)
    box(ax, 0.35, 0.24, 11.30, 0.62,
        "结论与边界总结（第7章）：厘清共视精度增益与覆盖互补航迹延长的作用条件与工程边界",
        size=SIZE_BODY, lw=1.05)

    save(fig, "fig1_2_tech_route.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    tech_route()
