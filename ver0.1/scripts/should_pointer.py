#!/usr/bin/env python3
"""
判断内容是否应该存为 Memory Pointer，并可选择直接存储。

用法：
  python should_pointer.py --file large.py
  python should_pointer.py --content "很长的文本..." --type user
  python should_pointer.py --file tb.txt --type traceback --save

输出：
  SHOULD_POINTER: yes/no
  REASON: ...
  TOKEN_ESTIMATE: 约 xxx
  如果带 --save 且判断为 yes，会同时调用存储并输出 pointer:xxx
"""

import argparse
import re
import sys
from pathlib import Path

# 阈值（可根据实际模型调整）
THRESHOLDS = {
    "file": {"lines": 150, "chars": 4000},
    "traceback": {"lines": 80, "chars": 3000},
    "search": {"lines": 30, "chars": 1500},
    "tool": {"lines": 40, "chars": 2500},
    "user": {"lines": 50, "chars": 3000},
    "code": {"lines": 100, "chars": 3500},
    "other": {"lines": 60, "chars": 2500},
}


def estimate_tokens(text: str) -> int:
    """粗略估算 token 数（中英文混合简单规则）"""
    # 英文约 4 字符/token，中文约 1.5～2 字符/token，这里取保守值
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    other_chars = len(text) - chinese_chars
    return int(chinese_chars / 1.8 + other_chars / 4)


def should_be_pointer(text: str, content_type: str = "other") -> tuple[bool, str, int]:
    lines = text.strip().splitlines()
    line_count = len(lines)
    char_count = len(text)
    token_est = estimate_tokens(text)

    th = THRESHOLDS.get(content_type, THRESHOLDS["other"])

    reasons = []
    if line_count > th["lines"]:
        reasons.append(f"行数 {line_count} > {th['lines']}")
    if char_count > th["chars"]:
        reasons.append(f"字符数 {char_count} > {th['chars']}")
    if token_est > 800:  # 通用 token 红线
        reasons.append(f"预估 token ≈ {token_est} > 800")

    if reasons:
        return True, "；".join(reasons), token_est
    return False, "未达到阈值", token_est


def main():
    parser = argparse.ArgumentParser(description="判断是否应存为 Memory Pointer")
    parser.add_argument("--file", help="从文件读取")
    parser.add_argument("--content", help="直接传入文本")
    parser.add_argument("--type", default="other",
                        choices=["traceback", "file", "search", "tool", "user", "code", "other"])
    parser.add_argument("--save", action="store_true", help="如果判断为 yes，则直接存储并返回 pointer")
    parser.add_argument("--extra", default="", help="存储时的额外标识")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="replace")
        extra = args.extra or Path(args.file).name
    elif args.content:
        text = args.content
        extra = args.extra
    else:
        text = sys.stdin.read()
        extra = args.extra

    if not text.strip():
        print("SHOULD_POINTER: no")
        print("REASON: 空内容")
        return

    yes, reason, token_est = should_be_pointer(text, args.type)

    print(f"SHOULD_POINTER: {'yes' if yes else 'no'}")
    print(f"REASON: {reason}")
    print(f"TOKEN_ESTIMATE: ≈ {token_est}")

    if yes and args.save:
        # 动态调用 pointer_save 逻辑，避免依赖外部文件路径问题
        from datetime import datetime
        pointers_dir = Path("pointers")
        pointers_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_extra = re.sub(r'[\\/:*?"<>|\s]', "_", extra)[:40] if extra else ""

        if safe_extra:
            pointer_id = f"{args.type}:{safe_extra}:{timestamp}"
            filename = f"{args.type}_{safe_extra}_{timestamp}.txt"
        else:
            pointer_id = f"{args.type}:{timestamp}"
            filename = f"{args.type}_{timestamp}.txt"

        filepath = pointers_dir / filename
        filepath.write_text(text, encoding="utf-8")
        print(f"POINTER: pointer:{pointer_id}")


if __name__ == "__main__":
    main()
