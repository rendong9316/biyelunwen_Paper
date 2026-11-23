"""提取 Natural Earth 公共地理数据的局部线段；记录来源与哈希。"""
from pathlib import Path
import hashlib
import json
import cartopy.io.shapereader as shp
from shapely.geometry import box, mapping

HERE = Path(__file__).resolve().parent
OUT = HERE / '数据/第四章'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bounds = box(104, 27, 114, 37)
    features, sources = [], []
    for category, name in [('cultural', 'admin_1_states_provinces_lines'), ('physical', 'rivers_lake_centerlines')]:
        path = Path(shp.natural_earth(resolution='10m', category=category, name=name))
        sources.append(dict(dataset=f'Natural Earth 1:10m {name}',
            url=f'https://naturalearthdata.com/downloads/10m-{category}-vectors/',
            sha256_shp=hashlib.sha256(path.read_bytes()).hexdigest(), license='Public domain'))
        for record in shp.Reader(path).records():
            geom = record.geometry
            if geom is None or not geom.intersects(bounds):
                continue
            clipped = geom.intersection(bounds)
            if clipped.is_empty:
                continue
            features.append(dict(type='Feature', geometry=mapping(clipped),
                properties={'kind':name, 'name':str(record.attributes.get('name',''))}))
    result = dict(type='FeatureCollection', features=features, sources=sources,
        note='仅作示意图地理背景；非导航或测绘成果，未绘制国界。')
    (OUT / 'map_background.geojson').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    print('saved local geographic lines:',len(features))


if __name__ == '__main__':
    main()
