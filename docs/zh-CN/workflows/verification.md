# 独立验证

验证由不同的编码智能体或独立会话执行：

```bash
./scripts/codex-verify.sh TASK-ID
```

验证者应追踪真实入口到真实数据源，检查各层是否真正连通，并寻找 hardcode、placeholder、mock-only、静默 fallback 和无副作用成功。

验证者禁止修代码、降低测试严格程度、删除失败用例、修改任务定义或用“看起来正确”代替运行。

```bash
./scripts/archqed verify TASK-ID
```

只有可执行验收全部成功、forbidden 扫描无发现、文档无漂移且控制状态为 `ready` 时，任务才会成为 `verified`。
