# 编译环节

编译负责把人类意图转换成 AI 开发控制数据，不写业务代码。

```bash
./scripts/codex-sync.sh
```

或显式调用：

```text
$archqed-compile 处理当前变化，更新契约、任务、追踪关系和缺口。
```

## 必须执行

1. `./scripts/archqed status --json`；
2. 有漂移时执行 `./scripts/archqed sync`；
3. 读取 `.archqed/project.json` 和当前变更；
4. `awaiting_approval` 时停止并要求人类审批；
5. 读取受影响的人类文档；
6. 更新 contracts 和 traceability；
7. 生成小而可验收的任务；
8. 从项目适配器读取真实命令；
9. 不明确内容写入 gaps；
10. 运行 `doctor` 并关闭编译。

## 禁止

- 修改人类文档迎合已有代码；
- 擅自决定默认值、数据源或构建命令；
- 编译阶段写业务实现；
- 伪造追踪关系以缩小影响；
- 把任务标为 `verified`。
