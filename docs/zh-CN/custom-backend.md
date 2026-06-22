# 自定义或未识别的后端

任何后端都可以使用 `generic` 适配器，不要求 ArchQED 预先认识其框架。

## 安装

```bash
./scripts/bootstrap.sh /项目路径 --adapter generic
```

## 配置命令

```bash
./scripts/archqed adapter configure generic \
  --command 'install=./tools/install.sh' \
  --command 'lint=./tools/lint.sh' \
  --command 'typecheck=./tools/typecheck.sh' \
  --command 'unit_test=./tools/test-unit.sh' \
  --command 'integration_test=./tools/test-integration.sh' \
  --command 'build=./tools/build.sh' \
  --command 'smoke_test=./tools/smoke.sh'
```

支持的命令名：

```text
install
lint
typecheck
unit_test
integration_test
build
smoke_test
```

不需要全部配置，但进入稳定开发前至少应有一个真实测试或构建命令。

清空一个命令：

```bash
./scripts/archqed adapter configure generic --command 'lint='
```

人工配置会在升级和重新探测后保留。
