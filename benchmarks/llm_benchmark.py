"""
LLM Benchmark - 多供应商 LLM 性能测试工具

测试多个 LLM 供应商和模型的性能表现，支持对比分析。
从 nanobot 的 config.json 读取模型列表进行测试。
"""

import asyncio
import json
import os
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from nanobot.providers.litellm_provider import LiteLLMProvider
from nanobot.providers.base import LLMResponse

NANOBOT_CONFIG_PATH = Path.home() / ".nanobot" / "config.json"


@dataclass
class ProviderConfig:
    """Provider configuration."""
    name: str
    display_name: str
    enabled: bool = True
    api_key: str = ""
    api_base: str = ""
    models: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class TestCase:
    """Test case configuration."""
    id: str
    name: str
    category: str
    description: str
    messages: list[dict[str, str]]
    expected_keywords: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    context_file: str | None = None


@dataclass
class TestResult:
    """Single test result."""
    test_id: str
    test_name: str
    provider: str
    model: str
    success: bool
    response_time: float
    token_usage: dict[str, int] | None
    error_message: str
    keyword_match_score: float
    response_content: str = ""


@dataclass
class BenchmarkReport:
    """Complete benchmark report."""
    timestamp: str
    summary: dict[str, Any]
    provider_comparison: dict[str, dict[str, Any]]
    model_comparison: dict[str, dict[str, Any]]
    test_case_results: dict[str, Any]
    detailed_results: list[dict[str, Any]]


