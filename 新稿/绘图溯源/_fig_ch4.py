"""第四章绘图兼容入口，使用当前地图对照和统计绘图脚本。"""
from pathlib import Path
import runpy

if __name__=='__main__':
    runpy.run_path(str(Path(__file__).with_name('_fig_ch4_filtering.py')),run_name='__main__')
