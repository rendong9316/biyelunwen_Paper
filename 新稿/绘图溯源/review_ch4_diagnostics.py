"""同实现加密扫参、冻结参数、汇总独立评价；--select 不读取评价结果。"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.io import loadmat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE/'数据/第四章/诊断'
OUT = HERE.parent/'Pictures'
plt.rcParams.update({'font.family': ['Times New Roman', 'SimSun'],
                     'axes.unicode_minus': False, 'font.size': 10.5})


def folder_name(q):
    return 'train_resample_q' + ({.02: '002', .2: '02'}.get(q, f'{q:g}'))


def scan_and_select():
    protocol_path = DATA/'refinement_protocol.json'
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    rows, sources, reference = [], {}, None
    for q in protocol['q_grid']:
        folder = DATA/folder_name(q)
        cfg = loadmat(folder/'configuration.mat', simplify_cells=True)
        assert bool(cfg['resample']) and np.isclose(float(cfg['q_psd']), q)
        assert np.isclose(float(cfg['slow']), .05) and np.isclose(float(cfg['fast']), .2)
        t = pd.read_csv(folder/'monte_carlo.csv')
        assert len(t) == 40 and not t.failed.any()
        assert set(t.seed) == set(range(42001, 42021))
        assert set(t.scene) == {'adsb'} and set(t.pd) == {.6}
        paired = t.set_index(['scene', 'pd', 'seed', 'method']).sort_index()
        cols = ['n_frames', 'n_hits', 'n_output', 'n_common', 'n_same_hit', 'raw_rmse_common_km']
        if reference is not None:
            assert reference.index.equals(paired.index)
            assert np.allclose(reference[cols], paired[cols])
        reference = paired
        for method, g in t.groupby('method'):
            rows.append(dict(q=q, method=method, runs=len(g),
                rmse_hit=g.position_rmse_hit_km.mean(), rmse_sd=g.position_rmse_hit_km.std(),
                raw=g.raw_rmse_common_km.mean(), nis=g.nis_mean.mean(), nees=g.nees_mean.mean(),
                nees95=g.nees_coverage95.mean()))
        for name in ['monte_carlo.csv', 'configuration.mat']:
            file = folder/name
            sources[str(file.relative_to(DATA))] = hashlib.sha256(file.read_bytes()).hexdigest()
    sweep = pd.DataFrame(rows)
    sweep.to_csv(DATA/'q_sensitivity.csv', index=False)
    g = sweep[sweep.method == 'IMM_UKF'].copy()
    g['eligible'] = g.nis.between(2.25, 3.75) & g.nees.between(3, 5)
    assert g.eligible.any(), '无参数满足已规定的均值工程容差，不能自动选取'
    chosen = g[g.eligible].sort_values(['rmse_hit', 'q']).iloc[0]
    q = float(chosen.q)
    selection = dict(q=q, slow=.05, fast=.2, resample=True,
        parameter_seeds=protocol['parameter_seeds'], evaluation_seeds=protocol['evaluation_seeds'],
        evaluation_folder=f'evaluate_dense_q{q:g}', sample_seed=protocol['evaluation_seeds'][0],
        selection_rule=protocol['selection_rule'],
        protocol_sha256=hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        parameter_data_sha256=sources)
    path = DATA/'parameter_selection.json'
    if path.exists():
        assert json.loads(path.read_text(encoding='utf-8')) == selection, '冻结参数或选参数据发生变化'
    else:
        path.write_text(json.dumps(selection, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(g[['q', 'rmse_hit', 'rmse_sd', 'nis', 'nees', 'eligible']].round(4).to_string(index=False))
    print(f'SELECTED q={q:g}; performance seeds 44001..44050; evaluation not used for selection')
    return sweep, selection


def plot_sensitivity(sweep, selection):
    g = sweep[sweep.method == 'IMM_UKF'].sort_values('q')
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), layout='constrained')
    for row in range(2):
        local = g if row == 0 else g[g.q.between(2, 20)]
        x = local.q.to_numpy()
        axes[row, 0].errorbar(x, local.rmse_hit, yerr=local.rmse_sd, color='#2471a3',
            marker='o', capsize=3, lw=1.3, label='IMM-UKF 均值及样本标准差')
        if row == 0:
            axes[row, 0].plot(x, local.raw, color='.45', ls='--', label='逐点定位均值')
        axes[row, 0].set_ylabel('位置 RMSE / km')
        for col, ref, label, color in [('nis', 3, 'NIS', '#b74436'), ('nees', 4, 'NEES', '#2471a3')]:
            axes[row, 1].plot(x, local[col], marker='s' if col == 'nis' else 'o',
                             color=color, lw=1.3, label=f'{label} 均值')
            axes[row, 1].axhline(ref, color=color, ls=':', lw=1, label=f'{label} 参考值 {ref}')
        axes[row, 1].set_ylabel('归一化平方统计量均值')
    for axis in axes.flat:
        axis.axvline(selection['q'], color='.4', ls='-.', lw=.8)
        axis.set_xlabel('过程噪声谱密度 q / (m²/s³)')
        axis.grid(ls=':', alpha=.4)
    for axis in axes[0]:
        axis.set_xscale('log')
        axis.set_xticks([.02, .2, 1, 5, 30], labels=['0.02', '0.2', '1', '5', '30'])
        axis.legend(fontsize=8)
    for axis in axes[1]:
        axis.set_xticks([2, 4, 6, 8, 10, 12, 16, 20])
    axes[0, 0].set_title('（a）全范围位置精度')
    axes[0, 1].set_title('（b）全范围不确定性统计')
    axes[1, 0].set_title('（c）2—20 区间位置精度')
    axes[1, 1].set_title('（d）2—20 区间不确定性统计')
    fig.savefig(OUT/'fig4_filter_improvement.png', dpi=240, facecolor='white', bbox_inches='tight')
    plt.close(fig)


def evaluate(selection):
    folder = DATA/selection['evaluation_folder']
    t = pd.read_csv(folder/'monte_carlo.csv')
    cfg = loadmat(folder/'configuration.mat', simplify_cells=True)
    assert np.isclose(float(cfg['q_psd']), selection['q']) and bool(cfg['resample'])
    assert int(cfg['seedbase']) == 44000 and len(t) == 800 and not t.failed.any()
    assert set(t.seed) == set(range(44001, 44051))
    assert not t.duplicated(['scene', 'pd', 'seed', 'method']).any()
    summary = t.groupby(['scene', 'pd', 'method']).agg(
        runs=('seed', 'size'), rmse_hit=('position_rmse_hit_km', 'mean'),
        rmse_sd=('position_rmse_hit_km', 'std'), raw=('raw_rmse_common_km', 'mean'),
        rmse_all=('position_rmse_all_km', 'mean'), velocity=('velocity_vector_rmse_ms', 'mean'),
        nis=('nis_mean', 'mean'), nees=('nees_mean', 'mean'), nees95=('nees_coverage95', 'mean'),
        nis95=('nis_coverage95', 'mean'), position95=('position_ellipse95', 'mean'),
        output=('output_fraction', 'mean'))
    summary.to_csv(DATA/'final_summary.csv')
    rng = np.random.default_rng(20261126)
    diffs = []
    for (scene, pdv), g in t[t.method == 'IMM_UKF'].groupby(['scene', 'pd']):
        delta = (g.position_rmse_hit_km-g.raw_rmse_common_km).to_numpy()
        boot = rng.choice(delta, (10000, len(delta)), replace=True).mean(axis=1)
        diffs.append(dict(scene=scene, pd=pdv, mean=delta.mean(),
                          ci_low=np.quantile(boot, .025), ci_high=np.quantile(boot, .975)))
    pd.DataFrame(diffs).to_csv(DATA/'final_differences.csv', index=False)
    print(summary.loc[(slice(None), .6, 'IMM_UKF'), :].round(3).to_string())
    print(pd.DataFrame(diffs).query('pd == .6').round(3).to_string(index=False))
    print('PASS: 800 final results; frozen parameters and independent seeds verified')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--select', action='store_true', help='仅扫描选参结果并冻结参数，不读取性能评价')
    args = parser.parse_args()
    sweep, selection = scan_and_select()
    plot_sensitivity(sweep, selection)
    if not args.select:
        evaluate(selection)
    sources = [HERE/name for name in ['diagnose_ch4_filtering.m', 'check_ch4_process_noise.m',
        'prepare_ch4_prototype.py', 'prepare_ch4_validation.py', 'review_ch4_diagnostics.py',
        'refine_ch4_q.m', 'evaluate_ch4_selected.m']]
    sources += list((HERE/'实验实现/第四章').glob('*.m'))
    meta = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (DATA/'diagnostic_source_hashes.json').write_text(
        json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
