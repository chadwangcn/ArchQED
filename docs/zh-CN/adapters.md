# 后端适配器

适配器只负责识别项目工具和记录候选命令，不改变 ArchQED 的架构、任务与证据协议。

## 内置适配器

| ID | 典型标识 |
|---|---|
| `python` | `pyproject.toml`、`requirements.txt`、Poetry、uv |
| `node` | `package.json` 和锁文件 |
| `java-maven` | `pom.xml`、`mvnw` |
| `java-gradle` | `build.gradle*`、`gradlew` |
| `go` | `go.mod` |
| `dotnet` | `*.sln`、`*.csproj` |
| `rust` | `Cargo.toml` |
| `php-composer` | `composer.json` |
| `ruby-bundler` | `Gemfile` |
| `generic` | 任意其他后端 |

## 探测

```bash
./scripts/archqed probe --target . --json
./scripts/archqed adapter detect --target . --json
```

结果包含候选、分数、证据、建议命令和歧义状态。分数只是探测依据，不是架构判断。

## 选择规则

- 单一候选自动选择；
- 第一候选与第二候选差距不足时阻塞；
- 无已知标识时使用 `generic`；
- 显式选择使用 `--adapter ID`；
- 只有确认探测标识不完整时才使用 `--allow-mismatch`。

## 命令来源

命令写入 `.archqed/project.json`，来源只有：

- `detected`：从锁文件、脚本或标准构建文件推断；
- `human`：人类显式配置。

ArchQED 不会为不存在的 npm script、Maven profile 或 Make target 编造命令。

## 运行项目检查

```bash
./scripts/archqed check
./scripts/archqed check --only unit_test --only build
```

默认不运行 `install`，除非显式增加 `--include-install`。执行结果保存到项目检查证据中。
