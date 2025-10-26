#!/usr/bin/env python3
"""
PhotoSift 60-Second Demo Script Timer
Validates script timing and provides speaking statistics
"""

import re
import time

def count_words(text):
    """Count words in text, excluding timestamps and formatting"""
    # Remove timestamps like [0:05], [0:15], etc.
    text = re.sub(r'\[\d+:\d+\]', '', text)
    # Remove markdown formatting
    text = re.sub(r'\*\*.*?\*\*', '', text)
    # Split by whitespace and count
    words = text.split()
    return len(words)

def estimate_speaking_time(word_count, wpm=150):
    """Estimate speaking time in seconds"""
    return (word_count / wpm) * 60

def format_time(seconds):
    """Format seconds as MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def validate_script_timing(script_text, target_seconds=60):
    """Validate if script fits target time"""
    word_count = count_words(script_text)
    estimated_time = estimate_speaking_time(word_count)

    print(f"📊 Script Analysis:")
    print(f"   Word Count: {word_count}")
    print(f"   Estimated Time: {format_time(estimated_time)}")
    print(f"   Target Time: {format_time(target_seconds)}")

    if abs(estimated_time - target_seconds) <= 5:  # Within 5 seconds
        print("   ✅ PERFECT: Script timing is excellent!")
        return True
    elif estimated_time < target_seconds:
        shortfall = target_seconds - estimated_time
        print(f"   ⚠️  SHORT: Add {format_time(shortfall)} more content")
        return False
    else:
        excess = estimated_time - target_seconds
        print(f"   ⚠️  LONG: Remove {format_time(excess)} of content")
        return False

def main():
    """Analyze all 60-second demo scripts"""
    print("🎬 PhotoSift 60-Second Demo Script Timer")
    print("=" * 50)

    scripts = {
        "Product Overview": """Struggling with thousands of messy photos scattered across your devices? Meet PhotoSift - the intelligent AI-powered photo organizer that transforms photo chaos into organized perfection in minutes!

[0:08] PhotoSift uses advanced artificial intelligence to find duplicate photos you never knew existed, even if they've been resized, cropped, or slightly edited.

[0:16] Our sophisticated blur detection algorithm analyzes every pixel to identify blurry images with surgical precision, scoring quality from excellent to very blurry.

[0:24] Smart AI classification automatically sorts your photos by content - distinguishing people photos from screenshots, documents, and more with incredible accuracy.

[0:32] Experience the modern, intuitive dark interface designed for efficiency, with batch processing capabilities that handle thousands of photos simultaneously.

[0:40] Safety first: PhotoSift includes a comprehensive trash manager so you can review and restore any accidentally deleted photos anytime.

[0:48] Works completely offline - your photos never leave your computer, ensuring complete privacy and security.

[0:56] Free to download, lightning-fast processing, professional results. Transform your photo library today!""",

        "Duplicate Detection": """Watch PhotoSift's AI duplicate detection find and eliminate photo clutter in seconds, saving you gigabytes of storage space!

[0:07] Simply select your photo folder and PhotoSift begins scanning instantly using advanced computer vision algorithms.

[0:14] Our AI analyzes visual content, not just file names or sizes - it finds duplicates even when photos have been resized, compressed, or edited.

[0:21] Results appear in organized groups with similarity scores - 95%+ matches are nearly identical, while 80% catches similar shots from burst photography.

[0:28] The adjustable threshold slider lets you customize sensitivity - catch more duplicates or be more conservative based on your needs.

[0:35] Check boxes make it easy to select which duplicates to remove, with options to keep the highest quality version automatically.

[0:42] Click the Clean button to safely move selected duplicates to trash - nothing is permanently deleted without your confirmation.

[0:49] The built-in trash manager lets you review all deletions and restore any photos you change your mind about.

[0:56] Clean your photo library efficiently and never worry about duplicate photos again!""",

        "Blur Detection": """Eliminate blurry photos forever with PhotoSift's professional-grade AI blur detection that gives you complete control over image quality!

[0:08] Upload your photo collection and PhotoSift's advanced Laplacian variance algorithm analyzes sharpness across every image instantly.

[0:16] Each photo receives a precise quality score: Excellent (>500) for crystal clear shots, Good (250-500) for acceptable quality, Fair (100-250) for usable images.

[0:24] Poor (50-100) and Very Blurry (<50) categories help you identify photos that should be deleted or edited.

[0:32] Color-coded results make quality assessment obvious at a glance - green for excellent, yellow for good, red for poor quality.

[0:40] Fine-tune the threshold slider to match your personal standards - keep only wedding photos, discard blurry vacation shots.

[0:48] Multi-threaded processing leverages all your computer's cores to analyze thousands of photos in just minutes.

[0:56] Achieve professional-quality photo libraries with consistent standards. No more blurry disappointments in your memories!""",

        "Image Classification": """PhotoSift's AI understands your photos like a human expert, automatically categorizing images to bring order to your visual collection!

[0:08] Powered by OpenAI's cutting-edge CLIP model, PhotoSift analyzes photo content with human-like understanding and context awareness.

[0:16] Currently, it expertly distinguishes People photos from Screenshots with incredible accuracy - portraits, selfies, group photos, and pet pictures.

