#!/usr/bin/env python3
"""
Tinyclaw Benchmark 报告生成器

生成 HTML/Markdown 格式的可视化报告

用法:
    python perf/report_generator.py [benchmark_result.json]
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any


def generate_markdown_report(data: dict[str, Any], output_path: Path) -> str:
    """生成 Markdown 格式报告"""
    
    lines = []
    
    # 标题
    lines.append("# Tinyclaw Performance Benchmark Report\n")
    lines.append(f"**Generated:** {data.get('timestamp', 'N/A')}\n")
    lines.append(f"**Version:** {data.get('tinyclaw_version', 'unknown')}\n")
    
    # 环境信息
    env = data.get('test_environment', {})
    lines.append("## Test Environment\n")
    lines.append(f"- **Python:** {env.get('python_version', 'N/A').split()[0]}")
    lines.append(f"- **Platform:** {env.get('platform', 'N/A')}")
    lines.append(f"- **CPU Count:** {env.get('cpu_count', 'N/A')}")
    lines.append("")
    
    # 汇总
    summary = data.get('summary', {})
    lines.append("## Summary\n")
    
    # 工具测试汇总
    tool_summary = summary.get('tool_benchmark', {})
    if tool_summary.get('status') != 'not_run':
        lines.append("### Tool Benchmark\n")
        lines.append(f"- **Total Tests:** {tool_summary.get('total_tests', 0)}")
        lines.append(f"- **Successful:** {tool_summary.get('successful', 0)}")
        lines.append(f"- **Failed:** {tool_summary.get('failed', 0)}")
        lines.append(f"- **Success Rate:** {tool_summary.get('successful', 0) / tool_summary.get('total_tests', 1) * 100:.1f}%")
        lines.append("")
        
        lines.append("#### Performance by Tool\n")
        lines.append("| Tool | Count | Avg (ms) | Min (ms) | Max (ms) | Median (ms) | Success Rate |")
        lines.append("|------|-------|----------|----------|----------|-------------|--------------|")
        
        for tool_name, stats in tool_summary.get('by_tool', {}).items():
            lines.append(
                f"| {tool_name} | {stats['count']} | "
                f"{stats['avg_time_ms']:.2f} | {stats['min_time_ms']:.2f} | "
                f"{stats['max_time_ms']:.2f} | {stats['median_time_ms']:.2f} | "
                f"{stats['success_rate']*100:.1f}% |"
            )
        lines.append("")
    
    # LLM 测试汇总
    llm_summary = summary.get('llm_benchmark', {})
    if llm_summary.get('status') != 'not_run':
        lines.append("### LLM Benchmark\n")
        lines.append(f"- **Total Tests:** {llm_summary.get('total_tests', 0)}")
        lines.append(f"- **Successful:** {llm_summary.get('successful', 0)}")
        lines.append(f"- **Failed:** {llm_summary.get('failed', 0)}")
        lines.append(f"- **Success Rate:** {llm_summary.get('successful', 0) / llm_summary.get('total_tests', 1) * 100:.1f}%")
        lines.append("")
        
        lines.append("#### Performance by Provider\n")
        lines.append("| Provider | Count | Avg Response (ms) | Tokens/s | Avg Tokens | Success Rate |")
        lines.append("|----------|-------|-------------------|----------|------------|--------------|")
        
        for provider, stats in llm_summary.get('by_provider', {}).items():
            lines.append(
                f"| {provider} | {stats['count']} | "
                f"{stats['avg_response_time_ms']:.2f} | {stats['avg_tokens_per_second']:.2f} | "
                f"{stats['avg_total_tokens']:.0f} | {stats['success_rate']*100:.1f}% |"
            )
        lines.append("")
    
    # 端到端测试汇总
    e2e_summary = summary.get('end_to_end_benchmark', {})
    if e2e_summary.get('status') != 'not_run':
        lines.append("### End-to-End Benchmark\n")
        lines.append(f"- **Total Tests:** {e2e_summary.get('total_tests', 0)}")
        lines.append(f"- **Successful:** {e2e_summary.get('successful', 0)}")
        lines.append(f"- **Failed:** {e2e_summary.get('failed', 0)}")
        lines.append("")
        
        lines.append("#### Performance by Category\n")
        lines.append("| Category | Count | Avg Time (ms) |")
        lines.append("|----------|-------|---------------|")
        
        for category, stats in e2e_summary.get('by_category', {}).items():
            lines.append(f"| {category} | {stats['count']} | {stats['avg_time_ms']:.2f} |")
        lines.append("")
    
    # 详细结果
    lines.append("## Detailed Results\n")
    
    # 工具详细结果
    tool_results = data.get('tool_results', [])
    if tool_results:
        lines.append("### Tool Execution Details\n")
        lines.append("| Tool | Operation | Time (ms) | Success | Error |")
        lines.append("|------|-----------|-----------|---------|-------|")
        
        for result in tool_results[:50]:  # 限制显示前50条
            error = result.get('error_message', '')
            error_short = error[:30] + '...' if len(error) > 30 else error
            lines.append(
                f"| {result.get('tool_name', 'N/A')} | {result.get('operation', 'N/A')} | "
                f"{result.get('total_time_ms', 0):.2f} | {result.get('success', False)} | "
                f"{error_short} |"
            )
        lines.append("")
    
    # LLM 详细结果
    llm_results = data.get('llm_results', [])
    if llm_results:
        lines.append("### LLM Call Details\n")
        lines.append("| Provider | Model | Operation | Response (ms) | Tokens/s | Total Tokens | Success |")
        lines.append("|----------|-------|-----------|---------------|----------|--------------|---------|")
        
        for result in llm_results[:50]:  # 限制显示前50条
            lines.append(
                f"| {result.get('provider', 'N/A')} | {result.get('model', 'N/A')} | "
                f"{result.get('operation', 'N/A')} | {result.get('response_time_ms', 0):.2f} | "
                f"{result.get('tokens_per_second', 0):.2f} | {result.get('total_tokens', 0)} | "
                f"{result.get('success', False)} |"
            )
        lines.append("")
    
    # 写入文件
    content = '\n'.join(lines)
    output_path.write_text(content, encoding='utf-8')
    return content


def generate_html_report(data: dict[str, Any], output_path: Path) -> str:
    """生成 HTML 格式报告"""
    
    env = data.get('test_environment', {})
    summary = data.get('summary', {})
    
    # 工具测试数据
    tool_summary = summary.get('tool_benchmark', {})
    tool_data = tool_summary.get('by_tool', {})
    
    # LLM 测试数据
    llm_summary = summary.get('llm_benchmark', {})
    llm_data = llm_summary.get('by_provider', {})
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tinyclaw Benchmark Report</title>
    <style>
        :root {{
            --primary: #2563eb;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --bg: #f8fafc;
            --card: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            background: var(--card);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        h1 {{ color: var(--primary); margin-bottom: 0.5rem; }}
        .meta {{ color: var(--text-muted); font-size: 0.9rem; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background: var(--card);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            font-size: 1.1rem;
            color: var(--text-muted);
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-value {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary);
        }}
        .metric-label {{ color: var(--text-muted); }}
        .success {{ color: var(--success); }}
        .danger {{ color: var(--danger); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            font-weight: 600;
            color: var(--text-muted);
            font-size: 0.85rem;
            text-transform: uppercase;
        }}
        tr:hover {{ background: #f8fafc; }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-success {{ background: #d1fae5; color: #065f46; }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        .section {{
            background: var(--card);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        .section h2 {{
            color: var(--primary);
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }}
        .chart-container {{
            height: 300px;
            margin: 1rem 0;
        }}
        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Tinyclaw Performance Benchmark</h1>
            <div class="meta">
                Generated: {data.get('timestamp', 'N/A')} | 
                Version: {data.get('tinyclaw_version', 'unknown')} | 
                Python: {env.get('python_version', 'N/A').split()[0]}
            </div>
        </header>
"""
    
    # 概览卡片
    html += """
        <div class="grid">
"""
    
    # 工具测试概览
    if tool_summary.get('status') != 'not_run':
        success_rate = tool_summary.get('successful', 0) / max(tool_summary.get('total_tests', 1), 1) * 100
        html += f"""
            <div class="card">
                <h2>🔧 Tool Benchmark</h2>
                <div class="metric">
                    <span class="metric-label">Total Tests</span>
                    <span class="metric-value">{tool_summary.get('total_tests', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Success Rate</span>
                    <span class="metric-value {'success' if success_rate >= 95 else 'danger'}">{success_rate:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Successful</span>
                    <span class="metric-value success">{tool_summary.get('successful', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Failed</span>
                    <span class="metric-value {'danger' if tool_summary.get('failed', 0) > 0 else ''}">{tool_summary.get('failed', 0)}</span>
                </div>
            </div>
"""
    
    # LLM 测试概览
    if llm_summary.get('status') != 'not_run':
        success_rate = llm_summary.get('successful', 0) / max(llm_summary.get('total_tests', 1), 1) * 100
        html += f"""
            <div class="card">
                <h2>🤖 LLM Benchmark</h2>
                <div class="metric">
                    <span class="metric-label">Total Tests</span>
                    <span class="metric-value">{llm_summary.get('total_tests', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Success Rate</span>
                    <span class="metric-value {'success' if success_rate >= 95 else 'danger'}">{success_rate:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Providers</span>
                    <span class="metric-value">{len(llm_data)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Failed</span>
                    <span class="metric-value {'danger' if llm_summary.get('failed', 0) > 0 else ''}">{llm_summary.get('failed', 0)}</span>
                </div>
            </div>
"""
    
    # 端到端测试概览
    e2e_summary = summary.get('end_to_end_benchmark', {})
    if e2e_summary.get('status') != 'not_run':
        html += f"""
            <div class="card">
                <h2>🔄 End-to-End Benchmark</h2>
                <div class="metric">
                    <span class="metric-label">Total Tests</span>
                    <span class="metric-value">{e2e_summary.get('total_tests', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Successful</span>
                    <span class="metric-value success">{e2e_summary.get('successful', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Failed</span>
                    <span class="metric-value {'danger' if e2e_summary.get('failed', 0) > 0 else ''}">{e2e_summary.get('failed', 0)}</span>
                </div>
            </div>
"""
    
    html += """
        </div>
"""
    
    # 工具测试详细表格
    if tool_data:
        html += """
        <div class="section">
            <h2>🔧 Tool Performance Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Tool</th>
                        <th>Count</th>
                        <th>Avg (ms)</th>
                        <th>Min (ms)</th>
                        <th>Max (ms)</th>
                        <th>Median (ms)</th>
                        <th>Success Rate</th>
                    </tr>
                </thead>
                <tbody>
"""
        for tool_name, stats in tool_data.items():
            success_class = 'success' if stats['success_rate'] >= 0.95 else 'danger' if stats['success_rate'] < 0.8 else ''
            html += f"""
                    <tr>
                        <td><strong>{tool_name}</strong></td>
                        <td>{stats['count']}</td>
                        <td>{stats['avg_time_ms']:.2f}</td>
                        <td>{stats['min_time_ms']:.2f}</td>
                        <td>{stats['max_time_ms']:.2f}</td>
                        <td>{stats['median_time_ms']:.2f}</td>
                        <td><span class="badge badge-{success_class}">{stats['success_rate']*100:.1f}%</span></td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </div>
"""
    
    # LLM 测试详细表格
    if llm_data:
        html += """
        <div class="section">
            <h2>🤖 LLM Performance Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Provider</th>
                        <th>Count</th>
                        <th>Avg Response (ms)</th>
                        <th>Tokens/s</th>
                        <th>Avg Tokens</th>
                        <th>Success Rate</th>
                    </tr>
                </thead>
                <tbody>
"""
        for provider, stats in llm_data.items():
            success_class = 'success' if stats['success_rate'] >= 0.95 else 'danger' if stats['success_rate'] < 0.8 else ''
            html += f"""
                    <tr>
                        <td><strong>{provider}</strong></td>
                        <td>{stats['count']}</td>
                        <td>{stats['avg_response_time_ms']:.2f}</td>
                        <td>{stats['avg_tokens_per_second']:.2f}</td>
                        <td>{stats['avg_total_tokens']:.0f}</td>
                        <td><span class="badge badge-{success_class}">{stats['success_rate']*100:.1f}%</span></td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </div>
"""
    
    # 端到端测试详细表格
    e2e_categories = e2e_summary.get('by_category', {})
    if e2e_categories:
        html += """
        <div class="section">
            <h2>🔄 End-to-End Performance Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Count</th>
                        <th>Avg Time (ms)</th>
                    </tr>
                </thead>
                <tbody>
"""
        for category, stats in e2e_categories.items():
            html += f"""
                    <tr>
                        <td><strong>{category}</strong></td>
                        <td>{stats['count']}</td>
                        <td>{stats['avg_time_ms']:.2f}</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </div>
"""
    
    # 环境信息
    html += f"""
        <div class="section">
            <h2>🖥️ Environment Information</h2>
            <pre>{json.dumps(env, indent=2, default=str)}</pre>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    output_path.write_text(html, encoding='utf-8')
    return html


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 查找最新的 benchmark 结果
        results_dir = Path("benchmark2/results")
        if not results_dir.exists():
            print("Error: No benchmark results found")
            sys.exit(1)
        
        json_files = sorted(results_dir.glob("tinyclaw_benchmark_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not json_files:
            print("Error: No benchmark results found")
            sys.exit(1)
        
        input_file = json_files[0]
        print(f"Using latest benchmark result: {input_file}")
    else:
        input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    # 读取 benchmark 结果
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 生成报告
    base_name = input_file.stem
    output_dir = input_file.parent
    
    # Markdown 报告
    md_path = output_dir / f"{base_name}.md"
    generate_markdown_report(data, md_path)
    print(f"Generated Markdown report: {md_path}")
    
    # HTML 报告
    html_path = output_dir / f"{base_name}.html"
    generate_html_report(data, html_path)
    print(f"Generated HTML report: {html_path}")


if __name__ == "__main__":
    main()
