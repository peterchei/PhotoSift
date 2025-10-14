"""
Debug script to analyze why images are being marked as duplicates
"""
import os
import sys
import numpy as np
from PIL import Image

# Add src to path
sys.path.insert(0, 'src')

from DuplicateImageIdentifier import get_clip_embedding_batch

# Test folder
folder = r"E:\Peter's Photo\22-03-2002 華山派聚會"

# Get image files
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
files = []
for dp, dn, filenames in os.walk(folder):
    for f in filenames:
        if os.path.splitext(f)[1].lower() in IMG_EXT:
            files.append(os.path.join(dp, f))

print(f"Found {len(files)} images in folder")
print()

# Take a sample of images to test
sample_size = min(10, len(files))
sample_files = files[:sample_size]

print(f"Analyzing {sample_size} images:")
for i, f in enumerate(sample_files):
    print(f"  {i+1}. {os.path.basename(f)}")
print()

# Get embeddings
print("Computing embeddings...")
embeddings = get_clip_embedding_batch(sample_files)

# Normalize embeddings for cosine similarity
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
normalized_embeddings = embeddings / norms

# Compute similarity matrix
similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)

# Print similarity matrix
print("\nSimilarity Matrix:")
print("=" * 80)
print(f"{'Image':<15}", end="")
for i in range(sample_size):
    print(f"{i+1:>8}", end="")
print()
print("-" * 80)

for i in range(sample_size):
    print(f"{i+1:<15}", end="")
    for j in range(sample_size):
        sim = similarity_matrix[i][j]
        if i == j:
            print(f"{'---':>8}", end="")
        else:
            print(f"{sim:>8.4f}", end="")
    print()

print()
print("=" * 80)

# Find pairs with high similarity
print("\nHigh Similarity Pairs (>95%):")
print("-" * 80)
found_high_sim = False
for i in range(sample_size):
    for j in range(i+1, sample_size):
        sim = similarity_matrix[i][j]
        if sim >= 0.95:
            found_high_sim = True
            print(f"{os.path.basename(sample_files[i]):30} <-> {os.path.basename(sample_files[j]):30} : {sim:.4f} ({sim*100:.2f}%)")

if not found_high_sim:
    print("No pairs found with >95% similarity")

print()
print("\nHigh Similarity Pairs (>90%):")
print("-" * 80)
found_high_sim = False
for i in range(sample_size):
    for j in range(i+1, sample_size):
        sim = similarity_matrix[i][j]
        if sim >= 0.90:
            found_high_sim = True
            print(f"{os.path.basename(sample_files[i]):30} <-> {os.path.basename(sample_files[j]):30} : {sim:.4f} ({sim*100:.2f}%)")

if not found_high_sim:
    print("No pairs found with >90% similarity")

# Statistics
print()
print("\nSimilarity Statistics:")
print("=" * 80)
# Get upper triangle (exclude diagonal)
upper_triangle = similarity_matrix[np.triu_indices(sample_size, k=1)]
print(f"Average similarity: {upper_triangle.mean():.4f} ({upper_triangle.mean()*100:.2f}%)")
print(f"Max similarity: {upper_triangle.max():.4f} ({upper_triangle.max()*100:.2f}%)")
print(f"Min similarity: {upper_triangle.min():.4f} ({upper_triangle.min()*100:.2f}%)")
print(f"Std deviation: {upper_triangle.std():.4f}")

# Count pairs above various thresholds
thresholds = [0.99, 0.98, 0.97, 0.96, 0.95, 0.90, 0.85, 0.80]
print()
print("Pairs above thresholds:")
for threshold in thresholds:
    count = np.sum(upper_triangle >= threshold)
    percentage = (count / len(upper_triangle)) * 100
    print(f"  >={threshold:.2f}: {count:3d} pairs ({percentage:.1f}%)")
