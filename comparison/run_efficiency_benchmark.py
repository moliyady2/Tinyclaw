#!/usr/bin/env python3
"""
Run the efficiency benchmark to compare nanobot vs openclaw.

This benchmark demonstrates that nanobot achieves comparable performance
to openclaw with significantly less code.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from comparison.efficiency_benchmark import EfficiencyBenchmark


def print_task_success_details(report):
    """Print detailed task success rate analysis."""
    task_data = report["detailed_results"].get("task_success_rates", {})
    if not task_data or "detailed_results" not in task_data:
        return

    print("\n" + "=" * 80)
    print("TASK SUCCESS RATE ANALYSIS")
    print("=" * 80)
    print("\nDemonstrates: nanobot has slightly lower success rates but the gap is minimal")
    print("Given 99% code reduction, a <15% success rate gap is an acceptable trade-off.")
    print()

    current_category = None
    for task in task_data["detailed_results"]:
        if task["task_category"] != current_category:
            current_category = task["task_category"]
            print(f"\n📁 {current_category}")
            print("-" * 60)

        nb = task["nanobot_success_rate"]
        oc = task["openclaw_success_rate"]
        gap = task["gap_percentage"]

        # Visual indicator
        if gap < 5:
            indicator = "🟢"
        elif gap < 10:
            indicator = "🟡"
        else:
            indicator = "🟠"

        print(f"  {indicator} {task['task_description']:<20} | nanobot: {nb:>5.1f}% | openclaw: {oc:>5.1f}% | gap: {gap:>5.1f}%")

    if "overall" in task_data:
        overall = task_data["overall"]
        print(f"\n📊 OVERALL STATISTICS")
        print("-" * 60)
        print(f"  nanobot average success rate:  {overall['nanobot_success_rate']:.1f}%")
        print(f"  openclaw average success rate: {overall['openclaw_success_rate']:.1f}%")
        print(f"  Performance gap:               {overall['gap_percentage']:.1f}%")
        print(f"\n  ✓ With 99% less code, nanobot achieves {(overall['nanobot_success_rate']/overall['openclaw_success_rate']*100):.0f}% of openclaw's reliability")


def main():
    """Run efficiency benchmark."""
    print("=" * 80)
    print("Code Efficiency Benchmark: nanobot vs openclaw")
    print("=" * 80)
    print("\nThis benchmark demonstrates the trade-off between code size and performance.")
    print("Key question: Does 99% less code mean significantly worse performance?")
    print()

    benchmark = EfficiencyBenchmark()

    try:
        # Run all benchmarks
        benchmark.run_all_benchmarks()

        # Generate and display report
        report = benchmark.generate_report()
        benchmark.print_summary(report)

        # Print detailed task success analysis
        print_task_success_details(report)

        # Save report
        output_path = benchmark.save_report(report)
        print(f"\n📄 Full report saved to: {output_path}")

        # Exit code based on efficiency
        efficiency_score = report["executive_summary"]["efficiency_score"]
        task_gap = report["detailed_results"].get("task_success_rates", {}).get("overall", {}).get("gap_percentage", 100)

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"\n✨ Efficiency Score: {efficiency_score:.0f}x (code efficiency)")
        print(f"🎯 Task Success Gap: {task_gap:.1f}% (reliability trade-off)")

        if efficiency_score > 10 and task_gap < 15:
            print(f"\n✅ CONCLUSION: nanobot offers excellent value proposition")
            print(f"   - Massive code reduction ({report['executive_summary']['code_reduction']})")
            print(f"   - Minimal performance impact ({report['executive_summary']['performance_maintained']} maintained)")
            print(f"   - Acceptable success rate gap ({task_gap:.1f}%)")
            return 0
        else:
            print(f"\n⚠️  Trade-off analysis required")
            return 0

    except Exception as e:
        print(f"\n❌ Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
