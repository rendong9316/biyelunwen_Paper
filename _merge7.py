# -*- coding: utf-8 -*-
"""把 新稿/ch1-ch7.md 合并为根目录 论文全文.md。

规则（严格对齐 md2word-workflow / 创建md注意事项.md）：
- 全文只保留一个 YAML 配置块（取自 ch1）；
- 每章恰好一个一级标题（# 第X章 ...），全文共 7 个一级标题；
- 不加入"参考文献"等任何额外一级标题（新稿正文无任何 [@文献] 引用）；
- 章内二至四级标题、公式/图/表标签与交叉引用原样保留；
- 图片源文件统一位于 新稿/Pictures：章节引用 Pictures/...，根目录合并稿自动转为 新稿/Pictures/...；
- 章与章之间以一个空行分隔。
"""
import os
import re

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
SRC = os.path.join(BASE, "新稿")
CHS = [f"ch{i}.md" for i in range(1, 8)]
OUT = os.path.join(BASE, "论文全文.md")


def split_yaml(txt):
    """返回 (yaml块含首尾---, 去掉yaml后的正文)。"""
    t = txt.lstrip("\ufeff")
    if not t.startswith("---"):
        return "", t
    end = t.find("\n---", 3)
    if end < 0:
        return "", t
    return t[:end + 4], t[end + 4:].lstrip("\n")


yaml_block = None
parts = []
for ch in CHS:
    p = os.path.join(SRC, ch)
    if not os.path.exists(p):
        raise SystemExit(f"缺少源文件: {p}")
    txt = open(p, encoding="utf-8").read()
    y, body = split_yaml(txt)
    if yaml_block is None:
        yaml_block = y
    body = body.strip()
    h1 = re.findall(r"^#\s+(.*)$", body, re.M)
    if len(h1) != 1:
        raise SystemExit(f"{ch} 一级标题数={len(h1)}: {h1}")
    # 规范化清洗（创建md注意事项.md）：删除矩阵换行 \\ 后多余的空格
    n_fix = body.count("\\\\ ")
    if n_fix:
        body = body.replace("\\\\ ", "\\\\")
        print(f"  {ch}: 清理矩阵换行后空格 {n_fix} 处")
    # 源章节相对于“新稿”引用图片；根目录合并稿只调整路径，不改图注与标签。
    body = re.sub(r'(!\[[^\]]*\]\()Pictures/', r'\1新稿/Pictures/', body)
    parts.append(body)

if yaml_block is None:
    raise SystemExit("未找到 YAML 配置块")

doc = yaml_block + "\n\n" + "\n\n".join(parts) + "\n"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)

n_cn = len(re.findall(r"[\u4e00-\u9fff]", doc))
print(f"已生成: {OUT}")
print(f"  一级标题: {len(re.findall(r'^# ', doc, re.M))} 个")
print(f"  汉字 {n_cn} | 图 {doc.count(chr(33) + '[')} | "
      f"表 {doc.count('{#tbl:')} | 公式 {doc.count('{#eq:')}")
print(f"  文件大小 {os.path.getsize(OUT) / 1024:.1f} KB")
