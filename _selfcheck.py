# -*- coding: utf-8 -*-
"""论文格式与一致性自检（多轮）"""
import os, re, sys, glob

BASE = r"D:/Desktop/毕设相关/AAA毕业论文撰写/格式排版"
CHS = ['ch1.md', 'ch2.md', 'ch3.md', 'ch4.md', 'ch5.md', 'ch6.md']

YAML_EXPECT = """---
chapters: true
chapDelim: "-"
numberSections: false
secHeaderDelim: " "
eqnLabels: arabic
autoEqnLabels: false
tableEqns: true
eqnBlockInlineMath: true
eqnIndexTemplate: "($$i$$)"
eqnPrefixTemplate: "公式($$i$$)"
figureTitle: "图"
figPrefix: ["图", "图"]
figIndexTemplate: "$$i$$"
tableTitle: "表"
tblPrefix: ["表", "表"]
tblIndexTemplate: "$$i$$"
titleDelim: " "
---"""

problems = []


def add(ch, kind, detail):
    problems.append((ch, kind, detail))


def read(fn):
    p = os.path.join(BASE, fn)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return f.read()


def strip_code(txt):
    return txt


def check_yaml(ch, txt):
    head = txt.lstrip('\ufeff').strip()
    if not head.startswith('---'):
        add(ch, 'YAML', '文件未以 --- 开头')
        return
    end = head.find('\n---', 3)
    if end < 0:
        add(ch, 'YAML', 'YAML 块未闭合')
        return
    got = head[:end + 4].strip()
    if got != YAML_EXPECT:
        # 逐行比对
        gl = got.splitlines()
        el = YAML_EXPECT.splitlines()
        if len(gl) != len(el):
            add(ch, 'YAML', f'行数不符 got={len(gl)} expect={len(el)}')
        else:
            for a, b in zip(gl, el):
                if a.strip() != b.strip():
                    add(ch, 'YAML', f'不一致: "{a.strip()}" != "{b.strip()}"')


def check_lists(ch, txt):
    lines = txt.splitlines()
    in_yaml = False
    yaml_cnt = 0
    in_code = False
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if s == '---':
            yaml_cnt += 1
            in_yaml = yaml_cnt < 2
            continue
        if in_yaml:
            continue
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        # 无序列表
        if re.match(r'^[-*+]\s+', s):
            add(ch, 'LIST', f'L{i}: {s[:50]}')
        # 有序列表
        if re.match(r'^\d+[.)]\s+', s):
            add(ch, 'LIST', f'L{i}: {s[:50]}')
        # 引用块
        if s.startswith('>'):
            add(ch, 'QUOTE', f'L{i}: {s[:50]}')


def check_wo(ch, txt):
    body = txt
    # 排除 YAML
    m = re.match(r'^\s*---\n.*?\n---\n', body, re.S)
    if m:
        body = body[m.end():]
    for mt in re.finditer(r'[^本自]我(?!们)', body):
        i = mt.start()
        ctx = body[max(0, i - 18):i + 14].replace('\n', ' ')
        add(ch, 'WO', ctx)


def check_math(ch, txt):
    # 独立公式块
    for mt in re.finditer(r'\$\$(.+?)\$\$(\s*\{#eq:[^}]+\})?', txt, re.S):
        body = mt.group(1)
        tag = mt.group(2) or ''
        for bad, name in [(r'\\bar\b', r'\bar'), (r'\\qquad', r'\qquad'),
                          (r'\\quad', r'\quad'), (r'\\;', r'\;'),
                          (r'\\:', r'\:'), (r'\\!', r'\!')]:
            if re.search(bad, body):
                add(ch, 'MATH_SPACE', f'{name} in: {body.strip()[:60]}')
        if re.search(r'\\ ', body):
            add(ch, 'MATH_SPACE', f'反斜杠空格 in: {body.strip()[:60]}')
    # 行内公式
    for mt in re.finditer(r'(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)', txt):
        body = mt.group(1)
        for bad, name in [(r'\\bar\b', r'\bar'), (r'\\qquad', r'\qquad'),
                          (r'\\quad', r'\quad'), (r'\\;', r'\;')]:
            if re.search(bad, body):
                add(ch, 'MATH_SPACE', f'inline {name}: {body[:50]}')
        if re.search(r'\\ ', body):
            add(ch, 'MATH_SPACE', f'inline 反斜杠空格: {body[:50]}')