class LLMBenchmark:
    """LLM benchmark runner."""

    def __init__(self, config_path: str = "llm_benchmark_config.json"):
        """Initialize benchmark with config file."""
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}
        self.providers: list[ProviderConfig] = []
        self.test_cases: list[TestCase] = []
        self.results: list[TestResult] = []

    def load_nanobot_config(self) -> dict[str, Any]:
        """Load nanobot config.json to get model list."""
        if not NANOBOT_CONFIG_PATH.exists():
            raise FileNotFoundError(f"NanoBot config not found: {NANOBOT_CONFIG_PATH}")
        
        with open(NANOBOT_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_nanobot_config(self, config: dict[str, Any]) -> None:
        """Save nanobot config.json."""
        with open(NANOBOT_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def backup_nanobot_config(self) -> Path:
        """Backup nanobot config before modification."""
        backup_path = NANOBOT_CONFIG_PATH.with_suffix('.json.bak')
        shutil.copy2(NANOBOT_CONFIG_PATH, backup_path)
        return backup_path

    def restore_nanobot_config(self, backup_path: Path) -> None:
        """Restore nanobot config from backup."""
        shutil.copy2(backup_path, NANOBOT_CONFIG_PATH)

    def get_models_from_nanobot_config(self) -> list[str]:
        """Get model list from nanobot config customProviders."""
        config = self.load_nanobot_config()
        providers_config = config.get('providers', {})
        custom_providers = providers_config.get('customProviders', [])
        
        for provider in custom_providers:
            models = provider.get('models', [])
            if models:
                return models
        
        raise ValueError("No models found in nanobot config customProviders")

    def setup_model_for_testing(self, model_name: str) -> None:
        """
        Setup nanobot config for testing a specific model:
        1. Move the model to the first position in models list
        2. Set the default model to the target model
        """
        config = self.load_nanobot_config()
        providers_config = config.get('providers', {})
        custom_providers = providers_config.get('customProviders', [])
        
        for provider in custom_providers:
            models = provider.get('models', [])
            if model_name in models:
                models.remove(model_name)
                models.insert(0, model_name)
                provider['models'] = models
                
                agents = config.get('agents', {})
                defaults = agents.get('defaults', {})
                defaults['model'] = model_name
                
                self.save_nanobot_config(config)
                print(f"✅ Configured for model: {model_name}")
                return
        
        raise ValueError(f"Model {model_name} not found in nanobot config")

    def load_config(self) -> None:
        """Load benchmark configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self._load_providers()
        self._load_test_cases()

    def _load_providers(self) -> None:
        """Load provider configurations from nanobot config."""
        nanobot_config = self.load_nanobot_config()
        providers_config = nanobot_config.get('providers', {})
        custom_providers = providers_config.get('customProviders', [])
        
        for cp in custom_providers:
            api_key = cp.get('apiKey', '')
            api_base = cp.get('apiBase', cp.get('defaultApiBase', ''))
            models = cp.get('models', [])
            
            if not api_key:
                continue
            
            model_list = []
            for model_name in models:
                model_list.append({
                    'name': model_name,
                    'enabled': True,
                    'max_tokens': 4096,
                    'temperature': 0.7
                })
            
            provider = ProviderConfig(
                name=cp.get('name', 'nvidia'),
                display_name=cp.get('displayName', 'NVIDIA NIM'),
                enabled=True,
                api_key=api_key,
                api_base=api_base,
                models=model_list
            )
            self.providers.append(provider)

    def _load_test_cases(self) -> None:
        """Load test case configurations."""
        test_cases_data = self.config.get('test_cases', [])

        for tc_data in test_cases_data:
            test_case = TestCase(
                id=tc_data['id'],
                name=tc_data['name'],
                category=tc_data.get('category', 'general'),
                description=tc_data.get('description', ''),
                messages=tc_data['messages'],
                expected_keywords=tc_data.get('expected_keywords', []),
                metrics=tc_data.get('metrics', []),
                context_file=tc_data.get('context_file')
            )
            self.test_cases.append(test_case)

    async def run_benchmark(self, restore_config: bool = True) -> BenchmarkReport:
        """Run complete benchmark."""
        backup_path = None
        if restore_config:
            backup_path = self.backup_nanobot_config()
        
        try:
            return await self._run_benchmark_internal()
        finally:
            if restore_config and backup_path and backup_path.exists():
                self.restore_nanobot_config(backup_path)
                print(f"🔄 Config restored from backup: {backup_path}")

    async def _run_benchmark_internal(self) -> BenchmarkReport:
        """Internal benchmark execution."""
        print("🚀 Starting LLM Benchmark...")
        print(f"📊 Providers: {len(self.providers)}")
        print(f"📝 Test cases: {len(self.test_cases)}")

        total_tests = sum(
            len([m for m in p.models if m.get('enabled', True)])
            for p in self.providers if p.enabled
        ) * len(self.test_cases)

        print(f"🔢 Total tests to run: {total_tests}\n")

        current_test = 0

        for provider in self.providers:
            if not provider.enabled:
                print(f"⏭️  Skipping disabled provider: {provider.display_name}")
                continue

            for model in provider.models:
                if not model.get('enabled', True):
                    continue

                model_name = model['name']
                print(f"\n🔧 Setting up config for model: {model_name}")
                self.setup_model_for_testing(model_name)
                
                print(f"🤖 Testing {provider.display_name}/{model_name}...")

                for test_case in self.test_cases:
                    current_test += 1
                    print(f"  [{current_test}/{total_tests}] {test_case.name}...", end=' ')

                    result = await self._run_single_test(provider, model, test_case)
                    self.results.append(result)

                    if result.success:
                        print(f"✅ {result.response_time:.2f}s")
                    else:
                        print(f"❌ {result.error_message[:50]}")

                print()

        return self._generate_report()

    async def _run_single_test(
        self,
        provider: ProviderConfig,
        model: dict[str, Any],
        test_case: TestCase
    ) -> TestResult:
        """Run a single test case."""
        try:
            # 检查 API Key 是否配置
            if not provider.api_key:
                return TestResult(
                    test_id=test_case.id,
                    test_name=test_case.name,
                    provider=provider.display_name,
                    model=model['name'],
                    success=False,
                    response_time=0.0,
                    token_usage=None,
                    error_message=f"API Key not configured for {provider.display_name}. "
                                  f"Please set {provider.name.upper()}_API_KEY environment variable.",
                    keyword_match_score=0.0
                )

            # Create provider instance with provider-specific api_base
            litellm_provider = LiteLLMProvider(
                api_key=provider.api_key,
                api_base=provider.api_base,
                default_model=model['name']
            )

            # Measure response time
            start_time = time.time()

            response: LLMResponse = await asyncio.wait_for(
                litellm_provider.chat(
                    messages=test_case.messages,
                    model=model['name'],
                    max_tokens=model.get('max_tokens', 4096),
                    temperature=model.get('temperature', 0.7)
                ),
                timeout=self.config.get('test_settings', {}).get('timeout_seconds', 120)
            )

            end_time = time.time()
            response_time = end_time - start_time

            # Calculate keyword match score
            keyword_score = self._calculate_keyword_score(
                response.content,
                test_case.expected_keywords
            )

            return TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                provider=provider.display_name,
                model=model['name'],
                success=True,
                response_time=response_time,
                token_usage=response.usage,
                error_message="",
                keyword_match_score=keyword_score,
                response_content=response.content[:500] if response.content else ""
            )

        except asyncio.TimeoutError:
            return TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                provider=provider.display_name,
                model=model['name'],
                success=False,
                response_time=0.0,
                token_usage=None,
                error_message="Timeout",
                keyword_match_score=0.0
            )
        except Exception as e:
            return TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                provider=provider.display_name,
                model=model['name'],
                success=False,
                response_time=0.0,
                token_usage=None,
                error_message=str(e),
                keyword_match_score=0.0
            )

    def _calculate_keyword_score(self, content: str, keywords: list[str]) -> float:
        """Calculate keyword match score."""
        if not keywords:
            return 1.0

        content_lower = content.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
        return matches / len(keywords)

    def _generate_report(self) -> BenchmarkReport:
        """Generate benchmark report."""
        # Calculate summary statistics
        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]

        summary = {
            "total_tests": len(self.results),
            "successful": len(successful_tests),
            "failed": len(failed_tests),
            "success_rate": len(successful_tests) / len(self.results) if self.results else 0,
            "avg_response_time": sum(r.response_time for r in successful_tests) / len(successful_tests) if successful_tests else 0,
            "total_tokens": sum(
                r.token_usage.get('total_tokens', 0)
                for r in successful_tests
                if r.token_usage
            )
        }

        # Provider comparison
        provider_comparison = {}
        for provider in self.providers:
            provider_results = [r for r in successful_tests if r.provider == provider.display_name]
            if provider_results:
                provider_comparison[provider.display_name] = {
                    "avg_response_time": sum(r.response_time for r in provider_results) / len(provider_results),
                    "median_response_time": sorted([r.response_time for r in provider_results])[len(provider_results) // 2],
                    "min_response_time": min(r.response_time for r in provider_results),
                    "max_response_time": max(r.response_time for r in provider_results),
                    "avg_token_usage": sum(
                        r.token_usage.get('total_tokens', 0)
                        for r in provider_results
                        if r.token_usage
                    ) / len(provider_results),
                    "test_count": len(provider_results)
                }

        # Model comparison
        model_comparison = {}
        for result in successful_tests:
            model_key = f"{result.provider}/{result.model}"
            if model_key not in model_comparison:
                model_results = [r for r in successful_tests if r.provider == result.provider and r.model == result.model]
                model_comparison[model_key] = {
                    "avg_response_time": sum(r.response_time for r in model_results) / len(model_results),
                    "median_response_time": sorted([r.response_time for r in model_results])[len(model_results) // 2],
                    "min_response_time": min(r.response_time for r in model_results),
                    "max_response_time": max(r.response_time for r in model_results),
                    "avg_token_usage": sum(
                        r.token_usage.get('total_tokens', 0)
                        for r in model_results
                        if r.token_usage
                    ) / len(model_results),
                    "test_count": len(model_results)
                }

        # Test case results
        test_case_results = {}
        for test_case in self.test_cases:
            tc_results = [r for r in successful_tests if r.test_id == test_case.id]
            test_case_results[test_case.id] = {
                "name": test_case.name,
                "results": [
                    {
                        "provider": r.provider,
                        "model": r.model,
                        "response_time": r.response_time,
                        "token_usage": r.token_usage,
                        "keyword_score": r.keyword_match_score
                    }
                    for r in tc_results
                ]
            }

        # Detailed results
        detailed_results = [
            {
                "test_id": r.test_id,
                "test_name": r.test_name,
                "provider": r.provider,
                "model": r.model,
                "success": r.success,
                "response_time": r.response_time,
                "token_usage": r.token_usage,
                "error_message": r.error_message,
                "keyword_match_score": r.keyword_match_score
            }
            for r in self.results
        ]

        return BenchmarkReport(
            timestamp=datetime.now().isoformat(),
            summary=summary,
            provider_comparison=provider_comparison,
            model_comparison=model_comparison,
            test_case_results=test_case_results,
            detailed_results=detailed_results
        )

    def save_report(self, report: BenchmarkReport, output_dir: str | None = None) -> str:
        """Save benchmark report to file."""
        if output_dir is None:
            output_dir = self.config.get('test_settings', {}).get('output_dir', './benchmarks/results')

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = output_path / f'benchmark_report_{timestamp}.json'

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': report.timestamp,
                'summary': report.summary,
                'provider_comparison': report.provider_comparison,
                'model_comparison': report.model_comparison,
                'test_case_results': report.test_case_results,
                'detailed_results': report.detailed_results
            }, f, indent=2, ensure_ascii=False)

        return str(report_file)

    def print_summary(self, report: BenchmarkReport) -> None:
        """Print benchmark summary to console."""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)

        print(f"\n🔢 Total Tests: {report.summary['total_tests']}")
        print(f"✅ Successful: {report.summary['successful']}")
        print(f"❌ Failed: {report.summary['failed']}")
        print(f"📈 Success Rate: {report.summary['success_rate']:.1%}")
        print(f"⏱️  Avg Response Time: {report.summary['avg_response_time']:.2f}s")
        print(f"📝 Total Tokens: {report.summary['total_tokens']:,}")

        print("\n" + "-" * 60)
        print("🏆 PROVIDER COMPARISON")
        print("-" * 60)

        for provider_name, stats in sorted(
            report.provider_comparison.items(),
            key=lambda x: x[1]['avg_response_time']
        ):
            print(f"\n📦 {provider_name}")
            print(f"   Avg Response Time: {stats['avg_response_time']:.2f}s")
            print(f"   Median Response Time: {stats['median_response_time']:.2f}s")
            print(f"   Min/Max: {stats['min_response_time']:.2f}s / {stats['max_response_time']:.2f}s")
            print(f"   Avg Token Usage: {stats['avg_token_usage']:.0f}")
            print(f"   Test Count: {stats['test_count']}")

        print("\n" + "-" * 60)
        print("🤖 MODEL COMPARISON")
        print("-" * 60)

        for model_key, stats in sorted(
            report.model_comparison.items(),
            key=lambda x: x[1]['avg_response_time']
        ):
            print(f"\n🔹 {model_key}")
            print(f"   Avg Response Time: {stats['avg_response_time']:.2f}s")
            print(f"   Median Response Time: {stats['median_response_time']:.2f}s")
            print(f"   Min/Max: {stats['min_response_time']:.2f}s / {stats['max_response_time']:.2f}s")
            print(f"   Avg Token Usage: {stats['avg_token_usage']:.0f}")
            print(f"   Test Count: {stats['test_count']}")

        print("\n" + "=" * 60)


async def main():
    """Main entry point."""
    benchmark = LLMBenchmark()
    benchmark.load_config()
    report = await benchmark.run_benchmark()
    benchmark.print_summary(report)
    report_file = benchmark.save_report(report)
    print(f"\n💾 Report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
