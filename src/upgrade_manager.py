import pyautogui
import logging
import time
import random
from src.mouse_utils import MouseController
from src.config import IMAGE_PATHS
import re
import pytesseract  # You'll need to install this


class BuilderChecker:
    def __init__(self):
        self.mouse = MouseController()

    def check_builder_availability(self):
        """Check if any builders are available by reading the X/Y text"""
        print("\n🏗️ Checking builder availability...")

        try:
            # Find and focus the builder count area
            builder_icon_loc = pyautogui.locateOnScreen(
                IMAGE_PATHS['upgrade']['builder_icon'],
                confidence=0.8
            )

            if not builder_icon_loc:
                print("❌ Couldn't find builder icon!")
                return False

            # The text is usually to the right of the builder icon
            # Adjust these offsets based on your game's layout
            x = builder_icon_loc.left + builder_icon_loc.width
            y = builder_icon_loc.top
            width = 50  # Width of area to capture text from
            height = builder_icon_loc.height

            # Screenshot just the builder count area
            builder_text = pyautogui.screenshot(region=(x, y, width, height))

            # Convert image to text
            text = pytesseract.image_to_string(builder_text)

            # Extract numbers using regex
            match = re.search(r'(\d+)/(\d+)', text)
            if match:
                busy_builders = int(match.group(1))
                total_builders = int(match.group(2))

                available_builders = total_builders - busy_builders

                if available_builders > 0:
                    print(f"✅ {available_builders} builder(s) available! ({busy_builders}/{total_builders})")
                    return True
                else:
                    print(f"ℹ️ No builders available ({busy_builders}/{total_builders})")
                    return False
            else:
                print("❌ Couldn't read builder count!")
                return False

        except Exception as e:
            logging.error(f"Error checking builder availability: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False

    def click_builder_menu(self):
        """Click the builder icon if builders are available"""
        if self.check_builder_availability():
            try:
                location = pyautogui.locateOnScreen(
                    IMAGE_PATHS['upgrade']['builder_icon'],
                    confidence=0.8
                )
                if location:
                    center = pyautogui.center(location)
                    self.mouse.human_move(center.x, center.y)
                    self.mouse.human_click()
                    print("✅ Clicked builder menu")
                    return True

                print("❌ Couldn't click builder icon")
                return False

            except Exception as e:
                logging.error(f"Error clicking builder menu: {str(e)}")
                print(f"❌ Error: {str(e)}")
                return False
        return False