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
        try:
            if not self._click_training_button('open_training_menu', "training menu"):
                return False

            if not self._click_training_button('train_army_button', "train army button"):
                return False

            for troop_type, quantity in troop_types:
                if self._is_queue_full():
                    print("⚠️ Training queue is full! Stopping training.")
                    break

                if not self._train_single_troop(troop_type, quantity):
                    print(f"❌ Failed to train {troop_type}")
                time.sleep(random.uniform(0.1, 0.2))

            self._click_training_button('close_training_menu', "close button")
            return True

        except Exception as e:
            logging.error(f"Error in train_troops: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False

    def _click_training_button(self, button_key, description):
        try:
            location = pyautogui.locateOnScreen(
                IMAGE_PATHS['training'][button_key],
                confidence=0.8
            )
            if location:
                click_point = pyautogui.center(location)
                self.mouse.human_move(click_point.x, click_point.y)
                self.mouse.human_click()
                return True
            print(f"❌ {description} not found!")
            return False
        except Exception as e:
            logging.error(f"Error clicking {description}: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False

    def _train_single_troop(self, troop_type, quantity):
        try:
            print(f"  Looking for {troop_type} troop image...")
            troop_image = IMAGE_PATHS['training']['troops'].get(troop_type)
            if not troop_image:
                print(f"❌ {troop_type} image not found in IMAGE_PATHS!")
                return False

            location = pyautogui.locateOnScreen(troop_image, confidence=0.7)
            if location:
                click_point = pyautogui.center(location)
                self.mouse.human_move(click_point.x, click_point.y)

                for i in range(quantity):
                    if self._is_queue_full():
                        print(f"⚠️ Queue full after training {i} {troop_type}(s)")
                        return True
                    self.mouse.human_click()
                    time.sleep(random.uniform(0.05, 0.1))

                print(f"✓ Trained {quantity} {troop_type}")
                return True
            print(f"❌ {troop_type} image not found!")
            return False
        except Exception as e:
            logging.error(f"Error training {troop_type}: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False

    def _is_queue_full(self):
        try:
            location = pyautogui.locateOnScreen(
                IMAGE_PATHS['training']['queue_full_message'],
                confidence=0.8
            )
            return location is not None
        except Exception as e:
            logging.error(f"Error checking queue status: {str(e)}")
            return False
