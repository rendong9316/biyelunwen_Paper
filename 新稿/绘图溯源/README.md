# 绘图溯源目录

用户于2026-11-20明确指定：正式图片统一位于相邻的 `../Pictures/`，绘图、图片提取和来源记录统一保存在本目录。以下命令从 `格式排版` 根目录执行，也可以从本目录直接运行脚本。

| 用途 | 命令 |
| ---- | ---- |
| 提取原理图并校验来源哈希 | `python 新稿/绘图溯源/_extract_ch1_assets.py` |
| 绘制绪论的黑白理论框架和技术路线 | `python 新稿/绘图溯源/_fig_ch1_new.py` |
| 第2章布设、传播模型与航迹分布 | `python 新稿/绘图溯源/_fig_ch2_new.py` |
| 第2章覆盖状态统计图 | `python 新稿/绘图溯源/_fig_scene_and_registration.py` |
| 第3章配准流程、可辨识性和转弯航迹图 | `python 新稿/绘图溯源/_fig_ch3_registration.py` |
| 第3章配准演示数据准备 | `python 新稿/绘图溯源/prepare_ch3_turn.py`；再以 MATLAB R2023a 运行 `export_ch3_registration.m` |
| 第3章虚高失配对照图 | `python 新稿/绘图溯源/plot_e7.py` |
| 第4章结构、地图与误差时序四图 | `python 新稿/绘图溯源/_fig_ch4_filtering.py` |
| 第4章50种子单站对照 | MATLAB R2023a 调用 `export_ch4_filtering(50)`；详见 `数据/第四章/README.md` |
| 第4章过程噪声敏感性与独立性能评价 | `python 新稿/绘图溯源/prepare_ch4_prototype.py`；MATLAB `check_ch4_process_noise`；同实现14档q扫参由 `refine_ch4_q.m` 与 `review_ch4_diagnostics.py --select` 完成；`evaluate_ch4_selected.m`运行新独立评价；正式图采用q=6及种子44001 |
| 第5章三幅图 | `python 新稿/绘图溯源/_fig_ch5.py` |
| 第5章在线策略与确认规则复核 | `python 新稿/校验工具/_check_ch5_online.py`；源结果快照与校验哈希见 `数据/第五章/` |
| 第6章三幅图 | `python 新稿/绘图溯源/_fig_ch6.py` |

`ch1_asset_sources.json` 记录复用图片的源文档、媒体条目、原始像素和 SHA-256。全部正式图的来源及数据口径见上级目录的 `图源清单.md`。

`历史脚本/` 保存三份旧稿生成器，输出仅限 `../Pictures/历史/`。其数据和论述属于旧稿，不得用于覆盖当前正式图。同名框图的不同历史副本也保存在图片历史子目录。

绪论及配准流程框图的白底、黑色文字与线条、矩形框和箭头风格已由用户确认，后续同类框图继续采用。第三章配准图使用当前 ADS-B 转弯航迹重新绘制，图片文字使用中文；不直接复用专利图片。

唯一正文为上级目录的 `论文全文.md`，图片引用统一使用相对于该文件的 `Pictures/...`。不再维护分章文件或合并稿，也不再调用合并脚本。从 `格式排版` 根目录运行 `python 新稿/校验工具/_check_figs.py` 和 `python 新稿/校验工具/_check_merged.py` 检查正文与图片。禁止把 `新稿/Pictures` 当作重复目录删除，禁止脚本重新创建根目录 `Pictures`。
