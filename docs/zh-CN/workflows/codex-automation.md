# Codex 自动使用 ArchQED

ArchQED 使用三个 Codex 原生机制。

## AGENTS.md

Codex 工作前读取根目录 `AGENTS.md`，因此每次运行都能看到漂移检查、单任务实现、禁止自验和反虚假规则。

## Repository Skills

```text
.agents/skills/archqed-compile/
.agents/skills/archqed-implement/
.agents/skills/archqed-verify/
```

Skill 可按 description 隐式匹配，也可显式调用 `$archqed-compile`、`$archqed-implement`、`$archqed-verify`。脚本使用显式调用，减少匹配错误。

## Project-scoped agents

```text
.codex/agents/archqed-compiler.toml
.codex/agents/archqed-implementer.toml
.codex/agents/archqed-verifier.toml
```

## 脚本

```bash
./scripts/codex-sync.sh
./scripts/codex-next.sh
./scripts/codex-verify.sh TASK-ID
```

脚本使用 `codex exec --sandbox workspace-write`。验证角色虽然需要写证据文件，但其指令明确禁止修改业务代码和测试。

自动化不替代人类审批、架构缺口决策和阶段切换。
