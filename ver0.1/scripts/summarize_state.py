#!/usr/bin/env python3
"""
简单历史状态摘要脚本（规则 + 模板）

用法：
  python summarize_state.py --goal "实现用户登录" --done "完成了数据库模型" --current "正在写接口" --decision "使用JWT" --next "写测试"
  python summarize_state.py --text "一大段对话文本"   # 尝试简单提取（效果有限）

主要用于强制模型输出统一格式的摘要，也可对已有文本做简单清洗。
"""

import argparse
import re
from datetime import datetime


TEMPLATE = """【当前任务状态摘要】
- 最终目标：{goal}
- 已完成：{done}
- 当前卡点：{current}
- 重要决策：{decision}
- 下一步计划：{next}
- 摘要时间：{time}
"""


def simple_extract(text: str) -> dict:
    """非常简单的关键词提取，仅作辅助，真正准确的摘要仍建议由模型生成后再用本脚本格式化。"""
    result = {
        "goal": "（未明确）",
        "done": "（未明确）",
        "current": "（未明确）",
        "decision": "（未明确）",
        "next": "（未明确）",
    }

    # 极简规则示例（可按需扩展）
    patterns = {
        "goal": [r"目标[是为：:]\s*(.+)", r"想要?\s*(.+)", r"实现\s*(.+)"],
        "done": [r"已完成[：:]\s*(.+)", r"完成了\s*(.+)"],
        "current": [r"当前[卡点进度：:]\s*(.+)", r"卡在\s*(.+)"],
        "decision": [r"决定\s*(.+)", r"采用\s*(.+)"],
        "next": [r"下一步[：:]\s*(.+)", r"接下来\s*(.+)"],
    }

    for key, pats in patterns.items():
        for pat in pats:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                result[key] = m.group(1).strip()[:100]
                break
    return result


def main():
    parser = argparse.ArgumentParser(description="生成或格式化任务状态摘要")
    parser.add_argument("--goal", default="")
    parser.add_argument("--done", default="")
    parser.add_argument("--current", default="")
    parser.add_argument("--decision", default="")
    parser.add_argument("--next", default="")
    parser.add_argument("--text", help="传入一段文本尝试简单提取")
    args = parser.parse_args()

    if args.text:
        extracted = simple_extract(args.text)
        goal = args.goal or extracted["goal"]
        done = args.done or extracted["done"]
        current = args.current or extracted["current"]
        decision = args.decision or extracted["decision"]
        next_plan = args.next or extracted["next"]
    else:
        goal = args.goal or "（未填写）"
        done = args.done or "（未填写）"
        current = args.current or "（未填写）"
        decision = args.decision or "（未填写）"
        next_plan = args.next or "（未填写）"

    summary = TEMPLATE.format(
        goal=goal,
        done=done,
        current=current,
        decision=decision,
        next=next_plan,
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    print(summary)


if __name__ == "__main__":
    main()
