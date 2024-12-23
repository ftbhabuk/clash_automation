# # src/attacker.py
# import pyautogui
# import random
# import time
# import logging
# from src.mouse_utils import MouseController
# from src.config import IMAGE_PATHS
#
# class Attacker:
#     def __init__(self):
#         self.mouse = MouseController()
#
#     def launch_attack(self, troop_types):
#         print("\n⚔️ Launching Attack...")
#
#         if self._click_attack_button():
#             print("✓ Clicked attack button")
#             time.sleep(random.uniform(0.5, 1.0))
#
#             if self._start_attack():
#                 print("✓ Started attack")
#                 time.sleep(random.uniform(1.0, 2.0))
#
#                 self._deploy_troops(troop_types)
#                 print("✓ Troops deployed")
#                 return True
#         return False
#
#     def _click_attack_button(self):
#         return self._click_image('attack_button', 'attack button')
#
#     def _start_attack(self):
#         return self._click_image('start_attack', 'start attack button')
#
#     def _deploy_troops(self, troop_types):
#         try:
#             print("  Deploying troops...")
#             location = pyautogui.locateOnScreen(
#                 IMAGE_PATHS['attack']['troop_deployment_area'], confidence=0.85
#             )
#             if location:
#                 deployment_area = pyautogui.center(location)
#                 for troop_type, quantity in troop_types:
#                     troop_image = IMAGE_PATHS['training']['troops'][troop_type]
#                     troop_location = pyautogui.locateOnScreen(troop_image, confidence=0.85)
#                     if troop_location:
#                         for _ in range(quantity):
#                             self.mouse.human_move(deployment_area.x, deployment_area.y)
#                             self.mouse.human_click()
#                             time.sleep(random.uniform(0.05, 0.1))  # Fast troop deployment
#                     else:
#                         print(f"❌ Troop {troop_type} not found for deployment!")
#             else:
#                 print("❌ Troop deployment area not found!")
#         except Exception as e:
#             logging.error(f"Error deploying troops: {str(e)}")
#             print(f"❌ Error: {str(e)}")
#
#     def _click_image(self, image_key, description):
#         try:
#             print(f"  Looking for {description}...")
#             location = pyautogui.locateOnScreen(
#                 IMAGE_PATHS['attack'][image_key], confidence=0.85
#             )
#             if location:
#                 center = pyautogui.center(location)
#                 self.mouse.human_move(center.x, center.y)
#                 self.mouse.human_click()
#                 return True
#             print(f"❌ {description} not found!")
#             return False
#         except Exception as e:
#             logging.error(f"Error clicking {description}: {str(e)}")
#             print(f"❌ Error: {str(e)}")
#             return False
