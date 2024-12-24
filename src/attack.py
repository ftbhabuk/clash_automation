import time
import random
import cv2
import pyautogui as pag
import numpy as np
from src.utils import locate_image_on_screen, click_at, get_loot_amounts
import os
import logging
import keyboard


class BoundaryDetector:
    def __init__(self):
        self.lower_boundary = np.array([10, 50, 150])
        self.upper_boundary = np.array([25, 180, 255])

        self.excluded_regions = [
            {'y_min': 0.8, 'y_max': 1.0, 'x_min': 0.0, 'x_max': 1.0},
            {'y_min': 0.7, 'y_max': 1.0, 'x_min': 0.8, 'x_max': 1.0},
            {'y_min': 0.85, 'y_max': 1.0, 'x_min': 0.0, 'x_max': 1.0}
        ]

    def create_mask_from_excluded_regions(self, image_shape):
        mask = np.ones(image_shape[:2], dtype=np.uint8) * 255
        h, w = image_shape[:2]

        for region in self.excluded_regions:
            y_min = int(region['y_min'] * h)
            y_max = int(region['y_max'] * h)
            x_min = int(region['x_min'] * w)
            x_max = int(region['x_max'] * w)
            mask[y_min:y_max, x_min:x_max] = 0

        return mask

    def detect_boundary(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        boundary_mask = cv2.inRange(hsv, self.lower_boundary, self.upper_boundary)
        excluded_mask = self.create_mask_from_excluded_regions(image.shape)
        boundary_mask = cv2.bitwise_and(boundary_mask, excluded_mask)

        kernel = np.ones((2, 2), np.uint8)
        boundary_mask = cv2.morphologyEx(boundary_mask, cv2.MORPH_OPEN, kernel)
        kernel_dilate = np.ones((3, 3), np.uint8)
        boundary_mask = cv2.dilate(boundary_mask, kernel_dilate, iterations=1)

        contours, _ = cv2.findContours(boundary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        deployment_points = []
        debug_image = image.copy()

        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            if area > 100 and area < 5000 and perimeter > 50:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    if (0.1 < cx / image.shape[1] < 0.9 and 0.1 < cy / image.shape[0] < 0.75):
                        for i in range(0, len(contour), 5):
                            point = contour[i][0]
                            deployment_points.append((int(point[0]), int(point[1])))

                        cv2.drawContours(debug_image, [contour], -1, (0, 255, 0), 2)

        debug_mask = cv2.cvtColor(boundary_mask, cv2.COLOR_GRAY2BGR)

        for point in deployment_points:
            cv2.circle(debug_image, point, 3, (0, 0, 255), -1)
            cv2.circle(debug_mask, point, 3, (0, 0, 255), -1)

        return deployment_points, debug_image, debug_mask


class Attacker:
    def __init__(self, gold_threshold=100000, elixir_threshold=100000,
                 dark_elixir_threshold=1000, debug_dir="debug_screenshots"):
        self.gold_threshold = gold_threshold
        self.elixir_threshold = elixir_threshold
        self.dark_elixir_threshold = dark_elixir_threshold
        self.debug_dir = debug_dir
        self.boundary_detector = BoundaryDetector()
        os.makedirs(self.debug_dir, exist_ok=True)

    def _click_attack_button(self):
        logging.info("Clicking 'Attack' button...")
        attack_button = locate_image_on_screen('game_images/attack/attack_button.png')
        if attack_button:
            click_at(attack_button)
            time.sleep(random.uniform(1.0, 1.5))
        else:
            raise Exception("Attack button not found!")

    def _click_find_match_button(self):
        logging.info("Clicking 'Find a Match' button...")
        find_match_button = locate_image_on_screen('game_images/attack/find_match.png')
        if find_match_button:
            click_at(find_match_button)
            time.sleep(random.uniform(1.5, 2.0))
        else:
            raise Exception("Find a Match button not found!")

    def _scout_base_for_loot(self):
        logging.info("Scouting base for loot...")
        loot = get_loot_amounts()
        if not loot:
            raise Exception("Failed to detect loot amounts!")

        gold, elixir, dark_elixir = loot
        logging.info(f"Found: Gold={gold:,}, Elixir={elixir:,}, Dark Elixir={dark_elixir:,}")
        return gold, elixir, dark_elixir

    def _click_next_button(self):
        logging.info("Skipping base...")
        next_button = locate_image_on_screen('game_images/attack/next_button.png')
        if next_button:
            click_at(next_button)
            time.sleep(random.uniform(2.0, 2.5))
        else:
            raise Exception("Next button not found!")

    def _detect_deployment_points(self):
        logging.info("Analyzing base for deployment points...")
        screenshot = pag.screenshot()
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        timestamp = time.strftime('%Y%m%d-%H%M%S')
        original_path = os.path.join(self.debug_dir, f"original_{timestamp}.png")
        cv2.imwrite(original_path, image)

        deployment_points, debug_image, debug_mask = self.boundary_detector.detect_boundary(image)

        debug_vis_path = os.path.join(self.debug_dir, f"detection_vis_{timestamp}.png")
        debug_mask_path = os.path.join(self.debug_dir, f"detection_mask_{timestamp}.png")
        cv2.imwrite(debug_vis_path, debug_image)
        cv2.imwrite(debug_mask_path, debug_mask)

        logging.info(f"Debug images saved in {self.debug_dir}")
        return deployment_points

    def _deploy_troops(self):
        logging.info("Deploying troops...")
        deployment_points = self._detect_deployment_points()

        if not deployment_points:
            logging.warning("No deployment points detected!")
            return

        # Get deployment points for mass deployment
        num_points = min(len(deployment_points), 10)  # Increased number of points
        selected_points = random.sample(deployment_points, num_points)

        # Sort points from outside to inside
        center_x = sum(p[0] for p in selected_points) / len(selected_points)
        center_y = sum(p[1] for p in selected_points) / len(selected_points)
        selected_points.sort(key=lambda p: -((p[0] - center_x) ** 2 + (p[1] - center_y) ** 2))

        logging.info(f"Starting rapid deployment at {num_points} points...")

        # Select first troop
        keyboard.press_and_release('1')
        time.sleep(0.1)  # Minimal wait for troop selection

        # Rapid deployment
        for point in selected_points:
            # Deploy multiple troops at each point rapidly
            for _ in range(2):  # Increased troops per point
                pag.click(point[0], point[1])
                time.sleep(0.05)  # Minimal delay between clicks

        # After deployment, look for and click return home button
        self._return_home()

    def _return_home(self):
        """Click the return home button after attack."""
        logging.info("Looking for return home button...")
        max_attempts = 10
        attempts = 0

        while attempts < max_attempts:
            return_home_button = locate_image_on_screen('game_images/attack/return_home.png')
            if return_home_button:
                click_at(return_home_button)
                logging.info("Clicked return home button")
                time.sleep(1.0)  # Wait for transition
                return True

            attempts += 1
            time.sleep(1.0)  # Wait between checks

        logging.warning("Return home button not found after maximum attempts")
        return False
    def find_and_attack(self, max_searches=50):
        logging.info("Starting attack cycle...")
        try:
            self._click_attack_button()
            self._click_find_match_button()

            searches = 0
            while searches < max_searches:
                searches += 1
                logging.info(f"Search attempt {searches}/{max_searches}")

                gold, elixir, dark_elixir = self._scout_base_for_loot()

                if (gold >= self.gold_threshold and
                        elixir >= self.elixir_threshold and
                        dark_elixir >= self.dark_elixir_threshold):

                    logging.info("Suitable base found! Starting attack...")
                    self._deploy_troops()
                    logging.info("Attack completed!")
                    break
                else:
                    if searches < max_searches:
                        self._click_next_button()
                    else:
                        logging.warning("Max searches reached without finding suitable base")

        except Exception as e:
            logging.error(f"Error during attack cycle: {str(e)}")
            raise