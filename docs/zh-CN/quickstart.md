# ArchQED 快速开始

## 1. 安装

```bash
git clone https://github.com/chadwangcn/ArchQED.git
cd ArchQED
python -m pip install .
./scripts/install-project.sh /你的项目路径 discovery
```

## 2. 编写人类文档

架构写在 `docs/architecture/`，功能细节写在 `docs/features/`。保持自然语言表达，同时给需要追踪的内容添加稳定 ID：

```markdown
ARCH-CONTENT-001
故事生成结果必须写入真实 ContentRepository，并能根据 content_id 读取。

REQ-STORY-014
请求和画像都没有 language_level 时返回 422，不允许静默默认值。
```

## 3. 记录变化

```bash
archqed sync
```

命令会创建 `.ai-control/changes/CHG-*.json` 并暂时关闭开发闸门。

## 4. 人类审批

当状态为 `awaiting_approval`：

```bash
archqed approve-change CHG-ID
```

Codex 被禁止自我审批。

## 5. 编译控制数据

```bash
./scripts/codex-sync.sh
```

Codex 使用 `$archqed-compile` 生成或更新 contracts、tasks、traceability 和 gaps，最后运行 `archqed compile-complete CHG-ID`。

## 6. 实现一个任务

```bash
./scripts/codex-next.sh
```

实现者每次只处理一个 `approved` 任务，并依次运行：

```bash
archqed task start TASK-ID
archqed task submit TASK-ID
```

任务只能到 `implemented_unverified`。

## 7. 独立验证

```bash
./scripts/codex-verify.sh TASK-ID
```

只有 `archqed verify TASK-ID` 的验收和扫描全部通过，任务才成为 `verified`。

## 8. 查看真实进度

```bash
archqed status
archqed task list
```

以状态和证据为准，不以智能体的自然语言声明为准。
