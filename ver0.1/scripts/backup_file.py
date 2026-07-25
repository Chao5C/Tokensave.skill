#!/usr/bin/env python3
"""
自动备份脚本（修改前后）

用法：
  python backup_file.py --file src/main.py --action before
  python backup_file.py --file src/main.py --action after

功能：
- 在 backups/YYYYMMDD_HHMMSS/ 下创建备份
- 文件名保持原名，并加上 _before 或 _after 后缀
- 在文件头部写入备份时间与动作注释
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path

BACKUPS_ROOT = Path("backups")


def backup_file(file_path: str, action: str) -> str:
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if action not in ("before", "after"):
        raise ValueError("action 必须是 before 或 after")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUPS_ROOT / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 目标文件名：原名_before.py / 原名_after.py
    stem = src.stem
    suffix = src.suffix
    dest_name = f"{stem}_{action}{suffix}"
    dest = backup_dir / dest_name

    # 读取原内容并添加头部注释
    original_content = src.read_text(encoding="utf-8", errors="replace")
    header = (
        f"# Backup time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"# Action: {action} modification\n"
        f"# Original path: {src.resolve()}\n"
        f"# {'=' * 60}\n\n"
    )
    dest.write_text(header + original_content, encoding="utf-8")

    return str(dest)


def main():
    parser = argparse.ArgumentParser(description="备份文件到带时间戳的目录")
    parser.add_argument("--file", required=True, help="要备份的文件路径")
    parser.add_argument("--action", required=True, choices=["before", "after"],
                        help="before=修改前, after=修改后")
    args = parser.parse_args()

    try:
        dest = backup_file(args.file, args.action)
        print(dest)  # 输出备份后的完整路径，方便确认
    except Exception as e:
        print(f"备份失败: {e}", file=__import__("sys").stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
