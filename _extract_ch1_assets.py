"""从用户提供的 Word 材料直接提取绪论原理图，并记录可复现来源。

在格式排版目录执行：python _extract_ch1_assets.py
仅复制明确选择的图片，不改写源 Word；不提取公式图片或旧算法流程。
"""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from PIL import Image

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parent / "文稿撰写" / "开题报告.docx"
OUTPUT = BASE / "Pictures" / "fig1_1_principle.png"
PROVENANCE = BASE / "新稿" / "ch1_asset_sources.json"
MEMBER = "word/media/image2.png"
ORIGINAL_CAPTION = "双照射源外辐射雷达系统示意图"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
# 源图尺寸为 13333×7500；只读尺寸与校验，不做高分辨率解码或重采样。
Image.MAX_IMAGE_PIXELS = 110_000_000


def main():
    source_bytes = SOURCE.read_bytes()
    with ZipFile(BytesIO(source_bytes)) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
        body = list(root.find("w:body", NS))
        relationships = {
            row.attrib["Id"]: row.attrib["Target"]
            for row in ET.fromstring(archive.read("word/_rels/document.xml.rels"))
        }
        paragraph_index = None
        for index, block in enumerate(body):
            content = "".join(node.text or "" for node in block.findall(".//w:t", NS))
            if ORIGINAL_CAPTION in content:
                linked = {
                    "word/" + relationships[value]
                    for element in body[index - 1].iter()
                    for value in element.attrib.values()
                    if value in relationships
                }
                if MEMBER in linked:
                    paragraph_index = index
                    break
        if paragraph_index is None:
            raise RuntimeError("原图与相邻图注的关系已变化，请重新核对 Word 媒体映射。")
        original = archive.read(MEMBER)
    with Image.open(BytesIO(original)) as im:
        dimensions = list(im.size)
        if im.format != "PNG":
            raise ValueError("预期原始 PNG 文件。")
        im.verify()
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_bytes(original)
    if sha256(OUTPUT.read_bytes()).digest() != sha256(original).digest():
        raise RuntimeError("提取文件与源图片字节不一致。")
    record = {
        "source_document": "../文稿撰写/开题报告.docx",
        "source_document_sha256": sha256(source_bytes).hexdigest(),
        "assets": [{
            "figure": "fig:ch1_principle",
            "output": OUTPUT.relative_to(BASE).as_posix(),
            "member": MEMBER,
            "original_caption": ORIGINAL_CAPTION,
            "image_sha256": sha256(original).hexdigest(),
            "pixels": dimensions,
            "processing": "原始 PNG 字节直接复制；未裁切、未重采样、未更改文字或色彩",
            "scope": "双源被动探测基本原理；共用接收端示意，不代表本文实验站点布设",
            "reproduce": "python _extract_ch1_assets.py",
        }],
    }
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Extracted {OUTPUT.name}: {dimensions[0]}x{dimensions[1]}, SHA-256 verified")
    print(f"Source manifest: {PROVENANCE.relative_to(BASE)}")


if __name__ == "__main__":
    main()
