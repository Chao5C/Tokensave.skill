#!/usr/bin/env python3
"""
超长 Traceback 智能截取脚本

用法：
  python truncate_traceback.py --file traceback.txt
  python truncate_traceback.py --content "完整traceback文本"
  cat traceback.txt | python truncate_traceback.py

策略：
- 保留最后 max_tail 行（真正报错位置）
- 保留最前面 max_head 行（入口）
- 过滤明显的第三方库帧（site-packages、dist-packages、lib/python 等）
- 如果总行数不超过阈值，直接原样输出
"""

import argparse
import sys
import re
from pathlib import Path

# 可配置参数
MAX_HEAD = 8
MAX_TAIL = 25
MAX_TOTAL_LINES = 60          # 超过此行数才进行截取
FILTER_PATTERNS = [
    r"site-packages",
    r"dist-packages",
    r"lib/python\d",
    r"lib\\python\d",
    r"[\\/]lib[\\/]",
    r"asyncio[\\/]",
    r"threading\.py",
    r"concurrent[\\/]futures",
]


def should_filter(line: str) -> bool:
    for pat in FILTER_PATTERNS:
        if re.search(pat, line, re.IGNORECASE):
            return True
    return False


def truncate_traceback(text: str) -> str:
    lines = text.strip().splitlines()
    if len(lines) <= MAX_TOTAL_LINES:
        return text.strip()

    # 过滤第三方库帧（但保留最后几帧，防止把真正错误也滤掉）
    filtered = []
    for i, line in enumerate(lines):
        # 最后 MAX_TAIL 行强制保留
        if i >= len(lines) - MAX_TAIL:
            filtered.append(line)
            continue
        if not should_filter(line):
            filtered.append(line)

    # 如果过滤后仍然很长，再做头尾截取
    if len(filtered) > MAX_TOTAL_LINES:
        head = filtered[:MAX_HEAD]
        tail = filtered[-MAX_TAIL:]
        middle_count = len(filtered) - MAX_HEAD - MAX_TAIL
        result = head + [f"\n...（中间省略 {middle_count} 行第三方/重复帧）...\n"] + tail
        return "\n".join(result)

    return "\n".join(filtered)


def main():
    parser = argparse.ArgumentParser(description="智能截取超长 traceback")
    parser.add_argument("--file", help="从文件读取 traceback")
    parser.add_argument("--content", help="直接传入 traceback 文本")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="replace")
    elif args.content:
        text = args.content
    else:
        # 支持管道输入
        text = sys.stdin.read()

    if not text.strip():
        print("（空内容）", file=sys.stderr)
        sys.exit(1)

    result = truncate_traceback(text)
    print(result)


if __name__ == "__main__":
    main()
