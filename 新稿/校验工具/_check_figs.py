# -*- coding: utf-8 -*-
"""检查唯一完整论文中的图片、标签、图源和相对路径。

从项目根目录运行：python 新稿/校验工具/_check_figs.py
"""
from pathlib import Path
import re
import struct
import sys

BASE = Path(__file__).resolve().parents[1]
DOC = BASE / "论文全文.md"
MANIFEST = BASE / "图源清单.md"
RE_IMG = re.compile(r"^!\[(.*?)\]\((.*?)\)\s*\{#fig:([A-Za-z0-9_\-]+)\}", re.M)
RE_REF = re.compile(r"\[@fig:([A-Za-z0-9_\-]+)\]")


def png_size(path):
    with path.open("rb") as handle:
        head = handle.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def main():
    text = DOC.read_text(encoding="utf-8")
    manifest = MANIFEST.read_text(encoding="utf-8")
    chapters = list(re.finditer(r"^# 第(\d+)章[^\n]*$", text, re.M))
    declarations = {}
    problems = []
    print("检查正文：", DOC)
    print("%-7s %-34s %-14s %8s %s" % ("图号", "文件", "像素", "KB", "标签"))
    for index, chapter in enumerate(chapters):
        number = int(chapter.group(1))
        end = chapters[index + 1].start() if index + 1 < len(chapters) else len(text)
        body = text[chapter.start():end]
        for sequence, (caption, rel, label) in enumerate(RE_IMG.findall(body), 1):
            figure = f"图{number}-{sequence}"
            full = (BASE / rel).resolve()
            if not rel.startswith("Pictures/") or not full.is_relative_to((BASE / "Pictures").resolve()):
                problems.append(f"{figure} 路径不在Pictures目录：{rel}")
            if label in declarations:
                problems.append(f"{figure} 重复标签：{label}")
            declarations[label] = (figure, rel)
            if not full.is_file():
                problems.append(f"{figure} 图片缺失：{rel}")
                continue
            dimensions = png_size(full)
            size_kb = full.stat().st_size / 1024
            if dimensions is None:
                problems.append(f"{figure} 不是合法PNG：{rel}")
            elif dimensions[0] < 900:
                problems.append(f"{figure} 图片宽度不足900像素")
            if size_kb < 20:
                problems.append(f"{figure} 图片体积不足20KB")
            if Path(rel).name not in manifest:
                problems.append(f"{figure} 未登记图源：{rel}")
            if not caption.strip():
                problems.append(f"{figure} 缺少图注")
            print("%-7s %-34s %-14s %8.0f %s" %
                  (figure, full.name, str(dimensions), size_kb, label))
    references = set(RE_REF.findall(text))
    for label in references - declarations.keys():
        problems.append(f"图片引用不存在：{label}")
    for label in declarations.keys() - references:
        problems.append(f"图片未被正文引用：{label}")
    # 单文件管理约束：防止旧分章与错误图片目录被重新创建。
    for forbidden in (BASE.parent / "Pictures", BASE / "绘图溯源" / "Pictures"):
        if forbidden.exists() and any(path.is_file() for path in forbidden.iterdir()):
            problems.append(f"错误图片输出目录仍有文件：{forbidden}")
    for index in range(1, 8):
        if (BASE / f"ch{index}.md").exists():
            problems.append(f"已停用的分章文件重新出现：ch{index}.md")
    if (BASE.parent / "论文全文.md").exists():
        problems.append("根目录完整稿副本重新出现")
    print(f"正式图片 {len(declarations)} 张；正文引用 {len(references)} 个。")
    if problems:
        print("\n".join("错误：" + item for item in problems))
        return 1
    print("PASS：唯一正文、图片文件、标签、相对路径和图源登记全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
