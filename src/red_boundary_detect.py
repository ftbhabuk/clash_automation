import pyautogui as pag
import numpy as np
import cv2
import time
from datetime import datetime


def test_boundary_detection():
    print("🔍 Testing boundary detection...")
    print("You have 3 seconds to switch to the game window...")
    time.sleep(3)

    # Take screenshot
    screenshot = pag.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    original = img.copy()

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define red color ranges (we might need to adjust these)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    # Create masks
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2

    # Find contours
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw results
    cv2.drawContours(img, contours, -1, (0, 255, 0), 2)  # Draw green lines over detected boundaries

    # Save debug images
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_dir = "debug_images"

    # Create debug directory if it doesn't exist
    import os
    os.makedirs(debug_dir, exist_ok=True)

    # Save different stages for debugging
    cv2.imwrite(f"{debug_dir}/original_{timestamp}.png", original)  # Original screenshot
    cv2.imwrite(f"{debug_dir}/red_mask_{timestamp}.png", red_mask)  # Just the red detection
    cv2.imwrite(f"{debug_dir}/detected_{timestamp}.png", img)  # Final result with green lines

    # Print boundary information
    if contours:
        all_points = np.concatenate(contours)
        x_coords = all_points[:, :, 0]
        y_coords = all_points[:, :, 1]

        boundaries = {
            'top': int(np.min(y_coords)),
            'bottom': int(np.max(y_coords)),
            'left': int(np.min(x_coords)),
            'right': int(np.max(x_coords))
        }

        print("\n📏 Detected Boundaries:")
        for key, value in boundaries.items():
            print(f"{key.capitalize()}: {value}")
    else:
        print("❌ No boundaries detected!")

    return len(contours) > 0


if __name__ == "__main__":
    print("🎮 Red Boundary Detection Test")
    print("Instructions:")
    print("1. Open Clash of Clans")
    print("2. Start an attack but don't deploy troops")
    print("3. Make sure red boundaries are visible")
    input("Press Enter when ready...")

    if test_boundary_detection():
        print("\n✅ Test completed! Check debug_images folder for results")
    else:
        print("\n❌ Test failed! No boundaries detected")