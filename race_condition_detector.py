#!/usr/bin/env python3
"""
Race Condition Security Tool
A comprehensive tool for detecting and analyzing race conditions in code.
"""

import os
import re
import ast
import argparse
import json
import threading
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RaceCondition:
    """Represents a detected race condition."""
    file_path: str
    line_number: int
    race_type: str
    description: str
    severity: str
    code_snippet: str
    recommendations: List[str]

class RaceConditionDetector:
    """Main class for detecting race conditions in code."""
    
    def __init__(self):
        self.race_conditions: List[RaceCondition] = []
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'}
        
        # Patterns for different types of race conditions
        self.patterns = {
            'file_race': [
                r'open\s*\([^)]*\)',
                r'write\s*\([^)]*\)',
                r'read\s*\([^)]*\)',
                r'f\.write\s*\([^)]*\)',
                r'f\.read\s*\([^)]*\)',
            ],
            'variable_race': [
                r'(\w+)\s*\+=\s*\w+',
                r'(\w+)\s*-=\s*\w+',
                r'(\w+)\s*\*=\s*\w+',
                r'(\w+)\s*/=\s*\w+',
                r'(\w+)\s*=\s*\1\s*[+\-*/]\s*\w+',
            ],
            'database_race': [
                r'INSERT\s+INTO',
                r'UPDATE\s+\w+',
                r'DELETE\s+FROM',
                r'SELECT\s+.*\s+FOR\s+UPDATE',
                r'BEGIN\s+TRANSACTION',
            ],
            'thread_race': [
                r'threading\.Thread',
                r'concurrent\.futures',
                r'asyncio\.',
                r'\.start\(\)',
                r'\.join\(\)',
            ],
            'lock_missing': [
                r'threading\.Lock',
                r'threading\.RLock',
                r'threading\.Semaphore',
                r'\.acquire\(\)',
                r'\.release\(\)',
            ]
        }
    
    def scan_file(self, file_path: str) -> List[RaceCondition]:
        """Scan a single file for race conditions."""
        conditions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return conditions
        
        # Check for file operations without proper locking
        conditions.extend(self._detect_file_races(file_path, lines))
        
        # Check for variable modifications without synchronization
        conditions.extend(self._detect_variable_races(file_path, lines))
        
        # Check for database operations without transactions
        conditions.extend(self._detect_database_races(file_path, lines))
        
        # Check for threading without proper synchronization
        conditions.extend(self._detect_threading_races(file_path, lines))
        
        # Check for missing locks in threaded code
        conditions.extend(self._detect_missing_locks(file_path, lines))
        
        return conditions
    
    def _detect_file_races(self, file_path: str, lines: List[str]) -> List[RaceCondition]:
        """Detect file operation race conditions."""
        conditions = []
        
        for i, line in enumerate(lines, 1):
            for pattern in self.patterns['file_race']:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if there's any locking mechanism around this operation
                    has_lock = self._check_for_locks(lines, i)
                    
                    if not has_lock:
                        conditions.append(RaceCondition(
                            file_path=file_path,
                            line_number=i,
                            race_type="File Operation Race",
                            description="File operation detected without proper synchronization",
                            severity="HIGH",
                            code_snippet=line.strip(),
                            recommendations=[
                                "Use file locking mechanisms",
                                "Implement proper error handling",
                                "Consider using atomic operations",
                                "Add retry logic with exponential backoff"
                            ]
                        ))
        
        return conditions
    
    def _detect_variable_races(self, file_path: str, lines: List[str]) -> List[RaceCondition]:
        """Detect variable modification race conditions."""
        conditions = []
        
        for i, line in enumerate(lines, 1):
            for pattern in self.patterns['variable_race']:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    variable = match.group(1)
                    
                    # Check if this variable is accessed in threaded context
                    if self._is_in_threaded_context(lines, i):
                        conditions.append(RaceCondition(
                            file_path=file_path,
                            line_number=i,
                            race_type="Variable Race",
                            description=f"Variable '{variable}' modified without synchronization in threaded context",
                            severity="MEDIUM",
                            code_snippet=line.strip(),
                            recommendations=[
                                "Use threading.Lock for variable access",
                                "Consider using atomic operations",
                                "Use thread-safe data structures",
                                "Implement proper synchronization"
                            ]
                        ))
        
        return conditions
    
    def _detect_database_races(self, file_path: str, lines: List[str]) -> List[RaceCondition]:
        """Detect database operation race conditions."""
        conditions = []
        
        for i, line in enumerate(lines, 1):
            for pattern in self.patterns['database_race']:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if there's proper transaction handling
                    has_transaction = self._check_for_transactions(lines, i)
                    
                    if not has_transaction:
                        conditions.append(RaceCondition(
                            file_path=file_path,
                            line_number=i,
                            race_type="Database Race",
                            description="Database operation without proper transaction handling",
                            severity="HIGH",
                            code_snippet=line.strip(),
                            recommendations=[
                                "Use database transactions",
                                "Implement proper rollback mechanisms",
                                "Add retry logic for failed operations",
                                "Consider using database-level locking"
                            ]
                        ))
        
        return conditions
    
    def _detect_threading_races(self, file_path: str, lines: List[str]) -> List[RaceCondition]:
        """Detect threading-related race conditions."""
        conditions = []
        
        for i, line in enumerate(lines, 1):
            for pattern in self.patterns['thread_race']:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if there's proper synchronization
                    has_sync = self._check_for_synchronization(lines, i)
                    
                    if not has_sync:
                        conditions.append(RaceCondition(
                            file_path=file_path,
                            line_number=i,
                            race_type="Threading Race",
                            description="Threading operation without proper synchronization",
                            severity="HIGH",
                            code_snippet=line.strip(),
                            recommendations=[
                                "Use threading.Lock or threading.RLock",
                                "Consider using threading.Semaphore",
                                "Implement proper thread coordination",
                                "Use thread-safe data structures"
                            ]
                        ))
        
        return conditions
    
    def _detect_missing_locks(self, file_path: str, lines: List[str]) -> List[RaceCondition]:
        """Detect missing locks in threaded code."""
        conditions = []
        
        # Find threaded sections
        threaded_sections = self._find_threaded_sections(lines)
        
        for start, end in threaded_sections:
            # Check if shared resources are accessed without locks
            shared_access = self._find_shared_resource_access(lines, start, end)
            
            for line_num in shared_access:
                conditions.append(RaceCondition(
                    file_path=file_path,
                    line_number=line_num,
                    race_type="Missing Lock",
                    description="Shared resource accessed without proper locking",
                    severity="HIGH",
                    code_snippet=lines[line_num - 1].strip(),
                    recommendations=[
                        "Add appropriate locks around shared resource access",
                        "Use context managers for lock management",
                        "Consider using atomic operations",
                        "Implement proper resource isolation"
                    ]
                ))
        
        return conditions
    
    def _check_for_locks(self, lines: List[str], line_num: int) -> bool:
        """Check if there are locks around the given line."""
        # Simple heuristic: look for lock-related keywords in nearby lines
        start = max(0, line_num - 10)
        end = min(len(lines), line_num + 10)
        
        for i in range(start, end):
            if any(keyword in lines[i].lower() for keyword in ['lock', 'acquire', 'release', 'with']):
                return True
        
        return False
    
    def _is_in_threaded_context(self, lines: List[str], line_num: int) -> bool:
        """Check if the line is within a threaded context."""
        # Look for threading indicators in the file
        threading_indicators = ['threading', 'Thread', 'concurrent', 'asyncio']
        
        for line in lines:
            if any(indicator in line for indicator in threading_indicators):
                return True
        
        return False
    
    def _check_for_transactions(self, lines: List[str], line_num: int) -> bool:
        """Check if there's proper transaction handling."""
        # Look for transaction-related keywords
        transaction_keywords = ['transaction', 'commit', 'rollback', 'begin', 'end']
        
        start = max(0, line_num - 20)
        end = min(len(lines), line_num + 20)
        
        for i in range(start, end):
            if any(keyword in lines[i].lower() for keyword in transaction_keywords):
                return True
        
        return False
    
    def _check_for_synchronization(self, lines: List[str], line_num: int) -> bool:
        """Check if there's proper synchronization."""
        sync_keywords = ['lock', 'semaphore', 'barrier', 'event', 'condition']
        
        start = max(0, line_num - 20)
        end = min(len(lines), line_num + 20)
        
        for i in range(start, end):
            if any(keyword in lines[i].lower() for keyword in sync_keywords):
                return True
        
        return False
    
    def _find_threaded_sections(self, lines: List[str]) -> List[Tuple[int, int]]:
        """Find sections of code that involve threading."""
        sections = []
        in_threaded_section = False
        start_line = 0
        
        for i, line in enumerate(lines, 1):
            if any(keyword in line for keyword in ['threading', 'Thread', 'concurrent']):
                if not in_threaded_section:
                    in_threaded_section = True
                    start_line = i
            elif in_threaded_section and line.strip() == '':
                # End of threaded section
                sections.append((start_line, i))
                in_threaded_section = False
        
        return sections
    
    def _find_shared_resource_access(self, lines: List[str], start: int, end: int) -> List[int]:
        """Find lines that access shared resources."""
        shared_access = []
        
        for i in range(start, end):
            line = lines[i - 1]
            # Look for variable assignments and modifications
            if re.search(r'\w+\s*[+\-*/]?=\s*\w+', line):
                shared_access.append(i)
        
        return shared_access
    
    def scan_directory(self, directory: str) -> List[RaceCondition]:
        """Scan a directory for race conditions."""
        all_conditions = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if Path(file_path).suffix in self.supported_extensions:
                    logger.info(f"Scanning {file_path}")
                    conditions = self.scan_file(file_path)
                    all_conditions.extend(conditions)
        
        return all_conditions
    
    def generate_report(self, conditions: List[RaceCondition], output_format: str = 'json') -> str:
        """Generate a report of detected race conditions."""
        if output_format == 'json':
            report = {
                'summary': {
                    'total_conditions': len(conditions),
                    'high_severity': len([c for c in conditions if c.severity == 'HIGH']),
                    'medium_severity': len([c for c in conditions if c.severity == 'MEDIUM']),
                    'low_severity': len([c for c in conditions if c.severity == 'LOW'])
                },
                'conditions': [
                    {
                        'file_path': c.file_path,
                        'line_number': c.line_number,
                        'race_type': c.race_type,
                        'description': c.description,
                        'severity': c.severity,
                        'code_snippet': c.code_snippet,
                        'recommendations': c.recommendations
                    }
                    for c in conditions
                ]
            }
            return json.dumps(report, indent=2)
        
        elif output_format == 'text':
            report = f"Race Condition Security Report\n{'='*50}\n\n"
            report += f"Total conditions found: {len(conditions)}\n"
            report += f"High severity: {len([c for c in conditions if c.severity == 'HIGH'])}\n"
            report += f"Medium severity: {len([c for c in conditions if c.severity == 'MEDIUM'])}\n"
            report += f"Low severity: {len([c for c in conditions if c.severity == 'LOW'])}\n\n"
            
            for condition in conditions:
                report += f"File: {condition.file_path}:{condition.line_number}\n"
                report += f"Type: {condition.race_type}\n"
                report += f"Severity: {condition.severity}\n"
                report += f"Description: {condition.description}\n"
                report += f"Code: {condition.code_snippet}\n"
                report += "Recommendations:\n"
                for rec in condition.recommendations:
                    report += f"  - {rec}\n"
                report += "\n"
            
            return report
        
        return ""

def main():
    """Main function to run the race condition detector."""
    parser = argparse.ArgumentParser(description='Race Condition Security Tool')
    parser.add_argument('path', help='File or directory to scan')
    parser.add_argument('--output', '-o', default='report.json', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json', help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    detector = RaceConditionDetector()
    
    if os.path.isfile(args.path):
        logger.info(f"Scanning file: {args.path}")
        conditions = detector.scan_file(args.path)
    elif os.path.isdir(args.path):
        logger.info(f"Scanning directory: {args.path}")
        conditions = detector.scan_directory(args.path)
    else:
        logger.error(f"Path does not exist: {args.path}")
        return 1
    
    # Generate and save report
    report = detector.generate_report(conditions, args.format)
    
    with open(args.output, 'w') as f:
        f.write(report)
    
    logger.info(f"Report saved to: {args.output}")
    logger.info(f"Found {len(conditions)} potential race conditions")
    
    return 0

if __name__ == '__main__':
    exit(main()) 