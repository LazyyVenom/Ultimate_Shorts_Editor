from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QMenuBar, QAction, QSplitter, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor

from ..components.menu_bar import CustomMenuBar
from ..components.left_panel import LeftPanel
from ..components.right_panel import RightPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate Shorts Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set dark theme
        self.setDarkTheme()
        
        # Initialize UI
        self.initUI()
    
    def setDarkTheme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QFrame {
                background-color: #353535;
                border: none;
            }
            
            QSplitter::handle {
                background-color: #444444;
                width: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #555555;
            }
        """)
    
    def initUI(self):
        """Initialize the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create and add menu bar
        self.menu_bar = CustomMenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Create splitter for two columns
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create left and right panels
        self.left_panel = LeftPanel()
        self.right_panel = RightPanel()
        
        # Add panels to splitter
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setSizes([420, 980])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
