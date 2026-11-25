"""核验第五章在线策略快照、系统主场景数据与关键表述。"""
from pathlib import Path
import hashlib
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE/'绘图溯源/数据/第五章'
PAPER = BASE/'论文全文.md'


def main():
    sources = json.loads((DATA/'sources.json').read_text(encoding='utf-8'))
    for name, meta in sources.items():
        source = BASE.parent.parent/meta['source']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == meta['sha256'], f'来源变化：{name}'
        snapshot = DATA/name
        assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == meta['sha256'], f'快照不匹配：{name}'

    expected = {
        'online_assoc_compare_A.csv': {'dualgate': (14, 14, 0), 'nn': (16, 14, 2),
                                       'sequential': (14, 14, 0), 'mewf': (14, 14, 0)},
        'online_assoc_compare_B.csv': {'dualgate': (20, 20, 0), 'nn': (23, 19, 4),
                                       'sequential': (20, 20, 0), 'mewf': (20, 20, 0)},
    }
    for filename, checks in expected.items():
        table = pd.read_csv(DATA/filename).set_index('method')
        for method, triple in checks.items():
            row = table.loc[method]
            assert (int(row.n_pairs), int(row.n_correct), int(row.n_wrong)) == triple

    summary = (DATA/'online_fr24_main_summary.txt').read_text(encoding='utf-8')
    assert '确认配对 35 对，正确 35 对' in summary
    assert '查准率 100.0%，查全率 94.6%' in summary
    paper = PAPER.read_text(encoding='utf-8')
    ch5 = paper.split('# 第5章', 1)[1].split('# 第6章', 1)[0]
    for statement in ['默认候选策略为双门限', '不采用匈牙利全局指派',
                      '37个实际具备两站确认航迹的目标对', '尚未充分覆盖更高并发']:
        assert statement in ch5, f'第五章缺少关键边界：{statement}'
    for stale in ['匈牙利算法求解全局', '正交分解显示收益', '63%', '26%', '11%']:
        assert stale not in ch5, f'第五章仍含旧结论：{stale}'
    assert '图[@fig:ch5_compare]' in ch5, '第五章策略对照图缺少正文交叉引用'
    assert all((BASE/'Pictures'/name).is_file() for name in
               ['fig5_1_mewf_framework.png', 'fig5_2_method_compare.png', 'fig5_3_decompose.png'])
    print('PASS：两个在线策略对照、FR24主场景、来源哈希及第五章核心算法表述一致。')


if __name__ == '__main__':
    main()
