# -*- coding: utf-8 -*-
"""E7 图：虚高失配 -> 融合增益衰减，标定前后两条曲线。"""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

_c = ["SimSun", "Microsoft YaHei", "SimHei"]
_a = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in _c if f in _a), "DejaVu Sans")
plt.rcParams["font.sans-serif"] = [FONT]
plt.rcParams["axes.unicode_minus"] = False

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.join(PROJECT, "文稿撰写", "_analysis")
rows = list(csv.DictReader(open(os.path.join(HERE, "e7_h_mismatch.csv"), encoding="utf-8")))

def agg(arm, key):
    out = {}
    for r in rows:
        if r["arm"] != arm:
            continue
        d = int(r["h_mismatch_km"])
        out.setdefault(d, []).append(float(r[key]))
    ds = sorted(out)
    mean = [sum(out[d]) / len(out[d]) for d in ds]
    sd = [(sum((x - sum(out[d]) / len(out[d])) ** 2 for x in out[d]) / (len(out[d]) - 1)) ** 0.5
          for d in ds]
    return ds, mean, sd

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

for ax, key, ylab, title in [
    (axes[0], "gain_pct", "融合增益 (%)", "(a) 融合增益随虚高失配衰减"),
    (axes[1], "rmse_fused", "融合位置均方根误差 / km", "（b）虚高失配与融合位置误差"),
]:
    for arm, lab, c, m in [("none", "不标定", "#c0392b", "o"),
                           ("mle3", "三参数标定", "#1f6fb4", "s")]:
        ds, mu, sd = agg(arm, key)
        ax.errorbar(ds, mu, yerr=sd, marker=m, color=c, lw=2, ms=6, capsize=4, label=lab)
    ax.set_xlabel(r"虚高标称失配 $d$ / km")
    ax.set_ylabel(ylab)
    ax.set_title(title, fontsize=11)
    ax.set_xticks([0, 10, 20, 40])
    ax.grid(alpha=0.3, ls="--")
    ax.legend(fontsize=9)

axes[0].annotate("41.9% 降至 8.5%", xy=(40, 8.5), xytext=(10, 10.5),
                 arrowprops=dict(arrowstyle="->", color="#c0392b"), color="#c0392b", fontsize=9)
axes[1].annotate("9.0 km 增至 30.1 km", xy=(40, 30.1), xytext=(16, 22),
                 arrowprops=dict(arrowstyle="->", color="#c0392b"), color="#c0392b", fontsize=9)

fig.tight_layout()
out = os.path.join(PROJECT, "格式排版", "新稿", "Pictures", "fig3_2_e7_mismatch.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=200)
plt.close(fig)
print("saved", out)
