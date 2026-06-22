# ArchQED · 构证

**人类定义架构，机器执行契约，证据证明完成。**

ArchQED 是一套面向任意后端仓库的通用协议、自包含 CLI 和编码智能体 Skill 套件。它不绑定任何业务项目、语言或框架。

> **无证据，不完成。**

## 只给编码智能体一个链接

```text
请在当前后端仓库中读取并严格执行：
https://raw.githubusercontent.com/chadwangcn/ArchQED/v0.2.0/BOOTSTRAP.md
```

具备公开 GitHub 访问、终端执行和仓库写权限的编码智能体会自行下载固定版本、探测后端技术栈、安装 ArchQED、自检并返回安装证据。

目标后端项目不需要使用 Python；只有 ArchQED 自身运行时要求 Python 3.11+。

## v0.2.0 — One-Link Bootstrap

- 一个公开链接完成安装引导；
- 自包含运行时安装到 `.archqed/runtime/`；
- 通用后端探测与歧义阻塞；
- Python、Node.js、Maven、Gradle、Go、.NET、Rust、PHP、Ruby 适配器；
- 任意其他后端使用 `generic` 并由人类配置命令；
- POSIX 和 PowerShell 支持；
- 安装、升级、卸载与证据记录；
- 自动安装 Compile、Implement、Verify 三个 Skill；
- 保留已有 `AGENTS.md` 和 `.codex/config.toml`；
- 对任何具体业务项目零耦合。

## 手动安装

```bash
git clone --depth 1 --branch v0.2.0 https://github.com/chadwangcn/ArchQED.git
cd ArchQED
./scripts/bootstrap.sh /后端项目路径
```

安装完成后：

```bash
cd /后端项目路径
./scripts/archqed doctor
./scripts/archqed status
```

## 自动开发流程

```bash
# 修改人类可读文档
vim docs/architecture/system.md
vim docs/features/story-generation.md

./scripts/archqed sync
./scripts/codex-sync.sh
./scripts/codex-next.sh
./scripts/codex-verify.sh TASK-ID
```

## 未识别的后端

```bash
./scripts/archqed adapter configure generic \
  --command 'unit_test=make test' \
  --command 'integration_test=make integration-test' \
  --command 'build=make build'
```

ArchQED 不会凭空生成测试或构建命令。

## 文档导航

- [一链接入](docs/zh-CN/one-link-bootstrap.md)
- [快速开始](docs/zh-CN/quickstart.md)
- [后端适配器](docs/zh-CN/adapters.md)
- [自定义后端](docs/zh-CN/custom-backend.md)
- [升级与卸载](docs/zh-CN/upgrade-uninstall.md)
- [初期架构反复修改](docs/zh-CN/workflows/early-architecture-iteration.md)
- [中期功能细节调整](docs/zh-CN/workflows/feature-refinement.md)
- [编译环节](docs/zh-CN/workflows/compile.md)
- [实现环节](docs/zh-CN/workflows/implementation.md)
- [独立验证](docs/zh-CN/workflows/verification.md)
- [Codex 自动使用](docs/zh-CN/workflows/codex-automation.md)
- [CLI 参考](docs/reference/cli.md)
