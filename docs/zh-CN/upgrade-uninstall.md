# 升级与卸载

## 升级

从新的固定 tag 克隆后，对同一项目再次执行 bootstrap：

```bash
/path/to/ArchQED-new/scripts/bootstrap.sh /项目路径
```

升级是幂等的：

- 更新 `.archqed/runtime/`；
- 更新 ArchQED 命名空间下的 Skills、Agents 和脚本；
- 替换 `AGENTS.md` 中的 ArchQED 托管区块；
- 保留托管区块之外的人类内容；
- 保留已有 `.codex/config.toml`；
- 保留人工配置的项目命令；
- 生成新的 bootstrap evidence。

## 卸载集成层

```bash
./scripts/archqed uninstall --target .
```

默认移除自包含运行时、Skills、Agents、脚本和托管指令，但保留 `.ai-control/` 与架构历史，避免丢失证据。

## 完全清理

```bash
./scripts/archqed uninstall --target . --purge-control-data
```

这会删除 `.archqed/` 和 `.ai-control/`。执行前应提交或备份证据。
