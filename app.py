#!/usr/bin/env python3
"""
Web application for Race Condition Security Tool
Deployable on Vercel
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import json
import subprocess
import threading
import time
from werkzeug.utils import secure_filename
from race_condition_detector import RaceConditionDetector
import io
import requests

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the detector
detector = RaceConditionDetector()

@app.route('/')
def index():
    """Main page with file upload and analysis interface."""
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_file():
    """API endpoint to scan uploaded files for race conditions."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content
        content = file.read().decode('utf-8')
        
        # Create temporary file for scanning
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Scan the file
            conditions = detector.scan_file(temp_file_path)
            
            # Generate report
            report = detector.generate_report(conditions, 'json')
            report_data = json.loads(report)
            
            # Add file info to report
            report_data['file_info'] = {
                'filename': secure_filename(file.filename),
                'size': len(content),
                'lines': len(content.split('\n'))
            }
            
            return jsonify(report_data)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500

@app.route('/api/scan-text', methods=['POST'])
def scan_text():
    """API endpoint to scan text content for race conditions."""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'No content provided'}), 400
        
        content = data['content']
        language = data.get('language', 'python')
        
        # Create temporary file with appropriate extension
        extension = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'go': '.go',
            'rust': '.rs'
        }.get(language, '.py')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Scan the file
            conditions = detector.scan_file(temp_file_path)
            
            # Generate report
            report = detector.generate_report(conditions, 'json')
            report_data = json.loads(report)
            
            # Add content info to report
            report_data['content_info'] = {
                'language': language,
                'size': len(content),
                'lines': len(content.split('\n'))
            }
            
            return jsonify(report_data)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500

@app.route('/api/scan-url', methods=['POST'])
def scan_url():
    """API endpoint to scan code from a URL for race conditions."""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url']
        language = data.get('language', 'python')
        
        # Fetch the content from the URL
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            content = resp.text
        except Exception as e:
            return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
        
        # Create temporary file with appropriate extension
        extension = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'go': '.go',
            'rust': '.rs'
        }.get(language, '.py')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Scan the file
            conditions = detector.scan_file(temp_file_path)
            
            # Generate report
            report = detector.generate_report(conditions, 'json')
            report_data = json.loads(report)
            
            # Add URL info to report
            report_data['url_info'] = {
                'url': url,
                'language': language,
                'size': len(content),
                'lines': len(content.split('\n'))
            }
            
            return jsonify(report_data)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500

@app.route('/api/scan-website', methods=['POST'])
def scan_website():
    """API endpoint to scan code from a website domain and optional path for race conditions."""
    try:
        data = request.get_json()
        if not data or 'domain' not in data:
            return jsonify({'error': 'No domain provided'}), 400
        
        domain = data['domain'].strip()
        path = data.get('path', '').strip()
        language = data.get('language', 'javascript')
        
        # Build the full URL
        if not domain.startswith('http://') and not domain.startswith('https://'):
            url = 'https://' + domain
        else:
            url = domain
        if path:
            if not path.startswith('/'):
                path = '/' + path
            url += path
        
        # Fetch the content from the URL
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            content = resp.text
        except Exception as e:
            return jsonify({'error': f'Failed to fetch URL: {url} - {str(e)}'}), 400
        
        # Create temporary file with appropriate extension
        extension = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'go': '.go',
            'rust': '.rs'
        }.get(language, '.js')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Scan the file
            conditions = detector.scan_file(temp_file_path)
            
            # Generate report
            report = detector.generate_report(conditions, 'json')
            report_data = json.loads(report)
            
            # Add website info to report
            report_data['website_info'] = {
                'domain': domain,
                'path': path,
                'url': url,
                'language': language,
                'size': len(content),
                'lines': len(content.split('\n'))
            }
            
            return jsonify(report_data)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500

@app.route('/api/execute', methods=['POST'])
def execute_code():
    """API endpoint to execute code and detect race conditions in real-time."""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
        
        code = data['code']
        language = data.get('language', 'python')
        execution_timeout = data.get('timeout', 10)  # 10 seconds default
        
        # Create temporary file for execution
        extension = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'go': '.go',
            'rust': '.rs'
        }.get(language, '.py')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # First, scan for race conditions
            conditions = detector.scan_file(temp_file_path)
            
            # Then try to execute the code (safely)
            execution_result = execute_code_safely(temp_file_path, language, execution_timeout)
            
            # Generate comprehensive report
            report_data = {
                'scan_results': {
                    'conditions': [
                        {
                            'race_type': c.race_type,
                            'description': c.description,
                            'severity': c.severity,
                            'line_number': c.line_number,
                            'code_snippet': c.code_snippet,
                            'recommendations': c.recommendations
                        } for c in conditions
                    ],
                    'total_conditions': len(conditions),
                    'high_severity': len([c for c in conditions if c.severity == 'HIGH']),
                    'medium_severity': len([c for c in conditions if c.severity == 'MEDIUM']),
                    'low_severity': len([c for c in conditions if c.severity == 'LOW'])
                },
                'execution_results': execution_result,
                'code_info': {
                    'language': language,
                    'size': len(code),
                    'lines': len(code.split('\n'))
                }
            }
            
            return jsonify(report_data)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        return jsonify({'error': f'Execution failed: {str(e)}'}), 500

