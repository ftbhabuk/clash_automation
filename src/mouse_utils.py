import pyautogui
import random
import time

class MouseController:
    @staticmethod
    def human_move(x, y):
        x += random.randint(-5, 5)
        y += random.randint(-5, 5)
        duration = random.uniform(0.3, 0.7)
        pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeOutQuad)
        time.sleep(random.uniform(0.1, 0.3))
    
    @staticmethod
    def human_click():
        pyautogui.click()
        time.sleep(random.uniform(0.1, 0.3))