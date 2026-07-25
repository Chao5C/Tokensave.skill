#!/usr/bin/env python3
"""
基于 AST 的符号定位脚本（类 / 函数 / 方法）

用法：
  python find_symbol.py --file src/main.py --name UserService
  python find_symbol.py --file src/main.py --name login --kind function
  python find_symbol.py --file src/main.py --list          # 列出所有类和函数

输出精确的起始行、结束行，方便后续用 read_file 的 offset/limit 精确读取。
"""

import argparse
import ast
import sys
from pathlib import Path


class SymbolFinder(ast.NodeVisitor):
    def __init__(self):
        self.symbols = []  # (name, kind, start_line, end_line, parent)

    def visit_ClassDef(self, node: ast.ClassDef):
        end_line = getattr(node, "end_lineno", node.lineno)
        self.symbols.append((node.name, "class", node.lineno, end_line, None))
        # 继续遍历方法
        old_parent = getattr(self, "_current_class", None)
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old_parent

    def visit_FunctionDef(self, node: ast.FunctionDef):
        end_line = getattr(node, "end_lineno", node.lineno)
        parent = getattr(self, "_current_class", None)
        kind = "method" if parent else "function"
        self.symbols.append((node.name, kind, node.lineno, end_line, parent))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)  # 复用逻辑


def find_symbols(source: str):
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"语法错误，无法解析 AST: {e}", file=sys.stderr)
        return []

    finder = SymbolFinder()
    finder.visit(tree)
    return finder.symbols


def main():
    parser = argparse.ArgumentParser(description="AST 符号定位")
    parser.add_argument("--file", required=True, help="Python 文件路径")
    parser.add_argument("--name", help="要查找的符号名（类/函数/方法）")
    parser.add_argument("--kind", choices=["class", "function", "method", "any"], default="any",
                        help="符号类型过滤")
    parser.add_argument("--list", action="store_true", help="列出文件中所有符号")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"文件不存在: {args.file}", file=sys.stderr)
        sys.exit(1)

    source = path.read_text(encoding="utf-8", errors="replace")
    symbols = find_symbols(source)

    if args.list or not args.name:
        if not symbols:
            print("未找到任何类或函数")
            return
        print(f"{'Name':<30} {'Kind':<10} {'Start':<8} {'End':<8} {'Parent'}")
        print("-" * 70)
        for name, kind, start, end, parent in symbols:
            parent_str = parent or ""
            print(f"{name:<30} {kind:<10} {start:<8} {end:<8} {parent_str}")
        return

    # 查找指定名称
    matches = []
    for name, kind, start, end, parent in symbols:
        if name != args.name:
            continue
        if args.kind != "any" and kind != args.kind:
            continue
        matches.append((name, kind, start, end, parent))

    if not matches:
        print(f"未找到符号: {args.name}")
        sys.exit(2)

    for name, kind, start, end, parent in matches:
        parent_info = f" (in class {parent})" if parent else ""
        print(f"FOUND: {kind} {name}{parent_info}")
        print(f"LINES: {start}-{end}")
        print(f"OFFSET: {start}")
        print(f"LIMIT: {end - start + 1}")


if __name__ == "__main__":
    main()
