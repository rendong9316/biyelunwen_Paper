"""第四章中文滤波图；所有结果读取R2023a导出，地图仅作淡色地理背景。"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

HERE=Path(__file__).resolve().parent
DATA=HERE/'数据/第四章'; OUT=HERE.parent/'Pictures'
BLUE,RED='#2471a3','#b74436'
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'font.size':10.5,
    'axes.unicode_minus':False,'mathtext.fontset':'stix'})


def save(fig,name):
    fig.savefig(OUT/name,dpi=240,facecolor='white',bbox_inches='tight',pad_inches=.12)
    plt.close(fig);print('saved',name)


def structure():
    fig,ax=plt.subplots(figsize=(9,4.7));ax.axis('off');ax.set(xlim=(0,10),ylim=(0,6))
    def box(x,y,w,h,text):
        ax.add_patch(Rectangle((x,y),w,h,fc='white',ec='black',lw=1.1))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10)
    def arrow(a,b):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.1,'color':'black'})
    box(.2,2.4,1.8,1.1,'上一时刻各模型\n状态、协方差\n及模型概率')
    box(2.6,2.4,1.5,1.1,'条件交互混合\n分模型初始化')
    box(4.7,4.7,1.7,.7,'匀速模型滤波')
    for y,text in [(3.7,'左转模型（缓转）'),(2.7,'左转模型（较快）'),(1.7,'右转模型（较快）'),(.7,'右转模型（缓转）')]:
        box(4.7,y,1.7,.7,text)
    box(7.1,3.0,2.5,1.1,'新息似然与模型概率更新\n合成状态及协方差')
    box(7.1,.7,2.5,1.1,'局部航迹输出\n位置、速度、协方差')
    arrow((2,2.95),(2.6,2.95))
    for y in [5.05,4.05,3.05,2.05,1.05]:
        arrow((4.1,2.95),(4.7,y));arrow((6.4,y),(7.1,3.55))
    arrow((8.35,3),(8.35,1.8))
    ax.text(5.55,5.85,'当前量测进入各模型；漏检时仅作预测',ha='center',fontsize=10)
    # 各后验模型保留后进入下一轮混合，不能以总融合状态覆盖各模型。
    ax.plot([7.0,7.0,.1,.1],[3.8,5.58,5.58,3.4],color='black',lw=.9,ls='--')
    arrow((.1,3.4),(.2,3.1))
    ax.text(2.6,5.65,'各模型后验与概率进入下一周期',ha='center',fontsize=9.5)
    save(fig,'fig4_1_imm_structure.png')


def background(ax,bounds):
    content=json.loads((DATA/'map_background.geojson').read_text(encoding='utf-8'))
    def draw(g,kind):
        typ=g['type'];c=g['coordinates']
        if typ=='LineString':
            a=np.asarray(c);ax.plot(a[:,0],a[:,1],color='#b9c9d0' if 'rivers' in kind else '.78',
                                 lw=.5,zorder=0)
        elif typ=='MultiLineString':
            for a in c:draw({'type':'LineString','coordinates':a},kind)
        elif typ=='GeometryCollection':
            for a in g['geometries']:draw(a,kind)
    for f in content['features']:draw(f['geometry'],f['properties']['kind'])
    ax.set_xlim(bounds[:2]);ax.set_ylim(bounds[2:]);ax.set_aspect(1/np.cos(np.radians(np.mean(bounds[2:]))))
    ax.grid(ls=':',color='.89',zorder=0);ax.set_xlabel('经度 / °E');ax.set_ylabel('纬度 / °N')
    # 仅标示少量城市位置用于空间索引。
    for name,x,y in [('宜昌',111.29,30.69),('恩施',109.48,30.27),('荆州',112.24,30.34),('襄阳',112.14,32.04),('十堰',110.79,32.65)]:
        if bounds[0]<x<bounds[1] and bounds[2]<y<bounds[3]:
            ax.plot(x,y,'.',color='.55',ms=3,zorder=1)
            ax.annotate(name,(x,y),xytext=(3,-8),textcoords='offset points',fontsize=8,color='.5')


def filter_line(ax,t,labels=False):
    coords=np.c_[t.lon,t.lat];lines=[];styles=[]
    for k in range(1,len(t)):
        if not np.isfinite(coords[k-1:k+1]).all() or t.track_id.iloc[k]!=t.track_id.iloc[k-1]:continue
        lines.append(coords[k-1:k+1]);styles.append('solid' if t.updated.iloc[k] else 'dashed')
    ax.add_collection(LineCollection(lines,colors=BLUE,linewidths=1.7,linestyles=styles,zorder=4))
    if labels:
        ax.plot([],[],color=BLUE,lw=1.7,label='IMM-UKF 航迹')
        ax.plot([],[],color=BLUE,ls='--',lw=1.3,label='漏检帧预测段')


def track_map(scene,title,output):
    t=pd.read_csv(DATA/f'{scene}_IMM_UKF_demo.csv')
    a=pd.concat([t.reference_lon,t.raw_lon,t.lon]);b=pd.concat([t.reference_lat,t.raw_lat,t.lat])
    # 固定量测种子；不依据误差挑选图示。
    bounds=[a.min()-.25,a.max()+.25,b.min()-.25,b.max()+.25]
    mid=(bounds[0]+bounds[1])/2
    width=max(bounds[1]-bounds[0],(bounds[3]-bounds[2])*.65/np.cos(np.radians(np.mean(bounds[2:]))))
    bounds[:2]=[mid-width/2,mid+width/2]
    fig,axes=plt.subplots(1,2,figsize=(8.5,6.2),layout='constrained')
    for i,ax in enumerate(axes):
        background(ax,bounds)
        ax.plot(t.reference_lon,t.reference_lat,'k-',lw=1.5,label='参考航迹',zorder=3)
        ax.scatter(t.raw_lon,t.raw_lat,s=14,facecolors='none',edgecolors=RED,
                   linewidths=.7,label='滤波前定位点',zorder=2,alpha=.9 if i==0 else .35)
        ax.plot(t.reference_lon.iloc[0],t.reference_lat.iloc[0],'ks',ms=4)
        if i==1:filter_line(ax,t,True)
        ax.set_title('（a）逐点定位' if i==0 else '（b）递推滤波输出')
        ax.legend(loc='upper left',framealpha=.95,fontsize=9)
    # 每幅图右侧给出相同位置的转弯局部放大；参考转弯样本决定窗口。
    turn=t.turn.astype(bool); indices=np.flatnonzero(turn)
    center=int(indices[len(indices)//2]) if len(indices) else len(t)//2
    x,y=t.reference_lon.iloc[center],t.reference_lat.iloc[center]
    for i,ax in enumerate(axes):
        mini=inset_axes(ax,width='44%',height='30%',loc='lower left',borderpad=1.4)
        mini.plot(t.reference_lon,t.reference_lat,'k-',lw=1.3)
        mini.scatter(t.raw_lon,t.raw_lat,s=9,facecolors='none',edgecolors=RED,linewidths=.6,alpha=.65)
        if i==1:filter_line(mini,t)
        mini.set_xlim(x-.30,x+.30);mini.set_ylim(y-.30,y+.30)
        mini.set_aspect(1/np.cos(np.radians(y)));mini.tick_params(labelsize=7)
        mini.set_title('转弯区段放大',fontsize=8);mini.grid(ls=':',alpha=.4)
        ax.add_patch(Rectangle((x-.3,y-.3),.6,.6,fc='none',ec='.4',ls=':',lw=.8,zorder=5))
    fig.suptitle(title,fontsize=12)
    save(fig,output)


def time_errors():
    fig,axes=plt.subplots(2,1,figsize=(9,5.6),sharex=False,layout='constrained')
    for ax,scene,title in zip(axes,['turn','adsb'],['（a）纯仿真转弯','（b）ADS-B 转弯轨迹']):
        t=pd.read_csv(DATA/f'{scene}_IMM_UKF_demo.csv');c=pd.read_csv(DATA/f'{scene}_CV_UKF_demo.csv')
        x=t.elapsed_sec/60
        ax.scatter(x,t.raw_error_km,marker='o',s=10,facecolors='none',edgecolors='.55',label='逐点定位')
        ax.plot(x,c.pos_error_km,color=RED,ls='--',lw=1.1,label='CV-UKF')
        ax.plot(x,t.pos_error_km,color=BLUE,lw=1.4,label='IMM-UKF')
        for k in np.flatnonzero(~t.hit.astype(bool)):
            ax.axvspan(x.iloc[k]-.24,x.iloc[k]+.24,color='.92',zorder=0)
        ax.set(title=title,xlabel='相对时间 / min',ylabel='位置误差 / km')
        ax.grid(ls=':',alpha=.4);ax.legend(fontsize=9,ncol=3,loc='upper left')
    save(fig,'fig4_error_time.png')


def summary():
    t=pd.read_csv(DATA/'monte_carlo.csv')
    assert not t.failed.any(),'存在未形成航迹的试验，须单独解释后再汇总'
    summary=t.groupby(['scene','pd','method']).agg(
        runs=('seed','size'),hit_rmse=('position_rmse_hit_km','mean'),
        hit_sd=('position_rmse_hit_km','std'),raw=('raw_rmse_common_km','mean'),
        all_rmse=('position_rmse_all_km','mean'),vel=('velocity_vector_rmse_ms','mean'),
        nis=('nis_mean','mean'),nees=('nees_mean','mean'),
        nis95=('nis_coverage95','mean'),nees95=('nees_coverage95','mean'),
        output=('output_fraction','mean'),tracks=('n_tracks','mean'))
    summary.to_csv(DATA/'summary.csv',float_format='%.6f');print(summary.round(3).to_string())
    # 种子为独立重复单位；同一种子的方法差作配对自助抽样。
    ci=[];rng=np.random.default_rng(20261124)
    for (scene,pdval),g in t.groupby(['scene','pd']):
        wide=g.pivot(index='seed',columns='method',values='position_rmse_all_km')
        delta=(wide.IMM_UKF-wide.CV_UKF).to_numpy()
        boot=rng.choice(delta,(10000,len(delta)),replace=True).mean(axis=1)
        ci.append({'scene':scene,'pd':pdval,'delta_mean_km':delta.mean(),
                   'ci_low':np.quantile(boot,.025),'ci_high':np.quantile(boot,.975)})
    pd.DataFrame(ci).to_csv(DATA/'paired_differences.csv',index=False)
    print(pd.DataFrame(ci).round(4).to_string(index=False))
    project=HERE.parents[2]
    source_paths=[HERE/'export_ch4_filtering.m',HERE/'_fig_ch4_filtering.py',HERE/'prepare_ch4_map.py',
        HERE/'数据/第三章/turn_reference.csv']
    root=project/'文稿撰写/single_target_with-turn'
    source_paths += [root/p for p in ['config/params_coverage_online.m','config/simulation_params_oracle.m',
        'ukf/ukf_jichu.m','ukf/ukf_imm.m','ukf/radar_params.m','simulation/bistatic_inverse_solver.m',
        'tracker/run_oracle_tracker_sequence.m','tracker/trackStarter_logic_oracle.m']]
    meta=dict(matlab_version='9.14.0.2206163 (R2023a)',seeds=[41001,41050],
        sample_seed=41001,bootstrap_seed=20261124,bootstrap_repetitions=10000,
        measurement='当前UKF的球面观测函数，真实和假定虚高均300km，零残余配准偏差',
        source_hashes={str(p.relative_to(project)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths})
    (DATA/'provenance.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    structure()
    track_map('turn','纯仿真转弯轨迹：同一组量测的滤波前后对比','fig4_simulation_tracks.png')
    track_map('adsb','ADS-B 数据驱动仿真：同一组量测的滤波前后对比','fig4_adsb_tracks.png')
    time_errors();summary()
