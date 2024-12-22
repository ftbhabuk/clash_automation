import pyautogui
import logging
import time
import random
from src.mouse_utils import MouseController
from src.config import IMAGE_PATHS


class TroopTrainer:
    def __init__(self):
        self.mouse = MouseController()

    def train_troops(self, troop_types):
        print("\n🎯 Attempting to train troops...")

        # Step 1: Open training menu
        if not self._click_image('open_training_menu', "training menu"):
            return False

        # Step 2: Click train army button
        if not self._click_image('train_army_button', "train army button"):
            return False

        # Step 3: Train troops
        for troop_type, quantity in troop_types:
            if not self._train_troop(troop_type, quantity):
                print(f"❌ Failed to train {troop_type}")
            time.sleep(random.uniform(0.1, 0.2))

        # Step 4: Close training menu
        self._click_image('close_training_menu', "close button")

        return True

    def _click_image(self, image_key, description, retries=3, confidence=0.85):
        try:
            print(f"  Looking for {description}...")
            location = self._retry_locate_on_screen(IMAGE_PATHS['training'][image_key], retries, confidence)
            if location:
                center = pyautogui.center(location)
                self.mouse.human_move(center.x, center.y)
                self.mouse.human_click()
                return True
            print(f"❌ {description} not found!")
            return False
        except Exception as e:
            logging.error(f"Error clicking {description}: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False

    def _train_troop(self, troop_type, quantity):
        try:
            print(f"  Looking for {troop_type} troop image...")
            troop_image = IMAGE_PATHS['training']['troops'][troop_type]
            location = self._retry_locate_on_screen(troop_image, retries=3, confidence=0.7)

            if location:
                center = pyautogui.center(location)
                self.mouse.human_move(center.x, center.y)

                for _ in range(quantity):
                    self.mouse.human_click()
                    time.sleep(random.uniform(0.05, 0.1))  # Faster clicking

                logging.info(f"Trained {quantity} {troop_type}")
                return True
            print(f"❌ {troop_type} image not found!")
            return False
        except Exception as e:
            logging.error(f"Error training {troop_type}: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False

    def _retry_locate_on_screen(self, image_path, retries, confidence):
        for _ in range(retries):
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                return location
            time.sleep(0.5)
        return None
