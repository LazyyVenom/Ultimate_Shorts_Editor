"""
Progress Dialog for Ultimate Shorts Editor
"""

from typing import Optional, Callable
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QProgressBar, QLabel, QTextEdit, QApplication
)
from PyQt5.QtCore import pyqtSignal, Qt, QThread, QTimer
from PyQt5.QtGui import QFont


class ProgressDialog(QDialog):
    """Dialog for showing progress of long-running operations"""
    
    # Signals
    cancelled = pyqtSignal()
    
    def __init__(self, title: str = "Processing", parent=None):
        super().__init__(parent)
        self.is_cancelled = False
        self.setup_ui(title)
        
    def setup_ui(self, title: str):
        """Setup the dialog UI"""
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.setModal(True)
        
        # Prevent closing with X button during critical operations
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
        )
        
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Progress percentage
        self.percentage_label = QLabel("0%")
        self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.percentage_label.setStyleSheet("font-weight: bold; margin: 5px;")
        layout.addWidget(self.percentage_label)
        
        # Time estimate
        self.time_label = QLabel("Time remaining: Calculating...")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(self.time_label)
        
        # Details section
        details_label = QLabel("Details:")
        details_label.setStyleSheet("font-size: 11px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setFont(QFont("monospace", 9))
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_operation)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Timer for time estimates
        self.start_time = None
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_time_estimate)
        self.update_timer.start(1000)  # Update every second
        
    def set_progress(self, value: int, status: str = ""):
        """Set progress value (0-100) and optional status"""
        self.progress_bar.setValue(max(0, min(100, value)))
        self.percentage_label.setText(f"{value}%")
        
        if status:
            self.status_label.setText(status)
            
        # Auto-start timing on first progress update
        if self.start_time is None and value > 0:
            from time import time
            self.start_time = time()
            
        QApplication.processEvents()  # Allow UI updates
        
    def add_detail(self, detail: str):
        """Add a detail line to the details text"""
        self.details_text.append(detail)
        # Auto-scroll to bottom
        scrollbar = self.details_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        QApplication.processEvents()
        
    def set_status(self, status: str):
        """Set the current status"""
        self.status_label.setText(status)
        QApplication.processEvents()
        
    def update_time_estimate(self):
        """Update time remaining estimate"""
        if self.start_time is None or self.progress_bar.value() <= 0:
            return
            
        from time import time
        elapsed = time() - self.start_time
        progress = self.progress_bar.value() / 100.0
        
        if progress > 0.01:  # Only estimate after 1% progress
            total_estimated = elapsed / progress
            remaining = total_estimated - elapsed
            
            if remaining > 0:
                if remaining < 60:
                    time_str = f"{int(remaining)} seconds"
                elif remaining < 3600:
                    minutes = int(remaining // 60)
                    seconds = int(remaining % 60)
                    time_str = f"{minutes}m {seconds}s"
                else:
                    hours = int(remaining // 3600)
                    minutes = int((remaining % 3600) // 60)
                    time_str = f"{hours}h {minutes}m"
                    
                self.time_label.setText(f"Time remaining: ~{time_str}")
            else:
                self.time_label.setText("Time remaining: Almost done...")
                
    def cancel_operation(self):
        """Cancel the current operation"""
        self.is_cancelled = True
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("Cancelling...")
        self.set_status("Cancelling operation...")
        self.cancelled.emit()
        
    def operation_completed(self, success: bool = True, message: str = ""):
        """Mark operation as completed"""
        if success:
            self.progress_bar.setValue(100)
            self.percentage_label.setText("100%")
            self.set_status("Completed successfully!")
            self.time_label.setText("Operation completed")
            if message:
                self.add_detail(f"✓ {message}")
        else:
            self.set_status("Operation failed!")
            self.time_label.setText("Operation failed")
            if message:
                self.add_detail(f"✗ {message}")
                
        # Enable close button, disable cancel
        self.cancel_btn.setEnabled(False)
        self.close_btn.setEnabled(True)
        self.update_timer.stop()
        
        # Allow closing with X button again
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowCloseButtonHint
        )
        
    def reset(self):
        """Reset the dialog for reuse"""
        self.is_cancelled = False
        self.start_time = None
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        self.status_label.setText("Initializing...")
        self.time_label.setText("Time remaining: Calculating...")
        self.details_text.clear()
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("Cancel")
        self.close_btn.setEnabled(False)
        
        # Prevent closing with X button during operations
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
        )
        
        # Restart timer
        if not self.update_timer.isActive():
            self.update_timer.start(1000)
            
    def closeEvent(self, event):
        """Handle close event"""
        if self.close_btn.isEnabled():
            # Operation completed, allow closing
            self.update_timer.stop()
            event.accept()
        else:
            # Operation in progress, ignore close
            event.ignore()


class TaskProgressDialog(ProgressDialog):
    """Progress dialog specifically for task execution with steps"""
    
    def __init__(self, task_name: str, total_steps: int, parent=None):
        super().__init__(f"Processing: {task_name}", parent)
        self.task_name = task_name
        self.total_steps = total_steps
        self.current_step = 0
        
    def start_step(self, step_name: str):
        """Start a new step"""
        self.current_step += 1
        progress = int((self.current_step / self.total_steps) * 100)
        self.set_progress(
            progress, 
            f"Step {self.current_step}/{self.total_steps}: {step_name}"
        )
        self.add_detail(f"Started: {step_name}")
        
    def complete_step(self, step_name: str, success: bool = True):
        """Complete the current step"""
        if success:
            self.add_detail(f"✓ Completed: {step_name}")
        else:
            self.add_detail(f"✗ Failed: {step_name}")
            
    def add_step_detail(self, detail: str):
        """Add detail for current step"""
        self.add_detail(f"  • {detail}")
