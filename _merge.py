# -*- coding: utf-8 -*-
"""合并各章为论文全文（单一 YAML 头）"""
import os, re

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
CHS = ['ch1.md', 'ch2.md', 'ch3.md', 'ch4.md', 'ch5.md', 'ch6.md']
OUT = os.path.join(BASE, '论文全文.md')


def split_yaml(txt):
    """返回 (yaml块, 正文)"""
    t = txt.lstrip('\ufeff')
    if not t.startswith('---'):
        return '', t
    end = t.find('\n---', 3)
    if end < 0:
        return '', t
    return t[:end + 4], t[end + 4:].lstrip('\n')


parts = []
yaml_block = None
for ch in CHS:
    p = os.path.join(BASE, ch)
    if not os.path.exists(p):
        print(f'[跳过] {ch} 不存在')
        continue
    txt = open(p, encoding='utf-8').read()
    y, body = split_yaml(txt)
    if yaml_block is None:
        yaml_block = y
    parts.append(body.strip())

# 参考文献
ref = os.path.join(BASE, '_参考文献.md')
ref_txt = ''
if os.path.exists(ref):
    r = open(ref, encoding='utf-8').read()
    _, rb = split_yaml(r)
    ref_txt = rb.strip()

doc = (yaml_block + '\n\n' + '\n\n'.join(parts))
if ref_txt:
    doc += '\n\n' + ref_txt
doc += '\n'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(doc)

n_cn = len(re.findall(r'[\u4e00-\u9fff]', doc))
n_fig = len(re.findall(r'!\[', doc))
n_tbl = len(re.findall(r'\{#tbl:', doc))
n_eq = len(re.findall(r'\{#eq:', doc))
print(f'已生成: {OUT}')
print(f'  汉字 {n_cn} | 图 {n_fig} | 表 {n_tbl} | 公式 {n_eq}')
print(f'  文件大小 {os.path.getsize(OUT)/1024:.1f} KB')
