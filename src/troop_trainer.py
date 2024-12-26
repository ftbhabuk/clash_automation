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
        print("\nAttempting to train troops...")
        try:
            # Open training menu
            if not self._click_training_button('open_training_menu', "training menu"):
                return False

            if not self._click_training_button('train_army_button', "train army button"):
                return False

            for troop_type, quantity in troop_types:
                print(f"\nStarting training for {quantity} {troop_type}(s)...")
                if not self._train_troop_batch(troop_type, quantity):
                    print(f"Failed to train {troop_type}.")
                time.sleep(random.uniform(0.2, 0.3))  # Small delay between troop types

            # Close training menu only after troops are queued
            print("Closing training menu.")
            self._click_training_button('close_training_menu', "close button")
            return True

        except Exception as e:
            logging.error(f"Error in train_troops: {str(e)}")
            print(f"Error: {str(e)}")
            return False

    def quick_train(self):
        """
        Performs quick train operation using the first preset army
        """
        print("\nAttempting quick train...")
        try:
            # Step 1: Open training menu first
            if not self._click_training_button('open_training_menu', "training menu"):
                return False
            time.sleep(random.uniform(0.5, 1.0))

            # Step 2: Click quick train button
            if not self._click_training_button('quick_train_button', "quick train button"):
                return False
            time.sleep(random.uniform(0.5, 1.0))

            # Step 3: Click the first quick train army slot
            if not self._click_training_button('quick_train_army1', "quick train army slot"):
                return False
            time.sleep(random.uniform(0.5, 1.0))

            # Step 4: Close the training menu (optional - game might do this automatically)
            self._click_training_button('close_training_menu', "close button")

            print("✓ Quick train completed successfully")
            return True

        except Exception as e:
            logging.error(f"Error in quick_train: {str(e)}")
            print(f"Error: {str(e)}")
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
                print(f"{description} clicked.")
                return True
            print(f"{description} not found!")
            return False
        except Exception as e:
            logging.error(f"Error clicking {description}: {str(e)}")
            print(f"Error: {str(e)}")
            return False

    def _train_troop_batch(self, troop_type, quantity):
        try:
            troop_image = IMAGE_PATHS['training']['troops'].get(troop_type)
            if not troop_image:
                print(f"{troop_type} image not found in IMAGE_PATHS!")
                return False

            location = pyautogui.locateOnScreen(troop_image, confidence=0.7)
            if location:
                click_point = pyautogui.center(location)
                self.mouse.human_move(click_point.x, click_point.y)

                # Click and hold to train multiple troops
                print(f"Clicking and holding to train {quantity} {troop_type}(s)...")
                self._click_and_hold(click_point, quantity)

                print(f"✓ Trained approximately {quantity} {troop_type}(s).")
                return True

            print(f"{troop_type} image not found!")
            return False

        except Exception as e:
            logging.error(f"Error training {troop_type}: {str(e)}")
            print(f"Error: {str(e)}")
            return False

    def _click_and_hold(self, point, quantity):
        """
        Simulates a click-and-hold to train multiple troops efficiently.
        The hold duration is calculated based on the quantity.
        """
        hold_time = quantity * 0.1  # Adjust 0.1 seconds per troop as needed
        pyautogui.mouseDown(point.x, point.y)
        time.sleep(hold_time)  # Simulate holding the click
        pyautogui.mouseUp(point.x, point.y)

    def _is_queue_full(self):
        try:
            location = pyautogui.locateOnScreen(
                IMAGE_PATHS['training']['queue_full_message'],
                confidence=0.8
            )
            if location:
                print("Training queue is full.")
            return location is not None
        except Exception as e:
            logging.error(f"Error checking queue status: {str(e)}")
            return False