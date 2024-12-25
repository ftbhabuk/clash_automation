import os
import numpy as np
import pyautogui as pag
import cv2
import pytesseract
from datetime import datetime

# Define the path for the builder icon
IMAGE_PATHS = {
    'upgrade': {
        'builder_icon': 'game_images/upgrade/builder_icon.png'
    }
}


def get_absolute_path(relative_path):
    """Convert relative path to absolute path."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)


def save_debug_screenshot(image, region, name):
    """Save a debug screenshot with region markers."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_dir = "debug_screenshots"
    os.makedirs(debug_dir, exist_ok=True)

    debug_path = os.path.join(debug_dir, f"debug_{name}_{timestamp}.png")

    # Add region information and boundary
    height, width = image.shape if len(image.shape) == 2 else image.shape[:2]
    cv2.rectangle(image, (0, 0), (width - 1, height - 1), (255, 255, 255), 1)
    cv2.putText(image, f"Region: {region}", (5, height - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    cv2.imwrite(debug_path, image)
    print(f"Saved debug image at {debug_path}")
    return debug_path


def preprocess_image(image):
    """Preprocess image for better OCR of white text on dark background."""
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)

    # Invert image (since text is white on black)
    gray = cv2.bitwise_not(gray)

    # Apply threshold to make text more clear
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Remove noise
    denoised = cv2.fastNlMeansDenoising(thresh)

    # Dilate slightly to connect text components
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.dilate(denoised, kernel, iterations=1)

    return processed


def get_available_builders():
    """Get the number of available builders with precise region detection."""
    try:
        # Get builder icon path
        builder_icon_path = get_absolute_path(IMAGE_PATHS['upgrade']['builder_icon'])
        print(f"Looking for builder icon at: {builder_icon_path}")

        # Locate builder icon on screen
        location = pag.locateOnScreen(builder_icon_path, confidence=0.8)

        if location:
            print(f"Builder icon found at: {location}")
            x, y, width, height = map(int, (location.left, location.top, location.width, location.height))

            # Define a more precise region for the builder count
            # The region should be just enough to capture "X/Y" format
            builder_region = (
                x + width,  # Start one icon width to the left
                y,  # Same vertical position as icon
                width,  # Region width same as icon width
                height  # Same height as icon
            )

            # Capture and process the region
            screenshot = pag.screenshot(region=builder_region)
            processed_image = preprocess_image(screenshot)

            # Save debug screenshot
            save_debug_screenshot(processed_image, builder_region, "builder_count")

            # OCR configuration specifically for "X/Y" format
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789/'
            text = pytesseract.image_to_string(processed_image, config=custom_config).strip()

            print(f"OCR Result: {text}")

            # Parse X/Y format
            if '/' in text:
                parts = text.split('/')
                if len(parts) == 2 and parts[0].isdigit():
                    return int(parts[0])

            print(f"Failed to parse builder count from text: {text}")
            return 0
        else:
            print("Builder icon not found on screen")
            return 0

    except Exception as e:
        print(f"Error in get_available_builders: {str(e)}")
        return 0


def main():
    print("Starting Builder Availability Check...")

    # Check if builder icon exists
    builder_path = get_absolute_path(IMAGE_PATHS['upgrade']['builder_icon'])
    if not os.path.exists(builder_path):
        print(f"Error: Builder icon not found at {builder_path}")
        return

    # Get available builders
    available = get_available_builders()
    print(f"\nAvailable builders: {available}")


if __name__ == "__main__":
    main()