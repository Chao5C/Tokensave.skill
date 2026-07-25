# OOP Code Assistant · v0.1

面向对象编程规范的代码创建与修改助手。

### 主要特性

- 先说明编程思路，再分块编写代码（每次最多 1～2 个类）
- 高置信度直接修改，低置信度必须用户确认
- **强制** Memory Pointer 检查（由脚本决策，模型不可自行跳过）
- **强制** 对话历史压缩
- 基于 AST 的精确符号定位（类 / 函数 / 方法）
- 修改前后自动时间戳备份
- 超长 traceback 智能截取
- 每个代码块强制添加【用途】注释
- 严格面向对象风格，禁止使用比喻解释

### 目录结构

```
oop-code-assistant-v0.1/
├── README.md                 # 本文件（中英双语）
├── SKILL.md                  # Skill 正文（英文）
└── scripts/
    ├── should_pointer.py     # 判断是否需要存为 Pointer（权威决策）
    ├── pointer_save.py       # 存储 Pointer
    ├── find_symbol.py        # AST 符号定位
    ├── truncate_traceback.py # 超长 traceback 截取
    ├── backup_file.py        # 自动备份
    ├── summarize_state.py    # 历史状态摘要
    └── extract_blocks.py     # 提取带用途注释的代码块
```

### 使用建议

将本目录放到 Agent 可加载的 skills 路径下，在有明确编程任务时保持本 skill 激活。

关键检查（Pointer 判断、备份、AST 定位、历史压缩）被设计为「更难绕过」——模型被要求必须先调用对应脚本，而不是自己主观决定。

### 版本

v0.1 — 初始正式版本

---
Object-oriented code creation and modification assistant.

### Key Features

- Explain the coding approach before writing any code
- Generate code in small chunks only (max 1–2 classes per step)
- High-confidence changes proceed directly; low-confidence changes require explicit user confirmation
- **Mandatory** Memory Pointer decision via script (model must not skip)
- **Mandatory** conversation history compression
- AST-based precise symbol location (classes / functions / methods)
- Automatic timestamped backups before and after every modification
- Intelligent truncation of long tracebacks
- Every code block must include a Purpose comment
- Strict object-oriented style; metaphors are prohibited in explanations

### Directory Structure

```
oop-code-assistant-v0.1/
├── README.md                 # This file (bilingual)
├── SKILL.md                  # Skill definition (English)
└── scripts/
    ├── should_pointer.py     # Authoritative decision: should content become a Pointer?
    ├── pointer_save.py       # Store content as Pointer
    ├── find_symbol.py        # AST-based symbol locator
    ├── truncate_traceback.py # Intelligent traceback truncation
    ├── backup_file.py        # Automatic before/after backup
    ├── summarize_state.py    # Task state summary formatter
    └── extract_blocks.py     # Extract blocks that already have Purpose comments
```

### Usage Recommendation

Place this directory where your agent can load skills. Keep the skill active for the entire duration of a programming task.

Critical checks (Pointer decision, backup, AST location, history compression) are intentionally made harder to bypass — the model is required to call the corresponding scripts rather than decide subjectively.

### Version

v0.1 — Initial formal release
