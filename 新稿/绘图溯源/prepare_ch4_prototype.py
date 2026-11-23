"""仅在隔离目录生成UKF加性过程噪声重采样试验版本，不改研究工程。"""
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[2]/'文稿撰写/single_target_with-turn/ukf'
OUT=HERE/'实验实现/第四章'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    original=(SOURCE/'ukf_jichu.m').read_text(encoding='utf-8')
    anchor='    [x_pred, P_pred, X_pred, ukf] = predict_step_ukf(ukf);'
    assert original.count(anchor)==1
    revised=original.replace(anchor,anchor+"\n    % 加性过程噪声已进入P_pred；量测变换必须使用匹配该协方差的Sigma点。\n    X_pred = sigma_points_ukf(x_pred, P_pred, ukf.n, ukf.lam);")
    revised=revised.replace('ukf_jichu','ukf_jichu_ch4')
    revised=revised.replace('    ukf.params = params;','    ukf.params = params;\n    ukf.ch4_resampled = true;',1)
    (OUT/'ukf_jichu_ch4.m').write_text(revised,encoding='utf-8')
    imm=(SOURCE/'ukf_imm.m').read_text(encoding='utf-8')
    imm=imm.replace('ukf_imm','ukf_imm_ch4').replace('ukf_jichu','ukf_jichu_ch4')
    imm=imm.replace('    imm.params = params;','    imm.params = params;\n    imm.ch4_resampled = true;',1)
    (OUT/'ukf_imm_ch4.m').write_text(imm,encoding='utf-8')
    hashes={name:hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() for name in ['ukf_jichu.m','ukf_imm.m']}
    (OUT/'sources.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    print('generated isolated process-noise resampling experiment')


if __name__=='__main__':main()
