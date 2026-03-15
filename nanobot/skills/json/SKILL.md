---
name: json
description: Process and manipulate JSON data using jq and Python. Use for filtering, transforming, querying, and formatting JSON files and API responses.
metadata: {"nanobot":{"emoji":"📋","requires":{"bins":["jq"]}}}
---

# JSON Skill

Use `jq` for JSON processing. Fallback to Python's `json` module for complex operations.

## Quick Reference

| Task | Command |
|------|---------|
| Pretty print | `cat file.json \| jq '.'` |
| Get field | `jq '.name' file.json` |
| Get nested | `jq '.user.email' file.json` |
| Array element | `jq '.items[0]' file.json` |
| Filter array | `jq '.users[] \| select(.age > 18)' file.json` |
| Transform | `jq '{new: .old}' file.json` |

## Basic Operations

```bash
# Pretty print JSON
cat data.json | jq '.'
echo '{"a":1,"b":2}' | jq '.'

# Read from file
jq '.' data.json

# Compact output (one line)
jq -c '.' data.json

# Raw output (no quotes)
jq -r '.name' data.json

# Sort keys
jq -S '.' data.json
```

## Extracting Data

```bash
# Get top-level field
jq '.name' user.json

# Get nested field
jq '.address.city' user.json

# Get array element
jq '.items[0]' data.json
jq '.items[-1]' data.json  # last element

# Get multiple fields
jq '.name, .email' user.json

# Array slicing
jq '.items[0:3]' data.json  # first 3 elements

# All array elements
jq '.items[]' data.json

# Array length
jq '.items | length' data.json
```

## Filtering Arrays

```bash
# Select by condition
jq '.users[] | select(.age >= 18)' data.json

# Select with multiple conditions
jq '.users[] | select(.age > 18 and .active == true)' data.json

# Select contains string
jq '.items[] | select(.name | contains("test"))' data.json

# Select by regex
jq '.users[] | select(.email | test("@gmail.com$"))' data.json

# Reject (opposite of select)
jq '.users[] | select(.active != false)' data.json
```

## Transforming Data

```bash
# Create new structure
jq '{username: .name, user_email: .email}' user.json

# Map over array
jq '.items | map(.price * 1.1)' data.json

# Map and select
jq '.users | map(select(.active) | .name)' data.json

# Group by
jq '.items | group_by(.category)' data.json

# Unique values
jq '.items | map(.category) | unique' data.json

# Flatten nested arrays
jq '.data | flatten' nested.json
```

## Aggregation

```bash
# Count elements
jq '.items | length' data.json

# Sum values
jq '.items | map(.price) | add' data.json

# Average
jq '.items | map(.price) | add / length' data.json

# Min/Max
jq '.items | map(.price) | min' data.json
jq '.items | map(.price) | max' data.json

# Any/All
jq '.items | map(.active) | any' data.json
jq '.items | map(.active) | all' data.json
```

## String Operations

```bash
# Concatenate
jq '{fullname: (.first + " " + .last)}' user.json

# Uppercase/Lowercase
jq '.name | ascii_upcase' user.json
jq '.name | ascii_downcase' user.json

# Split/Join
jq '.tags | split(", ")' data.json
jq '.items | join(", ")' data.json

# Substring
jq '.name[0:3]' user.json  # first 3 characters

# Replace
jq '.description | gsub("old"; "new")' data.json
```

## Conditional Logic

```bash
# If-then-else
jq '.age | if . >= 18 then "adult" else "minor" end' user.json

# Multiple conditions
jq 'if .status == "active" then "✓" elif .status == "pending" then "⏳" else "✗" end' data.json

# Default values
jq '.nickname // .name' user.json  # use name if nickname is null
jq '.count // 0' data.json         # default to 0
```

## Working with Arrays

```bash
# Add element
jq '.items + [{"name": "new"}]' data.json

# Remove element by index
jq 'del(.items[1])' data.json

# Remove field from all objects
jq '.items | map(del(.password))' data.json

# Sort
jq '.items | sort_by(.price)' data.json
jq '.items | sort_by(.name) | reverse' data.json

# Limit results
jq '.items[:10]' data.json  # first 10
jq '.items[-5:]' data.json  # last 5
```

## Python Fallback

For operations too complex for jq:

```bash
# Pretty print with Python
python -m json.tool data.json
python -c "import json,sys; print(json.dumps(json.load(sys.stdin), indent=2))" < data.json

# Complex transformation
python3 << 'EOF'
import json
with open('data.json') as f:
    data = json.load(f)
    
# Complex processing
result = [item for item in data['items'] if item['price'] > 100]
result.sort(key=lambda x: x['date'], reverse=True)

print(json.dumps(result, indent=2))
EOF
```

## Common Patterns

### Extract Specific Fields from Array
```bash
jq '.users[] | {name: .name, email: .email}' data.json
```

### Convert Array to Object
```bash
jq 'map({(.id): .name}) | add' users.json
```

### Merge Objects
```bash
jq -s '.[0] * .[1]' file1.json file2.json
```

### Remove Null Values
```bash
jq 'walk(if type == "object" then with_entries(select(.value != null)) else . end)' data.json
```

### Convert CSV to JSON (with Python)
```bash
python3 -c "import csv,json,sys; print(json.dumps(list(csv.DictReader(sys.stdin)), indent=2))" < data.csv
```

## Tips

- Use single quotes around jq expressions to prevent shell expansion
- Use `-r` for raw string output (removes quotes)
- Chain filters with `|` like Unix pipes
- Use `?` for optional field access: `.field?.subfield`
- Test complex queries on small samples first
