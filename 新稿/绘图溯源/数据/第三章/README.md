# 第三章配准图与参数表的数据

`turn_reference.csv` 从原始场景提取，`turn_selection.json` 记录源文件哈希、选段规则、身份和时间。选择按覆盖、连续性、独立身份及转弯形态进行，不根据配准结果选择。参考位置属于 ADS-B 驱动的运动轨迹，雷达量测仍为模型生成。

`turn_registration.csv` 保存 77 个时刻的原始仿真量测、配准前后位置和球面位置误差。该图不含漏检、滤波和关联；不是主系统端到端实验。

`calibration_mc.csv` 保存种子 42—51、两条链路的参数估计与对应下界。每个站的有效观测对数固定为 4 215 / 5 454。待测量测使用独立种子 20261123，校正参数采用种子 42 的 R1 估计。群距离单位为米，参数表中的虚高和距离偏置单位为千米，方位单位为度；定位图局部平面坐标仅用于显示，误差由球面距离计算。

生成调用当前工程的 `calibrate_radar_bias.m`、`estimate_system_bias.m`、`skywave_geometry.m` 和 `bistatic_inverse_solver.m`，使用配置 `params_coverage_registered.m`，并关闭标校缓存。生成环境为 MATLAB 9.14.0.2206163（R2023a）。研究工程源码未作修改。

从 `格式排版` 根目录复现：

```powershell
python 新稿/绘图溯源/prepare_ch3_turn.py
& 'C:\Program Files\MATLAB\R2023a\bin\matlab.exe' -batch "addpath('新稿/绘图溯源'); export_ch3_registration"
python 新稿/绘图溯源/_fig_ch3_registration.py
python 新稿/绘图溯源/plot_e7.py
```

最后一条命令读取原工程 `_analysis/e7_h_mismatch.csv`；本轮只重绘该对照图，没有重新运行其完整端到端实验。
