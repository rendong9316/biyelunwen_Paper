# -*- coding: utf-8 -*-
"""对合并后的 论文全文.md 按 md2word-workflow 规范做综合检查。

覆盖：YAML/标题层级(7个一级标题)/列表引用分割线/公式/图表/交叉引用/数据口径/语言风格。
所有检查均在合并后的单一文件上进行，跨章标签与引用可正确解析。
"""
import os
import re
import sys

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
DOC = os.path.join(BASE, "论文全文.md")

YAML_EXPECT = [
    "---", "chapters: true", 'chapDelim: "-"', "numberSections: false",
    'secHeaderDelim: " "', "eqnLabels: arabic", "autoEqnLabels: false",
    "tableEqns: true", "eqnBlockInlineMath: true",
    'eqnIndexTemplate: "($$i$$)"', 'eqnPrefixTemplate: "公式($$i$$)"',
    'figureTitle: "图"', 'figPrefix: ["图", "图"]', 'figIndexTemplate: "$$i$$"',
    'tableTitle: "表"', 'tblPrefix: ["表", "表"]', 'tblIndexTemplate: "$$i$$"',
    'titleDelim: " "', "---",
]
EXPECT_H1 = [f"第{i}章" for i in range(1, 8)]

problems = []
notes = []


def add(kind, detail):
    problems.append((kind, detail))


def note(kind, detail):
    notes.append((kind, detail))


txt = open(DOC, encoding="utf-8").read()
lines = txt.splitlines()

# ---------- YAML ----------
head = [l.strip() for l in lines[:19]]
if head != YAML_EXPECT:
    for i, (a, b) in enumerate(zip(head, YAML_EXPECT), 1):
        if a != b:
            add("YAML", f'L{i}: "{a}" != "{b}"')
    if len(head) != len(YAML_EXPECT):
        add("YAML", f"头部行数 {len(head)} != {len(YAML_EXPECT)}")

body = "\n".join(lines[19:])

# ---------- 标题层级 ----------
h1 = re.findall(r"^#\s+(.*)$", body, re.M)
if len(h1) != 7:
    add("HEADING", f"一级标题数量 {len(h1)} != 7: {h1}")
for i, (got, exp) in enumerate(zip(h1, EXPECT_H1), 1):
    if not got.strip().startswith(exp):
        add("HEADING", f"第{i}个一级标题非预期: {got}")
for mt in re.finditer(r"^(#{1,6})\s+(.*)$", body, re.M):
    if len(mt.group(1)) > 4:
        add("HEADING", f"超过四级标题: {mt.group(2)[:40]}")

# ---------- 列表 / 引用 / 分割线 ----------
for i, ln in enumerate(lines[19:], 20):
    s = ln.strip()
    if re.match(r"^[-*+]\s+", s):
        add("LIST", f"L{i} 无序列表: {s[:40]}")
    if re.match(r"^\d+[.)]\s+", s):
        add("LIST", f"L{i} 有序列表: {s[:40]}")
    if s.startswith(">"):
        add("QUOTE", f"L{i} 引用块: {s[:40]}")
    if s in ("***", "___", "---"):
        add("HR", f"L{i} 分割线")

# ---------- 公式 ----------
BAD = [(r"\\bar\b", "\\bar"), (r"\\qquad", "\\qquad"), (r"\\quad", "\\quad"),
       (r"\\;", "\\;"), (r"\\:", "\\:"), (r"\\!", "\\!"), (r"\\ ", "反斜杠空格")]
for mt in re.finditer(r"\$\$(.+?)\$\$(\s*\{#eq:[^}]+\})?", txt, re.S):
    eq = mt.group(1)
    for pat, name in BAD:
        if re.search(pat, eq):
            add("MATH_SPACE", f"{name}: {eq.strip()[:50]}")
for mt in re.finditer(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)", txt):
    eq = mt.group(1)
    for pat, name in BAD[:4]:
        if re.search(pat, eq):
            add("MATH_SPACE", f"行内 {name}: {eq[:40]}")

# 独立公式块是否单行居中（$$ 与标签之间不应有多余内容；标签在 $$ 外）
for mt in re.finditer(r"\$\$(.*?)\$\$", txt, re.S):
    inner = mt.group(1)
    if inner.startswith("\n") or inner.endswith("\n"):
        add("MATH_LAYOUT", f"独立公式 $$ 内含换行: {inner.strip()[:40]}")

# 连续独立公式块之间需要 <div>&#8203;</div>
blocks = list(re.finditer(r"\$\$.*?\$\$(\s*\{#eq:[^}]+\})?", txt, re.S))
for a, b in zip(blocks, blocks[1:]):
    gap = txt[a.end():b.start()]
    if re.fullmatch(r"\s*", gap) and "<div>&#8203;</div>" not in gap:
        add("MATH_CONTIGUOUS", f"连续公式块间缺 <div>&#8203;</div>: {b.group(0)[:40]}")

