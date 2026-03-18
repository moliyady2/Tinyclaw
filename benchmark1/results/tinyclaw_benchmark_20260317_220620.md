# Tinyclaw Performance Benchmark Report

**Generated:** 2026-03-17T22:06:08.226034

**Version:** 0.1.0

## Test Environment

- **Python:** 3.13.9
- **Platform:** Windows-11-10.0.26200-SP0
- **CPU Count:** 24

## Summary

### Tool Benchmark

- **Total Tests:** 41
- **Successful:** 38
- **Failed:** 3
- **Success Rate:** 92.7%

#### Performance by Tool

| Tool | Count | Avg (ms) | Min (ms) | Max (ms) | Median (ms) | Success Rate |
|------|-------|----------|----------|----------|-------------|--------------|
| write_file | 5 | 3.38 | 1.03 | 12.50 | 1.10 | 100.0% |
| read_file | 5 | 0.77 | 0.71 | 0.90 | 0.75 | 100.0% |
| list_dir | 5 | 0.68 | 0.64 | 0.75 | 0.67 | 100.0% |
| edit_file | 5 | 0.69 | 0.67 | 0.72 | 0.68 | 100.0% |
| exec | 12 | 27.42 | 15.68 | 46.40 | 24.58 | 100.0% |
| web_fetch | 6 | 1749.27 | 1364.40 | 2393.62 | 1489.78 | 50.0% |
| concurrent | 3 | 0.17 | 0.14 | 0.22 | 0.16 | 100.0% |

## Detailed Results

### Tool Execution Details

| Tool | Operation | Time (ms) | Success | Error |
|------|-----------|-----------|---------|-------|
| write_file | write_1 | 12.50 | True |  |
| write_file | write_2 | 1.21 | True |  |
| write_file | write_3 | 1.10 | True |  |
| write_file | write_4 | 1.03 | True |  |
| write_file | write_5 | 1.05 | True |  |
| read_file | read_1 | 0.78 | True |  |
| read_file | read_2 | 0.75 | True |  |
| read_file | read_3 | 0.90 | True |  |
| read_file | read_4 | 0.71 | True |  |
| read_file | read_5 | 0.71 | True |  |
| list_dir | list_1 | 0.69 | True |  |
| list_dir | list_2 | 0.66 | True |  |
| list_dir | list_3 | 0.67 | True |  |
| list_dir | list_4 | 0.75 | True |  |
| list_dir | list_5 | 0.64 | True |  |
| edit_file | edit_1 | 0.72 | True |  |
| edit_file | edit_2 | 0.69 | True |  |
| edit_file | edit_3 | 0.68 | True |  |
| edit_file | edit_4 | 0.67 | True |  |
| edit_file | edit_5 | 0.67 | True |  |
| exec | echo_1 | 20.98 | True |  |
| exec | echo_2 | 18.46 | True |  |
| exec | echo_3 | 18.31 | True |  |
| exec | ls_1 | 15.95 | True |  |
| exec | ls_2 | 15.68 | True |  |
| exec | ls_3 | 17.16 | True |  |
| exec | python_version_1 | 29.67 | True |  |
| exec | python_version_2 | 28.49 | True |  |
| exec | python_version_3 | 28.17 | True |  |
| exec | simple_math_1 | 44.75 | True |  |
| exec | simple_math_2 | 46.40 | True |  |
| exec | simple_math_3 | 44.99 | True |  |
| web_fetch | httpbin_get_1 | 1364.40 | True |  |
| web_fetch | httpbin_get_2 | 2393.62 | True |  |
| web_fetch | httpbin_get_3 | 1489.78 | True |  |
| web_fetch | example_1 | 638.57 | False | {"error": "[SSL: CERTIFICATE_V... |
| web_fetch | example_2 | 3559.64 | False | {"error": "[SSL: CERTIFICATE_V... |
| web_fetch | example_3 | 1899.80 | False | {"error": "[SSL: CERTIFICATE_V... |
| concurrent | concurrent_10_1 | 0.22 | True |  |
| concurrent | concurrent_10_2 | 0.16 | True |  |
| concurrent | concurrent_10_3 | 0.14 | True |  |
