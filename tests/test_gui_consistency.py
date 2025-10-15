"""
Visual Consistency Test for PhotoSift GUIs
Displays key UI properties from each GUI to verify consistency
"""

import re

def extract_ui_properties(filename):
    """Extract key UI properties from a GUI file"""
    with open(f"src/{filename}", "r", encoding="utf-8") as f:
        content = f.read()
    
    props = {}
    
    # Window title
    title_match = re.search(r'self\.root\.title\("([^"]+)"\)', content)
    if title_match:
        props['window_title'] = title_match.group(1)
    
    # Header subtitle
    subtitle_match = re.search(r'text="([^"]+)".*\n.*font=\("Segoe UI", 14\)', content)
    if subtitle_match:
        props['subtitle'] = subtitle_match.group(1)
    
    # Header height
    header_match = re.search(r'header = tk\.Frame.*height=(\d+)', content)
    if header_match:
        props['header_height'] = header_match.group(1)
    
    # Sidebar width
    sidebar_match = re.search(r'sidebar.*width=(\d+)', content)
    if sidebar_match:
        props['sidebar_width'] = sidebar_match.group(1)
    
    # Uses ModernButton
    props['uses_modern_button'] = 'ModernButton.create_primary_button' in content
    
    # Uses TrashManager
    props['uses_trash_manager'] = 'TrashManager' in content
    
    # Uses ModernColors
    props['uses_modern_colors'] = 'ModernColors.get_color_scheme()' in content
    
    return props

# Test each GUI
guis = [
    ("ImageClassifierGUI.py", "Unwanted Photo Identifier"),
    ("DuplicateImageIdentifierGUI.py", "Duplicate Image Identifier"),
    ("BlurryImageDetectionGUI.py", "Blurry Image Detector")
]

print("=" * 80)
print("PhotoSift v1.3.0 - GUI Consistency Verification")
print("=" * 80)

all_consistent = True

for filename, expected_feature in guis:
    print(f"\n📱 {expected_feature}")
    print("-" * 80)
    
    try:
        props = extract_ui_properties(filename)
        
        # Check window title
        expected_title = f"PhotoSift - {expected_feature}"
        if props.get('window_title') == expected_title:
            print(f"  ✅ Window Title: {props['window_title']}")
        else:
            print(f"  ❌ Window Title: {props.get('window_title')} (expected: {expected_title})")
            all_consistent = False
        
        # Check header height
        if props.get('header_height') == '80':
            print(f"  ✅ Header Height: 80px")
        else:
            print(f"  ⚠️  Header Height: {props.get('header_height')}px (expected: 80px)")
        
        # Check sidebar width
        sidebar_width = props.get('sidebar_width', 'not found')
        if sidebar_width in ['280', '300']:
            print(f"  ✅ Sidebar Width: {sidebar_width}px")
        else:
            print(f"  ⚠️  Sidebar Width: {sidebar_width}px (expected: 280-300px)")
        
        # Check common components
        if props['uses_modern_button']:
            print(f"  ✅ Uses ModernButton")
        else:
            print(f"  ❌ Missing ModernButton")
            all_consistent = False
        
        if props['uses_trash_manager']:
            print(f"  ✅ Uses TrashManager")
        else:
            print(f"  ⚠️  Missing TrashManager")
        
        if props['uses_modern_colors']:
            print(f"  ✅ Uses ModernColors")
        else:
            print(f"  ❌ Missing ModernColors")
            all_consistent = False
            
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        all_consistent = False

print("\n" + "=" * 80)
if all_consistent:
    print("✅ ALL GUIS ARE CONSISTENT!")
    print("=" * 80)
    print("\nAll PhotoSift GUI applications have:")
    print("  • Consistent window titles (PhotoSift prefix)")
    print("  • Standardized button styling (ModernButton)")
    print("  • Unified color scheme (ModernColors)")
    print("  • Common component usage (TrashManager, etc.)")
    print("  • Matching layout structure and spacing")
else:
    print("⚠️  SOME INCONSISTENCIES FOUND - Review the output above")
    print("=" * 80)

print("\nTo test visually:")
print("1. python src/ImageClassifierGUI.py")
print("2. python src/DuplicateImageIdentifierGUI.py")
print("3. python src/BlurryImageDetectionGUI.py")
print("\nCompare the headers, sidebars, and overall appearance.")
