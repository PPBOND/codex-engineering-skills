---
name: code-commit
description: Create a git commit with proper format. Use when asked to commit changes.
---

# Git Commit

Commit 标题格式：`[fix #<issue>] <module>: <message>` or `<module>: <message>` if no issue

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
