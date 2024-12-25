import cv2
import pyautogui as pag
import pytesseract
import numpy as np
import os
import time


def save_debug_screenshot(image, region, debug_dir="debug_screenshots", attempt=0):
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    debug_path = os.path.join(debug_dir, f"builder_region_{timestamp}_attempt{attempt}.png")
    cv2.imwrite(debug_path, image)
    print(f"📸 Debug screenshot saved: {debug_path}")


def enhance_contrast(image):
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)"""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def preprocess_image(image):
    """Enhanced preprocessing pipeline for better OCR results"""
    # Resize image (upscale)
    height, width = image.shape[:2]
    image = cv2.resize(image, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)

    # Enhance contrast
    image = enhance_contrast(image)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply bilateral filter to reduce noise while preserving edges
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Remove small noise
    kernel = np.ones((2, 2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # Dilate to make text more prominent
    binary = cv2.dilate(binary, kernel, iterations=1)

    return binary


def parse_builder_text(text):
    """Parse builder count from OCR text with improved error handling"""
    # Clean the text
    text = text.strip().replace(' ', '')

    # Try different parsing strategies
    if '/' in text:
        parts = text.split('/')
        if len(parts) == 2:
            # Try to extract numbers, handling potential OCR mistakes
            try:
                available = int(''.join(c for c in parts[0] if c.isdigit()))
                total = int(''.join(c for c in parts[1] if c.isdigit()))
                if 0 <= available <= total and total > 0:
                    return available, total
            except ValueError:
                pass
    return None, None


def get_available_builders(debug_mode=True, debug_dir="debug_screenshots", max_retries=3, retry_delay=1):
    """Extract the number of available builders with improved accuracy"""
    builder_region = (1264, 350, 65, 32)  # x, y, width, height

    results = []  # Store multiple readings for consistency check

    attempt = 0
    while attempt < max_retries:
        try:
            # Take a screenshot
            screenshot = pag.screenshot(region=builder_region)
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            if debug_mode:
                save_debug_screenshot(screenshot, builder_region, debug_dir, attempt)

            # Preprocess with enhanced pipeline
            processed_image = preprocess_image(screenshot)

            # Try multiple PSM modes for better accuracy
            psm_modes = [6, 7, 8]  # Different page segmentation modes

            for psm in psm_modes:
                custom_config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789/ -c tessedit_do_invert=0'
                text = pytesseract.image_to_string(processed_image, config=custom_config).strip()

                available, total = parse_builder_text(text)
                if available is not None and total is not None:
                    results.append((available, total))
                    print(f"Detected: {available}/{total} (PSM: {psm})")

        except Exception as e:
            print(f"Error in attempt {attempt + 1}: {str(e)}")
        finally:
            attempt += 1
            if attempt < max_retries:
                time.sleep(retry_delay)

    # Return most common result or (0, 0) if no consistent reading
    if results:
        # Get the most frequent reading
        from collections import Counter
        most_common = Counter(results).most_common(1)[0][0]
        return most_common

    return 0, 0


def main():
    print("Starting Enhanced Builder Availability Detection...")
    available_builders, total_builders = get_available_builders()
    print(f"\nFinal Result - Available Builders: {available_builders}")
    print(f"Final Result - Total Builders: {total_builders}")


if __name__ == "__main__":
    main()