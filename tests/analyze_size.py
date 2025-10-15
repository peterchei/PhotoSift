"""
Analyze PhotoSift.exe size and identify largest components
"""

import os
from pathlib import Path

print("=" * 70)
print("PhotoSift Size Analysis")
print("=" * 70)

# Check executable size
exe_path = Path("dist/PhotoSift.exe")
if exe_path.exists():
    exe_size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"\n📦 PhotoSift.exe: {exe_size_mb:.2f} MB")
else:
    print("\n❌ PhotoSift.exe not found in dist folder")
    print("Run build.bat first")
    exit(1)

# Check models directory
models_path = Path("models")
if models_path.exists():
    print(f"\n📁 Models Directory:")
    print("-" * 70)
    
    total_size = 0
    files = []
    
    for file in models_path.rglob("*"):
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            rel_path = file.relative_to(models_path)
            files.append((str(rel_path), size_mb))
    
    # Sort by size
    files.sort(key=lambda x: x[1], reverse=True)
    
    for filepath, size_mb in files:
        if size_mb > 1:
            print(f"  📄 {filepath:50} {size_mb:8.2f} MB")
        else:
            print(f"  📄 {filepath:50} {size_mb * 1024:8.2f} KB")
    
    print("-" * 70)
    print(f"  💾 Total Models Size: {total_size:.2f} MB ({total_size/exe_size_mb*100:.1f}% of exe)")

# Size breakdown
print(f"\n📊 Size Breakdown:")
print("-" * 70)
print(f"  • Total Executable:     {exe_size_mb:8.2f} MB (100%)")
print(f"  • CLIP Model:           {577:8.2f} MB (~98.5%)")
print(f"  • Code + Dependencies:  {exe_size_mb - 577:8.2f} MB (~1.5%)")

# Recommendations
print(f"\n💡 Optimization Opportunities:")
print("-" * 70)

if exe_size_mb > 500:
    print("  ⚠️  Large Size Detected (>500MB)")
    print()
    print("  Quick wins:")
    print("  1. ✅ LZMA2 compression reduces installer to ~500MB")
    print("  2. 🎯 Switch to CPU-only PyTorch: Save ~50-100 MB")
    print("  3. 🚀 Download model on first run: Reduce to ~9 MB")
    print()
    print("  The size is mainly due to the embedded CLIP AI model (577 MB).")
    print("  This enables offline AI-powered photo classification.")
    print()
    print("  For v1.3.1: Keep current approach (offline, professional)")
    print("  For v1.4.0: Consider CPU-only PyTorch optimization")
    print("  For v2.0: Consider download-on-demand model")
else:
    print("  ✅ Size is reasonable")

# Installer size estimate
print(f"\n📦 Estimated Sizes:")
print("-" * 70)
print(f"  • Uncompressed EXE:     {exe_size_mb:8.2f} MB")
print(f"  • LZMA2 Installer:      {exe_size_mb * 0.85:8.2f} MB (estimate)")
print(f"  • ZIP Installer:        {exe_size_mb * 0.95:8.2f} MB (estimate)")
print(f"  • MS Store MSIX:        {exe_size_mb * 0.94:8.2f} MB (estimate)")

print("\n" + "=" * 70)
print("For detailed analysis, see: SIZE_ANALYSIS_v1.3.1.md")
print("=" * 70)
