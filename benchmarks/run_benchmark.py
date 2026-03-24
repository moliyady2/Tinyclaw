#!/usr/bin/env python3
"""
Simple script to run LLM benchmark with proper environment setup.
Models and API configuration are loaded from nanobot's config.json.
"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.llm_benchmark import LLMBenchmark


async def main():
    """Run benchmark using nanobot config.json for models and API."""
    print("=" * 80)
    print("Starting LLM Benchmark")
    print("=" * 80)
    print("📋 Loading models from: ~/.nanobot/config.json")
    print()
    
    config_path = Path(__file__).parent / "llm_benchmark_config.json"
    benchmark = LLMBenchmark(config_path=str(config_path))
    
    try:
        benchmark.load_config()
        
        print(f"📊 Loaded {len(benchmark.providers)} provider(s)")
        for p in benchmark.providers:
            print(f"   - {p.display_name}: {len(p.models)} model(s)")
            for m in p.models:
                print(f"     • {m['name']}")
        print()
        
        report = await benchmark.run_benchmark(restore_config=True)
        
        output_path = benchmark.save_report(report)
        benchmark.print_summary(report)
        
        print(f"\nFull report saved to: {output_path}")
        
    except Exception as e:
        print(f"Error running benchmark: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
