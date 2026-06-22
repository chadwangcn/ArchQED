# 一链接入任意后端项目

永久入口：

```text
https://raw.githubusercontent.com/chadwangcn/ArchQED/main/BOOTSTRAP.md
```

把这一条链接交给具备公开 GitHub 访问、终端和仓库写权限的编码智能体即可。

## 为什么入口不带版本号

`main/BOOTSTRAP.md` 只是稳定通道入口，不会直接安装移动中的 `main` 代码。它读取：

```text
https://raw.githubusercontent.com/chadwangcn/ArchQED/main/stable.json
```

`stable.json` 给出当前稳定版本和不可变的 40 位 Git commit。安装协议会检出这个精确 commit，再运行安装器。因此兼顾：

- 用户只记一个永久链接；
- 安装结果仍然可复现；
- 发布新稳定版时只更新 `stable.json`；
- 发生问题时可以把稳定指针回退到上一 commit。

## 智能体会完成什么

```text
确认当前后端仓库根目录
→ 克隆公开 ArchQED 仓库
→ 读取 stable.json
→ 检出不可变 stable commit
→ 探测后端技术栈
→ 安装自包含运行时、Skills、Agents 和脚本
→ 初始化 .archqed 与 .ai-control
→ 运行 doctor
→ 生成 bootstrap evidence
→ 删除临时克隆
```

ArchQED 不会在安装过程中修改业务代码、依赖清单或构建配置。

## 探测歧义

多语言或多模块仓库可能同时出现 `pyproject.toml`、`package.json`、`pom.xml` 等。此时安装会停止并生成：

```text
.archqed/probe.json
```

人类选择后重新运行稳定 commit 中的安装器并传入：

```bash
--adapter java-maven
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
