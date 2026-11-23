"""第三章中文配准图：仅从溯源数据与解析公式重绘，不复制专利图片。"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
DATA = HERE / '数据/第三章'
OUT = HERE.parent / 'Pictures'
FONT_CN, FONT_WEST = 'SimSun', 'Times New Roman'
plt.rcParams.update({'font.family': [FONT_WEST, FONT_CN], 'font.size': 11,
    'axes.unicode_minus': False, 'axes.spines.top': False, 'axes.spines.right': False,
    'mathtext.fontset': 'stix'})
BLUE, RED = '#2471a3', '#b74436'


def save(fig, name):
    fig.savefig(OUT / name, dpi=240, facecolor='white')
    plt.close(fig)
    print('saved', name)


def workflow():
    fig, ax = plt.subplots(figsize=(9, 4.7))
    ax.set(xlim=(0, 10), ylim=(0, 5)); ax.axis('off')
    nodes = [(0.3, 3.5, 2.5, .85, '已匹配参考航迹\n位置、时刻与链路观测'),
             (3.75, 3.5, 2.5, .85, '建立参数化观测模型\n虚高、距离偏置、方位偏差'),
             (7.2, 3.5, 2.5, .85, '多航迹加权参数估计\n检查收敛与可辨识性'),
             (7.2, .9, 2.5, .85, '校正观测并更新虚高\n双基地位置重新解算'),
             (3.75, .9, 2.5, .85, '局部航迹状态与协方差\n对齐至统一比较时刻'),
             (.3, .9, 2.5, .85, '站间关联与状态融合\n校正后的公共空间基准')]
    for x, y, w, h, label in nodes:
        ax.add_patch(Rectangle((x, y), w, h, facecolor='white', edgecolor='black', lw=1.1))
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=11)
    for start, end in [((2.8,3.925),(3.75,3.925)),((6.25,3.925),(7.2,3.925)),
        ((8.45,3.5),(8.45,1.75)),((7.2,1.325),(6.25,1.325)),((3.75,1.325),(2.8,1.325))]:
        ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':'black','lw':1.2})
    ax.text(4.9, 2.65, '同一链路共享参数，两条链路分别估计', ha='center', fontsize=11)
    ax.text(4.9, .35, '标校参考用于估计；独立待测航迹的参考位置仅用于评价', ha='center', fontsize=10)
    fig.tight_layout()
    save(fig, 'fig3_registration_flow.png')


def information():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), layout='constrained')
    cv = np.linspace(.025, .3, 300)
    alpha = np.sqrt(1+cv**2)/cv
    axes[0].plot(cv, alpha, color='black', lw=1.7)
    axes[0].set(xlabel='灵敏度变异系数', ylabel='距离偏置标准差的几何放大因子',
                title='（a）几何变化影响参数分离')
    n = np.geomspace(100, 10000, 150)
    for v, style, col in [(.05,':','0.5'),(.12,'--',BLUE),(.22,'-', 'black')]:
        axes[1].plot(n, 10 / np.sqrt(n) * np.sqrt(1+v*v)/v, style, color=col,
                     lw=1.7, label=f'变异系数 {v:.2f}')
    axes[1].set(xscale='log', yscale='log', xlabel='独立观测样本数',
        ylabel='距离偏置标准差下界 / km', title='（b）相同噪声下的样本积累效应')
    axes[1].legend(frameon=False)
    axes[1].text(.97, .95, '距离噪声标准差：10 km', transform=axes[1].transAxes,ha='right',va='top',fontsize=10)
    for ax in axes:
        ax.grid(ls=':', color='.85')
    save(fig, 'fig3_1_crlb_vs_n.png')


def turning():
    table = pd.read_csv(DATA / 'turn_registration.csv')
    meta = json.loads((DATA / 'turn_selection.json').read_text(encoding='utf-8'))
    # 图中局部坐标仅作显示；评价误差由 MATLAB 球面距离计算。
    lon0, lat0 = table.reference_lon.iloc[0], table.reference_lat.iloc[0]
    def xy(prefix):
        return (6371 * np.cos(np.radians(lat0)) * np.radians(table[prefix+'_lon']-lon0),
                6371 * np.radians(table[prefix+'_lat']-lat0))
    tx, ty = xy('reference'); bx, by = xy('before'); axx, ayy = xy('after')
    fig, axs = plt.subplots(1, 2, figsize=(8, 6.2), layout='constrained', sharex=True, sharey=True)
    for ax, x, y, col, title, key in [(axs[0],bx,by,RED,'（a）配准前','before_error_km'),
                                     (axs[1],axx,ayy,BLUE,'（b）配准后','after_error_km')]:
        ax.plot(tx, ty, color='black', lw=1.7, label='ADS-B 参考航迹', zorder=3)
        ax.scatter(x, y, s=14, facecolors='none', edgecolors=col, linewidths=.85,
                   label='雷达定位点', zorder=2)
        ax.scatter([tx.iloc[0]],[ty.iloc[0]], marker='s', s=26, color='black',zorder=4)
        k = len(table)//2
        ax.annotate('',xy=(tx.iloc[k+2],ty.iloc[k+2]),xytext=(tx.iloc[k-2],ty.iloc[k-2]),
                    arrowprops={'arrowstyle':'->','color':'black','lw':1.8})
        ax.set_title(title)
        ax.set_xlabel('相对起点的东向距离 / km')
        ax.set_aspect('equal', adjustable='box')
        ax.grid(ls=':', color='.85')
        ax.legend(frameon=False, fontsize=10,loc='upper left')
        value = np.sqrt(np.mean(table[key]**2))
        ax.text(.04,.04,f'位置均方根误差：{value:.1f} km', transform=ax.transAxes, fontsize=10,
                bbox={'facecolor':'white','edgecolor':'none','pad':3})
    axs[0].set_ylabel('相对起点的北向距离 / km')
    # 相同显示范围，避免视觉缩放夸大效果。
    allx, ally = np.r_[tx,bx,axx], np.r_[ty,by,ayy]
    ylo, yhi = ally.min()-60, ally.max()+140
    midpoint = (allx.min()+allx.max())/2
    halfwidth = (yhi-ylo)*.34
    for ax in axs:
        ax.set_xlim(midpoint-halfwidth,midpoint+halfwidth); ax.set_ylim(ylo,yhi)
    fig.suptitle(f'转弯航迹配准示例（{meta["n_samples"]} 个参考采样点，间隔 30 s）',fontsize=12)
    save(fig, 'fig3_registration_demo.png')


def main():
    OUT.mkdir(exist_ok=True)
    workflow(); information(); turning()
    mc = pd.read_csv(DATA / 'calibration_mc.csv')
    for st, g in mc.groupby('station'):
        print('station',st,'n=',g.n_obs.iloc[0])
        for value,bound in [('h_km','bound_h_km'),('dR_km','bound_dR_km'),('dtheta_deg','bound_dtheta_deg')]:
            print(value, 'mean',g[value].mean(),'sd',g[value].std(),'bound',g[bound].mean())


if __name__=='__main__':
    main()
