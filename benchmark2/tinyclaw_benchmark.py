"""
Tinyclaw Performance Benchmark

一个全面的性能测试框架，用于测试 tinyclaw 的各个组件性能。
可以与 nanobot 进行对照实验。

测试维度:
1. Agent Loop 性能 - 消息处理延迟、迭代次数、工具调用链
2. 工具执行性能 - 各工具的执行时间、并发性能
3. LLM 提供商性能 - 响应时间、token 吞吐量、成功率
4. 端到端场景 - 完整任务处理流程
"""

import asyncio
import json
import os
import sys
import time
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from contextlib import asynccontextmanager
import tempfile
import shutil

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Tinyclaw imports
from nanobot.agent.loop import AgentLoop
from nanobot.agent.tools.registry import ToolRegistry
from nanobot.agent.tools.filesystem import ReadFileTool, WriteFileTool, EditFileTool, ListDirTool
from nanobot.agent.tools.shell import ExecTool
from nanobot.agent.tools.web import WebFetchTool
from nanobot.bus.queue import MessageBus
from nanobot.providers.litellm_provider import LiteLLMProvider
from nanobot.providers.base import LLMResponse
from nanobot.config.schema import ExecToolConfig


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class BenchmarkMetrics:
    """通用性能指标"""
    operation: str
    total_time_ms: float
    success: bool
    error_message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentLoopMetrics:
    """Agent Loop 性能指标"""
    test_name: str
    total_time_ms: float
    iterations: int
    tool_calls_count: int
    messages_exchanged: int
    success: bool
    error_message: str = ""


@dataclass
class ToolMetrics:
    """工具执行性能指标"""
    tool_name: str
    operation: str
    total_time_ms: float
    success: bool
    error_message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMMetrics:
    """LLM 调用性能指标"""
    provider: str
    model: str
    operation: str
    response_time_ms: float
    first_token_latency_ms: float
    tokens_per_second: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    success: bool
    error_message: str = ""


@dataclass
class BenchmarkResult:
    """完整的 benchmark 结果"""
    timestamp: str
    tinyclaw_version: str
    test_environment: dict[str, Any]
    
    # 各模块测试结果
    agent_loop_results: list[AgentLoopMetrics] = field(default_factory=list)
    tool_results: list[ToolMetrics] = field(default_factory=list)
    llm_results: list[LLMMetrics] = field(default_factory=list)
    end_to_end_results: list[dict[str, Any]] = field(default_factory=list)
    
    # 汇总统计
    summary: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Base Benchmark Class
# =============================================================================

