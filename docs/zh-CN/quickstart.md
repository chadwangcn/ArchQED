# ArchQED v0.2 快速开始

## 1. 一链接入

把下面这个永久链接交给编码智能体：

```text
https://raw.githubusercontent.com/chadwangcn/ArchQED/main/BOOTSTRAP.md
```

入口不带版本号，协议内部会固定实际安装的 release ref。

或手工执行当前稳定版本：

```bash
git clone --depth 1 --branch v0.2.0 https://github.com/chadwangcn/ArchQED.git
./ArchQED/scripts/bootstrap.sh /你的后端项目路径
```

## 2. 检查安装

```bash
cd /你的后端项目路径
./scripts/archqed doctor
./scripts/archqed status
cat .archqed/project.json
```

## 3. 编写人类文档

```markdown
ARCH-CONTENT-001
生成结果必须写入真实仓储，并能根据 ID 重新读取。

REQ-CONTENT-014
请求和配置都缺少 language_level 时返回 422，不允许静默默认值。
```

架构放 `docs/architecture/`，功能细节放 `docs/features/`。

## 4. 记录与编译

```bash
./scripts/archqed sync
./scripts/codex-sync.sh
```

需要审批时，人类执行：

```bash
./scripts/archqed approve-change CHANGE-ID
```

## 5. 实现和验证

```bash
./scripts/codex-next.sh
./scripts/codex-verify.sh TASK-ID
```

实现者最多提交到 `implemented_unverified`。只有确定性验证可以写入 `verified`。

## 6. 运行后端项目检查

```bash
./scripts/archqed check --only unit_test --only build
```
