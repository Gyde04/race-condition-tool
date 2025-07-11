# Race Condition Security Tool

A comprehensive security tool for detecting and analyzing race conditions in code. This tool helps identify potential race conditions that could lead to security vulnerabilities, data corruption, or unexpected behavior in concurrent applications.

## Features

- **Multi-language Support**: Detects race conditions in Python, JavaScript, TypeScript, Java, C++, C, Go, and Rust
- **Multiple Detection Types**:
  - File operation race conditions
  - Variable modification race conditions
  - Database operation race conditions
  - Threading synchronization issues
  - Missing locks in concurrent code
- **Comprehensive Reporting**: Generate detailed reports in JSON or text format
- **Severity Classification**: Categorizes issues by severity (HIGH, MEDIUM, LOW)
- **Actionable Recommendations**: Provides specific guidance for fixing detected issues

## Installation

No external dependencies required - uses only Python standard library.

```bash
# Make the tool executable
chmod +x race_condition_detector.py
```

## Usage

### Basic Usage

```bash
# Scan a single file
python race_condition_detector.py path/to/file.py

# Scan an entire directory
python race_condition_detector.py path/to/directory/

# Generate text report instead of JSON
python race_condition_detector.py path/to/file.py --format text

# Specify output file
python race_condition_detector.py path/to/file.py --output my_report.json

# Verbose output
python race_condition_detector.py path/to/file.py --verbose
```

### Command Line Options

- `path`: File or directory to scan (required)
- `--output, -o`: Output file path (default: report.json)
- `--format, -f`: Output format - json or text (default: json)
- `--verbose, -v`: Enable verbose logging

## Types of Race Conditions Detected

### 1. File Operation Races
Detects file operations (read/write) without proper synchronization:
```python
# Example of problematic code
with open('file.txt', 'a') as f:
    f.write(data)  # Race condition if multiple threads access
```

### 2. Variable Races
Detects variable modifications in threaded contexts without synchronization:
```python
# Example of problematic code
counter += 1  # Race condition in threaded context
```

### 3. Database Races
Detects database operations without proper transaction handling:
```python
# Example of problematic code
cursor.execute("UPDATE accounts SET balance = balance + 100")
```

### 4. Threading Races
Detects threading operations without proper synchronization:
```python
# Example of problematic code
thread = threading.Thread(target=worker)
thread.start()  # No coordination between threads
```

### 5. Missing Locks
Detects shared resource access without proper locking:
```python
# Example of problematic code
shared_list.append(item)  # No lock protection
```

## Example Output

### JSON Report
```json
{
  "summary": {
    "total_conditions": 3,
    "high_severity": 2,
    "medium_severity": 1,
    "low_severity": 0
  },
  "conditions": [
    {
      "file_path": "example.py",
      "line_number": 15,
      "race_type": "File Operation Race",
      "description": "File operation detected without proper synchronization",
      "severity": "HIGH",
      "code_snippet": "f.write(data)",
      "recommendations": [
        "Use file locking mechanisms",
        "Implement proper error handling",
        "Consider using atomic operations",
        "Add retry logic with exponential backoff"
      ]
    }
  ]
}
```

### Text Report
```
Race Condition Security Report
==================================================

Total conditions found: 3
High severity: 2
Medium severity: 1
Low severity: 0

File: example.py:15
Type: File Operation Race
Severity: HIGH
Description: File operation detected without proper synchronization
Code: f.write(data)
Recommendations:
  - Use file locking mechanisms
  - Implement proper error handling
  - Consider using atomic operations
  - Add retry logic with exponential backoff
```

## Testing the Tool

The `test_examples.py` file contains various examples of race conditions for testing:

```bash
# Test the detector on the example file
python race_condition_detector.py test_examples.py --format text
```

## Best Practices for Avoiding Race Conditions

### 1. Use Proper Locking
```python
import threading

lock = threading.Lock()

def safe_operation():
    with lock:
        # Critical section
        shared_variable += 1
```

### 2. Use Thread-Safe Data Structures
```python
from queue import Queue
from threading import Lock

# Thread-safe queue
queue = Queue()

# Thread-safe list with lock
safe_list = []
list_lock = Lock()
```

### 3. Use Atomic Operations
```python
import threading

# Atomic counter
counter = threading.Value('i', 0)

def increment():
    with counter.get_lock():
        counter.value += 1
```

### 4. Use Database Transactions
```python
import sqlite3

def safe_database_operation():
    conn = sqlite3.connect('database.db')
    try:
        conn.execute("BEGIN TRANSACTION")
        # Database operations
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()
```

### 5. Use File Locking
```python
import fcntl

def safe_file_write(data):
    with open('file.txt', 'a') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write(data)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

## Limitations

- Static analysis limitations: The tool uses pattern matching and heuristics
- False positives: May flag legitimate code as race conditions
- Language-specific: Some detection patterns are language-specific
- Context awareness: Limited understanding of complex synchronization patterns

## Contributing

To improve the tool:

1. Add new detection patterns for specific race condition types
2. Improve language support for additional programming languages
3. Enhance the analysis to reduce false positives
4. Add support for more sophisticated synchronization pattern detection

## Security Considerations

Race conditions can lead to:
- Data corruption
- Security vulnerabilities
- Inconsistent application state
- Performance issues
- Resource leaks

Regular scanning with this tool helps identify potential issues before they become problems in production.

## License

This tool is provided as-is for educational and security testing purposes. 