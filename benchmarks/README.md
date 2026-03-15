# LLM Benchmark - 多供应商 LLM 性能测试工具

用于测试和对比多个 LLM 供应商和模型的性能表现。

## 功能特点

- **多供应商支持**: 同时测试 NVIDIA NIM、Moonshot AI、MiniMax 等多个供应商
- **多模型对比**: 对比不同模型在相同测试场景下的性能
- **多维度测试**: 支持响应时间、Token 使用量、关键词匹配等多种指标
- **灵活配置**: 通过 JSON 配置文件自定义测试参数
- **详细报告**: 生成包含统计分析和可视化数据的完整报告

## 快速开始

### 1. 配置环境变量

在运行 benchmark 之前，需要配置各供应商的 API Key：

```bash
# Windows PowerShell
$env:NVIDIA_API_KEY = "your-nvidia-api-key"
$env:MOONSHOT_API_KEY = "your-moonshot-api-key"    # 从 https://platform.moonshot.cn 获取
$env:MINIMAX_API_KEY = "your-minimax-api-key"      # 从 https://www.minimax.chat 获取

# Linux/macOS
export NVIDIA_API_KEY="your-nvidia-api-key"
export MOONSHOT_API_KEY="your-moonshot-api-key"
export MINIMAX_API_KEY="your-minimax-api-key"
```

### 2. 运行测试

```bash
# 从项目根目录运行
python benchmarks/run_benchmark.py

# 或在 benchmarks 目录下运行
python run_benchmark.py
```

### 3. 查看结果

测试结果将保存在 `benchmarks/results/` 目录下，文件名格式为 `benchmark_report_YYYYMMDD_HHMMSS.json`。

## 配置文件说明

配置文件 `llm_benchmark_config.json` 包含以下主要部分：

### 测试设置 (test_settings)

```json
{
  "test_settings": {
    "warmup_runs": 1,        // 预热运行次数
    "test_runs": 3,          // 每个测试用例的运行次数
    "timeout_seconds": 120,  // 请求超时时间
    "output_dir": "./benchmarks/results",
    "save_responses": true   // 是否保存完整响应内容
  }
}
```

### 供应商配置 (providers)

每个供应商独立配置，包含自己的 `api_base` 和 `api_key`：

```json
{
  "providers": [
    {
      "name": "nvidia",
      "display_name": "NVIDIA NIM",
      "enabled": true,
      "api_key": "${NVIDIA_API_KEY}",  // 支持环境变量
      "api_base": "https://integrate.api.nvidia.com/v1",
      "models": [
        {
          "name": "z-ai/glm4.7",
          "enabled": true,
          "max_tokens": 4096,
          "temperature": 0.7
        }
      ]
    },
    {
      "name": "moonshot",
      "display_name": "Moonshot AI",
      "enabled": true,
      "api_key": "${MOONSHOT_API_KEY}",
      "api_base": "https://api.moonshot.cn/v1",
      "models": [
        {
          "name": "kimi-k2.5",
          "enabled": true,
          "max_tokens": 4096,
          "temperature": 1.0
        }
      ]
    },
    {
      "name": "minimax",
      "display_name": "MiniMax",
      "enabled": true,
      "api_key": "${MINIMAX_API_KEY}",
      "api_base": "https://api.minimax.chat/v1",
      "models": [
        {
          "name": "minimax-m2.1",
          "enabled": true,
          "max_tokens": 4096,
          "temperature": 0.7
        }
      ]
    }
  ]
}
```

### 测试用例 (test_cases)

预定义了 8 个测试场景：

1. **simple_qa** - 简单问答：测试基础对话能力
2. **code_generation** - 代码生成：测试代码编写能力
3. **long_context** - 长文本处理：测试长文本理解和生成
4. **chinese_reasoning** - 中文推理：测试中文逻辑推理
5. **creative_writing** - 创意写作：测试创意写作能力
6. **math_problem** - 数学问题：测试数学计算和推理
7. **multi_turn_conversation** - 多轮对话：测试对话连贯性
8. **tool_calling_simulation** - 工具调用模拟：测试工具理解能力

每个测试用例包含：
- 测试消息 (messages)
- 期望关键词 (expected_keywords)
- 评估指标 (metrics)

## 添加新的供应商

要添加新的供应商，只需在配置文件中添加新的 provider 配置：

