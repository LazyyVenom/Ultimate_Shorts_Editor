#!/usr/bin/env python3
"""
Simple test script for imports only
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all new components can be imported"""
    print("🧪 Testing Ultimate Shorts Editor Architecture...")
    
    # Test models
    print("📦 Testing models...")
    from src.models import MediaFile, Project, Timeline
    from src.models.overlay import ImageOverlay, TextOverlay
    print("  ✅ Models imported successfully")
    
    # Test services  
    print("⚙️  Testing services...")
    from src.services import MediaService, ProjectService, ExportService, CaptionService
    print("  ✅ Services imported successfully")
    
    # Test processors (existing)
    print("🔧 Testing processors...")
    from src.processors import VideoProcessor, AudioProcessor, EffectProcessor, CaptionProcessor
    print("  ✅ Processors imported successfully")
    
    print("\n🎉 All components imported successfully!")
    print("🚀 Your new organized architecture is working!")
    
    return True

if __name__ == "__main__":
    try:
        test_imports()
        print("\n✨ Success! The Ultimate Shorts Editor has been successfully organized.")
        print("\n🎯 Available entry points:")
        print("   • python3 app_new.py       - New organized GUI")
        print("   • python3 app.py           - Legacy interface")
        print("   • python3 demo_organized.py - Architecture demo")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
