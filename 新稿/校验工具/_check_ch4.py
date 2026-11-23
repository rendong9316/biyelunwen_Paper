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
    print('PASS：600条记录，50个配对种子、共同帧、嵌套命中、固定图示、汇总及来源哈希一致。')


if __name__=='__main__':
    main()
