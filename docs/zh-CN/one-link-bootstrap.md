# 一链接入任意后端项目

稳定入口：

```text
https://raw.githubusercontent.com/chadwangcn/ArchQED/v0.2.0/BOOTSTRAP.md
```

把这一条链接交给具备 GitHub 访问、终端和仓库写权限的编码智能体即可。该文档包含固定版本、前置条件、POSIX/PowerShell 命令、歧义处理和安装证据要求。

## 智能体会完成什么

```text
确认当前后端仓库根目录
→ 克隆 ArchQED v0.2.0 到临时目录
→ 探测后端技术栈
→ 安装自包含运行时、Skills、Agents 和脚本
→ 初始化 .archqed 与 .ai-control
→ 运行 doctor
→ 生成 bootstrap evidence
→ 删除临时克隆
```

ArchQED 不会在安装过程中修改业务代码、依赖清单或构建配置。

## 可复现性

正式使用固定 `v0.2.0`，不要把 `main` 作为生产安装来源。相同 tag 对应相同协议和代码。

## 探测歧义

多语言或多模块仓库可能同时出现 `pyproject.toml`、`package.json`、`pom.xml` 等。此时安装会停止并生成：

```text
.archqed/probe.json
```

人类选择后重新运行：

```bash
/path/to/ArchQED/scripts/bootstrap.sh . --adapter java-maven
```

禁止智能体为了继续工作而偷偷选择某个技术栈。

## 成功标准

```bash
./scripts/archqed doctor --json
./scripts/archqed status --json
```

同时必须存在：

```text
.ai-control/evidence/bootstrap/EVD-BOOTSTRAP-*.json
```
