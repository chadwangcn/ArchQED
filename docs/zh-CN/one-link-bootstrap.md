# 一链接入任意后端项目

永久入口：

```text
https://raw.githubusercontent.com/chadwangcn/ArchQED/main/BOOTSTRAP.md
```

把这一条链接交给具备 GitHub 访问、终端和仓库写权限的编码智能体即可。用户侧链接不带版本号；协议内部会固定实际安装的 release ref。

## 智能体会完成什么

```text
确认当前后端仓库根目录
→ 读取 main/BOOTSTRAP.md
→ 按协议克隆固定 release ref 到临时目录
→ 探测后端技术栈
→ 安装自包含运行时、Skills、Agents 和脚本
→ 初始化 .archqed 与 .ai-control
→ 运行 doctor
→ 生成 bootstrap evidence
→ 删除临时克隆
```

ArchQED 不会在安装过程中修改业务代码、依赖清单或构建配置。

## 入口稳定与安装可复现

永久入口始终使用 `main/BOOTSTRAP.md`。该协议文档内部声明稳定 release ref，例如 `v0.2.0`，安装代码从该 ref 获取，而不是直接把 `main` 当运行时来源。

因此同时满足：

- 人类和大模型始终使用同一个链接；
- 每次正式协议都能固定实际安装版本；
- 升级只需要更新入口协议，不需要用户更换链接。

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
