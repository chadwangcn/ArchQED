# 初期架构反复修改

项目初期使用：

```bash
archqed set-stage discovery
```

## 策略

- 架构和功能变化默认无需逐次审批；
- 所有变化保守地按全局影响处理；
- 一旦记录变化，开发入口关闭，直到重新编译；
- 不追求过早的局部影响精度。

## 连续修改

第一次 `archqed sync` 产生 `CHG-A`。文档继续修改后再次运行 `archqed sync`，ArchQED 会把 `CHG-A` 标为 `superseded`，从最后已接受基线重新计算并创建 `CHG-B`。旧变更不能再审批或关闭。

## 回退修改

文档恢复到已接受基线后运行 `archqed sync`，待处理变更会成为 `reverted`，控制状态恢复 `ready`。

## 推荐节奏

```text
人类连续刷新架构
→ 到可讨论节点时 sync
→ Codex compile
→ 只实现最小端到端闭环
→ 再继续刷新架构
```
