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

def get_loot_amounts():
    """
    Extract loot amounts from the screen using OCR.
    :return: Tuple (gold, elixir, dark_elixir) as integers or None if detection fails.
    """
    loot_region = (950, 350, 200, 100)  # Example region of loot display (adjust as needed)
    screenshot = pag.screenshot(region=loot_region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Preprocess image for OCR
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Extract text with Tesseract
    text = pytesseract.image_to_string(binary, config='--psm 6')
    print(f"OCR Text: {text}")

    try:
        # Parse loot amounts (e.g., Gold: 200000 Elixir: 150000 Dark Elixir: 500)
        lines = text.split('\n')
        gold = int(lines[0].split()[1].replace(',', ''))
        elixir = int(lines[1].split()[1].replace(',', ''))
        dark_elixir = int(lines[2].split()[2].replace(',', ''))
        return gold, elixir, dark_elixir
    except Exception as e:
        print(f"❌ Error parsing loot amounts: {str(e)}")
        return None
