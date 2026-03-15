---
name: http
description: Make HTTP requests and test APIs using curl. Use for REST API testing, webhook debugging, downloading files, and inspecting HTTP responses.
metadata: {"nanobot":{"emoji":"🌐","requires":{"bins":["curl"]}}}
---

# HTTP Skill

Use `curl` for HTTP requests and API testing. Prefer curl for its ubiquity and detailed output control.

## Quick Reference

| Task | Command |
|------|---------|
| GET request | `curl https://api.example.com/users` |
| POST JSON | `curl -X POST -H "Content-Type: application/json" -d '{"key":"val"}' URL` |
| Save response | `curl -o file.json URL` |
| Follow redirects | `curl -L URL` |
| View headers | `curl -I URL` |
| Verbose output | `curl -v URL` |

## Basic Requests

```bash
# Simple GET
curl https://api.github.com/users/octocat

# Save to file
curl -o data.json https://api.example.com/data
curl -O https://example.com/file.zip  # keep original filename

# Follow redirects
curl -L https://bit.ly/xxx

# Silent mode (no progress bar)
curl -s https://api.example.com/status
```

## Methods & Data

```bash
# POST with JSON
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com"}'

# POST with form data
curl -X POST https://api.example.com/upload \
  -F "file=@document.pdf" \
  -F "name=My Document"

# PUT request
curl -X PUT https://api.example.com/users/123 \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane"}'

# DELETE request
curl -X DELETE https://api.example.com/users/123

# PATCH request
curl -X PATCH https://api.example.com/users/123 \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}'
```

## Headers & Authentication

```bash
# Custom headers
curl -H "Authorization: Bearer token123" \
     -H "X-API-Version: 2" \
     https://api.example.com/data

# Basic auth
curl -u username:password https://api.example.com/protected

# API key in header
curl -H "X-API-Key: your-key-here" https://api.example.com/data

# User agent
curl -A "MyApp/1.0" https://api.example.com/data
```

## Inspecting Responses

```bash
# View response headers only
curl -I https://api.example.com/users

# View request and response headers (verbose)
curl -v https://api.example.com/users

# Show headers and body
curl -i https://api.example.com/users

# Write headers to file
curl -D headers.txt https://api.example.com/users
```

## JSON Handling

```bash
# Pretty print JSON response
curl -s https://api.github.com/users/octocat | python -m json.tool
curl -s https://api.github.com/users/octocat | jq '.'

# Send JSON from file
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d @user.json

# Extract specific field with jq
curl -s https://api.github.com/users/octocat | jq '.login, .id'
```

## Query Parameters

```bash
# URL with query string (quote to prevent shell expansion)
curl "https://api.example.com/search?q=hello+world&limit=10"

# URL encode parameters
curl "https://api.example.com/search?q=$(echo 'hello world' | jq -sRr @uri)"
```

## Timeouts & Retries

```bash
# Set timeout (seconds)
curl --max-time 30 https://api.example.com/slow-endpoint
curl --connect-timeout 10 https://api.example.com

# Retry on failure
curl --retry 3 --retry-delay 2 https://api.example.com/flaky
```

## Downloading Files

```bash
# Resume interrupted download
curl -C - -o large-file.zip https://example.com/file.zip

# Limit download speed
curl --limit-rate 1M -o file.zip https://example.com/file.zip

# Download multiple files
curl -O https://example.com/file1.zip \
     -O https://example.com/file2.zip
```

## Common Patterns

### Test API Health
```bash
curl -s -o /dev/null -w "%{http_code}" https://api.example.com/health
```

### Check Redirect Chain
```bash
curl -sIL https://bit.ly/xxx | grep -i "location\|http/"
```

### Measure Response Time
```bash
curl -s -o /dev/null -w "Total: %{time_total}s\nConnect: %{time_connect}s\n" URL
```

### POST with Heredoc
```bash
curl -X POST https://api.example.com/data \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "name": "test",
  "value": 123
}
EOF
```

## Tips

- Always quote URLs with query parameters
- Use `-s` for silent mode in scripts
- Use `-f` to fail on HTTP errors (exit code 22)
- Use `-S` with `-s` to show errors even in silent mode
- Combine: `curl -fsS` for script-friendly silent mode with error reporting
