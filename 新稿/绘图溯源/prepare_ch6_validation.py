"""将第四章已验证的滤波实现接入隔离的在线验证入口，不修改研究仓库。"""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2] / '文稿撰写' / 'single_target_with-turn'
OUT = HERE / '实验实现' / '第六章'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = {}
    for filename in ['ukf_jichu', 'ukf_imm']:
        source = HERE / '实验实现' / '第四章' / f'{filename}_ch4.m'
        code = source.read_text(encoding='utf-8')
        code = code.replace('ukf_imm_ch4', 'ukf_imm').replace('ukf_jichu_ch4', 'ukf_jichu')
        (OUT / f'{filename}.m').write_text(code, encoding='utf-8')
        sources[str(source.relative_to(HERE))] = hashlib.sha256(source.read_bytes()).hexdigest()
    source_files = [
        'run.m',
        'config/params_coverage_online.m',
        'config/params_coverage_registered.m',
        'config/simulation_params_oracle.m',
        'simulation/build_truth_scenario.m',
        'simulation/load_adsb_scenario.m',
        'tracker/central_track_manager.m',
        'ukf/ukf_dispatch.m',
        'fusion/+online_fuse/fuse_step.m',
        'fusion/+online_fuse/+algorithms/scc.m',
        'evaluation/evaluate_online_track_length.m',
        'evaluation/evaluate_paper_metrics_online.m',
        'evaluation/evaluate_online_metrics.m',
    ]
    source = ROOT / 'run.m'
    code = source.read_text(encoding='utf-8')
    code = code.replace('function result = run(', 'function result = run_ch6_pipeline(', 1)
    anchor = "    project_root = fileparts(mfilename('fullpath'));"
    assert code.count(anchor) == 1
    code = code.replace(anchor, "    isolated_root = fileparts(mfilename('fullpath'));\n"
                        "    project_root = fullfile(fileparts(fileparts(fileparts(fileparts(fileparts(isolated_root))))), ...\n"
                        "        '文稿撰写','single_target_with-turn');")
    anchor = '    if isempty(params_override)'
    assert code.count(anchor) == 1
    code = code.replace(anchor, "    addpath(isolated_root,'-begin');\n"
                        "    assert(contains(which('ukf_jichu'),isolated_root));\n"
                        "    assert(contains(which('ukf_imm'),isolated_root));\n\n" + anchor)
    (OUT / 'run_ch6_pipeline.m').write_text(code, encoding='utf-8')
    sources.update({f'研究工程/{rel}':hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
                    for rel in source_files})
    (OUT / 'sources.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('已生成隔离在线入口：沿用第四章完整预测协方差重采样，研究工程保持只读。')


if __name__ == '__main__':
    main()
