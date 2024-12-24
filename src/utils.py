import cv2
import pyautogui as pag
import pytesseract
import numpy as np
import time

# Configure Tesseract-OCR if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def locate_image_on_screen(image_path, confidence=0.8):
    """
    Locate an image on the screen using PyAutoGUI.
    :param image_path: Path to the image file.
    :param confidence: Confidence level for matching (default 0.8).
    :return: Center of the located image (x, y) or None if not found.
    """
    try:
        location = pag.locateCenterOnScreen(image_path, confidence=confidence)
        return location
    except Exception as e:
        print(f"❌ Error locating image {image_path}: {str(e)}")
        return None

def click_at(location):
    """
    Click at a given screen location.
    :param location: Tuple (x, y) coordinates.
    """
    x, y = location
    pag.click(x, y)
    time.sleep(0.5)


import os


def get_loot_amounts(debug_mode=True, debug_dir="debug_screenshots"):
    """
    Extract loot amounts from the screen using OCR.
    Save screenshots of the region for debugging purposes if enabled.
    :param debug_mode: Whether to save debug screenshots (default True).
    :param debug_dir: Directory to save debug screenshots (default "debug_screenshots").
    :return: Tuple (gold, elixir, dark_elixir) as integers or None if detection fails.
    """
    loot_region = (500, 400, 300, 150)  # Region covering loot display (adjust as needed)

    try:
        # Take a screenshot of the loot region
        screenshot = pag.screenshot(region=loot_region)
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Save the screenshot if debugging is enabled
        if debug_mode:
            os.makedirs(debug_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            debug_path = os.path.join(debug_dir, f"loot_region_{timestamp}.png")
            cv2.imwrite(debug_path, screenshot)
            print(f"📸 Debug screenshot saved: {debug_path}")

        # Preprocess the image for OCR
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)

        # Extract text with Tesseract OCR
        text = pytesseract.image_to_string(binary, config='--psm 6')
        print(f"OCR Text: {text}")

        # Parse loot amounts
        lines = text.split('\n')
        gold = int(lines[0].split()[1].replace(',', '')) if len(lines) > 0 else 0
        elixir = int(lines[1].split()[1].replace(',', '')) if len(lines) > 1 else 0
        dark_elixir = int(lines[2].split()[2].replace(',', '')) if len(lines) > 2 else 0

        return gold, elixir, dark_elixir

    except Exception as e:
        print(f"❌ Error parsing loot amounts: {str(e)}")
        return None

