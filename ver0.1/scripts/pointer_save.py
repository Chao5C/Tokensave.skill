#!/usr/bin/env python3
"""
Memory Pointer 存储脚本

用法示例：
  python pointer_save.py --type traceback --file /tmp/long_traceback.txt
  python pointer_save.py --type file --file src/main.py
  python pointer_save.py --type search --content "大量搜索结果..."
  python pointer_save.py --type code --file temp_module.py --extra UserService
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

POINTERS_DIR = Path("pointers")
POINTERS_DIR.mkdir(exist_ok=True)


def save_pointer(content: str, pointer_type: str, extra: str = "") -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_extra = re.sub(r'[\\/:*?"<>|\s]', "_", extra)[:40] if extra else ""

    if safe_extra:
        pointer_id = f"{pointer_type}:{safe_extra}:{timestamp}"
        filename = f"{pointer_type}_{safe_extra}_{timestamp}.txt"
    else:
        pointer_id = f"{pointer_type}:{timestamp}"
        filename = f"{pointer_type}_{timestamp}.txt"

    filepath = POINTERS_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return f"pointer:{pointer_id}"


def main():
    parser = argparse.ArgumentParser(description="Save content as Memory Pointer")
    parser.add_argument("--type", required=True,
                        choices=["traceback", "file", "search", "tool", "user", "code", "other"])
    parser.add_argument("--file", help="从文件读取内容")
    parser.add_argument("--content", help="直接传入内容")
    parser.add_argument("--extra", default="", help="额外标识，如文件名或关键词")
    args = parser.parse_args()

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8", errors="replace")
        extra = args.extra or Path(args.file).name
    elif args.content:
        content = args.content
        extra = args.extra
    else:
        raise SystemExit("必须提供 --file 或 --content")

    pointer = save_pointer(content, args.type, extra)
    print(pointer)


if __name__ == "__main__":
    main()
