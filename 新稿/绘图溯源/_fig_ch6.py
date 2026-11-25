# -*- coding: utf-8 -*-
"""生成第六章融合机理、种子配对结果与覆盖上界图。

输入数据为本目录下“数据/第六章”的冻结快照，正式图片输出到相邻 Pictures。
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
from matplotlib.patches import FancyBboxPatch
from review_ch6_validation import RUNS, vectors


HERE = Path(__file__).resolve().parent
DATA = HERE / "数据" / "第六章"
OUT = HERE.parent / "Pictures"
plt.rcParams.update({
    "font.family": ["Times New Roman", "SimSun"],
    "mathtext.fontset": "stix",
    "axes.unicode_minus": False,
    "font.size": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def fig6_1():
    """静态逆方差加权模型的理论有效边界。"""
    rho = np.linspace(0, 1, 500)
    ks = [1.0, 1.4, 2.0, 3.0]
    styles = ["-", "--", "-.", ":"]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for k, style in zip(ks, styles):
        ratio = k**2 / (1 + k**2) + 2 * rho * k**3 / (1 + k**2)**2
        limit = (1 + k**2) / (2 * k**3)
        ax.plot(rho, ratio, color="black", ls=style, lw=1.7,
                label=f"k={k:g}，边界 rho={min(limit, 1):.2f}")
        if limit <= 1:
            ax.plot(limit, 1, marker="o", ms=4, color="black")
    ax.axhline(1, color="0.45", ls="--", lw=1.0, label="与较优单站方差相等")
    ax.fill_between(rho, 0.5, 1, color="0.92", zorder=0)
    ax.text(0.97, 0.63, "融合方差较小区域", ha="right", color="0.25")
    ax.set(xlim=(0, 1), ylim=(0.5, 1.5),
           xlabel="两站误差相关系数 rho（理论模型）",
           ylabel="融合方差 / 较优单站方差",
           title="误差相关性与两站精度差异共同限定融合有效范围")
    ax.grid(ls=":", color="0.86")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "fig6_1_gain_region.png", dpi=220)
    plt.close(fig)


def _box(ax, xy, wh, text, fs=9.2):
    x, y = xy
    w, h = wh
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0.02",
                                facecolor="white", edgecolor="black", linewidth=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def fig6_2():
    """白底黑框呈现模型集与融合表现之间的待检验传导关系。"""
    fig, ax = plt.subplots(figsize=(10.2, 3.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    _box(ax, (0.2, 1.45), (2.25, 1.25), "ADS-B轨迹\n运动与转弯特征")
    _box(ax, (3.15, 1.45), (2.4, 1.25), "IMM 转弯率模型集\n与实际机动匹配程度")
    _box(ax, (6.25, 2.55), (2.35, 1.10), "单站误差与\n位置协方差诊断")
    _box(ax, (6.25, 0.65), (2.35, 1.10), "两站误差相关性\n中心化与非中心化指标")
    _box(ax, (9.4, 1.45), (2.35, 1.25), "在线状态融合\n精度与负增益频次")
    arrows = [((2.48, 2.08), (3.12, 2.08)), ((5.58, 2.15), (6.22, 3.02)),
              ((5.58, 1.95), (6.22, 1.22)), ((8.63, 3.02), (9.37, 2.40)),
              ((8.63, 1.20), (9.37, 1.75))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start,
                    arrowprops={"arrowstyle": "->", "color": "black", "lw": 1.1})
    ax.text(6, 0.12,
            "实验检验：在同一在线链路和配对随机种子下调整模型集，分别观测误差诊断与融合结果",
            ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig6_2_mechanism.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig6_3():
    """冻结参数下，正确双源共同目标历元上的种子配对结果。"""
    df = pd.read_csv(DATA / "model_common_epochs.csv")
    baseline = df[df.group == "wide"].set_index("seed")
    matched = df[df.group == "cruise"].set_index("seed")
    seeds = sorted(set(baseline.index) & set(matched.index))
    if len(seeds) != 20:
        raise ValueError(f"预期20个共同随机种子，实际为{len(seeds)}")
    specs = [("gain_rmse", "RMSE增益（%）"),
             ("gain_median", "中位误差增益（%）"),
             ("gain_p90", "90分位误差增益（%）")]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.2), sharex=True)
    for ax, (column, title) in zip(axes, specs):
        a = baseline.loc[seeds, column].to_numpy(float)
        b = matched.loc[seeds, column].to_numpy(float)
        for y0, y1 in zip(a, b):
            ax.plot([0, 1], [y0, y1], color="0.78", lw=0.7, zorder=1)
        ax.scatter(np.zeros(len(a)), a, s=19, color="0.35", zorder=2,
                   label="转弯率0.7/1.5°/s")
        ax.scatter(np.ones(len(b)), b, s=24, marker="^", facecolors="white",
                   edgecolors="black", linewidths=0.8, zorder=3,
                   label="巡航匹配0.05/0.2°/s")
        ax.axhline(0, color="black", lw=0.8, ls="--")
        ax.set_title(title, fontsize=9.5)
        ax.set_xticks([0, 1], ["较宽转弯率\n模型集", "巡航匹配\n模型集"])
        ax.grid(axis="y", ls=":", color="0.88")
        ax.text(0.04, 0.96,
                f"负增益：{int((a < 0).sum())}/{len(seeds)} → {int((b < 0).sum())}/{len(seeds)}",
                transform=ax.transAxes, va="top", fontsize=8.2)
        lo,hi=min(a.min(),b.min(),0),max(a.max(),b.max())
        ax.set_ylim(lo-max((hi-lo)*.12,2),hi+max((hi-lo)*.2,2))
        ax.scatter([0,1],[a.mean(),b.mean()],marker='D',s=42,color='#276b91',zorder=4)
        ax.plot([0,1],[a.mean(),b.mean()],color='#276b91',lw=1.6,zorder=3)
    axes[0].set_ylabel("相对同一配置下较优单站的误差改善比例")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False,
               bbox_to_anchor=(0.5, -0.01), fontsize=8.5)
    fig.suptitle("两组模型集在共同目标历元上的融合收益（20个配对随机种子）", y=1.02)
    fig.tight_layout(rect=(0, 0.09, 1, 0.98))
    fig.savefig(OUT / "fig6_3_negative_gain.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig6_4():
    """展示覆盖互补的在线实现长度比与几何并集上界。"""
    df = pd.read_csv(DATA / "coverage_common_window.csv").groupby('case').mean(numeric_only=True)
    df=df.loc[['vertical','diag45','near','far']]
    labels = ["垂直穿越", "45°斜穿", "近距穿越", "远距穿越"]
    if len(df) != 4:
        raise ValueError("覆盖上界扫描数据应包含四种穿越工况")
    y = np.arange(len(df))
    upper = df.geometry_ceiling_ratio.to_numpy(float)
    actual = df.geometric_normalized_system.to_numpy(float)
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    for i, (lo, hi) in enumerate(zip(actual, upper)):
        ax.plot([lo, hi], [i, i], color="0.45", lw=1.5, zorder=1)
    ax.scatter(actual, y, marker="o", s=46, color="black", label="系统有效输出（归一化）", zorder=3)
    ax.scatter(upper, y, marker="s", s=42, facecolors="white", edgecolors="black",
               label="覆盖并集几何上界", zorder=3)
    for i, pct in enumerate(df.union_realization):
        ax.text(upper[i] + 0.012, i, f"覆盖实现率 {100*pct:.1f}%", va="center", fontsize=8.3)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0.95, 1.85)
    ax.set_xlabel("帧数 / 较长单站几何覆盖帧数（统一分母）")
    ax.set_title("同一覆盖时间窗内的系统有效输出与几何并集（每工况5种子）")
    ax.grid(axis="x", ls=":", color="0.86")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0,1.0), fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig6_4_coverage_ceiling.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def _background(ax,bounds):
    geo=json.loads((HERE/'数据/第四章/map_background.geojson').read_text(encoding='utf-8'))
    def draw(g):
        kind=g['type']
        if kind=='LineString':
            a=np.asarray(g['coordinates']);ax.plot(a[:,0],a[:,1],color='.82',lw=.45,zorder=0)
        elif kind=='MultiLineString':
            for a in g['coordinates']:draw({'type':'LineString','coordinates':a})
        elif kind=='GeometryCollection':
            for part in g['geometries']:draw(part)
    for f in geo['features']:draw(f['geometry'])
    ax.set_xlim(bounds[:2]);ax.set_ylim(bounds[2:])
    # 保持局部经纬物理尺度，通过扩展数据范围填满地图面板，避免拉伸地理形状。
    ax.set_aspect(1/np.cos(np.deg2rad(np.mean(bounds[2:]))),adjustable='datalim')
    ax.set(xlabel='经度 / °E',ylabel='纬度 / °N')
    ax.grid(ls=':',color='.9',zorder=0)
    for name,x,y in [('宜昌',111.29,30.69),('荆州',112.24,30.34),('襄阳',112.14,32.04),
                      ('重庆',106.55,29.56),('达州',107.50,31.21),('汉中',107.02,33.07)]:
        if bounds[0]<x<bounds[1] and bounds[2]<y<bounds[3]:
            ax.plot(x,y,'.',color='.6',ms=2.5)
            ax.annotate(name,(x,y),xytext=(3,3),textcoords='offset points',fontsize=7,color='.5')


def _demo(label,seed,target,filename,title):
    df=pd.read_csv(RUNS/f'{label}_{seed}_samples.csv')
    df=df[df.target.eq(target)].sort_values('frame').copy()
    df=df[df.geometry_r1.eq(1)|df.geometry_r2.eq(1)].copy()
    t=(df.time_sec-df.time_sec.iloc[0])/60
    fig=plt.figure(figsize=(10,6.5))
    gs=fig.add_gridspec(2,2,width_ratios=[1,1.35],height_ratios=[1.8,1],hspace=.42,wspace=.30)
    ax=fig.add_subplot(gs[:,0]);err=fig.add_subplot(gs[0,1]);time=fig.add_subplot(gs[1,1])
    mid=(df.truth_lon.min()+df.truth_lon.max())/2
    half=max((df.truth_lon.max()-df.truth_lon.min())/2+.35,1.2)
    bounds=[mid-half,mid+half,df.truth_lat.min()-.35,df.truth_lat.max()+.35]
    _background(ax,bounds)
    colors={'r1':'#276b91','r2':'#ae563d','system':'#256d4c'}
    ax.plot(df.truth_lon,df.truth_lat,'--',color='.15',lw=1.2,label='参考轨迹')
    for name,desc,style in [('r1','R1局部航迹',':'),('r2','R2局部航迹','-.'),('system','系统航迹','-')]:
        x=df[f'{name}_lon'].to_numpy().copy();y=df[f'{name}_lat'].to_numpy().copy()
        if name=='system':
            x[df.n_sources.eq(0)]=np.nan;y[df.n_sources.eq(0)]=np.nan
        ax.plot(x,y,ls=style,color=colors[name],lw=1.3 if name=='system' else .8,label=desc)
        e=np.linalg.norm(vectors(df,name),axis=1)
        err.plot(t,e,ls=style,color=colors[name],lw=1.0,label=desc)
    ax.legend(frameon=False,fontsize=8,loc='lower left',bbox_to_anchor=(-.02,-.02))
    ax.set_title('地理位置与在线输出',fontsize=10)
    err.set(xlabel='进入覆盖并集后的时间 / min',ylabel='位置误差 / km',title='单目标误差时序（示意）')
    err.grid(ls=':',color='.88');err.legend(frameon=False,fontsize=8)
    err.fill_between(t,0,1,where=df.n_sources.eq(2),transform=err.get_xaxis_transform(),
                     color='#dcebe3',alpha=.4,zorder=0)
    dt=float(np.median(np.diff(t)))
    rows=[('R1视场',df.geometry_r1.eq(1),colors['r1']),('R2视场',df.geometry_r2.eq(1),colors['r2']),
          ('单源输出',df.n_sources.eq(1),'.55'),('双源输出',df.n_sources.eq(2),colors['system'])]
    for i,(desc,mask,color) in enumerate(rows):
        time.broken_barh([(x,dt) for x in t[mask]],(i-.25,.5),facecolors=color)
    time.set_yticks(range(4),[r[0] for r in rows]);time.invert_yaxis()
    time.set(xlabel='进入覆盖并集后的时间 / min',title='视场覆盖与有效源接力')
    time.grid(axis='x',ls=':',color='.88')
    fig.suptitle(title,fontsize=11,y=.98)
    fig.savefig(OUT/filename,dpi=230,bbox_inches='tight',pad_inches=.15)
    plt.close(fig)


def fig6_5():
    _demo('vertical',46101,1,'fig6_5_simulation_relay.png','纯仿真目标的在线航迹接力与双源融合示例')


def fig6_6():
    pick=json.loads((DATA/'demo_selection.json').read_text(encoding='utf-8'))
    _demo('system',pick['seed'],pick['target'],'fig6_6_adsb_relay.png',
          'ADS-B航迹驱动的覆盖互补与在线融合示例')


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig6_1()
    fig6_2()
    fig6_3()
    fig6_4()
    fig6_5()
    fig6_6()
    print("已生成第六章六幅图：理论、框图、种子配对、覆盖实现率及两个在线地图示例。")
