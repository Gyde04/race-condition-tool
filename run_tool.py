#!/usr/bin/env python3
"""
Launcher script for the Race Condition Security Tool
"""

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Race Condition Security Tool Launcher')
    parser.add_argument('--gui', action='store_true', help='Launch GUI version')
    parser.add_argument('--test', action='store_true', help='Run test examples')
    parser.add_argument('--demo', action='store_true', help='Run demo scan on test files')
    
    args, remaining_args = parser.parse_known_args()
    
    if args.gui:
        # Launch GUI version
        try:
            import tkinter
            from race_condition_gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Error: Could not import tkinter: {e}")
            print("GUI version requires tkinter. Use command-line version instead.")
            sys.exit(1)
        except Exception as e:
            print(f"Error launching GUI: {e}")
            sys.exit(1)
    
    elif args.test:
        # Run test examples
        print("Running test examples...")
        try:
            import test_examples
            print("Test examples loaded successfully.")
            print("You can now run: python race_condition_detector.py test_examples.py")
        except Exception as e:
            print(f"Error running test examples: {e}")
            sys.exit(1)
    
    elif args.demo:
        # Run demo scan
        print("Running demo scan on test files...")
        try:
            from race_condition_detector import RaceConditionDetector
            
            detector = RaceConditionDetector()
            conditions = detector.scan_file('test_examples.py')
            
            print(f"\nDemo scan complete!")
            print(f"Found {len(conditions)} potential race conditions:")
            
            for i, condition in enumerate(conditions, 1):
                print(f"\n{i}. {condition.race_type} (Severity: {condition.severity})")
                print(f"   File: {condition.file_path}:{condition.line_number}")
                print(f"   Description: {condition.description}")
                print(f"   Code: {condition.code_snippet}")
        
        except Exception as e:
            print(f"Error running demo scan: {e}")
            sys.exit(1)
    
    else:
        # Launch command-line version
        try:
            from race_condition_detector import main as cli_main
            # Pass remaining arguments to the CLI
            sys.argv = ['race_condition_detector.py'] + remaining_args
            cli_main()
        except Exception as e:
            print(f"Error launching command-line version: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main() 