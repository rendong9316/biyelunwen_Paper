# -*- coding: utf-8 -*-
"""绪论理论分析框架与研究技术路线；不包含章节导览或实验结果。

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
SIZE_BODY = 12
SIZE_SMALL = 10.5
COLOR_BLACK = "000000"
COLOR_WHITE = "FFFFFF"
INK = "#" + COLOR_BLACK
PAPER = "#" + COLOR_WHITE
LINE_SPACING = 1.25
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


def canvas(height):
    # 以约 20 cm 宽设计，缩放到论文版心后仍保留可读字号。
    fig, ax = plt.subplots(figsize=(8, height * 8 / 12))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, height)
    ax.axis("off")
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.025, top=0.975)
    return fig, ax


def label(ax, x, y, text, size=SIZE_BODY, **kwargs):
    return ax.text(x, y, text, ha="center", va="center", fontsize=size,
                   color=INK, linespacing=LINE_SPACING, **kwargs)


def box(ax, x, y, width, height, text, dashed=False, size=SIZE_BODY):
    ax.add_patch(Rectangle((x, y), width, height, facecolor=PAPER,
                           edgecolor=INK, linewidth=0.9,
                           linestyle="--" if dashed else "-"))
    rendered = label(ax, x + width / 2, y + height / 2, text, size)
    rendered._owner_box = (x, y, width, height)


def edge(ax, points, dashed=False):
    for start, end in zip(points[:-2], points[1:-1]):
        ax.plot([start[0], end[0]], [start[1], end[1]], color=INK,
                linewidth=0.85, linestyle="--" if dashed else "-")
    ax.add_patch(FancyArrowPatch(points[-2], points[-1],
                                arrowstyle="-|>", mutation_scale=12,
                                linewidth=0.85, color=INK,
                                linestyle="--" if dashed else "-"))


def save(fig, filename):
    # 避免以裁切补救布局；检查真实渲染的所有文本边界。
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


def analysis_framework():
    fig, ax = canvas(7.5)
    box(ax, 0.45, 6.52, 11.1, 0.63,
        "研究对象：低精度、断续观测下的双照射源航迹处理")
    positions = [0.45, 2.75, 5.05, 7.35, 9.65]
    titles = [
        "传播与量测\n几何约束\n偏差与噪声",
        "参数配准\n校正量测\n统一位置基准",
        "局部状态估计\n航迹状态\n协方差",
        "同源判定与指派\n配对结果\n确认延迟",
        "融合与航迹管理\n状态合成\n单源维持",
    ]
    for x, text in zip(positions, titles):
        box(ax, x, 4.95, 1.9, 1.05, text, size=SIZE_SMALL)
        edge(ax, [(x + 0.95, 6.50), (x + 0.95, 6.04)])
    for x in positions[:-1]:
        edge(ax, [(x + 1.92, 5.475), (x + 2.27, 5.475)])
    # 共同分析对象从处理链汇入两条分析线索。
    for x in (1.4, 3.7, 6.0, 8.3, 10.6):
        ax.plot([x, x], [4.90, 4.10], color=INK, linewidth=0.85)
    ax.plot([1.4, 10.6], [4.10, 4.10], color=INK, linewidth=0.85)
    edge(ax, [(3.1, 4.10), (3.1, 3.50)])
    edge(ax, [(8.9, 4.10), (8.9, 3.50)])
    box(ax, 0.5, 1.90, 5.2, 1.53,
        "精度分析\n传播偏差与参数可辨识性\n运动模型、局部误差及相关性\n加权估计的有效条件")
    box(ax, 6.3, 1.90, 5.2, 1.53,
        "持续跟踪分析\n漏检与局部航迹维持\n公共覆盖与配对确认\n覆盖互补及系统航迹延长")
    edge(ax, [(3.1, 1.86), (3.1, 1.45)])
    edge(ax, [(8.9, 1.86), (8.9, 1.45)])
    box(ax, 0.5, 0.45, 11.0, 0.92,
        "研究输出：各环节的作用机制、条件与适用边界\n"
        "由理论分析、可控实验和真实航迹驱动仿真共同检验",
        size=SIZE_SMALL)
    save(fig, "fig1_2_analysis.png")


def technical_route():
    fig, ax = canvas(9.6)
    label(ax, 6, 9.25, "双照射源航迹处理的研究程序")
    box(ax, 0.35, 7.95, 3.05, 0.95,
        "问题与模型建立\n传播、运动\n检测与覆盖", size=SIZE_SMALL)
    box(ax, 4.10, 7.95, 3.80, 0.95,
        "ADS-B 目标状态参考\n时段分离标校集与评估集", size=SIZE_SMALL)
    box(ax, 8.60, 7.95, 3.05, 0.95,
        "验证设计\n基线与消融\n敏感性分析", size=SIZE_SMALL)
    edge(ax, [(3.44, 8.425), (4.06, 8.425)])
    edge(ax, [(7.94, 8.425), (8.56, 8.425)])

    # 左栏离线标定只向量测校正注入估计参数。
    box(ax, 0.40, 6.10, 2.90, 1.00,
        "离线：独立标校集\n参考航迹与标校量测", size=SIZE_SMALL)
    edge(ax, [(4.7, 7.91), (4.7, 7.65), (1.85, 7.65), (1.85, 7.14)])
    box(ax, 0.40, 4.55, 2.90, 1.05,
        "加权最大似然估计\n虚高、距离偏差\n方位偏差", size=SIZE_SMALL)
    edge(ax, [(1.85, 6.06), (1.85, 5.64)])
    box(ax, 0.40, 3.03, 2.90, 0.97,
        "校正参数\n反馈量测校正\n及位置反演", size=SIZE_SMALL)
    edge(ax, [(1.85, 4.51), (1.85, 4.04)])

    # 中栏是逐周期实际处理顺序。
    box(ax, 4.10, 6.25, 3.80, 0.85,
        "在线：评估场景\n双链路量测生成", size=SIZE_SMALL)
    edge(ax, [(6, 7.91), (6, 7.14)])
    box(ax, 4.10, 5.03, 3.80, 0.85,
        "量测偏差校正\n位置反演", size=SIZE_SMALL)
    edge(ax, [(6, 6.21), (6, 5.92)])
    edge(ax, [(3.34, 3.515), (3.70, 3.515), (3.70, 5.455), (4.06, 5.455)])
    box(ax, 4.10, 3.71, 3.80, 0.94,
        "两链路独立 IMM-UKF\n有量测更新，缺测时预测", size=SIZE_SMALL)
    edge(ax, [(6, 4.99), (6, 4.69)])
    box(ax, 4.10, 2.38, 3.80, 0.94,
        "局部状态时间对齐\n候选判定与全局指派\n关联确认", size=SIZE_SMALL)
    edge(ax, [(6, 3.67), (6, 3.36)])
    box(ax, 4.10, 1.05, 3.80, 0.94,
        "系统航迹与融合输出\n双源融合、单源维持及删除", size=SIZE_SMALL)
    edge(ax, [(6, 2.34), (6, 2.03)])

    # 右栏的真值只进入评价，不进入跨源候选判别。
    box(ax, 8.60, 6.15, 3.10, 0.95,
        "评估集参考状态\n用于误差与身份核算", size=SIZE_SMALL)
    edge(ax, [(7.92, 8.05), (8.26, 8.05), (8.26, 7.29),
              (10.15, 7.29), (10.15, 7.14)], dashed=True)
    box(ax, 8.60, 3.65, 3.10, 1.55,
        "三类评价\n位置误差与不确定性\n配对正确性及误漏配\n有效覆盖帧与持续时间", size=SIZE_SMALL)
    edge(ax, [(10.15, 6.11), (10.15, 5.24)], dashed=True)
    edge(ax, [(7.94, 1.52), (8.22, 1.52), (8.22, 4.425), (8.56, 4.425)])
    box(ax, 8.60, 1.05, 3.10, 1.10,
        "重复试验与条件扫描\n区分算法、配置\n与覆盖条件的影响", size=SIZE_SMALL)
    edge(ax, [(10.15, 3.61), (10.15, 2.19)])
    label(ax, 6, 0.43,
          "实线：模型、参数与处理流；虚线：评价参考，不提供跨源配对身份",
          SIZE_SMALL)
    save(fig, "fig1_3_route.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    analysis_framework()
    technical_route()