def check_figcap(ch, txt):
    # 图注里不应出现 "图X-Y" 或 "图 N"
    for mt in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)(\{#[^}]+\})?', txt):
        cap, path, tag = mt.group(1), mt.group(2), mt.group(3) or ''
        if re.search(r'图\s*\d+[-–.]\d+', cap) or re.match(r'^图\s*\d+', cap.strip()):
            add(ch, 'FIGCAP_NUM', cap[:50])
        if not tag:
            add(ch, 'FIGCAP_TAG', f'缺 {{#fig:}} 标签: {cap[:40]}')
        # 文件存在性
        fp = os.path.join(BASE, path)
        if not os.path.exists(fp):
            add(ch, 'FIG_MISSING', path)


def check_tblcap(ch, txt):
    lines = txt.splitlines()
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith(':') and '{#tbl:' in s:
            cap = s
            if re.search(r'表\s*\d+[-–.]\d+', cap):
                add(ch, 'TBLCAP_NUM', cap[:50])
            # 前面必须空行
            if i > 0 and lines[i - 1].strip() != '':
                add(ch, 'TBLCAP_NONL', f'L{i+1} 表注前未空行')
    # 表格存在但无表注
    tbl_cnt = len(re.findall(r'^\|[^\n]*\|\s*$', txt, re.M))
    tag_cnt = len(re.findall(r'\{#tbl:', txt))
    if tbl_cnt > 0 and tag_cnt == 0:
        add(ch, 'TBL_NOTAG', f'有表格但无表注标签（表行 {tbl_cnt}）')


def check_refs(ch, txt):
    eq_def = set(re.findall(r'\{#eq:([^}]+)\}', txt))
    fig_def = set(re.findall(r'\{#fig:([^}]+)\}', txt))
    tbl_def = set(re.findall(r'\{#tbl:([^}]+)\}', txt))
    eq_ref = set(re.findall(r'@eq:([\w\-]+)', txt))
    fig_ref = set(re.findall(r'@fig:([\w\-]+)', txt))
    tbl_ref = set(re.findall(r'@tbl:([\w\-]+)', txt))
    for r in eq_ref - eq_def:
        add(ch, 'REF_MISSING', f'@eq:{r}')
    for r in fig_ref - fig_def:
        add(ch, 'REF_MISSING', f'@fig:{r}')
    for r in tbl_ref - tbl_def:
        add(ch, 'REF_MISSING', f'@tbl:{r}')
    # 定义了但从未引用
    for d in eq_def - eq_ref:
        add(ch, 'REF_UNUSED', f'eq:{d}')
    for d in fig_def - fig_ref:
        add(ch, 'REF_UNUSED', f'fig:{d}')
    for d in tbl_def - tbl_ref:
        add(ch, 'REF_UNUSED', f'tbl:{d}')


def check_bold(ch, txt):
    n = len(re.findall(r'\*\*[^*]+\*\*', txt))
    if n > 3:
        add(ch, 'BOLD', f'加粗 {n} 处（规范要求 ≤3）')


def check_heading(ch, txt):
    for mt in re.finditer(r'^(#{1,6})\s+(.*)$', txt, re.M):
        lvl = len(mt.group(1))
        if lvl > 4:
            add(ch, 'HEADING', f'{lvl} 级标题: {mt.group(2)[:40]}')
    # 一级标题必须只有 1 个（章）
    h1 = re.findall(r'^#\s+(.*)$', txt, re.M)
    if len(h1) != 1:
        add(ch, 'HEADING', f'一级标题 {len(h1)} 个: {h1}')


def cn_words(txt):
    return len(re.findall(r'[\u4e00-\u9fff]', txt))


def main():
    total = 0
    print('=' * 78)
    print('第 1 轮：格式硬约束（YAML / 列表 / 引用块 / 标题层级）')
    print('=' * 78)
    for ch in CHS:
        txt = read(ch)
        if txt is None:
            add(ch, 'MISSING', '文件不存在')
            continue
        total += cn_words(txt)
        check_yaml(ch, txt)
        check_lists(ch, txt)
        check_heading(ch, txt)

    print('\n' + '=' * 78)
    print('第 2 轮：数学公式规范（禁用间距命令 / \\bar）')
    print('=' * 78)
    for ch in CHS:
        txt = read(ch)
        if txt:
            check_math(ch, txt)

    print('\n' + '=' * 78)
    print('第 3 轮：图表规范（编号 / 标签 / 文件存在 / 表注空行）')
    print('=' * 78)
    for ch in CHS:
        txt = read(ch)
        if txt:
            check_figcap(ch, txt)
            check_tblcap(ch, txt)

    print('\n' + '=' * 78)
    print('第 4 轮：交叉引用完整性')
    print('=' * 78)
    for ch in CHS:
        txt = read(ch)
        if txt:
            check_refs(ch, txt)

    print('\n' + '=' * 78)
    print('第 5 轮：语言风格（“我” / 加粗过量）')
    print('=' * 78)
    for ch in CHS:
        txt = read(ch)
        if txt:
            check_wo(ch, txt)
            check_bold(ch, txt)

    # 输出
    print('\n' + '=' * 78)
    print(f'总汉字数：{total}')
    for ch in CHS:
        txt = read(ch)
        if txt:
            print(f'  {ch}: {cn_words(txt)} 字')
    print('=' * 78)

    if not problems:
        print('\n✅ 未发现问题')
        return 0

    from collections import Counter
    cnt = Counter(k for _, k, _ in problems)
    print(f'\n共 {len(problems)} 个问题：')
    for k, v in cnt.most_common():
        print(f'  {k}: {v}')

    print('\n明细：')
    for ch, kind, detail in problems:
        print(f'  [{ch}][{kind}] {detail}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
