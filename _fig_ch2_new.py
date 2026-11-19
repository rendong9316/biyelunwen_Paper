# -*- coding: utf-8 -*-
"""第2章插图（新稿）：两种布设的几何、群距离模型与 ADS-B 场景。

数据来源
  - 站点/波束参数：single_target_with-turn/config/simulation_params_oracle.m（近共视）
                   single_target_with-turn/config/params_coverage_online.m（覆盖互补）；
                   覆盖互补的波束中心 83.533/88.770 由 _analysis/diag_coverage_geometry.m 实测输出
  - 场景航迹：data/adsb_ns/scene_fr24_all.csv（adsb_ns_all，57 条航迹 / 2033 帧）

产出
  Pictures/fig2_1_layout.png        两种布设的平面几何（扇区、距离窗、走廊）
  Pictures/fig2_2_group_range.png   双基地群距离路径示意与群距离曲线
  Pictures/fig2_3_density.png       adsb_ns_all 的并发数与视场内外目标数
  Pictures/fig2_4_tracks.png        航迹平面分布与覆盖分段

复现：
  cd 格式排版
  python _fig_ch2_new.py
"""
import os
import csv
import math
import datetime as dt

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Polygon

_c = ["SimHei", "Microsoft YaHei", "SimSun"]
_a = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in _c if f in _a), "DejaVu Sans")
plt.rcParams["font.sans-serif"] = [FONT]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写"
OUT = os.path.join(BASE, "格式排版", "Pictures")
SCENE = os.path.join(BASE, "文稿撰写", "data", "adsb_ns", "scene_fr24_all.csv")
os.makedirs(OUT, exist_ok=True)

R_E = 6371.0
C_RED, C_BLUE, C_GREEN, C_ORANGE, C_GRAY = "#c0392b", "#2471a3", "#1e8449", "#d68910", "#7f8c8d"

NEAR = dict(r1=(104.0, 30.7), t1=(100.0, 30.7), c1=93.0,
            r2=(106.5, 29.6), t2=(102.5, 29.6), c2=93.0, half=22.5)
COMP = dict(r1=(92.50, 31.45), t1=(88.50, 31.45), c1=83.533,
            r2=(92.50, 30.55), t2=(88.50, 30.55), c2=88.770, half=7.5)
RMIN, RMAX = 1000.0, 2000.0


def bearing(lo1, la1, lo2, la2):
    p1, p2 = math.radians(la1), math.radians(la2)
    dl = math.radians(lo2 - lo1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.atan2(x, y)) % 360.0


def chord(lo1, la1, lo2, la2):
    p1, p2 = math.radians(la1), math.radians(la2)
    dl = math.radians(lo2 - lo1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_E * math.sin(math.asin(min(1.0, math.sqrt(a))))


def dest(lo, la, az, d):
    br = math.radians(az)
    p1, l1 = math.radians(la), math.radians(lo)
    dr = d / R_E
    p2 = math.asin(math.sin(p1) * math.cos(dr) + math.cos(p1) * math.sin(dr) * math.cos(br))
    l2 = l1 + math.atan2(math.sin(br) * math.sin(dr) * math.cos(p1),
                         math.cos(dr) - math.sin(p1) * math.sin(p2))
    return math.degrees(l2), math.degrees(p2)


def sector(lo, la, az, half, r1=RMIN, r2=RMAX, n=60):
    pts = [dest(lo, la, az - half + 2 * half * k / n, r1) for k in range(n + 1)]
    pts += [dest(lo, la, az + half - 2 * half * k / n, r2) for k in range(n + 1)]
    return pts


def in_view(lo, la, st, half):
    az = bearing(st[0], st[1], lo, la)
    d = chord(st[0], st[1], lo, la)
    return (abs((az - st[2] + 180) % 360 - 180) <= half) and (RMIN <= d <= RMAX)


def layout_panel(ax, cfg, title, alpha):
    for key, col, lab in (("r1", C_BLUE, "R1"), ("r2", C_GREEN, "R2")):
        st = cfg[key]
        cd = cfg["c1"] if key == "r1" else cfg["c2"]
        ax.add_patch(Polygon(sector(st[0], st[1], cd, cfg["half"]), closed=True,
                             fc=col, alpha=alpha, ec=col, lw=0.9))
        ax.plot(*st, "^", color=col, ms=9, zorder=6)
        ax.annotate(lab, st, textcoords="offset points", xytext=(6, 6), color=col, fontsize=10)
        tx = cfg["t1"] if key == "r1" else cfg["t2"]
        ax.plot(*tx, "s", color=C_RED, ms=5, zorder=5)
        ax.plot([tx[0], st[0]], [tx[1], st[1]], "--", color=C_RED, lw=0.9)
        ax.annotate("Tx" + lab[1], tx, textcoords="offset points", xytext=(-22, -13),
                    color=C_RED, fontsize=8.5)
    ax.set_xlabel("经度 / °E")
    ax.set_ylabel("纬度 / °N")
    ax.set_title(title, fontsize=10.5)
    ax.grid(ls=":", color="0.85")


def fig2_1():
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))

    layout_panel(axes[0], NEAR, "(a) 近共视布设：两站覆盖几乎重合", 0.16)
    axes[0].set_xlim(98, 127)
    axes[0].set_ylim(22, 38)

    layout_panel(axes[1], COMP, "(b) 覆盖互补布设：南北错开 100 km", 0.20)
    for lat in (30.36, 31.64):
        axes[1].axhline(lat, color="0.35", lw=0.8, ls=(0, (4, 3)))
    axes[1].plot([107.4, 107.4], [28.5, 33.4], color="0.35", lw=1.0)
    axes[1].annotate("走廊 107.4°E", (107.4, 33.4), textcoords="offset points",
                     xytext=(-54, 2), fontsize=9, color="0.3")
    axes[1].annotate("共视 142 km", (107.4, 31.0), textcoords="offset points",
                     xytext=(8, -3), fontsize=8.5, color="0.3")
    axes[1].text(111.6, 32.7, "仅 R1 覆盖", fontsize=9, color=C_BLUE, ha="center")
    axes[1].text(111.6, 29.4, "仅 R2 覆盖", fontsize=9, color=C_GREEN, ha="center")
    axes[1].set_xlim(84, 114)
    axes[1].set_ylim(27, 35)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_1_layout.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig2_1_layout.png")


