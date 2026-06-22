# 编译环节

编译负责把人类意图转换成 AI 开发控制数据，不写业务代码。

## 启动

```bash
./scripts/codex-sync.sh
```

或：

```text
$archqed-compile 处理当前变更，更新契约、任务、追踪关系和缺口。
```

## 必须执行

1. `archqed status --json`；
2. 有漂移时执行 `archqed sync`；
3. 读取当前变更；
4. `awaiting_approval` 时停止并要求人类审批；
5. 读取受影响的人类文档；
6. 更新 contracts 和 traceability；
7. 生成小而可验收的任务；
8. 不明确内容写入 gaps；
9. 运行 `archqed doctor`；
10. 执行 `archqed compile-complete CHANGE-ID`。

## 禁止

- 修改人类文档来迎合已有代码；
- 擅自决定默认值；
- 编译阶段写业务实现；
- 伪造追踪关系以缩小影响；
- 把任务标为 verified。
