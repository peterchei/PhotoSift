"""
Verify version numbers are consistent across all build files for PhotoSift
"""

import re

print("=" * 70)
print("PhotoSift Version Verification - Checking for 1.4.0")
print("=" * 70)

files_to_check = {
    'setup.py': (r'version\s*=\s*["\']([^"\']+)["\']', 'Python package version'),
    'pyproject.toml': (r'version\s*=\s*["\']([^"\']+)["\']', 'pyproject.toml version'),
    'version_info.txt': (r'filevers=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', 'Windows file version'),
    'create_store_package.bat': (r'Version="([^"]+)"', 'MS Store package version'),
    'create_store_assets.py': (r'PhotoSift v([\d.]+)', 'Store assets display version'),
}

expected_version = "1.4.0"
expected_store_version = "1.4.0.0"
all_correct = True

for filename, (pattern, description) in files_to_check.items():
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(pattern, content)
        if match:
            if 'filevers' in pattern:
                # Handle tuple format
                version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                version_full = f"{version}.{match.group(4)}"
                if version == expected_version:
                    print(f"✅ {filename:30} {description:30} = {version_full}")
                else:
                    print(f"❌ {filename:30} {description:30} = {version_full} (expected {expected_version})")
                    all_correct = False
            else:
                version = match.group(1)
                # Store package expects .0 at end
                if filename == 'create_store_package.bat':
                    if version == expected_store_version:
                        print(f"✅ {filename:30} {description:30} = {version}")
                    else:
                        print(f"❌ {filename:30} {description:30} = {version} (expected {expected_store_version})")
                        all_correct = False
                else:
                    if version == expected_version:
                        print(f"✅ {filename:30} {description:30} = {version}")
                    else:
                        print(f"❌ {filename:30} {description:30} = {version} (expected {expected_version})")
                        all_correct = False
        else:
            print(f"❌ {filename:30} {description:30} = NOT FOUND")
            all_correct = False
            
    except Exception as e:
        print(f"❌ {filename:30} Error reading file: {e}")
        all_correct = False

# Also check version_info.txt for FileVersion and ProductVersion strings
try:
    with open('version_info.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_version_match = re.search(r"StringStruct\(u'FileVersion',\s*u'([^']+)'\)", content)
    product_version_match = re.search(r"StringStruct\(u'ProductVersion',\s*u'([^']+)'\)", content)
    
    if file_version_match:
        version = file_version_match.group(1)
        if version == expected_version:
            print(f"✅ {'version_info.txt':30} {'FileVersion string':30} = {version}")
        else:
            print(f"❌ {'version_info.txt':30} {'FileVersion string':30} = {version} (expected {expected_version})")
            all_correct = False
    
    if product_version_match:
        version = product_version_match.group(1)
        if version == expected_version:
            print(f"✅ {'version_info.txt':30} {'ProductVersion string':30} = {version}")
        else:
            print(f"❌ {'version_info.txt':30} {'ProductVersion string':30} = {version} (expected {expected_version})")
            all_correct = False
            
except Exception as e:
    print(f"❌ Error checking version_info.txt strings: {e}")
    all_correct = False

print("\n" + "=" * 70)
if all_correct:
    print("✓ ALL VERSION NUMBERS ARE CORRECT (1.4.0)")
    print("=" * 70)
    print("\nReady to build:")
    print("  1. Run: .\\build.bat")
    print("  2. Run: python create_store_assets.py")
    print("  3. Run: .\\create_store_package.bat")
    print("  4. Create MSIX with makeappx.exe")
else:
    print("❌ VERSION INCONSISTENCIES FOUND")
    print("=" * 70)
    print("\nPlease fix the version numbers marked with ❌ above.")

print("\nExpected versions:")
print(f"  - Standard: {expected_version}")
print(f"  - Store/Windows: {expected_store_version}")
