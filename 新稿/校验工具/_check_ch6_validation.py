"""核验第六章冻结配置、共同目标历元、几何分母与正式图表登记。"""
from pathlib import Path
import hashlib
import json
import re

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / '绘图溯源/数据/第六章'
RUNS = DATA / '冻结验证'


def main():
    generator_sources=json.loads((BASE/'绘图溯源/实验实现/第六章/sources.json').read_text(encoding='utf-8'))
    research=BASE.parent.parent/'文稿撰写/single_target_with-turn'
    for rel,expected in generator_sources.items():
        source=(research/rel.removeprefix('研究工程/')) if rel.startswith('研究工程/') else (BASE/'绘图溯源'/rel)
        assert hashlib.sha256(source.read_bytes()).hexdigest()==expected,f'实验上游源码变化：{rel}'
    hashes=json.loads((DATA/'validation_hashes.json').read_text(encoding='utf-8'))
    for rel,expected in hashes.items():
        assert hashlib.sha256((DATA/rel).read_bytes()).hexdigest()==expected,rel
    protocol=json.loads((DATA/'validation_protocol.json').read_text(encoding='utf-8'))
    records=pd.read_csv(DATA/'model_common_epochs.csv')
    assert len(records)==40
    assert records.groupby('seed')['n'].nunique().eq(1).all()
    for seed in range(*[protocol['model_seeds'][0],protocol['model_seeds'][1]+1]):
        configs=[];tables=[]
        for group in ['wide','cruise']:
            config=json.loads((RUNS/f'{group}_{seed}_configuration.json').read_text(encoding='utf-8'))
            assert 'R2023a' in config['matlab'] and config['q']==6
            assert config.get('extraction_version',0)>=2
            p=config['params'];assert p['online_M']==6 and p['online_N']==8
            assert p['online_fusion_methods']==['SCC']
            configs.append({k:v for k,v in p.items() if k not in ['imm_ct_omega_slow_deg','imm_ct_omega_fast_deg']})
            df=pd.read_csv(RUNS/f'{group}_{seed}_samples.csv').query('n_sources == 2')
            assert not df.duplicated(['target','frame']).any()
            tables.append(df.set_index(['target','frame']))
        assert configs[0]==configs[1],f'模型集之外的参数不相同 seed={seed}'
        common=tables[0].index.intersection(tables[1].index)
        assert len(common)==int(records[records.seed.eq(seed)].n.iloc[0])
        assert np.allclose(tables[0].loc[common,['truth_lon','truth_lat']],
                           tables[1].loc[common,['truth_lon','truth_lat']])
    coverage=pd.read_csv(DATA/'coverage_common_window.csv')
    assert len(coverage)==20
    assert np.allclose(coverage.geometry_union,
                       coverage.geometry_r1+coverage.geometry_r2-coverage.geometry_overlap)
    assert (coverage.system_longest<=coverage.geometry_union).all()
    assert np.allclose(coverage.union_realization,coverage.system_longest/coverage.geometry_union)
    assert np.allclose(coverage.geometric_normalized_system/coverage.geometry_ceiling_ratio,
                       coverage.union_realization)
    coverage_summary=pd.read_csv(DATA/'coverage_common_window.csv').groupby('case').union_realization.mean()
    assert np.isclose(coverage_summary.min(),.938,atol=.003)
    assert np.isclose(coverage_summary.max(),.959,atol=.003)
    systems=pd.read_csv(DATA/'system_segment_summary.csv')
    assert len(systems)==3 and systems.targets_with_local_output.eq(59).all()
    for seed in range(protocol['system_seeds'][0],protocol['system_seeds'][1]+1):
        config=json.loads((RUNS/f'system_{seed}_configuration.json').read_text(encoding='utf-8'))
        assert config.get('extraction_version',0)>=4
    assert np.allclose(systems.mean_track_ratio.mean(),1.265,atol=.002)
    assert np.allclose(systems.system_rmse.mean(),5.126,atol=.01)
    paired=pd.read_csv(DATA/'model_paired_summary.csv').set_index('metric')
    assert paired.loc['system_rmse','wide_negative']==0
    assert paired.loc['system_rmse','cruise_negative']==0
    assert np.isclose(paired.loc['system_rmse','wide_mean'],5.280,atol=.01)
    assert np.isclose(paired.loc['system_rmse','cruise_mean'],5.041,atol=.01)
    # 解析边界确实使静态方差比等于1；k为标准差比。
    for k in [1.,1.4,2.,3.]:
        rho=(1+k*k)/(2*k**3)
        assert np.isclose(k*k/(1+k*k)+2*rho*k**3/(1+k*k)**2,1)
    text=(BASE/'论文全文.md').read_text(encoding='utf-8')
    ch6=text.split('# 第6章',1)[1].split('# 第7章',1)[0]
    for stale in ['27/47','91.6%','1.314','退化为 SCC','未在两站滤波器间递推互协方差','mc_online_chain.csv']:
        assert stale not in ch6,f'第六章残留过时结论：{stale}'
    for path in re.findall(r'\]\((Pictures/fig6[^)]+)\)',ch6):
        assert (BASE/path).is_file(),path
        assert Path(path).name in (BASE/'图源清单.md').read_text(encoding='utf-8')
    print('PASS：第六章哈希、R2023a/q=6/6-of-8、20种子共同历元、20次覆盖分母及理论边界一致。')


if __name__=='__main__':
    main()