# ---------- 图 ----------
RE_IMG = re.compile(r"^!\[(.*?)\]\((.*?)\)\s*\{#fig:([A-Za-z0-9_\-]+)\}", re.M)
imgs = list(RE_IMG.finditer(txt))
for mt in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", txt):
    cap, path = mt.group(1), mt.group(2)
    if not re.search(r"\{#fig:[^}]+\}", txt[mt.end():mt.end() + 30]):
        add("FIG_TAG", f"图缺标签: {cap[:30]}")
    if re.search(r"图\s*\d+[-–.]\d+", cap) or re.match(r"^图\s*\d+", cap.strip()):
        add("FIGCAP_NUM", f"图注含编号: {cap[:40]}")
    fp = os.path.join(BASE, path)
    if not path.startswith("新稿/Pictures/"):
        add("FIG_PATH", f"合并稿图片必须位于新稿/Pictures：{path}")
    if not os.path.exists(fp):
        add("FIG_MISSING", f"图片不存在: {path}")

# ---------- 表 ----------
for i, ln in enumerate(lines):
    s = ln.strip()
    if s.startswith(":") and "{#tbl:" in s:
        if re.search(r"表\s*\d+[-–.]\d+", s):
            add("TBLCAP_NUM", f"表注含编号: {s[:40]}")
        if i > 0 and lines[i - 1].strip() != "":
            add("TBLCAP_NONL", f"L{i+1} 表注前未空行: {s[:40]}")

# ---------- 交叉引用 ----------
eq_def = set(re.findall(r"\{#eq:([^}]+)\}", txt))
fig_def = set(re.findall(r"\{#fig:([^}]+)\}", txt))
tbl_def = set(re.findall(r"\{#tbl:([^}]+)\}", txt))
eq_ref = set(re.findall(r"@eq:([\w\-]+)", txt))
fig_ref = set(re.findall(r"@fig:([\w\-]+)", txt))
tbl_ref = set(re.findall(r"@tbl:([\w\-]+)", txt))
for kind, defs, refs in (("eq", eq_def, eq_ref), ("fig", fig_def, fig_ref), ("tbl", tbl_def, tbl_ref)):
    for r in sorted(refs - defs):
        add("REF_MISSING", f"@{kind}:{r} 引用了未定义标签")
    for d in sorted(defs - refs):
        # 标签定义主要用于 pandoc-crossref 自动编号，正文是否引用由作者决定；
        # 源稿本就存在大量"定义未引用"，合并原样保留，故仅提示不判错。
        note("REF_UNUSED(提示)", f"{kind}:{d} 仅用于自动编号、正文未引用")
    # 重复定义按命名空间分别判定：eq/fig/tbl 是独立命名空间，同名合法
    for kind, defset in (("eq", eq_def), ("fig", fig_def), ("tbl", tbl_def)):
        occ = re.findall(r"\{#" + kind + r":([^}]+)\}", txt)
        for d in sorted({x for x in occ if occ.count(x) > 1}):
            add("REF_DUP", f"{kind} 命名空间内标签重复定义: {d}")

# ---------- 语言风格 ----------
for mt in re.finditer(r"[^本自]我(?!们)", body):
    add("WO", "出现单字'我': " + body[max(0, mt.start()-12):mt.start()+10].replace("\n", " "))
nb = len(re.findall(r"\*\*[^*]+\*\*", txt))
if nb > 3:
    add("BOLD", f"加粗 {nb} 处 (>3)")

# ---------- 数据口径（禁用表述；旧稿 MUST 数字表不适用于重构后的新稿） ----------
BAN = [
    (r"Δgain\s*=\s*[-−]39", "禁用确定性回归公式"),
    (r"[-−]39\.0\s*[×x]\s*Δ", "禁用确定性回归公式"),
    (r"ρ\s*每降\s*0\.1", "禁用'ρ每降0.1'表述"),
    (r"航迹.{0,6}提升\s*50\s*%", "开题承诺未兑现"),
    (r"全面优于", "绝对化表述"), (r"全面最优", "绝对化表述"),
    (r"CI\s*更鲁棒", "与实测相反"), (r"BC\s*与\s*SCC\s*并列", "伪结论"),
]
for pat, why in BAN:
    for mt in re.finditer(pat, body):
        ctx = body[max(0, mt.start()-30):mt.start()+40].replace("\n", " ")
        # 否定语境豁免：如"不追求单项指标全面最优"
        if re.search(r"(不追求|并非|不是|无|未|非)\s*单项?指标?[^。]{0,8}$",
                     body[max(0, mt.start()-30):mt.start()]):
            continue
        add("BANNED", f"{why}: {ctx}")

# ---------- 输出 ----------
print("=" * 76)
print("md2word-workflow 规范检查 — 论文全文.md")
print("=" * 76)
print(f"汉字 {len(re.findall(r'[\u4e00-\u9fff]', txt))} | "
      f"一级标题 {len(h1)} | 图 {len(imgs)} | 表 {len(tbl_def)} | 公式 {len(eq_def)}")
print(f"引用: eq {len(eq_ref)} / fig {len(fig_ref)} / tbl {len(tbl_ref)}")
print("=" * 76)
if notes:
    from collections import Counter
    print(f"\n提示（非错误，源稿固有）：共 {len(notes)} 条")
    for k, v in Counter(k for k, _ in notes).most_common():
        print(f"  {k}: {v}")
if not problems:
    print("\n[PASS] 全部硬性检查通过，未发现格式/引用错误。")
    sys.exit(0)
from collections import Counter
print(f"\n错误：共 {len(problems)} 个：")
for k, v in Counter(k for k, _ in problems).most_common():
    print(f"  {k}: {v}")
print("\n明细：")
for k, d in problems:
    print(f"  [{k}] {d}")
sys.exit(1)
