"""仅按几何与转弯程度选择演示航迹，不根据配准结果挑选。"""
from pathlib import Path
from collections import defaultdict
import csv
import hashlib
import importlib.util
import json
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / '数据' / '第三章'
PROJECT = HERE.parents[2]
SCENE = PROJECT / '文稿撰写/data/adsb_ns/scene_fr24_all.csv'
CALIB = PROJECT / '文稿撰写/single_target_with-turn/data/adsb/calib_utc12_18.csv'


def main():
    spec = importlib.util.spec_from_file_location('scene_geometry', HERE / '_fig_ch2_new.py')
    geo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geo)
    with CALIB.open(encoding='utf-8-sig', newline='') as f:
        calib_ids = {r[0] for r in csv.reader(f)}
    groups = defaultdict(list)
    for row in geo.read_scene():
        groups[row['icao']].append(row)
    candidates = []
    cfg = geo.COMP
    for ident, points in groups.items():
        if ident in calib_ids:
            continue
        runs, run = [], []
        for point in sorted(points, key=lambda p: p['t']):
            valid = (not 12 <= point['t'].hour < 18 and geo.in_view(
                point['lon'], point['lat'], (*cfg['r1'], cfg['c1']), cfg['half']))
            if not valid or (run and (point['t'] - run[-1]['t']).total_seconds() != 30):
                if run:
                    runs.append(run)
                run = []
            if valid:
                run.append(point)
        if run:
            runs.append(run)
        for run in runs:
            if len(run) < 35:
                continue
            headings = np.unwrap(np.radians([geo.bearing(a['lon'], a['lat'], b['lon'], b['lat'])
                for a, b in zip(run[:-5], run[5:])]))
            turn = abs(float(np.degrees(np.median(headings[-5:]) - np.median(headings[:5]))))
            candidates.append((turn, ident, run))
    if not candidates:
        raise RuntimeError('没有符合条件的独立转弯航迹')
    turn, ident, points = max(candidates, key=lambda x: (x[0], x[1]))
    DATA.mkdir(parents=True, exist_ok=True)
    with (DATA / 'turn_reference.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_sec', 'lon', 'lat'])
        writer.writerows([((p['t'] - points[0]['t']).total_seconds(), p['lon'], p['lat']) for p in points])
    meta = dict(source=str(SCENE.relative_to(PROJECT)),
        source_sha256=hashlib.sha256(SCENE.read_bytes()).hexdigest(),
        calibration_source=str(CALIB.relative_to(PROJECT)),
        calibration_sha256=hashlib.sha256(CALIB.read_bytes()).hexdigest(),
        track_id=ident, start_utc=str(points[0]['t']), end_utc=str(points[-1]['t']),
        n_samples=len(points), heading_change_deg=turn,
        selection='R1视场内、时间连续30 s、至少35点、UTC12–18之外、身份不在标校表；取首尾五步航向中位数变化最大的段',
        note='仅选择几何形态，尚未生成噪声或计算配准效果；雷达量测由模型生成')
    (DATA / 'turn_selection.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
