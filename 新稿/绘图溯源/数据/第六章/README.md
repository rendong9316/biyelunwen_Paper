# 第六章正式实验来源与复现

正式正文使用 `冻结验证/`，由 MATLAB R2023a 重新导出。参数与样本在运行前写入 `validation_protocol.json`：q=6 m²/s³，第四章完整预测协方差重采样，在线双门限及6/8确认，SCC融合。模型集20个配对种子46011—46030；覆盖工况各5种子46101—46105；63段ADS-B覆盖互补场景3种子46201—46203。评价数据不用于重新选择q或转弯率。

## 复现步骤

从 `格式排版` 根目录执行：

```powershell
python 新稿/绘图溯源/prepare_ch6_validation.py
& 'C:\Program Files\MATLAB\R2023a\bin\matlab.exe' -batch "addpath('新稿/绘图溯源'); export_ch6_validation('model',46011:46030); export_ch6_validation('coverage',46101:46105); export_ch6_validation('system',46201:46203)"
python 新稿/绘图溯源/review_ch6_validation.py
python 新稿/绘图溯源/_fig_ch6.py
python 新稿/校验工具/_check_ch6_validation.py
```

生成器仅在 `绘图溯源/实验实现/第六章` 创建隔离入口及滤波文件，保持研究工程源码不变。`run_ch6_pipeline.m` 根据当前工程 `run.m` 生成，修改入口名、工程定位和搜索路径优先级；`ukf_jichu.m` 和 `ukf_imm.m` 来自已验证的第四章隔离实现，只还原函数名以接入原在线调度。`sources.json` 保存生成时的上游代码哈希。每次运行的完整参数、MATLAB版本和提取版本写入对应 configuration JSON；模型对照和覆盖快照的 `extraction_version=2` 核验双源帧的实际绑定；系统场景采用 `extraction_version=4`，进一步核验单源帧当时实际活跃的源，不能根据另一站遗留的绑定编号是否非零判断有效性。日志为UTF-8。

导出遇到同提取版本、已完成的样本时跳过，不根据运行结果筛种子。若需要独立重跑核验，可先备份相应 `冻结验证` 输出，再执行同一命令；不要删除用户数据或跨仓库修改历史。

## 统计口径

`model_common_epochs.csv` 是两模型集都正确双源输出的相同目标—历元交集，模型集间精度比较以此为主；`model_all_dual_epochs.csv` 是各组自身全部正确双源历元，用于描述实际系统可用性。参考身份仅用于事后核验，算法候选和确认不接收目标真值。误差采用局部东北尺度（111.32 cos(latitude)、110.57 km/degree）；三种指标分别为向量误差模的RMSE、中位数和线性插值90分位数。

`model_paired_summary.csv` 在种子层面计算“巡航减较宽”的均值差、双侧t分布95%置信区间及Wilcoxon检验；正文主要报告效应量和单项区间，不将多指标未经校正的p值作为普遍因果证据。中心化rho减去各站在同一种子共同集合上的总体均值；raw_cross不去均值。单站协方差诊断与交叉误差结构分开解释。

`coverage_common_window.csv` 在相同真值时间窗、两站几何覆盖并集内计数。几何实现率是最长一个正确系统编号的输出帧数/几何并集帧数。局部航迹和系统输出允许预测延续，但并集外的帧不计入几何实现率。实际航迹长度比使用该集合内最长单站局部航迹的帧数作分母，不与几何分母混除。四工况为合成轨迹、速度230 m/s、Pd=0.6，无系统偏差。

`system_segment_summary.csv` 对63段场景分开计算单源与正确双源精度，目标—历元占比与整场景时间帧比例不同。长度比对有局部输出目标计算，同时保留全部63段的输出表及覆盖记录，不把未形成航迹的目标静默删除后宣称全场景覆盖。

`demo_selection.json` 固定使用首个系统评价种子，要求两站单独覆盖各至少3帧、正确双源至少8帧；按双源时长、总输出时长、目标号排序，未按定位误差选图。底图复用 `数据/第四章/map_background.geojson`，地理数据来源沿用该目录README，不代表实测雷达回波。

`validation_hashes.json` 是正式原始导出文件的SHA-256清单；汇总表可由原始CSV重新计算。

## 历史对照的处置

`历史对照/` 保存前一版论文曾引用的三份研究工程输出：`mc_online_chain.csv`、`mc_online_chain_v2.csv` 和 `ceiling_sweep.csv`。它们用于复核旧版47/50种子差异、相关指标口径和几何分母；与第四章q=6完整预测协方差重采样的正式实现不一致，不用于本轮结论。SHA-256依次为 `02C4BD45416697AD7824CE2B618502E5A15DA6C8E5E61B8BBA95A27E9E7D4424`、`AA368EDE3EFE1E2232133C27CD64E51DFD08290138A4D42C54DB51AC3397AA90`、`998626DF93CB19E973636AFC906B1DE391307A380EB74045B2C2287A01CC12E8`。旧结果仅作修订溯源；正文图表和统计仅读取冻结验证数据。
