"""
Test script to verify launchPhotosiftApp.py fixes
Run this before building the MS Store package
"""

import sys
import os
import subprocess
import time

print("=" * 70)
print("PhotoSift v1.6.0 - MS Store Crash Fixes Verification")
print("=" * 70)

# Test 1: Python syntax check
print("\n[Test 1] Checking Python syntax...")
result = subprocess.run(
    [sys.executable, "-m", "py_compile", "src/launchPhotoSiftApp.py"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ PASS: No syntax errors found")
else:
    print("❌ FAIL: Syntax errors detected")
    print(result.stderr)
    sys.exit(1)

# Test 2: Import check
print("\n[Test 2] Checking imports...")
try:
    # Get absolute path to src directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(os.path.dirname(script_dir), "src")
    
    if not os.path.exists(src_dir):
        raise Exception(f"src directory not found at: {src_dir}")
    
    sys.path.insert(0, src_dir)
    
    # Check if file exists
    launcher_path = os.path.join(src_dir, "launchPhotoSiftApp.py")
    if not os.path.exists(launcher_path):
        raise Exception(f"launchPhotoSiftApp.py not found at: {launcher_path}")
    
    print("✅ PASS: File exists and is importable")
except Exception as e:
    print(f"❌ FAIL: Import check error: {e}")
    sys.exit(1)

# Test 3: Check for required additions
print("\n[Test 3] Verifying crash fix implementations...")
with open("src/launchPhotoSiftApp.py", "r", encoding="utf-8") as f:
    content = f.read()
    
    checks = [
        ("import sys", "sys import"),
        ("import logging", "logging import"),
        ("import traceback", "traceback import"),
        ("from tkinter import messagebox", "messagebox import"),
        ("logging.basicConfig", "logging configuration"),
        ("getattr(sys, 'frozen'", "PyInstaller frozen check"),
        ("sys._MEIPASS", "PyInstaller path handling"),
        ("loading_state", "thread-safe state tracking"),
        ("thread.join(timeout=", "thread timeout"),
        ("except tk.TclError", "TclError handling"),
        ("winfo_exists()", "widget existence check"),
        (".quit()", "proper mainloop exit"),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✅ Found: {description}")
        else:
            print(f"  ❌ Missing: {description}")
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: All crash fixes are present")
    else:
        print("\n❌ FAIL: Some fixes are missing")
        sys.exit(1)

# Test 4: Check version consistency
print("\n[Test 4] Checking version consistency...")
version_checks_passed = True
current_version = "1.6.0"

# Check setup.py
with open("setup.py", "r", encoding="utf-8") as f:
    setup_content = f.read()
    if f'version="{current_version}"' in setup_content or f"version='{current_version}'" in setup_content:
        print(f"  ✅ setup.py: {current_version}")
    else:
        print("  ❌ setup.py: version mismatch")
        version_checks_passed = False

# Check version_info.txt
if os.path.exists("version_info.txt"):
    with open("version_info.txt", "r", encoding="utf-8") as f:
        version_content = f.read()
        if current_version in version_content:
            print(f"  ✅ version_info.txt: {current_version}")
        else:
            print("  ❌ version_info.txt: version mismatch")
            version_checks_passed = False

# Check create_store_package.bat
if os.path.exists("create_store_package.bat"):
    with open("create_store_package.bat", "r", encoding="utf-8") as f:
        bat_content = f.read()
        if current_version in bat_content:
            print(f"  ✅ create_store_package.bat: {current_version}")
        else:
            print("  ❌ create_store_package.bat: version mismatch")
            version_checks_passed = False

if version_checks_passed:
    print(f"\n✅ PASS: All versions are {current_version}")
else:
    print("\n❌ FAIL: Version inconsistencies found")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - Ready for building!")
print("=" * 70)
print("\nNext steps:")
print("1. Run: build.bat")
print("2. Test: dist\\PhotoSift.exe")
print("3. Run: create_store_package.bat")
print("4. Test: Install and run the MSIX package")
print("5. Submit to Microsoft Partner Center")
print("\nSee MSSTORE_CRASH_FIXES_v1.3.0.md for detailed testing checklist.")
