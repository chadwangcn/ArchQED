# 实现环节

实现由 Codex 使用 `archqed-implement` Skill 执行。

```bash
./scripts/codex-next.sh
```

标准流程：

1. `archqed sync --check`；
2. `archqed task next --json`；
3. 只选择一个任务；
4. 阅读任务引用的人类文档、契约和依赖；
5. `archqed task start TASK-ID`；
6. 先补真实路径测试，再写业务代码；
7. 接通真实 API、repository、数据库、队列、存储或模型调用；
8. 运行任务验收命令；
9. `archqed task submit TASK-ID`；
10. 请求独立 verifier。

默认值来源、数据源、错误策略或一致性边界不明确时，任务应转为 `needs_clarification`，不能猜测。

实现者不能修改验收标准来适配错误实现，不能用 mock 替代生产路径，也不能把任务标为 `verified`。
