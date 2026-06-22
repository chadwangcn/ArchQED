# 独立验证

验证应由不同的 Codex 子智能体或独立会话执行：

```bash
./scripts/codex-verify.sh TASK-ID
```

验证者应追踪真实入口到真实数据源，检查前后端、repository、存储和外部服务是否真实连通，并寻找 hardcode、placeholder、mock-only 和静默 fallback。

验证者禁止修代码、降低测试严格程度、删除失败用例、修改任务定义或用“看起来正确”代替运行。

任务必须先是 `implemented_unverified`，然后执行：

```bash
archqed verify TASK-ID
```

只有存在可执行验收、所有命令退出码为 0、forbidden 扫描无发现、文档无漂移、控制平面为 ready 时，任务才会成为 `verified`。
