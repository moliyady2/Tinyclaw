#!/usr/bin/env python3
"""
Simple script to run LLM benchmark with proper environment setup.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.llm_benchmark import LLMBenchmark


async def main():
    """Run benchmark with environment variable setup."""
    # Load API key from environment or config
    api_key = os.getenv("NVIDIA_API_KEY", "")
    
    if not api_key:
        print("Warning: NVIDIA_API_KEY not set. Please set it in your environment.")
        print("Example: export NVIDIA_API_KEY='nvapi-xxxxx'")
        print("\nOr update the config file directly at benchmarks/llm_benchmark_config.json")
        return
    
    print("=" * 80)
    print("Starting LLM Benchmark")
    print("=" * 80)
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    # Initialize and run benchmark
    benchmark = LLMBenchmark()
    
    try:
        await benchmark.run_benchmark()
        
        # Generate report
        report = benchmark.generate_report()
        
        # Save and display
        output_path = benchmark.save_report(report)
        benchmark.print_summary(report)
        
        print(f"\nFull report saved to: {output_path}")
        
    except Exception as e:
        print(f"Error running benchmark: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
