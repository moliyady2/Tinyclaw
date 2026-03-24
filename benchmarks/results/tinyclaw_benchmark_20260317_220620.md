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

| Tool        | Count | Avg (ms) | Min (ms) | Max (ms) | Median (ms) | Success Rate |
| ----------- | ----- | -------- | -------- | -------- | ----------- | ------------ |
| write\_file | 5     | 3.38     | 1.03     | 12.50    | 1.10        | 100.0%       |
| read\_file  | 5     | 0.77     | 0.71     | 0.90     | 0.75        | 100.0%       |
| list\_dir   | 5     | 0.68     | 0.64     | 0.75     | 0.67        | 100.0%       |
| edit\_file  | 5     | 0.69     | 0.67     | 0.72     | 0.68        | 100.0%       |
| exec        | 12    | 27.42    | 15.68    | 46.40    | 24.58       | 100.0%       |
| web\_fetch  | 6     | 1749.27  | 1364.40  | 2393.62  | 1489.78     | 50.0%        |
| concurrent  | 3     | 0.17     | 0.14     | 0.22     | 0.16        | 100.0%       |

## Detailed Results

### Tool Execution Details

| Tool        | Operation          | Time (ms) | Success | Error                               |
| ----------- | ------------------ | --------- | ------- | ----------------------------------- |
| write\_file | write\_1           | 12.50     | True    | <br />                              |
| write\_file | write\_2           | 1.21      | True    | <br />                              |
| write\_file | write\_3           | 1.10      | True    | <br />                              |
| write\_file | write\_4           | 1.03      | True    | <br />                              |
| write\_file | write\_5           | 1.05      | True    | <br />                              |
| read\_file  | read\_1            | 0.78      | True    | <br />                              |
| read\_file  | read\_2            | 0.75      | True    | <br />                              |
| read\_file  | read\_3            | 0.90      | True    | <br />                              |
| read\_file  | read\_4            | 0.71      | True    | <br />                              |
| read\_file  | read\_5            | 0.71      | True    | <br />                              |
| list\_dir   | list\_1            | 0.69      | True    | <br />                              |
| list\_dir   | list\_2            | 0.66      | True    | <br />                              |
| list\_dir   | list\_3            | 0.67      | True    | <br />                              |
| list\_dir   | list\_4            | 0.75      | True    | <br />                              |
| list\_dir   | list\_5            | 0.64      | True    | <br />                              |
| edit\_file  | edit\_1            | 0.72      | True    | <br />                              |
| edit\_file  | edit\_2            | 0.69      | True    | <br />                              |
| edit\_file  | edit\_3            | 0.68      | True    | <br />                              |
| edit\_file  | edit\_4            | 0.67      | True    | <br />                              |
| edit\_file  | edit\_5            | 0.67      | True    | <br />                              |
| exec        | echo\_1            | 20.98     | True    | <br />                              |
| exec        | echo\_2            | 18.46     | True    | <br />                              |
| exec        | echo\_3            | 18.31     | True    | <br />                              |
| exec        | ls\_1              | 15.95     | True    | <br />                              |
| exec        | ls\_2              | 15.68     | True    | <br />                              |
| exec        | ls\_3              | 17.16     | True    | <br />                              |
| exec        | python\_version\_1 | 29.67     | True    | <br />                              |
| exec        | python\_version\_2 | 28.49     | True    | <br />                              |
| exec        | python\_version\_3 | 28.17     | True    | <br />                              |
| exec        | simple\_math\_1    | 44.75     | True    | <br />                              |
| exec        | simple\_math\_2    | 46.40     | True    | <br />                              |
| exec        | simple\_math\_3    | 44.99     | True    | <br />                              |
| web\_fetch  | httpbin\_get\_1    | 1364.40   | True    | <br />                              |
| web\_fetch  | httpbin\_get\_2    | 2393.62   | True    | <br />                              |
| web\_fetch  | httpbin\_get\_3    | 1489.78   | True    | <br />                              |
| web\_fetch  | example\_1         | 638.57    | False   | {"error": "\[SSL: CERTIFICATE\_V... |
| web\_fetch  | example\_2         | 3559.64   | False   | {"error": "\[SSL: CERTIFICATE\_V... |
| web\_fetch  | example\_3         | 1899.80   | False   | {"error": "\[SSL: CERTIFICATE\_V... |
| concurrent  | concurrent\_10\_1  | 0.22      | True    | <br />                              |
| concurrent  | concurrent\_10\_2  | 0.16      | True    | <br />                              |
| concurrent  | concurrent\_10\_3  | 0.14      | True    | <br />                              |