[0:24] App screenshots, error messages, websites, and digital interfaces are automatically categorized as Screenshots.

[0:32] Each classification includes confidence scores showing how certain the AI is about its decision - easily review uncertain results.

[0:40] The system learns from millions of training examples, providing consistent and reliable categorization you can trust.

[0:48] Future updates will expand to more categories like Landscapes, Food, Documents, and Events as the AI capabilities grow.

[0:56] Your photo library deserves intelligent organization. Let PhotoSift's AI do the heavy lifting for you!""",

        "Before/After": """See the dramatic transformation as PhotoSift turns photo chaos into a perfectly organized, professional-quality collection!

[0:07] BEFORE: 5,000 messy photos scattered across folders, hundreds of duplicates wasting storage, blurry shots mixed with perfect images.

[0:14] PhotoSift's comprehensive AI analysis begins - duplicate detection finds 800 identical or similar photos you never spotted.

[0:21] Blur detection identifies 300 low-quality images that should be removed or edited, maintaining only the best shots.

[0:28] Smart classification organizes remaining photos by content type, making your collection searchable and manageable.

[0:35] AFTER: Clean, organized collection with only the highest quality photos, perfectly sorted and easy to navigate.

[0:42] Results: Saved 2.3GB of storage space, removed 1,100 unwanted photos, created a professional photo library.

[0:49] Entire process completed in just 8 minutes - faster than manually sorting through a single folder.

[0:56] Your precious memories deserve this level of care. Give your photos the PhotoSift treatment today!""",

        "Quick Tips": """Master PhotoSift like a pro with these essential tips and tricks that will maximize your photo organization efficiency!

[0:07] TIP 1: Master keyboard shortcuts - Ctrl+A selects all, Delete moves to trash, Ctrl+Z undoes any action instantly.

[0:14] TIP 2: Always start with small test folders to verify results before processing your entire photo collection.

[0:21] TIP 3: Lower duplicate threshold to 80% catches more similar photos, raise to 95% for identical matches only.

[0:28] TIP 4: Blur detection works best on JPEGs - RAW files may need different threshold settings for optimal results.

[0:35] TIP 5: Use the trash manager religiously to review deletions - nothing is permanently lost in PhotoSift.

[0:42] TIP 6: Process large collections in batches to maintain control and monitor progress effectively.

[0:49] TIP 7: PhotoSift remembers your settings between sessions, so your preferred thresholds are always ready.

[0:56] BONUS: Combine all three tools - deduplication, blur removal, and classification - for complete photo perfection!""",

        "Why Choose PhotoSift": """Why waste countless hours manually organizing photos when PhotoSift's AI can do it perfectly in minutes?

[0:07] TRADITIONAL METHOD: Hours of scrolling through thousands of photos, squinting to spot duplicates, guessing at blur quality.

[0:14] PHOTOSIFT ADVANTAGE: Advanced AI analyzes every pixel, finds duplicates you miss, provides objective quality scores.

[0:21] SPEED: 10x faster than manual sorting, processes thousands of photos in minutes instead of hours.

[0:28] ACCURACY: Never misses duplicates, applies consistent quality standards, categorizes content intelligently.

[0:35] FEATURES: Complete offline processing, modern interface, batch operations, safe trash recovery system.

[0:42] PRIVACY: Your photos never leave your computer - complete security and privacy protection.

[0:49] RESULTS: Clean organized library, significant storage savings, enhanced photo viewing experience.

[0:56] Stop wasting time on manual photo organization. Choose PhotoSift and reclaim your time for creating memories!""",

        "Social Media Teaser": """📸 Tired of drowning in photo chaos? Watch this transformation! ✨

[0:06] 5,000 messy photos become perfectly organized in just minutes with PhotoSift's AI magic.

[0:12] 🤖 Advanced AI finds duplicates you never knew existed - even resized or edited versions.

[0:18] 🔍 Surgical blur detection removes low-quality shots automatically with precise scoring.

[0:24] 🏷️ Smart classification sorts people photos from screenshots with incredible accuracy.

[0:30] ⚡ Lightning-fast processing handles thousands of photos simultaneously.

[0:36] 🛡️ Complete privacy - works offline, photos never leave your device.

[0:42] 🎨 Modern dark interface designed for efficiency and ease of use.

[0:48] 💾 Frees up gigabytes of storage by removing unwanted duplicates and blurs.

[0:54] 🚀 Completely free to download. Transform your photo library today!

[0:60] #PhotoSift #AI #PhotoOrganization #DigitalDeclutter #PhotoManagement"""
    }

    total_scripts = len(scripts)
    perfect_scripts = 0

    for title, script in scripts.items():
        print(f"\n🎬 {title}")
        print("-" * 40)
        if validate_script_timing(script):
            perfect_scripts += 1

    print(f"\n📈 SUMMARY:")
    print(f"   Total Scripts: {total_scripts}")
    print(f"   Perfect Timing: {perfect_scripts}")
    print(f"   Success Rate: {(perfect_scripts/total_scripts)*100:.1f}%")

    if perfect_scripts == total_scripts:
        print("   🎉 ALL SCRIPTS ARE PERFECTLY TIMED!")
    else:
        print("   ⚠️  Some scripts need timing adjustments.")

if __name__ == "__main__":
    main()