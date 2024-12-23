import time
import random
import cv2
import pyautogui as pag
from src.utils import locate_image_on_screen, click_at, get_loot_amounts

class Attacker:
    def __init__(self, gold_threshold, elixir_threshold, dark_elixir_threshold):
        self.gold_threshold = gold_threshold
        self.elixir_threshold = elixir_threshold
        self.dark_elixir_threshold = dark_elixir_threshold

    def _click_attack_button(self):
        print("🏹 Clicked 'Attack' button.")
        attack_button = locate_image_on_screen('game_images/attack/attack_button.png')
        if attack_button:
            click_at(attack_button)
            time.sleep(1)
        else:
            raise Exception("Attack button not found!")

    def _click_find_match_button(self):
        print("🌐 Clicked 'Find a Match' button.")
        find_match_button = locate_image_on_screen('game_images/attack/find_match.png')
        if find_match_button:
            click_at(find_match_button)
            time.sleep(2)
        else:
            raise Exception("Find a Match button not found!")

    def _scout_base_for_loot(self):
        print("🔍 Scouting base for loot...")
        loot = get_loot_amounts()
        if not loot:
            raise Exception("Failed to detect loot on base.")
        gold, elixir, dark_elixir = loot
        print(f"💰 Loot found: Gold={gold}, Elixir={elixir}, Dark Elixir={dark_elixir}")
        return gold, elixir, dark_elixir

    def _click_next_button(self):
        print("🔄 Skipping base...")
        next_button = locate_image_on_screen('game_images/attack/next_button.png')
        if next_button:
            click_at(next_button)
            time.sleep(random.uniform(2.0, 3.0))
        else:
            raise Exception("Next button not found!")

    def _deploy_troops(self):
        print("⚔️ Deploying troops...")
        deployment_areas = [
            (700, 300), (800, 400), (900, 500), (1000, 600)  # Example screen coordinates
        ]
        for coord in deployment_areas:
            pag.click(coord[0], coord[1])
            time.sleep(random.uniform(0.2, 0.5))
        print("✔️ Troops deployed.")

    def find_and_attack(self):
        # Step 1: Click on 'Attack'
        self._click_attack_button()

        # Step 2: Click 'Find a Match'
        self._click_find_match_button()

        while True:
            # Step 3: Scout the base
            gold, elixir, dark_elixir = self._scout_base_for_loot()

            # Step 4: Check loot thresholds
            if (gold >= self.gold_threshold and
                elixir >= self.elixir_threshold and
                dark_elixir >= self.dark_elixir_threshold):
                print("🎯 Suitable base found! Initiating attack.")
                self._deploy_troops()
                break
            else:
                self._click_next_button()
