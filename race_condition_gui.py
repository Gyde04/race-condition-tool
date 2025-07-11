#!/usr/bin/env python3
"""
GUI wrapper for the Race Condition Security Tool
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import threading
from pathlib import Path
import sys

# Import our race condition detector
from race_condition_detector import RaceConditionDetector

class RaceConditionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Race Condition Security Tool")
        self.root.geometry("800x600")
        
        self.detector = RaceConditionDetector()
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File/Directory selection
        ttk.Label(main_frame, text="Select file or directory:").grid(row=0, column=0, sticky="w", pady=5)
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=50)
        path_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_path)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Scan button
        scan_btn = ttk.Button(main_frame, text="Scan for Race Conditions", command=self.start_scan)
        scan_btn.grid(row=1, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Results area
        ttk.Label(main_frame, text="Scan Results:").grid(row=3, column=0, sticky="w", pady=5)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=5)
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, height=10)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Details tab
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="Details")
        
        self.details_text = scrolledtext.ScrolledText(self.details_frame, height=10)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Export button
        export_btn = ttk.Button(main_frame, text="Export Report", command=self.export_report)
        export_btn.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.results = []
    
    def browse_path(self):
        """Open file dialog to select file or directory."""
        if messagebox.askyesno("Select Type", "Select directory? (No for file)"):
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename(
                filetypes=[
                    ("Python files", "*.py"),
                    ("JavaScript files", "*.js"),
                    ("TypeScript files", "*.ts"),
                    ("Java files", "*.java"),
                    ("C++ files", "*.cpp"),
                    ("C files", "*.c"),
                    ("Go files", "*.go"),
                    ("Rust files", "*.rs"),
                    ("All files", "*.*")
                ]
            )
        
        if path:
            self.path_var.set(path)
    
    def start_scan(self):
        """Start the scanning process in a separate thread."""
        path = self.path_var.get()
        
        if not path:
            messagebox.showerror("Error", "Please select a file or directory to scan.")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("Error", "Selected path does not exist.")
            return
        
        # Start progress bar
        self.progress.start()
        self.status_var.set("Scanning...")
        
        # Disable scan button
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button) and widget.cget("text") == "Scan for Race Conditions":
                widget.configure(state="disabled")
        
        # Run scan in separate thread
        scan_thread = threading.Thread(target=self.perform_scan, args=(path,))
        scan_thread.daemon = True
        scan_thread.start()
    
    def perform_scan(self, path):
        """Perform the actual scanning."""
        try:
            if os.path.isfile(path):
                conditions = self.detector.scan_file(path)
            else:
                conditions = self.detector.scan_directory(path)
            
            # Update UI in main thread
            self.root.after(0, self.update_results, conditions)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def update_results(self, conditions):
        """Update the UI with scan results."""
        self.results = conditions
        
        # Stop progress bar
        self.progress.stop()
        self.status_var.set(f"Scan complete. Found {len(conditions)} potential race conditions.")
        
        # Re-enable scan button
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button) and widget.cget("text") == "Scan for Race Conditions":
                widget.configure(state="normal")
        
        # Update summary
        self.update_summary(conditions)
        
        # Update details
        self.update_details(conditions)
    
    def update_summary(self, conditions):
        """Update the summary tab."""
        self.summary_text.delete(1.0, tk.END)
        
        summary = f"Race Condition Security Report\n{'='*50}\n\n"
        summary += f"Total conditions found: {len(conditions)}\n"
        summary += f"High severity: {len([c for c in conditions if c.severity == 'HIGH'])}\n"
        summary += f"Medium severity: {len([c for c in conditions if c.severity == 'MEDIUM'])}\n"
        summary += f"Low severity: {len([c for c in conditions if c.severity == 'LOW'])}\n\n"
        
        if conditions:
            summary += "Race Condition Types Found:\n"
            types = set(c.race_type for c in conditions)
            for race_type in types:
                count = len([c for c in conditions if c.race_type == race_type])
                summary += f"  - {race_type}: {count}\n"
        
        self.summary_text.insert(1.0, summary)
    
    def update_details(self, conditions):
        """Update the details tab."""
        self.details_text.delete(1.0, tk.END)
        
        if not conditions:
            self.details_text.insert(1.0, "No race conditions found.")
            return
        
        details = "Detailed Race Condition Report\n" + "="*50 + "\n\n"
        
        for i, condition in enumerate(conditions, 1):
            details += f"{i}. File: {condition.file_path}:{condition.line_number}\n"
            details += f"   Type: {condition.race_type}\n"
            details += f"   Severity: {condition.severity}\n"
            details += f"   Description: {condition.description}\n"
            details += f"   Code: {condition.code_snippet}\n"
            details += "   Recommendations:\n"
            for rec in condition.recommendations:
                details += f"     - {rec}\n"
            details += "\n"
        
        self.details_text.insert(1.0, details)
    
    def export_report(self):
        """Export the scan results to a file."""
        if not self.results:
            messagebox.showwarning("Warning", "No results to export. Please run a scan first.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    report = self.detector.generate_report(self.results, 'json')
                else:
                    report = self.detector.generate_report(self.results, 'text')
                
                with open(file_path, 'w') as f:
                    f.write(report)
                
                messagebox.showinfo("Success", f"Report exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def show_error(self, error_msg):
        """Show error message."""
        self.progress.stop()
        self.status_var.set("Scan failed")
        
        # Re-enable scan button
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button) and widget.cget("text") == "Scan for Race Conditions":
                widget.configure(state="normal")
        
        messagebox.showerror("Error", f"Scan failed: {error_msg}")

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = RaceConditionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 