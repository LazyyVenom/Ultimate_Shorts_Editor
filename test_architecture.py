#!/usr/bin/env python3
"""
Quick test script for the new organized Ultimate Shorts Editor architecture
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all new components can be imported"""
    print("🧪 Testing component imports...")
    
    try:
        # Test models
        from src.models import MediaFile, Project, Timeline, ImageOverlay, TextOverlay
        print("✅ Models imported successfully")
        
        # Test services  
        from src.services import MediaService, ProjectService, ExportService, CaptionService
        print("✅ Services imported successfully")
        
        # Test processors (existing)
        from src.processors import VideoProcessor, AudioProcessor, EffectProcessor, CaptionProcessor
        print("✅ Processors imported successfully")
        
        # Test UI components
        from src.ui.components import MediaInputWidget, PreviewWidget, OverlayWidget, ProgressDialog
        print("✅ UI Components imported successfully")
        
        # Test main app
        from src.app import UltimateShortEditorApplication
        print("✅ Main application imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of the new architecture"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from src.app import UltimateShortEditorApplication
        from src.models.media_file import MediaType
        
        # Create application
        app = UltimateShortEditorApplication()
        print("✅ Application created successfully")
        
        # Create a new project
        project = app.create_project("Test Project")
        print("✅ Project created successfully")
        
        # Test media service methods
        supported_formats = app.get_supported_formats()
        print(f"✅ Media service working - supports {len(supported_formats)} format categories")
        
        # Test project service
        project_info = app.get_project_info()
        if project_info:
            print(f"✅ Project service working - project: {project_info.get('name', 'Unknown')}")
        else:
            print("✅ Project service working - no active project")
        
        # Test validation
        errors = app.validate_project()
        print(f"✅ Project validation working - found {len(errors)} issues (expected for empty project)")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Ultimate Shorts Editor - New Organized Architecture\n")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test functionality  
    functionality_ok = test_basic_functionality()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Functionality: {'✅ PASS' if functionality_ok else '❌ FAIL'}")
    
    if imports_ok and functionality_ok:
        print("\n🎉 All tests passed! The new architecture is working correctly.")
        print("\n🎯 Next steps:")
        print("   • Run `python3 app_new.py` for GUI mode")
        print("   • Run `python3 demo_organized.py` to explore components")
        print("   • Check README.md for detailed usage instructions")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return imports_ok and functionality_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
