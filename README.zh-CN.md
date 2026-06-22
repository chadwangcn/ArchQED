# ArchQED · 构证

**人类定义架构，机器执行契约，证据证明完成。**

ArchQED 把面向人类的架构和功能细节文档转换为可执行的工程控制数据，并且只接受有复现证据的完成状态。

> **无证据，不完成。**

## v0.1.0 提供

- `discovery`、`stabilizing`、`delivery` 三个阶段；
- 初期连续修改时的变更覆盖与回退处理；
- 中期基于 `REQ-*` 稳定标识的局部影响分析；
- Compile、Implement、Verify 三个 Codex Skill；
- 项目级 Codex 编译、实现、验证智能体；
- 可执行验收、反虚假实现扫描和证据包；
- 中文全流程使用文档。

## 安装

```bash
git clone https://github.com/chadwangcn/ArchQED.git
cd ArchQED
python -m pip install .
./scripts/verify.sh
```

安装到现有项目：

```bash
./scripts/install-project.sh /你的项目路径 discovery
```

## 第一次使用

```bash
cd /你的项目路径
vim docs/architecture/system.md
vim docs/features/story-generation.md
archqed sync
./scripts/codex-sync.sh
./scripts/codex-next.sh
archqed status
```

## 文档导航

- [快速开始](docs/zh-CN/quickstart.md)
- [初期架构反复修改](docs/zh-CN/workflows/early-architecture-iteration.md)
- [中期功能细节调整](docs/zh-CN/workflows/feature-refinement.md)
- [编译环节](docs/zh-CN/workflows/compile.md)
- [实现环节](docs/zh-CN/workflows/implementation.md)
- [独立验证](docs/zh-CN/workflows/verification.md)
- [Codex 自动使用](docs/zh-CN/workflows/codex-automation.md)
- [CLI 参考](docs/reference/cli.md)

## 关键规则

实现智能体只能提交 `implemented_unverified`。只有 `archqed verify TASK-ID` 在验收命令全部成功且反虚假扫描没有发现问题时，才能写入 `verified`。
