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

    def _get_loot_amounts(self, region):
        """
        Extract loot amounts using OCR.
        """
        try:
            screenshot = pyautogui.screenshot(region=region)
            loot_text = pytesseract.image_to_string(screenshot, config='--psm 7')
            loot_numbers = [int(''.join(filter(str.isdigit, line))) for line in loot_text.split('\n') if line.strip()]
            return loot_numbers if len(loot_numbers) == 3 else [0, 0, 0]
        except Exception as e:
            logging.error(f"Error reading loot amounts: {str(e)}")
            return [0, 0, 0]

    def find_and_attack(self, loot_threshold):
        """
        Skip bases until the loot meets or exceeds the threshold, then attack.
        """
        print("\n🔍 Searching for bases with sufficient loot...")
        gold_threshold, elixir_threshold, dark_elixir_threshold = loot_threshold

        while True:
            # Read loot amounts
            loot_region = (700, 150, 200, 50)  # Adjust to the area where loot is displayed
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

    def _click_next_button(self):
        """
        Click the 'Next' button to skip the base.
        """
        try:
            location = pyautogui.locateOnScreen(IMAGE_PATHS['attack']['next_button'], confidence=0.8)
            if location:
                click_point = pyautogui.center(location)
                self.mouse.human_move(click_point.x, click_point.y)
                self.mouse.human_click()
                print("⏭️ Next button clicked.")
            else:
                print("❌ Next button not found!")
        except Exception as e:
            logging.error(f"Error clicking Next button: {str(e)}")

    def _deploy_troops(self):
        """
        Deploy troops for the attack.
        """
        try:
            deployment_area = pyautogui.locateOnScreen(IMAGE_PATHS['attack']['troop_deployment_area'], confidence=0.8)
            if deployment_area:
                click_point = pyautogui.center(deployment_area)
                for _ in range(30):  # Adjust troop count
                    self.mouse.human_move(click_point.x, click_point.y)
                    self.mouse.human_click()
                    time.sleep(random.uniform(0.1, 0.2))
                print("⚔️ Troops deployed.")
            else:
                print("❌ Deployment area not found!")
        except Exception as e:
            logging.error(f"Error deploying troops: {str(e)}")
