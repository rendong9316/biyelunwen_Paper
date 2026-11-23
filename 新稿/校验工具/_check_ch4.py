"""审计第四章统计的配对、样本掩码、图示与原始导出的对应关系。"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

BASE=Path(__file__).resolve().parents[1]
DATA=BASE/'绘图溯源/数据/第四章'


def main():
    t=pd.read_csv(DATA/'monte_carlo.csv')
    assert len(t)==600 and not t.failed.any()
    assert not t.duplicated(['scene','pd','seed','method']).any()
    assert set(t.seed)==set(range(41001,41051))
    assert np.isfinite(t.select_dtypes('number').to_numpy()).all()
    assert ((t.n_same_hit<=t.n_common)&(t.n_common<=t.n_output)&(t.n_output<=t.n_frames)).all()
    for _,group in t.groupby(['scene','pd','seed']):
        assert len(group)==2
        for key in ['n_frames','n_hits','n_output','n_common','n_same_hit','n_tracks','raw_rmse_common_km']:
            assert np.isclose(group[key].iloc[0],group[key].iloc[1])
    hits=t[t.method=='IMM_UKF'].pivot(index=['scene','seed'],columns='pd',values='n_hits')
    assert (hits[.9]>=hits[.6]).all()
    pilot=BASE.parent/'paper_review_tmp/ch4_pilot_metrics.csv'
    if pilot.exists():
        p=pd.read_csv(pilot).set_index(['scene','pd','seed','method']).sort_index()
        f=t.set_index(['scene','pd','seed','method']).loc[p.index].sort_index()
        assert np.allclose(p.select_dtypes('number'),f.select_dtypes('number'),equal_nan=True)
    for scene in ['straight','turn','adsb']:
        a=pd.read_csv(DATA/f'{scene}_CV_UKF_demo.csv')
        b=pd.read_csv(DATA/f'{scene}_IMM_UKF_demo.csv')
        assert (a.hit==b.hit).all()
        for key in ['reference_lon','reference_lat','raw_lon','raw_lat','raw_error_km']:
            assert np.allclose(a[key],b[key],equal_nan=True)
        common=a.lon.notna()&b.lon.notna();same=common&a.hit.astype(bool)
        for name,frame in [('CV_UKF',a),('IMM_UKF',b)]:
            rec=t[(t.scene==scene)&(t.pd==.6)&(t.seed==41001)&(t.method==name)].iloc[0]
            assert rec.n_common==common.sum() and rec.n_same_hit==same.sum()
            assert np.isclose(rec.position_rmse_hit_km,np.sqrt(np.mean(frame.pos_error_km[same]**2)))
            assert np.isclose(rec.position_rmse_all_km,np.sqrt(np.mean(frame.pos_error_km[common]**2)))
    summary=pd.read_csv(DATA/'summary.csv').set_index(['scene','pd','method'])
    for key,g in t.groupby(['scene','pd','method']):
        assert np.isclose(summary.loc[key,'hit_rmse'],g.position_rmse_hit_km.mean(),atol=1e-6)
    meta=json.loads((DATA/'provenance.json').read_text(encoding='utf-8'))
    for rel,sha in meta['source_hashes'].items():
        p=BASE.parents[1]/rel
        assert hashlib.sha256(p.read_bytes()).hexdigest()==sha, f'源码或输入发生变化: {rel}'
    # 当前正文的数据由冻结参数记录确定；上述600条仅留作历史溯源检查。
    selection=json.loads((DATA/'诊断/parameter_selection.json').read_text(encoding='utf-8'))
    protocol_path=DATA/'诊断/refinement_protocol.json'
    protocol=json.loads(protocol_path.read_text(encoding='utf-8'))
    assert hashlib.sha256(protocol_path.read_bytes()).hexdigest()==selection['protocol_sha256']
    for rel,sha in selection['parameter_data_sha256'].items():
        assert hashlib.sha256((DATA/'诊断'/rel).read_bytes()).hexdigest()==sha
    formal=DATA/'诊断'/selection['evaluation_folder']
    f=pd.read_csv(formal/'monte_carlo.csv')
    assert len(f)==800 and not f.failed.any()
    assert not f.duplicated(['scene','pd','seed','method']).any()
    assert set(f.seed)==set(range(44001,44051))
    for scene in ['straight','turn','adsb','adsb_holdout']:
        a=pd.read_csv(formal/f'{scene}_CV_UKF_demo.csv')
        b=pd.read_csv(formal/f'{scene}_IMM_UKF_demo.csv')
        for key in ['hit','reference_lon','reference_lat','raw_lon','raw_lat','raw_error_km']:
            assert np.allclose(a[key],b[key],equal_nan=True)
        common=a.lon.notna()&b.lon.notna();same=common&a.hit.astype(bool)
        for name,frame in [('CV_UKF',a),('IMM_UKF',b)]:
            rec=f[(f.scene==scene)&(f.pd==.6)&(f.seed==selection['sample_seed'])&(f.method==name)].iloc[0]
            assert rec.n_common==common.sum() and rec.n_same_hit==same.sum()
            assert np.isclose(rec.position_rmse_hit_km,np.sqrt(np.mean(frame.pos_error_km[same]**2)))
            assert np.isclose(rec.position_rmse_all_km,np.sqrt(np.mean(frame.pos_error_km[common]**2)))
    reference=None
    for q in protocol['q_grid']:
        suffix={.02:'002',.2:'02'}.get(q,f'{q:g}')
        scan=pd.read_csv(DATA/f'诊断/train_resample_q{suffix}/monte_carlo.csv')
        assert len(scan)==40 and not scan.failed.any()
        assert set(scan.seed)==set(range(42001,42021))
        paired=scan.set_index(['scene','pd','seed','method']).sort_index()
        cols=['n_frames','n_hits','n_output','n_common','n_same_hit','raw_rmse_common_km']
        if reference is not None:
            assert reference.index.equals(paired.index)
            assert np.allclose(reference[cols],paired[cols])
        reference=paired
    summary=pd.read_csv(DATA/'诊断/final_summary.csv').set_index(['scene','pd','method'])
    for key,g in f.groupby(['scene','pd','method']):
        assert np.isclose(summary.loc[key,'rmse_hit'],g.position_rmse_hit_km.mean())
        assert np.isclose(summary.loc[key,'raw'],g.raw_rmse_common_km.mean())
    scan=pd.read_csv(DATA/'诊断/q_sensitivity.csv')
    g=scan[scan.method=='IMM_UKF']
    eligible=g[g.nis.between(2.25,3.75)&g.nees.between(3,5)]
    assert np.isclose(eligible.sort_values(['rmse_hit','q']).iloc[0].q,selection['q'])
    assert not set(f.seed)&set(range(42001,42021))
    manuscript=(BASE/'论文全文.md').read_text(encoding='utf-8')
    ch4=manuscript.split('# 第4章',1)[1].split('# 第5章',1)[0]
    for historical_word in ['原配置','候选配置','机动配置','原实现','修正后']:
        assert historical_word not in ch4
    print(f'PASS：正式800条方法记录及{40*len(protocol["q_grid"])}条同实现扫参记录配对一致；参数规则、数据哈希和固定效果图通过。')


if __name__=='__main__':
    main()