```json
{
  "name": "new_provider",
  "display_name": "New Provider",
  "enabled": true,
  "api_key": "${NEW_PROVIDER_API_KEY}",
  "api_base": "https://api.newprovider.com/v1",
  "models": [
    {
      "name": "model-name",
      "enabled": true,
      "max_tokens": 4096,
      "temperature": 0.7
    }
  ]
}
```

## 添加新的测试用例

在 `test_cases` 数组中添加新的测试用例：

```json
{
  "id": "my_test",
  "name": "我的测试",
  "category": "custom",
  "description": "测试描述",
  "messages": [
    {
      "role": "user",
      "content": "测试问题"
    }
  ],
  "expected_keywords": ["关键词1", "关键词2"],
  "metrics": ["response_time", "token_usage"]
}
```

## 报告解读

生成的报告包含以下信息：

### 汇总统计 (summary)
- 总测试数
- 成功/失败数
- 成功率
- 平均响应时间
- 总 Token 使用量

### 供应商对比 (provider_comparison)
每个供应商的统计数据：
- 平均响应时间
- 中位数响应时间
- 最小/最大响应时间
- 平均 Token 使用量
- 测试次数

### 模型对比 (model_comparison)
每个模型的详细统计数据，格式与供应商对比相同。

### 测试用例结果 (test_case_results)
每个测试场景下各模型的表现数据。

### 详细结果 (detailed_results)
每次测试的详细记录，包括：
- 测试 ID 和名称
- 供应商和模型
- 是否成功
- 响应时间
- Token 使用量
- 错误信息（如有）
- 关键词匹配得分

## 示例输出

```
🚀 Starting LLM Benchmark...
📊 Providers: 3
📝 Test cases: 8
🔢 Total tests to run: 72

🤖 Testing NVIDIA NIM/z-ai/glm4.7...
  [1/72] 简单问答... ✅ 28.45s
  [2/72] 代码生成... ✅ 68.92s
  ...

🤖 Testing Moonshot AI/kimi-k2.5...
  [25/72] 简单问答... ✅ 2.15s
  [26/72] 代码生成... ✅ 5.82s
  ...

🤖 Testing MiniMax/minimax-m2.1...
  [49/72] 简单问答... ✅ 1.05s
  [50/72] 代码生成... ✅ 2.95s
  ...

============================================================
📊 BENCHMARK SUMMARY
============================================================

🔢 Total Tests: 72
✅ Successful: 72
❌ Failed: 0
📈 Success Rate: 100.0%
⏱️  Avg Response Time: 8.45s
📝 Total Tokens: 45,280

------------------------------------------------------------
🏆 PROVIDER COMPARISON
------------------------------------------------------------

📦 MiniMax
   Avg Response Time: 2.18s
   Median Response Time: 1.95s
   Min/Max: 0.85s / 4.52s
   Avg Token Usage: 757
   Test Count: 24

📦 Moonshot AI
   Avg Response Time: 4.28s
   Median Response Time: 3.85s
   Min/Max: 1.92s / 8.76s
   Avg Token Usage: 892
   Test Count: 24

📦 NVIDIA NIM
   Avg Response Time: 52.35s
   Median Response Time: 48.92s
   Min/Max: 16.25s / 96.81s
   Avg Token Usage: 1529
   Test Count: 24

💾 Report saved to: benchmarks/results/benchmark_report_20260310_114855.json
```

## 注意事项

1. **API Key 安全**: 不要将真实的 API Key 直接写入配置文件，使用环境变量方式
2. **成本控制**: 运行完整的 benchmark 会产生 API 调用费用，请注意控制测试次数
3. **网络稳定性**: 确保网络连接稳定，避免因网络问题导致测试失败
4. **超时设置**: 根据模型响应速度调整 `timeout_seconds`，避免不必要的等待

## 故障排除

### API Key 未配置
```
❌ API Key not configured for Moonshot AI. Please set MOONSHOT_API_KEY environment variable.
```
**解决**: 设置对应的环境变量

### 请求超时
```
❌ Timeout
```
**解决**: 增加 `timeout_seconds` 配置，或检查网络连接

### 模型不可用
```
❌ Model not found or not available
```
**解决**: 检查模型名称是否正确，以及该模型是否在对应供应商上可用
