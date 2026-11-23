# -*- coding: utf-8 -*-
"""按场景目标帧绘制覆盖组成。

从格式排版目录运行：python 新稿/绘图溯源/_fig_scene_and_registration.py
第三章配准图现由 _fig_ch3_registration.py 重绘，本脚本不再复制原图。
"""
from collections import Counter
from pathlib import Path
import importlib.util

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "Pictures"
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("chapter2_figures", HERE / "_fig_ch2_new.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    rows = module.read_scene()
    cfg = module.COMP
    counts = Counter()
    for row in rows:
        flags = tuple(module.in_view(row["lon"], row["lat"],
                      (*cfg[key], cfg[center]), cfg["half"])
                      for key, center in (("r1", "c1"), ("r2", "c2")))
        counts[flags] += 1
    categories = [(False, False), (True, False), (False, True), (True, True)]
    labels = ["两站均不可见", "仅 R1 可见", "仅 R2 可见", "两站同时可见"]
    values = [counts[key] for key in categories]
    total = sum(values)
    assert total == len(rows) and total > 0
    fig, ax = plt.subplots(figsize=(9, 4.3))
    bars = ax.barh(labels[::-1], values[::-1], color=["#4b4b4b", "#868686", "#b5b5b5", "#dedede"],
                   edgecolor="black", height=0.62)
    for bar, value in zip(bars, values[::-1]):
        ax.text(value + total * .012, bar.get_y() + bar.get_height() / 2,
                f"{value:,}（{value / total:.1%}）", va="center", fontsize=11)
    ax.set_xlim(0, max(values) * 1.42)
    ax.set_xlabel("目标帧数（30 s / 帧）")
    ax.set_title(f"主场景目标帧的覆盖状态（共 {total:,} 个）")
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.grid(True, linestyle=":", alpha=.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "fig2_3_density.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("coverage counts:", dict(zip(labels, values)), "total:", total)


if __name__ == "__main__":
    main()
