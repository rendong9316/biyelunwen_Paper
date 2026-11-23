"""保存预选附加轨迹及冻结的独立验证方案，不按验证误差筛选轨迹。"""
from pathlib import Path
import csv,json,hashlib,importlib.util

HERE=Path(__file__).resolve().parent


def main():
    spec=importlib.util.spec_from_file_location('g',HERE/'_fig_ch2_new.py')
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    pts=sorted([r for r in g.read_scene() if r['icao']=='T14342'],key=lambda r:r['t'])
    runs=[];run=[]
    for r in pts:
        ok=g.in_view(r['lon'],r['lat'],(*g.COMP['r1'],g.COMP['c1']),g.COMP['half']) and not 12<=r['t'].hour<18
        if not ok or (run and (r['t']-run[-1]['t']).total_seconds()!=30):
            if run:runs.append(run)
            run=[]
        if ok:run.append(r)
    if run:runs.append(run)
    run=max(runs,key=len);assert len(run)==66
    out=HERE/'数据/第四章/诊断';out.mkdir(parents=True,exist_ok=True)
    with (out/'validation_reference.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['elapsed_sec','lon','lat'])
        w.writerows([[(r['t']-run[0]['t']).total_seconds(),r['lon'],r['lat']] for r in run])
    meta={'track':'T14342','n_samples':len(run),'start_utc':str(run[0]['t']),'end_utc':str(run[-1]['t']),
        'source_sha256':hashlib.sha256(Path(g.SCENE).read_bytes()).hexdigest(),
        'rule':'按已选身份取R1视场内最长连续段，不根据滤波误差选择；不用于训练',
        'frozen_candidate':{'q':20,'slow':.05,'fast':.2,'resample':True},
        'training_seeds':'42001..42020','validation_seeds':'43001..43050'}
    (out/'validation_protocol.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('saved frozen validation protocol and 66-point second track')


if __name__=='__main__':main()
