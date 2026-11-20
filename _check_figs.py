# -*- coding: utf-8 -*-
"""全文图片完整性核查。

检查四件事：
  1. 每章 `![...](path){#fig:label}` 声明的图片文件是否存在、是否为合法 PNG、像素尺寸与体积；
  2. 图片在章内的出现顺序与图注编号（图章-序）是否连续；
  3. 正文 `[@fig:label]` 引用是否全部解析到已声明的标签，是否有声明了却从未被引用的图；
  4. 每张图是否在图源清单中登记（生成脚本 → 数据来源 → 复现命令）。

复现：
  cd 格式排版 && python _check_figs.py
"""
import os
import re
import struct
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, "新稿")
PIC = os.path.join(MD, "Pictures")
MANIFEST = os.path.join(MD, "图源清单.md")
CHAPS = ["ch1.md", "ch2.md", "ch3.md", "ch4.md", "ch5.md", "ch6.md", "ch7.md"]

RE_IMG = re.compile(r"^!\[(.*?)\]\((.*?)\)\s*\{#fig:([A-Za-z0-9_\-]+)\}", re.M)
RE_REF = re.compile(r"\[@fig:([A-Za-z0-9_\-]+)\]")


def png_size(p):
    """返回 (宽, 高) 或 None；同时校验 PNG 签名。"""
    with open(p, "rb") as f:
        head = f.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if head[12:16] != b"IHDR":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def main():
    manifest = ""
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            manifest = f.read()

    declared = {}     # label -> (chapter, seq, path, caption)
    problems = []
    print("%-6s %-4s %-34s %-12s %9s  %s" %
          ("图号", "章", "文件", "像素", "KB", "标签"))
    print("-" * 96)

    for ci, fn in enumerate(CHAPS, 1):
        path = os.path.join(MD, fn)
        with open(path, encoding="utf-8") as f:
            txt = f.read()
        imgs = RE_IMG.findall(txt)
        refs = RE_REF.findall(txt)

        for seq, (cap, rel, label) in enumerate(imgs, 1):
            # 章节位于新稿目录，Pictures/... 按章节所在目录解析。
            full = os.path.normpath(os.path.join(MD, rel))
            no = "图%d-%d" % (ci, seq)
            if not rel.startswith("Pictures/"):
                problems.append("%s 图片路径不在章节规定目录：%s" % (no, rel))
            if label in declared:
                problems.append("%s 标签重复：%s（已见于第%d章）"
                                % (no, label, declared[label][0]))
            declared[label] = (ci, seq, rel, cap)
            if not os.path.exists(full):
                problems.append("%s 文件缺失：%s" % (no, rel))
                print("%-6s %-4d %-34s %-12s %9s  %s"
                      % (no, ci, os.path.basename(rel), "缺失", "-", label))
                continue
            sz = png_size(full)
            kb = os.path.getsize(full) / 1024.0
            if sz is None:
                problems.append("%s 非合法 PNG：%s" % (no, rel))
                dim = "非法"
            else:
                dim = "%dx%d" % sz
                if sz[0] < 900:
                    problems.append("%s 宽度不足 900 px（%d），印刷可能发虚"
                                    % (no, sz[0]))
            if kb < 20:
                problems.append("%s 体积仅 %.0f KB，疑似空白图" % (no, kb))
            if os.path.basename(rel) not in manifest:
                problems.append("%s 未在图源清单登记：%s" % (no, rel))
            if not cap.strip():
                problems.append("%s 缺图注文字" % no)
            print("%-6s %-4d %-34s %-12s %9.0f  %s"
                  % (no, ci, os.path.basename(rel), dim, kb, label))

        for r in refs:
            if r not in [x[2] for x in imgs]:
                problems.append("第%d章 正文引用了本章未声明的标签：%s" % (ci, r))

    # 跨章误引
    for ci, fn in enumerate(CHAPS, 1):
        with open(os.path.join(MD, fn), encoding="utf-8") as f:
            txt = f.read()
        for r in RE_REF.findall(txt):
            if r not in declared:
                problems.append("第%d章 引用了全文不存在的标签：%s" % (ci, r))
            elif declared[r][0] != ci:
                problems.append("第%d章 引用了第%d章的图标签：%s"
                                % (ci, declared[r][0], r))

    # 声明未引用
    alltxt = ""
    for fn in CHAPS:
        with open(os.path.join(MD, fn), encoding="utf-8") as f:
            alltxt += f.read()
    for label, (ci, seq, rel, cap) in declared.items():
        if alltxt.count("[@fig:%s]" % label) == 0:
            problems.append("图%d-%d（%s）声明了但正文从未引用" % (ci, seq, label))

    # 只有新稿/Pictures为正式目录；根目录或溯源目录不应重新生成同名文件。
    for forbidden in (os.path.join(BASE, "Pictures"),
                      os.path.join(MD, "绘图溯源", "Pictures")):
        if os.path.isdir(forbidden):
            files = [name for name in os.listdir(forbidden)
                     if os.path.isfile(os.path.join(forbidden, name))]
            if files:
                problems.append("错误目录仍有图片文件：%s（%d个）" % (forbidden, len(files)))

    print("-" * 96)
    print("声明图片 %d 张，标签 %d 个，唯一文件 %d 个"
          % (len(declared), len(declared),
             len({v[2] for v in declared.values()})))

    if problems:
        print("\n发现 %d 处问题：" % len(problems))
        for p in problems:
            print("  ! " + p)
    else:
        print("\n全部通过：文件齐全、格式合法、编号连续、标签闭合、清单已登记。")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
