#!/usr/bin/env python3
"""
Tinyclaw benchmark2ormance Benchmark 运行脚本

用法:
    python benchmark2/run_benchmark.py [options]

选项:
    --tools-only        仅运行工具测试
    --llm-only          仅运行 LLM 测试
    --e2e-only          仅运行端到端测试
    --config PATH       指定配置文件路径
    --output-dir DIR    指定输出目录
    --compare FILE      与之前的测试结果进行对比

示例:
    # 运行所有测试
    python benchmark2/run_benchmark.py

    # 仅运行工具测试
    python benchmark2/run_benchmark.py --tools-only

    # 使用自定义配置
    python benchmark2/run_benchmark.py --config my_config.json

    # 对比两次测试结果
    python benchmark2/run_benchmark.py --compare benchmark2/results/tinyclaw_benchmark_20240101_120000.json
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from benchmark2.tinyclaw_benchmark import (
    TinyclawBenchmarkRunner,
    ToolBenchmark,
    LLMBenchmark,
    EndToEndBenchmark,
)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Tinyclaw benchmark2ormance Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
环境变量:
    需要在环境变量中设置相应的 API Key 才能运行 LLM 测试:
    - OPENROUTER_API_KEY
    - ANTHROPIC_API_KEY
    - OPENAI_API_KEY
    - DEEPSEEK_API_KEY
    - MOONSHOT_API_KEY
    - DASHSCOPE_API_KEY
        """
    )
    
    parser.add_argument(
        "--tools-only",
        action="store_true",
        help="仅运行工具测试"
    )
    parser.add_argument(
        "--llm-only",
        action="store_true",
        help="仅运行 LLM 测试"
    )
    parser.add_argument(
        "--e2e-only",
        action="store_true",
        help="仅运行端到端测试"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="benchmark2/tinyclaw_benchmark_config.json",
        help="配置文件路径 (默认: benchmark2/tinyclaw_benchmark_config.json)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="benchmark2/results",
        help="输出目录 (默认: benchmark2/results)"
    )
    parser.add_argument(
        "--compare",
        type=str,
        help="与之前的测试结果进行对比"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志"
    )
    
    return parser.parse_args()


def compare_reports(current: dict, previous: dict):
    """对比两次测试结果"""
    print("\n" + "=" * 60)
    print("📊 Benchmark Comparison")
    print("=" * 60)
    
    # 对比工具测试
    current_tools = current.get("summary", {}).get("tool_benchmark", {})
    previous_tools = previous.get("summary", {}).get("tool_benchmark", {})
    
    if current_tools.get("status") != "not_run" and previous_tools.get("status") != "not_run":
        print("\n🔧 Tool Benchmark Comparison:")
        
        current_by_tool = current_tools.get("by_tool", {})
        previous_by_tool = previous_tools.get("by_tool", {})
        
        for tool_name in current_by_tool:
            if tool_name in previous_by_tool:
                curr = current_by_tool[tool_name]
                prev = previous_by_tool[tool_name]
                
                avg_diff = curr["avg_time_ms"] - prev["avg_time_ms"]
                avg_diff_pct = (avg_diff / prev["avg_time_ms"] * 100) if prev["avg_time_ms"] > 0 else 0
                
                symbol = "📈" if avg_diff < 0 else "📉" if avg_diff > 0 else "➡️"
                
                print(f"\n  {tool_name}:")
                print(f"    {symbol} Avg: {curr['avg_time_ms']:.2f}ms vs {prev['avg_time_ms']:.2f}ms "
                      f"({avg_diff:+.2f}ms, {avg_diff_pct:+.1f}%)")
    
    # 对比 LLM 测试
    current_llm = current.get("summary", {}).get("llm_benchmark", {})
    previous_llm = previous.get("summary", {}).get("llm_benchmark", {})
    
    if current_llm.get("status") != "not_run" and previous_llm.get("status") != "not_run":
        print("\n🤖 LLM Benchmark Comparison:")
        
        current_by_provider = current_llm.get("by_provider", {})
        previous_by_provider = previous_llm.get("by_provider", {})
        
        for provider in current_by_provider:
            if provider in previous_by_provider:
                curr = current_by_provider[provider]
                prev = previous_by_provider[provider]
                
                resp_diff = curr["avg_response_time_ms"] - prev["avg_response_time_ms"]
                resp_diff_pct = (resp_diff / prev["avg_response_time_ms"] * 100) if prev["avg_response_time_ms"] > 0 else 0
                
                symbol = "📈" if resp_diff < 0 else "📉" if resp_diff > 0 else "➡️"
                
                print(f"\n  {provider}:")
                print(f"    {symbol} Avg Response: {curr['avg_response_time_ms']:.2f}ms vs "
                      f"{prev['avg_response_time_ms']:.2f}ms ({resp_diff:+.2f}ms, {resp_diff_pct:+.1f}%)")
                print(f"       Tokens/s: {curr['avg_tokens_per_second']:.2f} vs {prev['avg_tokens_per_second']:.2f}")
    
    print("\n" + "=" * 60)


async def main():
    """主函数"""
    args = parse_args()
    
    # 配置日志
    logger.remove()
    log_level = "DEBUG" if args.verbose else "INFO"
    logger.add(lambda msg: print(msg, end=""), level=log_level)
    
    # 检查参数冲突
    if sum([args.tools_only, args.llm_only, args.e2e_only]) > 1:
        print("错误: --tools-only, --llm-only, --e2e-only 不能同时使用")
        sys.exit(1)
    
    # 创建 runner
    runner = TinyclawBenchmarkRunner()
    
    # 根据参数添加 benchmark
    if args.tools_only:
        runner.add_benchmark(ToolBenchmark())
    elif args.llm_only:
        runner.add_benchmark(LLMBenchmark(args.config))
    elif args.e2e_only:
        runner.add_benchmark(EndToEndBenchmark())
    else:
        # 运行所有测试
        runner.add_benchmark(ToolBenchmark())
        runner.add_benchmark(LLMBenchmark(args.config))
        runner.add_benchmark(EndToEndBenchmark())
    
    try:
        # 运行测试
        await runner.run_all()
        
        # 打印摘要
        runner.print_summary()
        
        # 保存报告
        report_path = runner.save_report(args.output_dir)
        print(f"\n💾 Report saved to: {report_path}")
        
        # 如果指定了对比，进行对比分析
        if args.compare:
            compare_path = Path(args.compare)
            if compare_path.exists():
                with open(compare_path, 'r', encoding='utf-8') as f:
                    previous_report = json.load(f)
                
                with open(report_path, 'r', encoding='utf-8') as f:
                    current_report = json.load(f)
                
                compare_reports(current_report, previous_report)
            else:
                print(f"\n⚠️  Comparison file not found: {args.compare}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        # 清理
        runner.cleanup()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
