---
name: code-commit
description: Create a git commit with proper format. Use when asked to commit changes.
---

# Git Commit

Commit 标题格式：`[fix #<issue>] <module>: <message>` or `<module>: <message>` if no issue

## Karpathy 范围检查

暂存前读取并应用
[`../code-auto/references/karpathy-coding-guardrails.md`](../code-auto/references/karpathy-coding-guardrails.md) 的“保持改动外科手术式”原则：每个暂存文件必须属于当前目标或是本次改动产生的孤儿清理；无关格式化、重构和历史遗留清理不能混入提交。

## Workflow

1. `git status` + `git diff` 检查变更
2. `git log --oneline -3` 参考提交风格
3. `git add <files>` 暂存相关文件（不要提交 `.claude/` 等无关文件）
4. 提交：

```bash
git commit -s -m "$(cat <<'EOF'
[fix #<issue>] <module>: <short description>

<optional body>
EOF
)"
```

`-s` 自动添加当前用户的 Signed-off-by 信息。
