# -*- coding: utf-8 -*-
"""第3章图：距离偏置估计精度随标校航迹数与距离跨度的变化。

数据来源：关于毕业论文撰写的若干事项 §9.1（全国走廊 N–sigma_R 曲线）、
§9.6.1（波束内样本 4215/5454 条对应的 CRLB 1.29/2.16 km）。
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

_c = ["SimHei", "Microsoft YaHei", "SimSun"]
_a = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in _c if f in _a), "DejaVu Sans")
plt.rcParams["font.sans-serif"] = [FONT]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Pictures", "fig3_1_crlb_vs_n.png")

SR = 10.0          # sigma_R, km
CV_NAT = 0.2155    # 全国走廊 CV(s)

def crlb(n, cv):
    return SR / np.sqrt(n) * np.sqrt(1 + cv ** 2) / cv

fig, ax = plt.subplots(figsize=(6.8, 4.6))

n = np.logspace(0, 4.1, 400)
ax.plot(n, crlb(n, CV_NAT), color="#1f6fb4", lw=2,
        label="全国走廊标校（CV(s)=0.216）")

n_pts = np.array([20, 100, 900, 5000, 10803])
s_pts = crlb(n_pts, CV_NAT)
ax.plot(n_pts, s_pts, "o", color="#1f6fb4", ms=5, zorder=3)

for x, y, lab, off, ha in [(20, s_pts[0], "20 条：10.6 km", (10, 6), "left"),
                           (10803, s_pts[-1], "10 803 条：0.46 km", (-12, -6), "right")]:
    ax.annotate(lab, (x, y), textcoords="offset points", xytext=off, ha=ha,
                fontsize=9, color="#1f6fb4")

beam = [(4215, 1.29, "R1：4 215 条，1.29 km", (12, -8)),
        (5454, 2.16, "R2：5 454 条，2.16 km", (12, 18))]
for x, y, lab, off in beam:
    ax.plot(x, y, "^", color="#c0392b", ms=7, zorder=4)
    ax.annotate(lab, (x, y), textcoords="offset points", xytext=off,
                fontsize=9, color="#c0392b", ha="left", va="center")

ax.axhline(2.35, color="0.45", ls="--", lw=1.2)
ax.text(4.2, 2.52, "计入电离层漂移后的可达精度 2.35 km", fontsize=8.5, color="0.35")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(3, 60000)
ax.set_ylim(0.3, 100)
ax.set_xlabel("标校航迹数 N")
ax.set_ylabel(r"距离偏置标准差 $\sigma_{\Delta R}$ / km", labelpad=10)
ax.grid(True, which="both", ls=":", color="0.85")
ax.legend(loc="upper right", fontsize=9, framealpha=0.9)

fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=200)
print("saved", OUT)
