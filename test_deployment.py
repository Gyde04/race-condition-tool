#!/usr/bin/env python3
"""
Test script to verify deployment structure and functionality
"""

import os
import sys
import json

def test_file_structure():
    """Test that all required files exist."""
    required_files = [
        'app.py',
        'vercel.json',
        'requirements.txt',
        'race_condition_detector.py',
        'templates/index.html',
        'README.md'
    ]
    
    print("🔍 Checking file structure...")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files present")
        return True

def test_vercel_config():
    """Test vercel.json configuration."""
    print("\n🔍 Checking Vercel configuration...")
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['version', 'builds', 'routes']
        for key in required_keys:
            if key in config:
                print(f"✅ {key}")
            else:
                print(f"❌ {key} - MISSING")
                return False
        
        print("✅ Vercel configuration valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading vercel.json: {e}")
        return False

def test_requirements():
    """Test requirements.txt."""
    print("\n🔍 Checking requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        required_packages = ['Flask', 'Werkzeug']
        for package in required_packages:
            if package in content:
                print(f"✅ {package}")
            else:
                print(f"❌ {package} - MISSING")
                return False
        
        print("✅ Requirements file valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def test_app_structure():
    """Test Flask app structure."""
    print("\n🔍 Checking Flask app structure...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        required_elements = [
            'from flask import',
            'app = Flask',
            '@app.route',
            'if __name__ == \'__main__\':'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✅ {element}")
            else:
                print(f"❌ {element} - MISSING")
                return False
        
        print("✅ Flask app structure valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def test_detector_import():
    """Test that the detector can be imported."""
    print("\n🔍 Testing detector import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        from race_condition_detector import RaceConditionDetector
        detector = RaceConditionDetector()
        
        print("✅ Detector imported successfully")
        print(f"✅ Supported extensions: {detector.supported_extensions}")
        print(f"✅ Pattern types: {list(detector.patterns.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing detector: {e}")
        return False

def test_template():
    """Test HTML template."""
    print("\n🔍 Checking HTML template...")
    
    try:
        with open('templates/index.html', 'r') as f:
            content = f.read()
        
        required_elements = [
            '<title>Race Condition Security Tool</title>',
            'function scanFile()',
            'function scanCode()',
            'displayResults'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✅ {element}")
            else:
                print(f"❌ {element} - MISSING")
                return False
        
        print("✅ HTML template valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Race Condition Security Tool - Deployment Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_vercel_config,
        test_requirements,
        test_app_structure,
        test_detector_import,
        test_template
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Push to Git repository")
        print("2. Connect to Vercel")
        print("3. Deploy!")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 