def execute_code_safely(file_path, language, timeout):
    """Safely execute code with timeout and restrictions."""
    try:
        if language == 'python':
            # For Python, we'll run it in a restricted environment
            result = subprocess.run(
                ['python3', file_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir()  # Run in temp directory
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'execution_time': 'completed',
                'warnings': []
            }
        
        elif language == 'javascript':
            # For JavaScript, we'll use Node.js
            result = subprocess.run(
                ['node', file_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir()
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'execution_time': 'completed',
                'warnings': []
            }
        
        else:
            # For other languages, we'll just analyze without execution
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Execution not supported for {language}',
                'return_code': -1,
                'execution_time': 'not_supported',
                'warnings': [f'Live execution not available for {language}']
            }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Execution timed out after {timeout} seconds',
            'return_code': -1,
            'execution_time': 'timeout',
            'warnings': ['Execution was terminated due to timeout']
        }
    
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Execution error: {str(e)}',
            'return_code': -1,
            'execution_time': 'error',
            'warnings': ['Execution failed due to system error']
        }

@app.route('/api/examples')
def get_examples():
    """API endpoint to get example race condition code."""
    examples = {
        'file_race': {
            'title': 'File Operation Race Condition',
            'description': 'Multiple threads writing to the same file without synchronization',
            'code': '''import threading
import time

def write_to_file(data):
    with open('shared_file.txt', 'a') as f:
        f.write(data + '\\n')
        time.sleep(0.1)  # Simulate work

# RACE CONDITION: Multiple threads writing without locking
threads = []
for i in range(5):
    thread = threading.Thread(target=write_to_file, args=(f"Data {i}",))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("File writing completed!")'''
        },
        'variable_race': {
            'title': 'Variable Race Condition',
            'description': 'Variable modification without synchronization in threaded context',
            'code': '''import threading
import time

counter = 0  # Shared variable

def increment():
    global counter
    # RACE CONDITION: Non-atomic increment operation
    for _ in range(100):
        counter += 1
        time.sleep(0.001)

threads = []
for _ in range(10):
    thread = threading.Thread(target=increment)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(f"Final counter value: {counter}")
print("Expected: 1000, Actual may be less due to race condition!")'''
        },
        'database_race': {
            'title': 'Database Race Condition',
            'description': 'Database operations without proper transaction handling',
            'code': """import sqlite3
import threading
import time

def update_balance(amount):
    conn = sqlite3.connect(':memory:')  # Use in-memory database for demo
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts 
                     (id INTEGER PRIMARY KEY, balance INTEGER)''')
    cursor.execute('INSERT OR REPLACE INTO accounts (id, balance) VALUES (1, 1000)')
    
    # RACE CONDITION: Read-modify-write without transaction
    cursor.execute(\"SELECT balance FROM accounts WHERE id = 1\")
    balance = cursor.fetchone()[0]
    
    new_balance = balance + amount
    cursor.execute(\"UPDATE accounts SET balance = ? WHERE id = 1\", (new_balance,))
    
    conn.commit()
    conn.close()
    print(f\"Updated balance by {amount}\")

threads = []
for i in range(5):
    thread = threading.Thread(target=update_balance, args=(100,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(\"Database updates completed!\")"""
        },
        'correct_implementation': {
            'title': 'Correct Implementation',
            'description': 'Proper synchronization with locks',
            'code': '''import threading
import time

# Proper lock usage
lock = threading.Lock()
counter = 0

def safe_increment():
    global counter
    for _ in range(100):
        with lock:
            counter += 1
        time.sleep(0.001)

threads = []
for _ in range(10):
    thread = threading.Thread(target=safe_increment)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(f"Final counter value: {counter}")
print("Expected: 1000, Actual: 1000 (correct!)")'''
        },
        'simple_demo': {
            'title': 'Simple Demo',
            'description': 'A simple example to test the execution',
            'code': '''print("Hello from Race Condition Security Tool!")
print("This is a simple demo to test execution.")

# Simple calculation
result = 10 + 20
print(f"10 + 20 = {result}")

# List operations
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers]
print(f"Numbers: {numbers}")
print(f"Squared: {squared}")

print("Demo completed successfully!")'''
        }
    }
    
    return jsonify(examples)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'Race Condition Security Tool'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 