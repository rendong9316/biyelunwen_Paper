"""按冻结协议复算第六章共同历元统计、覆盖实现率和系统分段误差。"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
DATA = HERE / '数据' / '第六章'
RUNS = DATA / '冻结验证'


def read(label, seed, kind='samples'):
    return pd.read_csv(RUNS / f'{label}_{seed}_{kind}.csv')


def vectors(df, prefix):
    delta = df[[f'{prefix}_lon', f'{prefix}_lat']].to_numpy(float) - df[['truth_lon', 'truth_lat']].to_numpy(float)
    delta[:, 0] *= 111.32 * np.cos(np.deg2rad(df.truth_lat))
    delta[:, 1] *= 110.57
    return delta


def score(df):
    errors = {name: vectors(df, name) for name in ['r1', 'r2', 'system']}
    result = {'n': len(df)}
    for name, vec in errors.items():
        norms = np.linalg.norm(vec, axis=1)
        result[f'{name}_rmse'] = float(np.sqrt(np.mean(norms**2)))
        result[f'{name}_median'] = float(np.median(norms))
        result[f'{name}_p90'] = float(np.quantile(norms, .9))
    for key in ['rmse', 'median', 'p90']:
        best = min(result[f'r1_{key}'], result[f'r2_{key}'])
        result[f'gain_{key}'] = 100 * (best - result[f'system_{key}']) / best
    a, b = errors['r1'], errors['r2']
    result['raw_cross'] = float(np.sum(a*b) / np.sqrt(np.sum(a*a)*np.sum(b*b)))
    a = a - a.mean(axis=0)
    b = b - b.mean(axis=0)
    result['centered_rho'] = float(np.sum(a*b) / np.sqrt(np.sum(a*a)*np.sum(b*b)))
    for col in ['nees1', 'nees2']:
        result[col] = float(df[col].mean())
    return result


def paired(rows):
    wide = rows[rows.group == 'wide'].set_index('seed')
    cruise = rows[rows.group == 'cruise'].set_index('seed')
    result = []
    for key in ['system_rmse','system_median','system_p90','gain_rmse','gain_median',
                'gain_p90','centered_rho','raw_cross','nees1','nees2']:
        a, b = wide[key], cruise.loc[wide.index, key]
        diff = (b-a).to_numpy()
        se = stats.sem(diff)
        low, high = stats.t.interval(.95, len(diff)-1, loc=diff.mean(), scale=se)
        p = stats.wilcoxon(diff, zero_method='wilcox').pvalue if np.any(diff) else 1.
        result.append(dict(metric=key, n=len(diff), wide_mean=a.mean(), cruise_mean=b.mean(),
                           delta_mean=diff.mean(), ci95_low=low, ci95_high=high,
                           p_wilcoxon=p, wide_negative=int((a<0).sum()),
                           cruise_negative=int((b<0).sum())))
    return pd.DataFrame(result)


def main():
    protocol = json.loads((DATA/'validation_protocol.json').read_text(encoding='utf-8'))
    rows, available = [], []
    for seed in range(protocol['model_seeds'][0], protocol['model_seeds'][1]+1):
        frames = {}
        for name in ['wide','cruise']:
            df = read(name, seed)
            mask = df.n_sources.eq(2) & df[['r1_lon','r2_lon','system_lon']].notna().all(axis=1)
            frames[name] = df[mask].set_index(['target','frame'])
            available.append(dict(group=name,seed=seed,**score(frames[name])))
        common = frames['wide'].index.intersection(frames['cruise'].index)
        assert len(common)>0, f'种子{seed}没有共同双源历元'
        for name in ['wide','cruise']:
            rows.append(dict(group=name,seed=seed,**score(frames[name].loc[common])))
    matched = pd.DataFrame(rows)
    matched.to_csv(DATA/'model_common_epochs.csv',index=False)
    pd.DataFrame(available).to_csv(DATA/'model_all_dual_epochs.csv',index=False)
    summary = paired(matched)
    summary.to_csv(DATA/'model_paired_summary.csv',index=False)
    cov = []
    for seed in range(protocol['coverage_seeds'][0],protocol['coverage_seeds'][1]+1):
        for case in protocol['coverage_cases']:
            df=read(case,seed,'lengths')
            assert len(df)==1
            row=df.iloc[0].to_dict()
            assert row['system_longest']<=row['geometry_union']
            row.update(case=case,seed=seed)
            row['geometry_ceiling_ratio']=row['geometry_union']/max(row['geometry_r1'],row['geometry_r2'])
            row['geometric_normalized_system']=row['system_longest']/max(row['geometry_r1'],row['geometry_r2'])
            cov.append(row)
    pd.DataFrame(cov).to_csv(DATA/'coverage_common_window.csv',index=False)
    systems=[]
    for seed in range(protocol['system_seeds'][0],protocol['system_seeds'][1]+1):
        df=read('system',seed)
        dual=df[df.n_sources.eq(2)]
        one=df[df.n_sources.eq(1)]
        errors=np.linalg.norm(vectors(one,'system'),axis=1)
        row=dict(seed=seed,**score(dual))
        row['single_rmse']=float(np.sqrt(np.mean(errors**2)))
        row['single_frames']=len(one)
        row['dual_fraction']=len(dual)/(len(one)+len(dual))
        lengths=read('system',seed,'lengths')
        covered=lengths[(lengths.geometry_union>0)&((lengths.local_r1_longest+lengths.local_r2_longest)>0)]
        row['mean_track_ratio']=covered.track_ratio.mean()
        row['mean_union_realization']=covered.union_realization.mean()
        row['targets_with_local_output']=len(covered)
        row['scene_targets']=len(lengths)
        systems.append(row)
    pd.DataFrame(systems).to_csv(DATA/'system_segment_summary.csv',index=False)
    # 图示选择只使用覆盖与输出时长；不依据定位误差挑选“好看”样本。
    df=read('system',protocol['system_seeds'][0])
    candidates=[]
    for tid,g in df.groupby('target'):
        if (g.geometry_r1.eq(1) & g.geometry_r2.eq(0)).sum()<3 or (g.geometry_r2.eq(1) & g.geometry_r1.eq(0)).sum()<3:
            continue
        if g.n_sources.eq(2).sum()<8:
            continue
        candidates.append((int(g.n_sources.eq(2).sum()),int(g.n_sources.gt(0).sum()),int(tid)))
    assert candidates,'没有满足两站接力示意条件的目标'
    candidates.sort(key=lambda x:(-x[0],-x[1],x[2]))
    selected=dict(seed=protocol['system_seeds'][0],target=candidates[0][2],
                  selection='先要求两站单独覆盖各不少于3帧、正确双源不少于8帧；再按双源帧数、总输出帧数降序，目标号升序')
    (DATA/'demo_selection.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    hashes={str(p.relative_to(DATA)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(RUNS.glob('*')) if p.is_file()}
    (DATA/'validation_hashes.json').write_text(json.dumps(hashes,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(summary.to_string(index=False))
    print('\nCOVERAGE\n',pd.DataFrame(cov).groupby('case')[['geometry_ceiling_ratio','track_ratio','union_realization']].mean())
    print('\nSYSTEM\n',pd.DataFrame(systems).mean(numeric_only=True).to_string())


if __name__=='__main__':
    main()
