# hank-skills

Claude Code 自定义 Skills 集合仓库。

## Skills 列表

| Skill | 说明 |
|-------|------|
| [interactive-diff-review](skills/interactive-diff-review/SKILL.md) | 交互式 Git Diff 逐块代码审查。解析 diff → 逐 hunk 展示分析 → 收集 Accept/Reject 决策 → 覆盖率校验 → 生成 Markdown 审查报告。 |

## 目录结构

```
hank-skills/
├── README.md
└── skills/
    └── interactive-diff-review/
        ├── SKILL.md              # Skill 定义与工作流编排
        ├── scripts/
        │   ├── resolve_diff.py   # Diff 来源解析 + 语言检测
        │   └── parse_hunks.py    # Unified diff → 结构化 hunks
        └── references/
            ├── review-format.md  # 审查展示格式与分析字段
            ├── report-template.md# 审查报告模板
            └── edge-cases.md     # 边界情况处理
```

## 安装

```bash
# 安装指定 skill
npx skills add https://github.com/hankjs/hank-skills --skill interactive-diff-review
```

## 使用方式

在 Claude Code 中通过 `/interactive-diff-review` 调用，支持以下参数：

```bash
/interactive-diff-review                        # 自动检测：staged → workspace
/interactive-diff-review <commit>               # 指定 commit
/interactive-diff-review <commit_a> <commit_b>  # commit 区间
```
