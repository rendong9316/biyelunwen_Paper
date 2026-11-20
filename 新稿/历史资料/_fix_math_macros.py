# -*- coding: utf-8 -*-
"""把新稿中的间距命令与 bar 命令换成规范卡允许的写法（规则 6）。

规则：禁止 bar 命令（一律 overline）、quad、qquad、分号冒号感叹号间距、反斜杠+空格；
并列子式用逗号分隔，不用间距命令。
"""
import io
import re

BS = chr(92)
FILES = ["ch2.md", "ch3.md", "ch4.md", "ch5.md"]
PAIRS = [
    (BS + "bar" + BS + "rho", BS + "overline{" + BS + "rho}"),
    (BS + "bar" + BS + "phi", BS + "overline{" + BS + "phi}"),
]

for f in FILES:
    s = io.open(f, encoding="utf-8").read()
    before = s.count(BS + "quad") + s.count(BS + "bar")
    s = s.replace(BS + "qquad", ", ").replace(BS + "quad", ", ")
    for a, b in PAIRS:
        s = s.replace(a, b)
    s = re.sub(BS + r"bar\{([^{}]*)\}",
               lambda m: BS + "overline{" + m.group(1) + "}", s)
    s = s.replace(BS + ",", " ")
    s = re.sub(r"[ ]{2,}", " ", s)
    s = s.replace(",,", ",").replace(", ,", ",").replace(" , ", ", ")
    io.open(f, "w", encoding="utf-8").write(s)
    print(f, "changed", before)
