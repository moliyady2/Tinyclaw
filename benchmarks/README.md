# LLM Capability Benchmark

多供应商 LLM 能力对比测试工具，用于评估不同 LLM 模型在各项任务上的表现。

## 测试维度

### 1. 基础能力
- **简单问答**：基础对话和常识问答
- **中文推理**：中文语境下的逻辑推理

### 2. 代码能力
- **代码生成**：根据需求生成代码
- **数学问题**：解决数学计算问题

### 3. 长文本处理
- **上下文理解**：长文本内容理解和总结

### 4. 创意能力
- **创意写作**：故事创作、文案撰写

### 5. 对话能力
- **多轮对话**：上下文连贯性和记忆能力

### 6. 工具理解
- **工具调用**：理解和使用工具的能力

## 核心指标

| 指标 | 说明 |
|------|------|
| 响应时间（response_time） | 模型响应所需时间 |
| Token 使用量（token_usage） | 输入+输出的 token 总数 |
| 响应长度（response_length） | 响应内容的字符数 |
| 代码质量（code_quality） | 生成代码的正确性和规范性 |
| 推理质量（reasoning_quality） | 逻辑推理的准确性 |
| 创造力评分（creativity_score） | 创意内容的原创性和质量 |
| 准确性（accuracy） | 回答的正确程度 |
| 上下文感知（context_awareness） | 理解上下文的能力 |
| 工具理解（tool_understanding） | 使用工具的能力 |

## 支持的模型

- **NVIDIA NIM**: z-ai/glm4.7, moonshotai/kimi-k2.5, minimaxai/minimax-m2.1
- **其他提供商**: 可通过配置文件添加

## 使用方法

### 设置 API Key

```powershell
# Windows PowerShell
$env:NVIDIA_API_KEY = "nvapi-xxxxx"
```

### 运行测试

```bash
cd d:\Project\tinyclaw-main
python benchmarks\run_benchmark.py
```

### 自定义配置

编辑 `benchmarks/llm_benchmark_config.json`：
- 添加/删除测试模型
- 修改测试用例
- 调整评分标准

## 配置文件说明

`llm_benchmark_config.json` 结构：
```json
{
  "providers": [...],  // 提供商配置
  "test_cases": [...], // 测试用例
  "settings": {...}    // 全局设置
}
```

## 测试结果

测试完成后会生成 JSON 报告，包含：
- 各模型在各测试项的得分
- 综合排名
- 详细响应内容

## 文件说明

| 文件 | 说明 |
|------|------|
| `llm_benchmark.py` | 核心测试框架 |
| `run_benchmark.py` | 测试运行脚本 |
| `llm_benchmark_config.json` | 测试配置文件 |
| `results/` | 测试结果目录（自动生成） |

## 注意事项

1. **必须设置 API Key**，否则无法运行
2. 测试会调用真实的 LLM API，产生费用
3. 确保网络连接正常
4. 测试时间较长（取决于模型数量和测试用例）

## 故障排除

### 错误：Config file not found
确保在正确的目录运行命令，或检查配置文件路径。

### 错误：'LLMResponse' object has no attribute 'token_usage'
这是已知问题，已修复。请确保使用最新版本的代码。

### 错误：No API key configured
检查环境变量是否正确设置：
```powershell
$env:NVIDIA_API_KEY
```
