"""从同一递推实现的蒙特卡洛结果绘制过程噪声敏感性图，汇总独立性能评价。"""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from scipy.io import loadmat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent;DATA=HERE/'数据/第四章/诊断';OUT=HERE.parent/'Pictures'
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'axes.unicode_minus':False,'font.size':10.5})


def main():
    trains=[]
    for f in sorted(DATA.glob('train*/monte_carlo.csv')):
        t=pd.read_csv(f);cfg=loadmat(f.parent/'configuration.mat',simplify_cells=True)
        for method,g in t.groupby('method'):
            trains.append(dict(label=f.parent.name,method=method,q=float(cfg['q_psd']),slow=float(cfg['slow']),
                fast=float(cfg['fast']),resample=bool(cfg.get('resample',False)),
                rmse_hit=g.position_rmse_hit_km.mean(),rmse_all=g.position_rmse_all_km.mean(),
                nees=g.nees_mean.mean(),nees95=g.nees_coverage95.mean(),nis=g.nis_mean.mean()))
    pd.DataFrame(trains).to_csv(DATA/'training_summary.csv',index=False)
    frames=[]
    for label in ['validate_baseline','validate_candidate']:
        t=pd.read_csv(DATA/label/'monte_carlo.csv');t['configuration']=label;frames.append(t)
        assert len(t)==800 and not t.failed.any()
        assert set(t.seed)==set(range(43001,43051))
        assert not set(t.seed)&set(range(42001,42021))
    a,b=frames
    protocol=json.loads((DATA/'validation_protocol.json').read_text(encoding='utf-8'))
    config=loadmat(DATA/'validate_candidate/configuration.mat',simplify_cells=True)
    assert float(config['q_psd'])==protocol['frozen_candidate']['q']==20
    assert bool(config['resample']) and int(config['seedbase'])==43000
    assert not any(combined for combined in [])
    original=HERE.parents[2]/'文稿撰写/single_target_with-turn/ukf'
    prototype_sources=json.loads((HERE/'实验实现/第四章/sources.json').read_text(encoding='utf-8'))
    for name,sha in prototype_sources.items():
        assert hashlib.sha256((original/name).read_bytes()).hexdigest()==sha,'原工程源码已发生变化'
    keys=['scene','pd','seed','method']
    aa=a.set_index(keys).sort_index();bb=b.set_index(keys).sort_index()
    for col in ['n_frames','n_hits','n_output','n_common','n_same_hit','raw_rmse_common_km']:
        assert np.allclose(aa[col],bb[col]),f'跨配置比较样本不相同: {col}'
    combined=pd.concat(frames,ignore_index=True)
    summary=combined.groupby(['configuration','scene','pd','method']).agg(
        runs=('seed','size'),rmse_hit=('position_rmse_hit_km','mean'),rmse_sd=('position_rmse_hit_km','std'),
        raw=('raw_rmse_common_km','mean'),rmse_all=('position_rmse_all_km','mean'),
        velocity=('velocity_vector_rmse_ms','mean'),nis=('nis_mean','mean'),nees=('nees_mean','mean'),
        nees95=('nees_coverage95','mean'),nis95=('nis_coverage95','mean'),
        position95=('position_ellipse95','mean'),output=('output_fraction','mean'))
    summary.to_csv(DATA/'validation_summary.csv')
    rng=np.random.default_rng(20261125);diff=[]
    for (scene,pdv),g in combined[combined.method=='IMM_UKF'].groupby(['scene','pd']):
        wide=g.pivot(index='seed',columns='configuration',values='position_rmse_hit_km')
        raw=g[g.configuration=='validate_candidate'].sort_values('seed').raw_rmse_common_km.to_numpy()
        for label,delta in [('candidate_minus_baseline',(wide.validate_candidate-wide.validate_baseline).to_numpy()),
                            ('candidate_minus_raw',wide.validate_candidate.to_numpy()-raw)]:
            boot=rng.choice(delta,(10000,len(delta)),replace=True).mean(axis=1)
            diff.append(dict(scene=scene,pd=pdv,contrast=label,mean=delta.mean(),
                ci_low=np.quantile(boot,.025),ci_high=np.quantile(boot,.975)))
    pd.DataFrame(diff).to_csv(DATA/'validation_differences.csv',index=False)
    print(summary.loc[(slice(None),slice(None),.6,'IMM_UKF'),:].round(3).to_string())
    print(pd.DataFrame(diff).query('pd == .6').round(3).to_string(index=False))
    sweep=[]
    for suffix,q in [('002',.02),('02',.2),('2',2.),('20',20.)]:
        folder=DATA/f'train_resample_q{suffix}'
        cfg=loadmat(folder/'configuration.mat',simplify_cells=True)
        assert bool(cfg['resample']) and np.isclose(float(cfg['q_psd']),q)
        assert np.isclose(float(cfg['slow']),.05) and np.isclose(float(cfg['fast']),.2)
        t=pd.read_csv(folder/'monte_carlo.csv')
        assert set(t.seed)==set(range(42001,42021)) and not t.failed.any()
        assert set(t.scene)=={'adsb'} and set(t.pd)=={.6}
        for method,g in t.groupby('method'):
            sweep.append(dict(q=q,method=method,runs=len(g),
                rmse_hit=g.position_rmse_hit_km.mean(),rmse_sd=g.position_rmse_hit_km.std(),
                raw=g.raw_rmse_common_km.mean(),nis=g.nis_mean.mean(),nees=g.nees_mean.mean(),
                nees95=g.nees_coverage95.mean()))
    sweep=pd.DataFrame(sweep)
    sweep.to_csv(DATA/'q_sensitivity.csv',index=False)
    g=sweep[sweep.method=='IMM_UKF'].sort_values('q');x=g.q.to_numpy()
    fig,ax=plt.subplots(1,2,figsize=(9,3.7),layout='constrained')
    ax[0].errorbar(x,g.rmse_hit,yerr=g.rmse_sd,color='#2471a3',marker='o',
                   capsize=4,lw=1.4,label='IMM-UKF 均值及样本标准差')
    ax[0].plot(x,g.raw,color='.45',ls='--',label='逐点定位均值')
    ax[0].set(title='（a）位置估计精度',ylabel='有量测帧位置 RMSE / km')
    for col,ref,label,color in [('nis',3,'NIS','#b74436'),('nees',4,'NEES','#2471a3')]:
        ax[1].plot(x,g[col],marker='s' if col=='nis' else 'o',color=color,lw=1.3,label=f'{label} 均值')
        ax[1].axhline(ref,color=color,ls=':',lw=1,label=f'{label} 理论参考值 {ref}')
    ax[1].set(title='（b）不确定性统计',ylabel='归一化平方统计量均值')
    for axis in ax:
        axis.set_xscale('log');axis.set_xticks(x,labels=['0.02','0.2','2','20'])
        axis.set_xlabel('过程噪声谱密度 q / (m²/s³)')
        axis.legend(fontsize=8.5);axis.grid(ls=':',alpha=.4)
    fig.savefig(OUT/'fig4_filter_improvement.png',dpi=240,facecolor='white',bbox_inches='tight');plt.close(fig)
    print('PASS: 1600 validation results; paired samples and seed separation verified')
    sources=[HERE/'diagnose_ch4_filtering.m',HERE/'check_ch4_process_noise.m',HERE/'prepare_ch4_prototype.py',HERE/'prepare_ch4_validation.py',
             HERE/'review_ch4_diagnostics.py']+list((HERE/'实验实现/第四章').glob('*.m'))
    meta={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (DATA/'diagnostic_source_hashes.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
