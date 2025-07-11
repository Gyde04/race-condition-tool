#!/usr/bin/env python3
"""
Test examples demonstrating various race conditions.
These files are used to test the race condition detector.
"""

# Example 1: File operation race condition
def file_race_example():
    """Demonstrates file operation race condition."""
    import os
    
    # RACE CONDITION: Multiple threads writing to the same file without locking
    def write_to_file(data):
        with open('shared_file.txt', 'a') as f:
            f.write(data + '\n')
    
    # This should trigger a race condition detection
    import threading
    threads = []
    for i in range(5):
        thread = threading.Thread(target=write_to_file, args=(f"Data {i}",))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

# Example 2: Variable race condition
def variable_race_example():
    """Demonstrates variable race condition."""
    import threading
    
    counter = 0  # Shared variable
    
    def increment():
        nonlocal counter
        # RACE CONDITION: Non-atomic increment operation
        counter += 1
    
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=increment)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print(f"Final counter value: {counter}")

# Example 3: Database race condition
def database_race_example():
    """Demonstrates database race condition."""
    import sqlite3
    
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
    
    import threading
    threads = []
    for i in range(5):
        thread = threading.Thread(target=update_balance, args=(100,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

# Example 4: Missing lock example
def missing_lock_example():
    """Demonstrates missing lock in threaded code."""
    import threading
    
    shared_data = []
    
    def add_data(item):
        # RACE CONDITION: No lock around shared resource access
        shared_data.append(item)
    
    def remove_data():
        # RACE CONDITION: No lock around shared resource access
        if shared_data:
            return shared_data.pop()
        return None
    
    threads = []
    for i in range(10):
        thread = threading.Thread(target=add_data, args=(f"item_{i}",))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

# Example 5: Threading without synchronization
def threading_race_example():
    """Demonstrates threading race condition."""
    import threading
    import time
    
    def worker():
        # RACE CONDITION: No synchronization between threads
        time.sleep(0.1)
        print(f"Thread {threading.current_thread().name} completed")
    
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker, name=f"Worker-{i}")
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

# Example 6: Correct implementation (should not trigger warnings)
def correct_implementation():
    """Demonstrates correct implementation with proper synchronization."""
    import threading
    import time
    
    # Proper lock usage
    lock = threading.Lock()
    counter = 0
    
    def safe_increment():
        nonlocal counter
        with lock:
            counter += 1
    
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=safe_increment)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print(f"Final counter value: {counter}")

if __name__ == "__main__":
    print("Running race condition examples...")
    
    # Uncomment to test specific examples
    # file_race_example()
    # variable_race_example()
    # database_race_example()
    # missing_lock_example()
    # threading_race_example()
    # correct_implementation() 