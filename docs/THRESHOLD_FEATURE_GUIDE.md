# Duplicate Detection Threshold Feature - Visual Guide

## Before Enhancement
```
┌────────────────────────────────────────┐
│  PhotoSift - Duplicate Image Finder    │
├────────────────────────────────────────┤
│                                        │
│  [Select Folder]                       │
│  No folder selected                    │
│                                        │
│  Duplications                          │
│  ┌──────────────────────────────────┐ │
│  │                                  │ │
│  │  (Groups listed here)            │ │
│  │                                  │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```
- Fixed threshold: 95% similarity
- No user control over sensitivity
- Had to re-scan to try different values

## After Enhancement
```
┌────────────────────────────────────────┐
│  PhotoSift - Duplicate Image Finder    │
├────────────────────────────────────────┤
│                                        │
│  [Select Folder]                       │
│  No folder selected                    │
│                                        │
│  Similarity Threshold                  │  ← NEW!
│  [━━━━━━━━●━━━━━━━━━━━━] 95%          │  ← NEW!
│  • 98-99%: Identical images            │  ← NEW!
│  • 95-97%: Near duplicates             │  ← NEW!
│  • 90-94%: Similar images              │  ← NEW!
│  • 80-89%: Loosely related             │  ← NEW!
│                                        │
│  [Re-group with New Threshold]         │  ← NEW!
│                                        │
│  Duplications (25)                     │
│  ┌──────────────────────────────────┐ │
│  │ 📂 image1.jpg (3 duplicates)     │ │
│  │ 📂 image2.jpg (2 duplicates)     │ │
│  │                                  │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## Feature Highlights

### 1. Threshold Slider
```
Similarity Threshold
[━━━━━━━━━━━━━━●━━━━━━━━] 95%
 80%              90%              99%
 ↓                ↓                ↓
Loose          Normal          Strict
```

### 2. Quality Guide
```
• 98-99%: Identical images
  - Exact duplicates
  - Minimal pixel differences
  
• 95-97%: Near duplicates  ← DEFAULT
  - Same image, different quality
  - Same image, different size
  - Very minor edits
  
• 90-94%: Similar images
  - Same subject, different angle
  - Edited versions
  - Color corrected variants
  
• 80-89%: Loosely related
  - Same scene, different moment
  - Related photos from same shoot
```

### 3. Re-group Button
```
After initial scan:
  [Re-group with New Threshold]
  
Features:
  ✓ 10-20x faster than initial scan
  ✓ No image re-processing
  ✓ Instant results
  ✓ Experiment freely
```

## Usage Flow

### Initial Scan (Slow - First Time)
```
1. Click [Select Folder]
   └─> Load all images (100 images)
   
2. Extract CLIP embeddings
   └─> Process: ▓▓▓▓▓▓▓▓▓▓ 100%
   └─> Time: ~30 seconds
   
3. Group duplicates at 95% threshold
   └─> Found: 25 duplicate groups
   
4. [Re-group] button appears
```

### Re-group (Fast - Subsequent)
```
1. Adjust threshold slider to 90%
   
2. Click [Re-group with New Threshold]
   └─> Use cached embeddings
   └─> Process: ▓▓▓▓▓▓▓▓▓▓ 100%
   └─> Time: ~3 seconds ⚡
   
3. New grouping results
   └─> Found: 45 duplicate groups
   
4. Repeat as needed
```

## Technical Architecture

### Data Flow
```
[User Selects Folder]
        ↓
[Scan All Images] → [Extract CLIP Embeddings]
        ↓                    ↓
[Store in Memory] ← [Calculate Similarities]
        ↓                    ↓
[Group by Threshold] ← [User Adjusts Slider]
        ↓
[Display Results]
        ↓
[User Clicks Re-group] → [Use Cached Embeddings]
        ↓                         ↓
[New Grouping] ← [New Threshold Applied]
        ↓
[Update Display]
```

### Performance Comparison
```
Operation                    | Time      | Why
─────────────────────────────|-----------|──────────────────
Initial Scan (100 images)    | ~30 sec   | Load + Embeddings
Re-group with New Threshold  | ~3 sec    | Only re-grouping
Speedup Factor              | 10x       | Skip image loading
```

## Real-World Examples

### Example 1: Photo Collection
```
Threshold: 98%
Results: 5 groups
- Finds exact duplicates only
- Misses edited versions

Threshold: 95%  ← RECOMMENDED
Results: 12 groups
- Finds exact duplicates
- Finds resized versions
- Finds quality variations

Threshold: 90%
Results: 25 groups
- All of the above
- Finds color corrections
- Finds minor edits
```

### Example 2: Screenshot Collection
```
Threshold: 99%
Results: 3 groups
- Only perfect matches

Threshold: 95%
Results: 8 groups
- Similar screenshots
- Different timestamps
- Minor UI differences
```

## Benefits Summary

✅ **User Control**: Adjust sensitivity to your needs
✅ **Speed**: Re-group in seconds, not minutes
✅ **Flexibility**: Experiment without re-scanning
✅ **Education**: Learn what each threshold does
✅ **Consistency**: Same UX as Blur Detection
✅ **Efficiency**: One scan, unlimited re-groups

## Keyboard Shortcuts (Future Enhancement)
```
Ctrl + T: Focus threshold slider
Ctrl + R: Re-group with new threshold
Ctrl + +: Increase threshold (stricter)
Ctrl + -: Decrease threshold (looser)
```

## Status Bar Messages

### Initial Scan
```
Before: "Processing images 50/100 (50%)"
After:  "Done! 25 images have duplicates (50 total) at 95% similarity threshold"
        ↑                                               ↑
        Shows count                                Shows threshold used
```

### Re-group
```
During: "Re-grouping: 100/100 (100%)"
After:  "Done! 45 images have duplicates (90 total) at 90% similarity threshold"
```

## Error Handling

### No Folder Selected
```
User clicks [Re-group] before scanning
↓
Show message: "Please scan a folder first before re-grouping."
```

### Invalid Threshold
```
Slider enforces range: 80% - 99%
No invalid values possible
```

## Future Enhancements

1. **Threshold Presets**
   ```
   [Strict] [Normal] [Loose] [Custom]
   ```

2. **Threshold History**
   ```
   Recently used: 95%, 90%, 87%
   ```

3. **Auto-Suggest Threshold**
   ```
   "Based on your images, we recommend 92%"
   ```

4. **Batch Processing**
   ```
   Try multiple thresholds at once
   Compare results side-by-side
   ```

5. **Export Settings**
   ```
   Save threshold preferences
   Apply to future scans
   ```
