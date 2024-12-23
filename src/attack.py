import pyautogui
import pytesseract
import logging
import time
import random
from PIL import Image
from src.mouse_utils import MouseController
from src.config import IMAGE_PATHS

class Attacker:
    def __init__(self):
        self.mouse = MouseController()
        self.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust path for your system
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def _click_attack_button(self):
        """
        Click the 'Attack' button in the home village.
        """
        try:
            location = pyautogui.locateOnScreen(IMAGE_PATHS['attack']['attack_button'], confidence=0.8)
            if location:
                click_point = pyautogui.center(location)
                self.mouse.human_move(click_point.x, click_point.y)
                self.mouse.human_click()
                print("🏹 Clicked 'Attack' button.")
                time.sleep(2)
            else:
                print("❌ 'Attack' button not found!")
        except Exception as e:
            logging.error(f"Error clicking 'Attack' button: {str(e)}")

    def _click_find_match(self):
        """
        Click the 'Find a Match' button.
        """
        try:
            location = pyautogui.locateOnScreen(IMAGE_PATHS['attack']['find_match'], confidence=0.8)
            if location:
                click_point = pyautogui.center(location)
                self.mouse.human_move(click_point.x, click_point.y)
                self.mouse.human_click()
                print("🌐 Clicked 'Find a Match' button.")
                time.sleep(5)  # Wait for cloud scouting to load
            else:
                print("❌ 'Find a Match' button not found!")
        except Exception as e:
            logging.error(f"Error clicking 'Find a Match' button: {str(e)}")

    def find_and_attack(self, loot_threshold):
        """
        Skip bases until the loot meets or exceeds the threshold, then attack.
        """
        print("\n🔍 Starting attack sequence...")

        # Step 1: Click 'Attack' button in the home village
        self._click_attack_button()

        # Step 2: Click 'Find a Match'
        self._click_find_match()

        # Step 3: Search for bases with sufficient loot
        gold_threshold, elixir_threshold, dark_elixir_threshold = loot_threshold

        while True:
            # Read loot amounts
            loot_region = (700, 150, 200, 50)  # Adjust based on loot area
            gold, elixir, dark_elixir = self._get_loot_amounts(loot_region)
            print(f"💰 Loot found: Gold={gold}, Elixir={elixir}, Dark Elixir={dark_elixir}")

            if gold >= gold_threshold and elixir >= elixir_threshold and dark_elixir >= dark_elixir_threshold:
                print("🎯 Found a base with sufficient loot! Starting attack...")
                self._deploy_troops()
                break
            else:
                print("🔄 Skipping base...")
                self._click_next_button()

            time.sleep(random.uniform(2.0, 3.0))  # Wait before looking at the next base
