"""
Button Color Consistency Verification for PhotoSift GUIs
Extracts and compares button styling across all three GUI applications
"""

import re

def extract_button_info(filename):
    """Extract button creation info from a GUI file"""
    with open(f"src/{filename}", "r", encoding="utf-8") as f:
        content = f.read()
    
    buttons = {}
    
    # Find Select Folder button
    select_folder_match = re.search(
        r'(self\.select_btn|select_btn)\s*=\s*ModernButton\.create_\w+_button\([^)]*"Select Folder"[^)]*\)',
        content, re.DOTALL
    )
    if not select_folder_match:
        # Try alternate pattern
        select_folder_match = re.search(
            r'(ModernButton\.create_\w+_button|tk\.Button)\([^)]*text="Select Folder"[^)]*\)',
            content, re.DOTALL
        )
    
    if select_folder_match:
        btn_text = select_folder_match.group(0)
        if 'ModernButton.create_primary_button' in btn_text:
            buttons['Select Folder'] = '🔵 Primary (Blue)'
        elif 'ModernButton.create_secondary_button' in btn_text:
            buttons['Select Folder'] = '⚪ Secondary (Gray)'
        elif 'ModernButton.create_danger_button' in btn_text:
            buttons['Select Folder'] = '🔴 Danger (Red)'
        elif "bg=self.colors['accent']" in btn_text:
            buttons['Select Folder'] = '🔵 Primary (Blue - tk.Button)'
        else:
            buttons['Select Folder'] = '❓ Unknown'
    
    # Find Select All button
    select_all_match = re.search(
        r'self\.select_all_btn\s*=\s*(ModernButton\.create_\w+_button|tk\.Button)\([^)]*\)',
        content, re.DOTALL
    )
    if select_all_match:
        btn_text = select_all_match.group(0)
        if 'ModernButton.create_primary_button' in btn_text:
            buttons['Select All'] = '🔵 Primary (Blue)'
        elif 'ModernButton.create_secondary_button' in btn_text:
            buttons['Select All'] = '⚪ Secondary (Gray)'
        elif 'ModernButton.create_danger_button' in btn_text:
            buttons['Select All'] = '🔴 Danger (Red)'
        elif "bg=self.colors['accent']" in btn_text:
            buttons['Select All'] = '🔵 Primary (Blue - tk.Button)'
        else:
            buttons['Select All'] = '❓ Unknown'
    
    # Find Clean button
    clean_match = re.search(
        r'self\.clean_btn\s*=\s*(ModernButton\.create_\w+_button|tk\.Button)\([^)]*\)',
        content, re.DOTALL
    )
    if clean_match:
        btn_text = clean_match.group(0)
        if 'ModernButton.create_primary_button' in btn_text:
            buttons['Clean'] = '🔵 Primary (Blue)'
        elif 'ModernButton.create_secondary_button' in btn_text:
            buttons['Clean'] = '⚪ Secondary (Gray)'
        elif 'ModernButton.create_danger_button' in btn_text:
            buttons['Clean'] = '🔴 Danger (Red)'
        elif "bg=self.colors['danger']" in btn_text:
            buttons['Clean'] = '🔴 Danger (Red - tk.Button)'
        else:
            buttons['Clean'] = '❓ Unknown'
    
    return buttons

# Test each GUI
guis = [
    ("ImageClassifierGUI.py", "Unwanted Photo Identifier"),
    ("DuplicateImageIdentifierGUI.py", "Duplicate Image Identifier"),
    ("BlurryImageDetectionGUI.py", "Blurry Image Detector")
]

print("=" * 90)
print("PhotoSift v1.3.0 - Button Color Consistency Verification")
print("=" * 90)

expected_colors = {
    'Select Folder': '🔵 Primary (Blue)',
    'Select All': '🔵 Primary (Blue)',
    'Clean': '🔴 Danger (Red)'
}

all_data = []
all_consistent = True

for filename, app_name in guis:
    try:
        buttons = extract_button_info(filename)
        all_data.append((app_name, buttons))
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        all_consistent = False

# Display table
print("\n{:<35} {:<25} {:<25} {:<25}".format(
    "Application", "Select Folder", "Select All", "Clean"
))
print("-" * 110)

for app_name, buttons in all_data:
    select_folder = buttons.get('Select Folder', '❓ Not found')
    select_all = buttons.get('Select All', '❓ Not found')
    clean = buttons.get('Clean', '❓ Not found')
    
    # Check if colors match expected
    sf_match = '🔵 Primary (Blue)' in select_folder
    sa_match = '🔵 Primary (Blue)' in select_all
    c_match = '🔴 Danger (Red)' in clean
    
    if not (sf_match and sa_match and c_match):
        all_consistent = False
    
    print("{:<35} {:<25} {:<25} {:<25}".format(
        app_name, select_folder, select_all, clean
    ))

print("\n" + "=" * 90)

if all_consistent:
    print("✅ ALL BUTTON COLORS ARE CONSISTENT!")
    print("=" * 90)
    print("\nStandardized button colors:")
    print("  🔵 Select Folder → Primary Blue (accent color)")
    print("  🔵 Select All    → Primary Blue (accent color)")
    print("  🔴 Clean         → Danger Red (destructive action)")
    print("\nThis provides:")
    print("  • Visual consistency across all three PhotoSift applications")
    print("  • Clear color coding (blue for actions, red for destructive operations)")
    print("  • Better user experience with predictable button styling")
else:
    print("❌ INCONSISTENCIES FOUND!")
    print("=" * 90)
    print("\nExpected colors:")
    for btn, color in expected_colors.items():
        print(f"  {btn}: {color}")
    print("\nPlease review the table above to see which buttons need updating.")

print("\n" + "=" * 90)