def fig2_2():
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.2))

    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.4, 5.0), 9.2, 0.6, fc="#d6eaf8", ec="#5d8aa8", lw=0.9))
    ax.text(5.0, 5.3, "电离层", ha="center", fontsize=9.5)
    ax.plot([0.4, 9.6], [0.50, 0.50], color="#34495e", lw=1.5)
    ax.text(9.30, 0.62, "地面", fontsize=8, va="center", ha="right", color=C_GRAY)

    ax.plot(2.0, 0.50, "^", ms=11, color=C_RED)
    ax.text(1.88, 0.60, "Tx", ha="right", fontsize=10)
    ax.plot(8.0, 0.50, "v", ms=11, color=C_BLUE)
    ax.text(8.12, 0.60, "Rx", ha="left", fontsize=10)
    ax.plot(5.4, 0.50, "o", ms=8, color="#1c2833")
    ax.text(5.55, 0.60, "目标", fontsize=9.5)

    for a, b, c in (((2.0, 0.55), (3.7, 5.0), C_RED), ((3.7, 5.0), (5.4, 0.55), C_RED),
                    ((8.0, 0.55), (6.7, 5.0), C_BLUE), ((6.7, 5.0), (5.4, 0.55), C_BLUE)):
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-", color=c, lw=1.2))

    ax.annotate("", xy=(5.4, 5.0), xytext=(5.4, 0.60),
                arrowprops=dict(arrowstyle="<->", color=C_ORANGE, lw=1.1, ls="--"))
    ax.text(5.55, 3.1, r"$h$", color=C_ORANGE, fontsize=12)
    ax.annotate("", xy=(8.0, 0.22), xytext=(2.0, 0.22),
                arrowprops=dict(arrowstyle="<->", color="#34495e", lw=1.0))
    for x in (2.0, 8.0):
        ax.plot([x, x], [0.46, 0.22], color="#34495e", lw=0.8, ls=":")
    ax.text(3.05, 0.22, "基线 $L_b$", ha="center", va="center", fontsize=9,
            bbox=dict(fc="white", ec="none", pad=1.5))
    ax.text(2.42, 2.55, "发射路径", color=C_RED, fontsize=9)
    ax.text(6.30, 2.20, "接收路径", color=C_BLUE, fontsize=9)
    ax.set_title("(a) 天波双基地传播路径与等效虚高", fontsize=10.5)

    ax = axes[1]
    r1 = np.linspace(300, 2000, 400)
    L = 380.0
    for h, ls, c in [(280, ":", "#95a5a6"), (300, "-", C_BLUE), (320, "--", C_RED)]:
        s_ = 4 * h / np.sqrt((r1 + L) ** 2 + 4 * h ** 2) + 4 * h / np.sqrt(r1 ** 2 + 4 * h ** 2)
        ax.plot(r1, s_, ls, color=c, lw=1.5, label="$h$ = %d km" % h)
    for x in (1000, 1900):
        ax.axvline(x, color="0.7", lw=0.8, ls=":")
    ax.set_xlabel("目标至接收站的地面距离  / km")
    ax.set_ylabel(r"灵敏度  $\partial R_g / \partial h$")
    ax.set_title("(b) 群距离对虚高的灵敏度随距离衰减", fontsize=10.5)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.grid(alpha=0.3, ls=":")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_2_group_range.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig2_2_group_range.png")


