import cv2
import numpy as np
import os
from src.DarkImageDetection import DarkImageDetector

def test_dark_detection():
    detector = DarkImageDetector(threshold=40.0)
    
    # 1. Create a pure black image (0 brightness)
    black_img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite("black.jpg", black_img)
    
    is_dark, score = detector.is_dark("black.jpg")
    print(f"Black image - is_dark: {is_dark}, score: {score}")
    assert is_dark == True
    assert score == 0.0
    
    # 2. Create a pure white image (255 brightness)
    white_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    cv2.imwrite("white.jpg", white_img)
    
    is_dark, score = detector.is_dark("white.jpg")
    print(f"White image - is_dark: {is_dark}, score: {score}")
    assert is_dark == False
    assert score == 255.0
    
    # 3. Create a grey image (128 brightness)
    grey_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
    cv2.imwrite("grey.jpg", grey_img)
    
    is_dark, score = detector.is_dark("grey.jpg")
    print(f"Grey image - is_dark: {is_dark}, score: {score}")
    assert is_dark == False
    assert score == 128.0

    # Cleanup
    os.remove("black.jpg")
    os.remove("white.jpg")
    os.remove("grey.jpg")
    
    print("\nTests passed successfully!")

if __name__ == "__main__":
    test_dark_detection()
