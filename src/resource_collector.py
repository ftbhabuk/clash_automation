import pyautogui
import logging
import time
import random
from datetime import datetime
from src.mouse_utils import MouseController
from src.config import IMAGE_PATHS, COOLDOWNS

# resource_collectors.py
class ResourceCollector:
    def __init__(self):
        self.last_collection = {}
        self.mouse = MouseController()

    def _can_collect(self, resource_type, current_time):
        """Check if the cooldown period has passed for a resource type."""
        last_collected_time = self.last_collection.get(resource_type, 0)
        cooldown = COOLDOWNS['collection']
        return (current_time - last_collected_time) >= cooldown

    def collect_resources(self):
        print("\n🔍 Checking resources...")
        current_time = datetime.now().timestamp()
        collected_any = False

        for resource_type, image_path in IMAGE_PATHS['collectors'].items():
            if self._can_collect(resource_type, current_time):
                print(f"  Looking for {resource_type} collector...")
                if self._collect_resource(resource_type, image_path):
                    print(f"✓ Collected {resource_type}")
                    self.last_collection[resource_type] = current_time
                    collected_any = True
                    time.sleep(random.uniform(0.2, 0.4))  # Faster delay
                else:
                    print(f"- No full {resource_type} collectors found")

        if not collected_any:
            print("- No resources ready for collection")

    def _collect_resource(self, resource_type, image_path):
        """Locate and click the resource on the screen."""
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=0.8)
            if location:
                center = pyautogui.center(location)
                self.mouse.human_move(center.x, center.y)
                self.mouse.human_click()
                return True
            return False
        except Exception as e:
            logging.error(f"Error collecting {resource_type}: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False
