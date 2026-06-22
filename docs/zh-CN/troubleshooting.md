# 常见问题

## control_state 不是 ready

运行 `archqed status --json`：

- `awaiting_approval`：人类执行 `archqed approve-change CHANGE-ID`；
- `needs_compile`：运行 `./scripts/codex-sync.sh`；
- 有 drift：运行 `archqed sync`。

## 连续修改很多次

再次运行 `archqed sync`。旧待处理变更会成为 `superseded`。

## 小改动导致全局失效

检查是否缺少 `REQ-*` ID、任务 `source_refs`、是否同时改了架构文档、或者仍处于 discovery。

## Codex 看不到 Skill

```bash
find .agents/skills -name SKILL.md
```

重启 Codex 会话，或显式输入 `$archqed-compile`。

## Codex 说完成但 verify 失败

以 `archqed verify` 的退出码和证据文件为准。自然语言声明没有状态权限。
