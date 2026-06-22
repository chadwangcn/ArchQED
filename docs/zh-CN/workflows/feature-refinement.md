# 中期功能细节反复调整

架构基本稳定后切换：

```bash
./scripts/archqed set-stage stabilizing
```

结构性设计继续放在 `docs/architecture/`；校验、默认值来源、错误码、接口行为和局部验收等细节放在 `docs/features/`。

## 稳定 ID

```markdown
REQ-STORY-014
请求和画像都没有 language_level 时返回 422。
```

任务引用：

```json
{"id":"TASK-STORY-014","source_refs":["REQ-STORY-014"]}
```

该细节变化时，只有引用它的任务进入 `needs_recompile` 或 `requires_revalidation`，无关的已验证任务保持 `verified`。

如果缺少稳定 ID 或追踪关系，ArchQED 会扩大影响范围，而不是伪造精确性。