def read_scene():
    rows = []
    with open(SCENE, encoding="utf-8-sig") as f:
        for r in csv.reader(f):
            if len(r) >= 11:
                rows.append(dict(icao=r[0], lat=float(r[1]), lon=float(r[2]),
                                 t=dt.datetime.strptime(r[10][:19], "%Y-%m-%d %H:%M:%S")))
    return rows


def fig2_3(rows):
    times = sorted({r["t"] for r in rows})
    idx = {t: i for i, t in enumerate(times)}
    cnt_all = [0] * len(times)
    cnt1 = [0] * len(times)
    cnt2 = [0] * len(times)
    for r in rows:
        i = idx[r["t"]]
        cnt_all[i] += 1
        cnt1[i] += int(in_view(r["lon"], r["lat"], (COMP["r1"][0], COMP["r1"][1], COMP["c1"]), COMP["half"]))
        cnt2[i] += int(in_view(r["lon"], r["lat"], (COMP["r2"][0], COMP["r2"][1], COMP["c2"]), COMP["half"]))

    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    ax.plot(times, cnt_all, color="0.55", lw=0.9, label="场景内目标数")
    ax.plot(times, cnt1, color=C_BLUE, lw=0.9, label="落入 R1 视场")
    ax.plot(times, cnt2, color=C_GREEN, lw=0.9, label="落入 R2 视场")
    ax.set_ylabel("目标数")
    ax.set_xlabel("UTC 时刻")
    ax.grid(ls=":", color="0.88")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax.set_title("adsb_ns_all：57 条航迹、2 033 帧的同时在场目标数", fontsize=10.5)
    fig.autofmt_xdate(rotation=0, ha="center")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_3_density.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig2_3_density.png")
    return np.mean(cnt_all), np.max(cnt_all), np.mean(cnt1), np.mean(cnt2)


def fig2_4(rows):
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    by = {}
    for r in rows:
        by.setdefault(r["icao"], []).append(r)
    n_only1 = n_only2 = n_both = n_none = 0
    for icao, pts in by.items():
        pts.sort(key=lambda r: r["t"])
        ax.plot([p["lon"] for p in pts], [p["lat"] for p in pts], color="0.82", lw=0.7, zorder=1)
        for p in pts:
            v1 = in_view(p["lon"], p["lat"], (COMP["r1"][0], COMP["r1"][1], COMP["c1"]), COMP["half"])
            v2 = in_view(p["lon"], p["lat"], (COMP["r2"][0], COMP["r2"][1], COMP["c2"]), COMP["half"])
            if v1 and v2:
                ax.plot(p["lon"], p["lat"], ".", ms=2.4, color="#8e44ad", zorder=3)
                n_both += 1
            elif v1:
                ax.plot(p["lon"], p["lat"], ".", ms=2.4, color=C_BLUE, zorder=3)
                n_only1 += 1
            elif v2:
                ax.plot(p["lon"], p["lat"], ".", ms=2.4, color=C_GREEN, zorder=3)
                n_only2 += 1
            else:
                n_none += 1
    ax.text(106.0, 35.2, "R1 覆盖带（北）", color=C_BLUE, fontsize=9.5)
    ax.text(106.0, 26.4, "R2 覆盖带（南）", color=C_GREEN, fontsize=9.5)
    ax.set_xlim(103, 114)
    ax.set_ylim(25, 36)
    ax.set_xlabel("经度 / °E")
    ax.set_ylabel("纬度 / °N")
    ax.grid(ls=":", color="0.9")
    ax.set_title("航迹点按覆盖状态着色：蓝仅 R1、绿仅 R2、紫两站共视", fontsize=10.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_4_tracks.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  -> fig2_4_tracks.png  (仅R1 %d / 仅R2 %d / 共视 %d / 视场外 %d)"
          % (n_only1, n_only2, n_both, n_none))


if __name__ == "__main__":
    fig2_1()
    fig2_2()
    rows = read_scene()
    print("  场景统计：均值 %.1f 峰值 %d  R1均值 %.1f  R2均值 %.1f" % fig2_3(rows))
    fig2_4(rows)
