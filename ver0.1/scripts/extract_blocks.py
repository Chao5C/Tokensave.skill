#!/usr/bin/env python3
"""
从 Python 文件中提取带【用途】注释的代码块

用法：
  python extract_blocks.py --file src/main.py
  python extract_blocks.py --file src/main.py --output-dir blocks/

输出：
- 默认打印所有找到的代码块
- 如果指定 --output-dir，则把每个块保存为独立 txt 文件
  文件名格式：用途摘要_起始行-结束行.txt
"""

import argparse
import re
from pathlib import Path


PURPOSE_PATTERN = re.compile(r"#\s*【用途】\s*(.+)", re.UNICODE)


def extract_blocks(source: str):
    """
    简单按「用途注释」分割代码块。
    返回列表：[(purpose, start_line, end_line, code), ...]
    行号从 1 开始。
    """
    lines = source.splitlines()
    blocks = []
    current_purpose = None
    current_start = None
    current_lines = []

    for i, line in enumerate(lines, start=1):
        m = PURPOSE_PATTERN.search(line)
        if m:
            # 遇到新的用途注释，先保存上一个块
            if current_purpose is not None and current_lines:
                blocks.append((
                    current_purpose,
                    current_start,
                    i - 1,
                    "\n".join(current_lines)
                ))
            current_purpose = m.group(1).strip()
            current_start = i
            current_lines = [line]
        else:
            if current_purpose is not None:
                current_lines.append(line)

    # 处理最后一个块
    if current_purpose is not None and current_lines:
        blocks.append((
            current_purpose,
            current_start,
            len(lines),
            "\n".join(current_lines)
        ))

    return blocks


def safe_filename(text: str, max_len: int = 40) -> str:
    text = re.sub(r'[\\/:*?"<>|]', "_", text)
    text = text.strip()[:max_len]
    return text or "unnamed"


def main():
    parser = argparse.ArgumentParser(description="提取带【用途】注释的代码块")
    parser.add_argument("--file", required=True, help="要分析的 Python 文件")
    parser.add_argument("--output-dir", help="如果指定，则把每个块保存为独立文件")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"文件不存在: {args.file}", file=__import__("sys").stderr)
        raise SystemExit(1)

    source = path.read_text(encoding="utf-8", errors="replace")
    blocks = extract_blocks(source)

    if not blocks:
        print("未找到任何带【用途】注释的代码块。")
        return

    if args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for purpose, start, end, code in blocks:
            fname = f"{safe_filename(purpose)}_{start}-{end}.txt"
            (out_dir / fname).write_text(code, encoding="utf-8")
            print(f"已保存: {out_dir / fname}")
    else:
        for idx, (purpose, start, end, code) in enumerate(blocks, 1):
            print(f"\n===== 代码块 {idx} =====")
            print(f"用途: {purpose}")
            print(f"行号: {start}-{end}")
            print("-" * 40)
            print(code)
            print("=" * 40)


if __name__ == "__main__":
    main()