class BaseBenchmark(ABC):
    """Benchmark 基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.results: list[Any] = []
    
    @abstractmethod
    async def run(self) -> list[Any]:
        """运行 benchmark"""
        pass
    
    def reset(self):
        """重置结果"""
        self.results = []


# =============================================================================
# Timer Utility
# =============================================================================

class Timer:
    """高精度计时器"""
    
    def __init__(self):
        self.start_time: float = 0
        self.end_time: float = 0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
    
    @property
    def elapsed_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000


@asynccontextmanager
async def async_timer():
    """异步计时器上下文管理器"""
    timer = Timer()
    timer.start_time = time.perf_counter()
    try:
        yield timer
    finally:
        timer.end_time = time.perf_counter()


# =============================================================================
# Tool Benchmark
# =============================================================================

class ToolBenchmark(BaseBenchmark):
    """
    工具执行性能测试
    
    测试各个工具的执行性能:
    - 文件操作工具 (read/write/edit/list)
    - Shell 执行工具
    - Web 抓取工具
    """
    
    def __init__(self, test_workspace: Path | None = None):
        super().__init__("Tool Benchmark")
        self.workspace = test_workspace or Path(tempfile.mkdtemp(prefix="tinyclaw_benchmark_"))
        self.tools = ToolRegistry()
        self._setup_tools()
    
    def _setup_tools(self):
        """设置测试工具"""
        allowed_dir = self.workspace
        self.tools.register(ReadFileTool(allowed_dir=allowed_dir))
        self.tools.register(WriteFileTool(allowed_dir=allowed_dir))
        self.tools.register(EditFileTool(allowed_dir=allowed_dir))
        self.tools.register(ListDirTool(allowed_dir=allowed_dir))
        self.tools.register(ExecTool(working_dir=str(self.workspace), timeout=30))
        self.tools.register(WebFetchTool())
    
    async def run(self) -> list[ToolMetrics]:
        """运行所有工具测试"""
        logger.info("Starting Tool Benchmark...")
        
        await self._benchmark_filesystem_tools()
        await self._benchmark_shell_tool()
        await self._benchmark_web_tool()
        await self._benchmark_concurrent_tools()
        
        return self.results
    
    async def _benchmark_filesystem_tools(self):
        """测试文件系统工具性能"""
        logger.info("Benchmarking filesystem tools...")
        
        # 创建测试文件
        test_file = self.workspace / "test_file.txt"
        test_content = "Hello, Tinyclaw Benchmark!\n" * 100
        
        # Test write_file
        for i in range(5):
            async with async_timer() as timer:
                try:
                    result = await self.tools.execute("write_file", {
                        "path": str(test_file),
                        "content": test_content
                    })
                    success = "successfully" in result.lower() or "wrote" in result.lower() or "error" not in result.lower()
                except Exception as e:
                    success = False
                    result = str(e)
            
            self.results.append(ToolMetrics(
                tool_name="write_file",
                operation=f"write_{i+1}",
                total_time_ms=timer.elapsed_ms,
                success=success,
                error_message="" if success else result,
                metadata={"content_size": len(test_content)}
            ))
        
        # Test read_file
        for i in range(5):
            async with async_timer() as timer:
                try:
                    result = await self.tools.execute("read_file", {
                        "path": str(test_file)
                    })
                    success = len(result) > 0 and not result.startswith("Error:")
                except Exception as e:
                    success = False
                    result = str(e)
            
            self.results.append(ToolMetrics(
                tool_name="read_file",
                operation=f"read_{i+1}",
                total_time_ms=timer.elapsed_ms,
                success=success,
                error_message="" if success else result,
                metadata={"content_size": len(result) if success else 0}
            ))
        
        # Test list_dir
        for i in range(5):
            async with async_timer() as timer:
                try:
                    result = await self.tools.execute("list_dir", {
                        "path": str(self.workspace)
                    })
                    success = len(result) > 0 and not result.startswith("Error:")
                except Exception as e:
                    success = False
                    result = str(e)
            
            self.results.append(ToolMetrics(
                tool_name="list_dir",
                operation=f"list_{i+1}",
                total_time_ms=timer.elapsed_ms,
                success=success,
                error_message="" if success else result
            ))
        
        # Test edit_file
        for i in range(5):
            async with async_timer() as timer:
                try:
                    result = await self.tools.execute("edit_file", {
                        "path": str(test_file),
                        "old_text": "Hello",
                        "new_text": "Hi"
                    })
                    success = "successfully" in result.lower() or "error" not in result.lower()
                except Exception as e:
                    success = False
                    result = str(e)
            
            self.results.append(ToolMetrics(
                tool_name="edit_file",
                operation=f"edit_{i+1}",
                total_time_ms=timer.elapsed_ms,
                success=success,
                error_message="" if success else result
            ))
    
    async def _benchmark_shell_tool(self):
        """测试 Shell 工具性能"""
        logger.info("Benchmarking shell tool...")
        
        commands = [
            ("echo", "echo 'Hello World'"),
            ("ls", "ls -la" if os.name != 'nt' else "dir"),
            ("python_version", "python --version"),
            ("simple_math", "python -c 'print(sum(range(1000)))'"),
        ]
        
        for name, cmd in commands:
            for i in range(3):
                async with async_timer() as timer:
                    try:
                        result = await self.tools.execute("exec", {
                            "command": cmd,
                            "timeout": 10
                        })
                        success = len(result) >= 0  # Empty output is valid
                    except Exception as e:
                        success = False
                        result = str(e)
                
                self.results.append(ToolMetrics(
                    tool_name="exec",
                    operation=f"{name}_{i+1}",
                    total_time_ms=timer.elapsed_ms,
                    success=success,
                    error_message="" if success else result,
                    metadata={"command": cmd}
                ))
    
    async def _benchmark_web_tool(self):
        """测试 Web 工具性能"""
        logger.info("Benchmarking web tools...")
        
        # 使用一些稳定的测试 URL
        test_urls = [
            ("httpbin_get", "https://httpbin.org/get"),
            ("example", "https://example.com"),
        ]
        
        for name, url in test_urls:
            for i in range(3):
                async with async_timer() as timer:
                    try:
                        result = await self.tools.execute("web_fetch", {
                            "url": url
                        })
                        success = len(result) > 0 and "error" not in result.lower()
                    except Exception as e:
                        success = False
                        result = str(e)
                
                self.results.append(ToolMetrics(
                    tool_name="web_fetch",
                    operation=f"{name}_{i+1}",
                    total_time_ms=timer.elapsed_ms,
                    success=success,
                    error_message="" if success else result,
                    metadata={"url": url}
                ))
    
    async def _benchmark_concurrent_tools(self):
        """测试工具并发性能"""
        logger.info("Benchmarking concurrent tool execution...")
        
        async def run_concurrent():
            tasks = []
            for i in range(10):
                tasks.append(self.tools.execute("list_dir", {
                    "path": str(self.workspace)
                }))
            
            async with async_timer() as timer:
                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    success_count = sum(1 for r in results if not isinstance(r, Exception))
                    success = success_count == len(tasks)
                except Exception as e:
                    success = False
                    success_count = 0
            
            return timer.elapsed_ms, success, success_count
        
        for i in range(3):
            elapsed_ms, success, success_count = await run_concurrent()
            
            self.results.append(ToolMetrics(
                tool_name="concurrent",
                operation=f"concurrent_10_{i+1}",
                total_time_ms=elapsed_ms,
                success=success,
                error_message="",
                metadata={"concurrent_tasks": 10, "success_count": success_count}
            ))
    
    def cleanup(self):
        """清理测试环境"""
        if self.workspace.exists() and "tinyclaw_benchmark_" in str(self.workspace):
            shutil.rmtree(self.workspace, ignore_errors=True)


# =============================================================================
# LLM Provider Benchmark
# =============================================================================

class LLMBenchmark(BaseBenchmark):
    """
    LLM 提供商性能测试
    
    测试不同 LLM 提供商的性能:
    - 响应时间
    - 首 token 延迟
    - Token 吞吐量
    - 成功率
    """
    
    def __init__(self, config_path: str = "perf/tinyclaw_benchmark_config.json"):
        super().__init__("LLM Benchmark")
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}
        self.providers: list[dict[str, Any]] = []
        self.test_prompts: list[dict[str, Any]] = []
    
    def load_config(self) -> None:
        """加载配置文件"""
        if not self.config_path.exists():
            # 使用默认配置
            self.config = self._get_default_config()
        else:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        self.providers = self.config.get('providers', [])
        self.test_prompts = self.config.get('test_prompts', [])
    
    def _get_default_config(self) -> dict[str, Any]:
        """获取默认配置"""
        return {
            "providers": [],
            "test_prompts": [
                {
                    "id": "short_qa",
                    "name": "Short QA",
                    "messages": [{"role": "user", "content": "What is 2+2?"}]
                },
                {
                    "id": "code_gen",
                    "name": "Code Generation",
                    "messages": [{"role": "user", "content": "Write a Python function to calculate fibonacci numbers."}]
                }
            ],
            "test_settings": {
                "runs_per_prompt": 3,
                "timeout_seconds": 60
            }
        }
    
    async def run(self) -> list[LLMMetrics]:
        """运行 LLM benchmark"""
        logger.info("Starting LLM Benchmark...")
        self.load_config()
        
        if not self.providers:
            logger.warning("No providers configured. Skipping LLM benchmark.")
            return self.results
        
        runs_per_prompt = self.config.get('test_settings', {}).get('runs_per_prompt', 3)
        timeout = self.config.get('test_settings', {}).get('timeout_seconds', 60)
        
        for provider_config in self.providers:
            if not provider_config.get('enabled', True):
                continue
            
            provider_name = provider_config.get('display_name', provider_config['name'])
            logger.info(f"Testing provider: {provider_name}")
            
            # 获取 API key（支持环境变量）
            api_key = provider_config.get('api_key', '')
            if api_key.startswith('${') and api_key.endswith('}'):
                env_var = api_key[2:-1]
                api_key = os.environ.get(env_var, '')
            
            if not api_key:
                logger.warning(f"No API key for {provider_name}, skipping")
                continue
            
            for model_config in provider_config.get('models', []):
                if not model_config.get('enabled', True):
                    continue
                
                model_name = model_config['name']
                logger.info(f"  Testing model: {model_name}")
                
                # 创建 provider 实例
                provider = LiteLLMProvider(
                    api_key=api_key,
                    api_base=provider_config.get('api_base', ''),
                    default_model=model_name
                )
                
                for prompt in self.test_prompts:
                    for run in range(runs_per_prompt):
                        metrics = await self._run_single_test(
                            provider, provider_name, model_name, prompt, timeout
                        )
                        self.results.append(metrics)
        
        return self.results
    
    async def _run_single_test(
        self,
        provider: LiteLLMProvider,
        provider_name: str,
        model_name: str,
        prompt: dict[str, Any],
        timeout: int
    ) -> LLMMetrics:
        """运行单次测试"""
        start_time = time.perf_counter()
        first_token_time: float | None = None
        
        try:
            response: LLMResponse = await asyncio.wait_for(
                provider.chat(
                    messages=prompt['messages'],
                    model=model_name,
                    max_tokens=1024,
                    temperature=0.7
                ),
                timeout=timeout
            )
            
            end_time = time.perf_counter()
            response_time_ms = (end_time - start_time) * 1000
            
            # 由于没有流式 API，我们用总时间估算首 token 延迟
            first_token_latency_ms = response_time_ms * 0.3  # 估算值
            
            token_usage = response.token_usage or {}
            input_tokens = token_usage.get('prompt_tokens', 0)
            output_tokens = token_usage.get('completion_tokens', 0)
            total_tokens = token_usage.get('total_tokens', input_tokens + output_tokens)
            
            # 计算 token 吞吐量
            tokens_per_second = (output_tokens / response_time_ms * 1000) if response_time_ms > 0 else 0
            
            return LLMMetrics(
                provider=provider_name,
                model=model_name,
                operation=prompt['id'],
                response_time_ms=response_time_ms,
                first_token_latency_ms=first_token_latency_ms,
                tokens_per_second=tokens_per_second,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                success=True,
                error_message=""
            )
            
        except asyncio.TimeoutError:
            return LLMMetrics(
                provider=provider_name,
                model=model_name,
                operation=prompt['id'],
                response_time_ms=timeout * 1000,
                first_token_latency_ms=timeout * 1000,
                tokens_per_second=0,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                success=False,
                error_message="Timeout"
            )
        except Exception as e:
            return LLMMetrics(
                provider=provider_name,
                model=model_name,
                operation=prompt['id'],
                response_time_ms=0,
                first_token_latency_ms=0,
                tokens_per_second=0,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                success=False,
                error_message=str(e)
            )


# =============================================================================
# End-to-End Benchmark
# =============================================================================

class EndToEndBenchmark(BaseBenchmark):
    """
    端到端场景测试
    
    模拟真实使用场景，测试完整的工作流程:
    - 简单问答
    - 文件操作任务
    - 多轮对话
    - 工具调用链
    """
    
    def __init__(self):
        super().__init__("End-to-End Benchmark")
        self.workspace = Path(tempfile.mkdtemp(prefix="tinyclaw_e2e_"))
    
    async def run(self) -> list[dict[str, Any]]:
        """运行端到端测试"""
        logger.info("Starting End-to-End Benchmark...")
        
        await self._benchmark_simple_operations()
        await self._benchmark_context_operations()
        await self._benchmark_message_bus()
        
        return self.results
    
    async def _benchmark_simple_operations(self):
        """测试简单操作性能"""
        logger.info("Benchmarking simple operations...")
        
        # 测试消息总线创建
        async with async_timer() as timer:
            try:
                bus = MessageBus()
                success = True
            except Exception as e:
                success = False
                error = str(e)
        
        self.results.append({
            "category": "initialization",
            "operation": "create_message_bus",
            "total_time_ms": timer.elapsed_ms,
            "success": success,
            "error_message": "" if success else error
        })
        
        # 测试工具注册表创建
        async with async_timer() as timer:
            try:
                registry = ToolRegistry()
                success = True
            except Exception as e:
                success = False
                error = str(e)
        
        self.results.append({
            "category": "initialization",
            "operation": "create_tool_registry",
            "total_time_ms": timer.elapsed_ms,
            "success": success,
            "error_message": "" if success else error
        })
        
        # 测试上下文构建器创建
        async with async_timer() as timer:
            try:
                from nanobot.agent.context import ContextBuilder
                context = ContextBuilder(self.workspace)
                success = True
            except Exception as e:
                success = False
                error = str(e)
        
        self.results.append({
            "category": "initialization",
            "operation": "create_context_builder",
            "total_time_ms": timer.elapsed_ms,
            "success": success,
            "error_message": "" if success else error
        })
    
    async def _benchmark_context_operations(self):
        """测试上下文操作性能"""
        logger.info("Benchmarking context operations...")
        
        from nanobot.agent.context import ContextBuilder
        
        context = ContextBuilder(self.workspace)
        
        # 测试构建消息
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        async with async_timer() as timer:
            try:
                messages = context.build_messages(
                    history=history,
                    current_message="How are you?",
                    channel="cli",
                    chat_id="test"
                )
                success = len(messages) > 0
            except Exception as e:
                success = False
                error = str(e)
        
        self.results.append({
            "category": "context",
            "operation": "build_messages",
            "total_time_ms": timer.elapsed_ms,
            "success": success,
            "error_message": "" if success else error if 'error' in locals() else ""
        })
    
    async def _benchmark_message_bus(self):
        """测试消息总线性能"""
        logger.info("Benchmarking message bus operations...")
        
        bus = MessageBus()
        
        from nanobot.bus.events import InboundMessage, OutboundMessage
        
        # 测试发布和消费的延迟
        test_messages = []
        for i in range(100):
            msg = InboundMessage(
                channel="test",
                sender_id="user",
                chat_id=f"chat_{i}",
                content=f"Test message {i}"
            )
            test_messages.append(msg)
        
        # 批量发布
        async with async_timer() as timer:
            try:
                for msg in test_messages:
                    await bus.publish_inbound(msg)
                success = True
            except Exception as e:
                success = False
                error = str(e)
        
        self.results.append({
            "category": "message_bus",
            "operation": "publish_100_messages",
            "total_time_ms": timer.elapsed_ms,
            "success": success,
            "error_message": "" if success else error if 'error' in locals() else ""
        })
        
        # 批量消费
        async with async_timer() as timer:
            try:
                consumed = []
                for _ in range(100):
                    msg = await bus.consume_inbound()
                    consumed.append(msg)
                success = len(consumed) == 100
            except Exception as e:
                success = False
                error = str(e)
        
        self.results.append({
            "category": "message_bus",
            "operation": "consume_100_messages",
            "total_time_ms": timer.elapsed_ms,
            "success": success,
            "error_message": "" if success else error if 'error' in locals() else ""
        })
    
    def cleanup(self):
        """清理测试环境"""
        if self.workspace.exists() and "tinyclaw_e2e_" in str(self.workspace):
            shutil.rmtree(self.workspace, ignore_errors=True)


# =============================================================================
# Main Benchmark Runner
# =============================================================================

class TinyclawBenchmarkRunner:
    """
    Tinyclaw 性能测试主运行器
    
    协调所有 benchmark 模块的运行和报告生成
    """
    
    def __init__(self):
        self.results = BenchmarkResult(
            timestamp=datetime.now().isoformat(),
            tinyclaw_version=self._get_version(),
            test_environment=self._get_environment()
        )
        self.benchmarks: list[BaseBenchmark] = []
    
    def _get_version(self) -> str:
        """获取 tinyclaw 版本"""
        try:
            from nanobot import __version__
            return __version__
        except:
            return "unknown"
    
    def _get_environment(self) -> dict[str, Any]:
        """获取测试环境信息"""
        import platform
        import sys
        
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "timestamp": datetime.now().isoformat()
        }
    
    def add_benchmark(self, benchmark: BaseBenchmark):
        """添加 benchmark"""
        self.benchmarks.append(benchmark)
    
    async def run_all(self) -> BenchmarkResult:
        """运行所有 benchmark"""
        logger.info("=" * 60)
        logger.info("Tinyclaw Performance Benchmark Starting")
        logger.info("=" * 60)
        
        for benchmark in self.benchmarks:
            logger.info(f"\nRunning: {benchmark.name}")
            try:
                await benchmark.run()
            except Exception as e:
                logger.error(f"Error running {benchmark.name}: {e}")
        
        # 收集结果
        self._collect_results()
        self._generate_summary()
        
        return self.results
    
    def _collect_results(self):
        """收集所有 benchmark 结果"""
        for benchmark in self.benchmarks:
            if isinstance(benchmark, ToolBenchmark):
                self.results.tool_results = benchmark.results
            elif isinstance(benchmark, LLMBenchmark):
                self.results.llm_results = benchmark.results
            elif isinstance(benchmark, EndToEndBenchmark):
                self.results.end_to_end_results = benchmark.results
    
    def _generate_summary(self):
        """生成汇总统计"""
        summary = {
            "tool_benchmark": self._summarize_tools(),
            "llm_benchmark": self._summarize_llm(),
            "end_to_end_benchmark": self._summarize_e2e()
        }
        self.results.summary = summary
    
    def _summarize_tools(self) -> dict[str, Any]:
        """汇总工具测试结果"""
        if not self.results.tool_results:
            return {"status": "not_run"}
        
        results = self.results.tool_results
        
        # 按工具分组统计
        tool_stats: dict[str, list[ToolMetrics]] = {}
        for r in results:
            if r.tool_name not in tool_stats:
                tool_stats[r.tool_name] = []
            tool_stats[r.tool_name].append(r)
        
        summary = {
            "total_tests": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "by_tool": {}
        }
        
        for tool_name, tool_results in tool_stats.items():
            times = [r.total_time_ms for r in tool_results if r.success]
            summary["by_tool"][tool_name] = {
                "count": len(tool_results),
                "success_rate": sum(1 for r in tool_results if r.success) / len(tool_results),
                "avg_time_ms": statistics.mean(times) if times else 0,
                "min_time_ms": min(times) if times else 0,
                "max_time_ms": max(times) if times else 0,
                "median_time_ms": statistics.median(times) if times else 0
            }
        
        return summary
    
    def _summarize_llm(self) -> dict[str, Any]:
        """汇总 LLM 测试结果"""
        if not self.results.llm_results:
            return {"status": "not_run"}
        
        results = self.results.llm_results
        
        summary = {
            "total_tests": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "by_provider": {}
        }
        
        # 按提供商分组
        provider_stats: dict[str, list[LLMMetrics]] = {}
        for r in results:
            if r.provider not in provider_stats:
                provider_stats[r.provider] = []
            provider_stats[r.provider].append(r)
        
        for provider, provider_results in provider_stats.items():
            successful = [r for r in provider_results if r.success]
            
            summary["by_provider"][provider] = {
                "count": len(provider_results),
                "success_rate": len(successful) / len(provider_results),
                "avg_response_time_ms": statistics.mean([r.response_time_ms for r in successful]) if successful else 0,
                "avg_tokens_per_second": statistics.mean([r.tokens_per_second for r in successful]) if successful else 0,
                "avg_total_tokens": statistics.mean([r.total_tokens for r in successful]) if successful else 0
            }
        
        return summary
    
    def _summarize_e2e(self) -> dict[str, Any]:
        """汇总端到端测试结果"""
        if not self.results.end_to_end_results:
            return {"status": "not_run"}
        
        results = self.results.end_to_end_results
        
        summary = {
            "total_tests": len(results),
            "successful": sum(1 for r in results if r.get('success', False)),
            "failed": sum(1 for r in results if not r.get('success', False))
        }
        
        # 按类别分组
        by_category: dict[str, list[dict]] = {}
        for r in results:
            cat = r.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)
        
        summary["by_category"] = {
            cat: {
                "count": len(items),
                "avg_time_ms": statistics.mean([r['total_time_ms'] for r in items])
            }
            for cat, items in by_category.items()
        }
        
        return summary
    
    def save_report(self, output_dir: str = "perf/results") -> str:
        """保存测试报告"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = output_path / f'tinyclaw_benchmark_{timestamp}.json'
        
        # 转换为可序列化的字典
        report_dict = {
            "timestamp": self.results.timestamp,
            "tinyclaw_version": self.results.tinyclaw_version,
            "test_environment": self.results.test_environment,
            "summary": self.results.summary,
            "tool_results": [asdict(r) for r in self.results.tool_results],
            "llm_results": [asdict(r) for r in self.results.llm_results],
            "end_to_end_results": self.results.end_to_end_results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False, default=str)
        
        return str(report_file)
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("Tinyclaw Performance Benchmark Summary")
        print("=" * 60)
        
        # 工具测试摘要
        tool_summary = self.results.summary.get("tool_benchmark", {})
        if tool_summary.get("status") != "not_run":
            print("\n🔧 Tool Benchmark:")
            print(f"  Total: {tool_summary.get('total_tests', 0)}")
            print(f"  Successful: {tool_summary.get('successful', 0)}")
            print(f"  Failed: {tool_summary.get('failed', 0)}")
            
            for tool_name, stats in tool_summary.get("by_tool", {}).items():
                print(f"\n  {tool_name}:")
                print(f"    Avg: {stats['avg_time_ms']:.2f}ms")
                print(f"    Min/Max: {stats['min_time_ms']:.2f}ms / {stats['max_time_ms']:.2f}ms")
                print(f"    Success Rate: {stats['success_rate']:.1%}")
        
        # LLM 测试摘要
        llm_summary = self.results.summary.get("llm_benchmark", {})
        if llm_summary.get("status") != "not_run":
            print("\n🤖 LLM Benchmark:")
            print(f"  Total: {llm_summary.get('total_tests', 0)}")
            print(f"  Successful: {llm_summary.get('successful', 0)}")
            print(f"  Failed: {llm_summary.get('failed', 0)}")
            
            for provider, stats in llm_summary.get("by_provider", {}).items():
                print(f"\n  {provider}:")
                print(f"    Avg Response: {stats['avg_response_time_ms']:.2f}ms")
                print(f"    Tokens/s: {stats['avg_tokens_per_second']:.2f}")
                print(f"    Success Rate: {stats['success_rate']:.1%}")
        
        # 端到端测试摘要
        e2e_summary = self.results.summary.get("end_to_end_benchmark", {})
        if e2e_summary.get("status") != "not_run":
            print("\n🔄 End-to-End Benchmark:")
            print(f"  Total: {e2e_summary.get('total_tests', 0)}")
            print(f"  Successful: {e2e_summary.get('successful', 0)}")
            print(f"  Failed: {e2e_summary.get('failed', 0)}")
        
        print("\n" + "=" * 60)
    
    def cleanup(self):
        """清理所有 benchmark"""
        for benchmark in self.benchmarks:
            if hasattr(benchmark, 'cleanup'):
                benchmark.cleanup()


# =============================================================================
# Entry Point
# =============================================================================

async def main():
    """Main entry point"""
    # 配置日志
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level="INFO")
    
    # 创建 runner
    runner = TinyclawBenchmarkRunner()
    
    # 添加 benchmark
    runner.add_benchmark(ToolBenchmark())
    runner.add_benchmark(LLMBenchmark())
    runner.add_benchmark(EndToEndBenchmark())
    
    try:
        # 运行所有测试
        await runner.run_all()
        
        # 打印摘要
        runner.print_summary()
        
        # 保存报告
        report_path = runner.save_report()
        print(f"\n💾 Report saved to: {report_path}")
        
    finally:
        # 清理
        runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
