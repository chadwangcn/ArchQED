# 实现环节

实现由编码智能体使用 `archqed-implement` Skill 执行：

```bash
./scripts/codex-next.sh
```

## 标准流程

1. 检查文档无漂移且控制状态为 `ready`；
2. 读取 `.archqed/project.json`；
3. 获取一个 `approved` 任务；
4. 阅读任务引用的人类文档、契约和依赖；
5. 标记 `in_progress`；
6. 先补真实路径测试，再写业务代码；
7. 接通真实 transport、service、repository、数据库、队列、存储或外部服务；
8. 执行任务验收和适配器中启用的命令；
9. 提交为 `implemented_unverified`；
10. 请求独立 verifier。

默认值来源、数据源、错误策略、技术栈选择或项目命令不明确时，任务必须阻塞，不能猜测。
