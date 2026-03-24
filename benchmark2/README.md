# Tinyclaw Performance Benchmark

Tinyclaw 综合性能测试框架，用于测试 Agent Loop、工具执行和 LLM 提供商的性能表现。

## 测试内容

### 1. Agent Loop 性能测试
- 消息处理延迟
- 迭代次数统计
- 工具调用链性能

### 2. 工具执行性能测试
- 文件系统操作（read_file, write_file, list_dir）
- Shell 命令执行
- Web 请求处理
- 并发工具执行能力

### 3. LLM 提供商性能测试
- 响应时间（latency）
- Token 吞吐量（throughput）
- 成功率（success rate）
- 并发性能（concurrent tasks）

### 4. 端到端场景测试
- 完整任务处理流程
- 多步骤推理性能

## 支持的 LLM 提供商

- OpenRouter
- Anthropic
- OpenAI
- DeepSeek
- Moonshot AI
- DashScope
- 其他 LiteLLM 支持的提供商

## 使用方法

### 运行所有测试

```bash
cd d:\Project\tinyclaw-main
python benchmark2\run_benchmark.py
```

### 仅运行特定测试

```bash
# 仅运行工具测试
python benchmark2\run_benchmark.py --tools-only

# 仅运行 LLM 测试
python benchmark2\run_benchmark.py --llm-only

# 仅运行端到端测试
python benchmark2\run_benchmark.py --e2e-only
```

### 使用自定义配置

```bash
python benchmark2\run_benchmark.py --config my_config.json
```

### 对比两次测试结果

```bash
python benchmark2\run_benchmark.py --compare benchmark2\results\tinyclaw_benchmark_20240101_120000.json
```

## 配置文件

`tinyclaw_benchmark_config.json` 包含：
- 测试的提供商列表
- 每个提供商的模型配置
- 测试用例定义
- 性能指标阈值

## 测试结果

测试结果保存在 `benchmark2/results/` 目录，包含：
- 详细的性能指标
- 提供商对比数据
- 模型对比数据
- 可视化图表数据

## 报告生成

使用 `report_generator.py` 生成 HTML 报告：

```bash
python benchmark2\report_generator.py --input benchmark2\results\tinyclaw_benchmark_20260324_080622.json
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `tinyclaw_benchmark.py` | 核心测试框架 |
| `run_benchmark.py` | 测试运行脚本 |
| `report_generator.py` | 报告生成工具 |
| `tinyclaw_benchmark_config.json` | 测试配置文件 |
| `results/` | 测试结果目录 |

## 注意事项

1. 运行 LLM 测试需要配置 API Key
2. 确保网络连接正常
3. 测试会消耗 API 配额，请注意成本控制
