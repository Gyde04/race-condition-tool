#!/usr/bin/env python3
"""
Web application for Race Condition Security Tool
Deployable on Vercel
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import json
from werkzeug.utils import secure_filename
from race_condition_detector import RaceConditionDetector
import io

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

@app.route('/api/examples')
def get_examples():
    """API endpoint to get example race condition code."""
    examples = {
        'file_race': {
            'title': 'File Operation Race Condition',
            'description': 'Multiple threads writing to the same file without synchronization',
            'code': '''import threading

def write_to_file(data):
    with open('shared_file.txt', 'a') as f:
        f.write(data + '\\n')

# RACE CONDITION: Multiple threads writing without locking
threads = []
for i in range(5):
    thread = threading.Thread(target=write_to_file, args=(f"Data {i}",))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()'''
        },
        'variable_race': {
            'title': 'Variable Race Condition',
            'description': 'Variable modification without synchronization in threaded context',
            'code': '''import threading

counter = 0  # Shared variable

def increment():
    global counter
    # RACE CONDITION: Non-atomic increment operation
    counter += 1

threads = []
for _ in range(10):
    thread = threading.Thread(target=increment)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(f"Final counter value: {counter}")'''
        },
        'database_race': {
            'title': 'Database Race Condition',
            'description': 'Database operations without proper transaction handling',
            'code': '''import sqlite3
import threading

def update_balance(amount):
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    
    # RACE CONDITION: Read-modify-write without transaction
    cursor.execute("SELECT balance FROM accounts WHERE id = 1")
    balance = cursor.fetchone()[0]
    
    new_balance = balance + amount
    cursor.execute("UPDATE accounts SET balance = ? WHERE id = 1", (new_balance,))
    
    conn.commit()
    conn.close()

threads = []
for i in range(5):
    thread = threading.Thread(target=update_balance, args=(100,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()'''
        },
        'correct_implementation': {
            'title': 'Correct Implementation',
            'description': 'Proper synchronization with locks',
            'code': '''import threading

# Proper lock usage
lock = threading.Lock()
counter = 0

def safe_increment():
    global counter
    with lock:
        counter += 1

threads = []
for _ in range(10):
    thread = threading.Thread(target=safe_increment)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(f"Final counter value: {counter}")'''
        }
    }
    
    return jsonify(examples)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'Race Condition Security Tool'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 