from PyQt5.QtWidgets import QMenuBar, QAction, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

class CustomMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupMenus()
        self.setStyleSheet("""
            QMenuBar {
                background-color: #353535;
                color: #ffffff;
                border-bottom: 1px solid #555555;
                padding: 2px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                margin: 2px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #4a90e2;
            }
            
            QMenuBar::item:pressed {
                background-color: #357abd;
            }
            
            QMenu {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #4a90e2;
            }
            
            QMenu::separator {
                height: 1px;
                background-color: #555555;
                margin: 5px 0px;
            }
        """)
    
    def setupMenus(self):
        """Setup all menu items"""
        self.setupFileMenu()
        self.setupDefaultsMenu()
        self.setupExportMenu()
    
    def setupFileMenu(self):
        """Setup File menu"""
        file_menu = self.addMenu("File")
        
        # New action
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.onNew)
        file_menu.addAction(new_action)
        
        # Save action
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.onSave)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Clear action
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.onClear)
        file_menu.addAction(clear_action)
    
    def setupDefaultsMenu(self):
        """Setup Defaults menu"""
        defaults_menu = self.addMenu("Defaults")
        
        # Effects action
        effects_action = QAction("Effects", self)
        effects_action.triggered.connect(self.onEffects)
        defaults_menu.addAction(effects_action)
        
        # Files action
        files_action = QAction("Files", self)
        files_action.triggered.connect(self.onFiles)
        defaults_menu.addAction(files_action)
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.onSettings)
        defaults_menu.addAction(settings_action)
        
        # Export Settings action
        export_settings_action = QAction("Export Settings", self)
        export_settings_action.triggered.connect(self.onExportSettings)
        defaults_menu.addAction(export_settings_action)
    
    def setupExportMenu(self):
        """Setup Export menu"""
        export_menu = self.addMenu("Export")
        
        # Quick Export action
        quick_export_action = QAction("Quick Export (Using Default)", self)
        quick_export_action.triggered.connect(self.onQuickExport)
        export_menu.addAction(quick_export_action)
        
        # Export Custom action
        export_custom_action = QAction("Export Custom", self)
        export_custom_action.triggered.connect(self.onExportCustom)
        export_menu.addAction(export_custom_action)
    
    # Menu action handlers (placeholders for now)
    def onNew(self):
        print("New project")
    
    def onSave(self):
        print("Save project")
    
    def onClear(self):
        print("Clear project")
    
    def onEffects(self):
        print("Effects settings")
    
    def onFiles(self):
        print("Files settings")
    
    def onSettings(self):
        print("General settings")
    
    def onExportSettings(self):
        print("Export settings")
    
    def onQuickExport(self):
        print("Quick export")
    
    def onExportCustom(self):
        print("Custom export")
