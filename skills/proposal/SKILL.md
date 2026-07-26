---
name: proposal
description: Extract proposal from plan file and submit as GitLab issue with structured comments
---

# Plan to GitLab Issue

从计划文件提取 Proposal 并提交 GitLab Issue（body + 多个 comments）。

## Workflow

### 1. 读取计划文件

读取用户指定的计划文件（如 `task_plan.md`）。

### 2. 提取并整理内容

| 部分 | 内容 |
|------|------|
| Issue Body | Proposal 概要（概述、需求背景、变更范围、兼容性） |
| Comment 1 | 具体修改方案（diff 格式） |
| Comment 2 | 使用示例和预期效果 |

### 3. 获取仓库信息

```bash
git remote -v  # 确认目标仓库 group/project
```

### 4. 创建 Issue

```bash
glab issue create --repo <group>/<project> \
  --title "[feat] 功能标题" \
  --description "$(cat <<'EOF'
## 概述
...

## 需求背景
...

## 变更范围
| 文件 | 变更类型 |
|------|----------|
| path/to/file | 描述 |

## 兼容性
...
EOF
)"
```

### 5. 添加修改方案 Comment

```bash
glab issue note <issue_number> --repo <group>/<project> --message "$(cat <<'EOF'
## 修改方案

### 修改 1: `path/to/file1`

\`\`\`diff
 existing code
+new code
\`\`\`
EOF
)"
```

### 6. 添加示例 Comment

```bash
glab issue note <issue_number> --repo <group>/<project> --message "$(cat <<'EOF'
## 使用示例

\`\`\`cpp
// 示例代码
\`\`\`

## 预期效果

\`\`\`
命令输出示例
\`\`\`
EOF
)"
```

## Output

完成后返回 Issue URL 和各 Comment 锚点链接：

```
已完成 Issue 提交：

- **Issue**: https://gitlab.example.com/group/project/-/issues/22
  - Body: Proposal 概要
  - Comment 1: 修改方案
  - Comment 2: 使用示例和预期效果
```

## Notes

- 使用 `<<'EOF'` 避免变量展开
- 从 issue 创建输出中提取编号用于后续 comment
