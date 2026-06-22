# Codex 自动使用 ArchQED

ArchQED 使用三类仓库级机制。

## AGENTS.md

Codex 开始工作前会读取根目录 `AGENTS.md`。Bootstrap 只替换 ArchQED 托管区块，保留团队原有内容。

## Repository Skills

```text
.agents/skills/archqed-compile/
.agents/skills/archqed-implement/
.agents/skills/archqed-verify/
```

Skill 可按 description 隐式匹配，也可显式调用 `$archqed-compile`、`$archqed-implement`、`$archqed-verify`。自动化脚本使用显式调用，减少选错流程。

## Project-scoped agents

```text
.codex/agents/archqed-compiler.toml
.codex/agents/archqed-implementer.toml
.codex/agents/archqed-verifier.toml
```

## 确定性入口

```bash
./scripts/codex-sync.sh
./scripts/codex-next.sh
./scripts/codex-verify.sh TASK-ID
```

PowerShell 对应文件也会安装。验证角色需要写证据文件，因此使用 workspace-write，但其角色契约禁止修改业务代码和测试。

不支持 Codex Skill 发现的其他编码智能体仍可读取 `AGENTS.md`、Skill 文档、`.archqed/project.json` 和 CLI 工作流。
