# 常见问题

## control_state 不是 ready

```bash
./scripts/archqed status --json
```

- `awaiting_approval`：人类执行 `approve-change`；
- `needs_compile`：运行 `codex-sync.sh`；
- 有 drift：运行 `sync`。

## 多个适配器候选

读取 `.archqed/probe.json`，由人类选择后重新 bootstrap。禁止智能体静默选择。

## generic 没有命令

```bash
./scripts/archqed adapter configure generic --command 'unit_test=...'
```

## Codex 看不到 Skill

```bash
find .agents/skills -name SKILL.md
./scripts/archqed doctor
```

重启 Codex 会话，或显式输入 `$archqed-compile`。

## 智能体说完成但 verify 失败

以 CLI 退出码和 `.ai-control/evidence/` 为准。自然语言声明没有状态权限。
