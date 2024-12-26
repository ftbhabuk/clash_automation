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
        print(f" Error locating image {image_path}: {str(e)}")
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

def get_loot_amounts(debug_mode=True, debug_dir="debug_screenshots", max_retries=5, retry_delay=3):
    """
    Extract loot amounts from the screen using OCR, with retries.
    Returns tuple of (gold, elixir, dark_elixir) or None if detection fails after retries.
    """
    # Adjust these coordinates based on your game window size
    loot_region = (494, 385, 210, 145)  # Make this smaller to focus just on the loot area

    attempt = 0
    while attempt < max_retries:
        try:
            # Take a screenshot of the loot region
            screenshot = pag.screenshot(region=loot_region)
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Save debug screenshot if enabled
            if debug_mode:
                os.makedirs(debug_dir, exist_ok=True)
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                debug_path = os.path.join(debug_dir, f"loot_region_{timestamp}_attempt{attempt}.png")
                cv2.imwrite(debug_path, screenshot)
                print(f"📸 Debug screenshot saved: {debug_path}")

            # Image preprocessing for better OCR
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

            # Apply threshold with OTSU to handle varying brightness
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Add some preprocessing to improve text detection
            kernel = np.ones((2, 2), np.uint8)
            binary = cv2.dilate(binary, kernel, iterations=1)

            # Configure Tesseract for digits only
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789,'
            text = pytesseract.image_to_string(binary, config=custom_config)

            # Clean and parse the text
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            # Extract numbers using regex
            import re
            numbers = [int(re.sub(r'[^0-9]', '', line)) for line in lines if re.search(r'\d', line)]

            if len(numbers) >= 2:
                gold = numbers[0]
                elixir = numbers[1]
                dark_elixir = numbers[2] if len(numbers) > 2 else 0

                print(f" Detected loot - Gold: {gold}, Elixir: {elixir}, Dark Elixir: {dark_elixir}")
                return gold, elixir, dark_elixir
            else:
                raise ValueError(f"Could not parse numbers from text: {text}")

        except Exception as e:
            attempt += 1
            print(f" Error parsing loot amounts (Attempt {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                print(f" Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(" Max retries reached. Returning None.")
                return None
