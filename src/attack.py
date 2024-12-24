import time
import random
import cv2
import pyautogui as pag
import numpy as np
from src.utils import locate_image_on_screen, click_at, get_loot_amounts
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clash_bot.log'),
        logging.StreamHandler()
    ]
)


class BoundaryDetector:
    def __init__(self):
        # Refined HSV ranges for Clash building borders
        self.lower_boundary = np.array([10, 50, 150])  # Lower orange-brown
        self.upper_boundary = np.array([25, 180, 255])  # Upper orange-brown

        # Define regions to exclude (normalized coordinates)
        self.excluded_regions = [
            # Bottom UI bar region (adjust these values as needed)
            {'y_min': 0.8, 'y_max': 1.0, 'x_min': 0.0, 'x_max': 1.0},
            # Next button region (bottom right)
            {'y_min': 0.7, 'y_max': 1.0, 'x_min': 0.8, 'x_max': 1.0},
            # Troop selection area (bottom)
            {'y_min': 0.85, 'y_max': 1.0, 'x_min': 0.0, 'x_max': 1.0}
        ]

    def create_mask_from_excluded_regions(self, image_shape):
        """Create a mask with excluded regions blacked out."""
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
        """Detect the orange-brown building boundary lines with improved filtering."""
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Create initial boundary mask
        boundary_mask = cv2.inRange(hsv, self.lower_boundary, self.upper_boundary)

        # Create and apply excluded regions mask
        excluded_mask = self.create_mask_from_excluded_regions(image.shape)
        boundary_mask = cv2.bitwise_and(boundary_mask, excluded_mask)

        # Remove noise while preserving thin lines
        kernel = np.ones((2, 2), np.uint8)
        boundary_mask = cv2.morphologyEx(boundary_mask, cv2.MORPH_OPEN, kernel)

        # Thicken the detected lines slightly
        kernel_dilate = np.ones((3, 3), np.uint8)
        boundary_mask = cv2.dilate(boundary_mask, kernel_dilate, iterations=1)

        # Find contours focusing on the building boundaries
        contours, _ = cv2.findContours(boundary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours based on area and location
        deployment_points = []
        debug_image = image.copy()

        for contour in contours:
            # Get contour properties
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            # Filter for building boundary characteristics
            if area > 100 and area < 5000 and perimeter > 50:
                # Calculate contour centroid
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # Check if centroid is in valid deployment area
                    if (0.1 < cx / image.shape[1] < 0.9 and
                            0.1 < cy / image.shape[0] < 0.75):  # Adjusted upper bound

                        # Sample points along the contour
                        for i in range(0, len(contour), 5):
                            point = contour[i][0]
                            deployment_points.append((int(point[0]), int(point[1])))

                        # Draw contour on debug image
                        cv2.drawContours(debug_image, [contour], -1, (0, 255, 0), 2)

        # Create debug visualization
        debug_mask = cv2.cvtColor(boundary_mask, cv2.COLOR_GRAY2BGR)

        # Draw deployment points
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

        # Create debug directory if it doesn't exist
        os.makedirs(self.debug_dir, exist_ok=True)

    def _click_attack_button(self):
        """Click the 'Attack' button to start searching for bases."""
        logging.info("🏹 Clicking 'Attack' button...")
        attack_button = locate_image_on_screen('game_images/attack/attack_button.png')
        if attack_button:
            click_at(attack_button)
            time.sleep(random.uniform(1.0, 1.5))
        else:
            raise Exception("❌ Attack button not found!")

    def _click_find_match_button(self):
        """Click the 'Find a Match' button to search for opponents."""
        logging.info("🔍 Clicking 'Find a Match' button...")
        find_match_button = locate_image_on_screen('game_images/attack/find_match.png')
        if find_match_button:
            click_at(find_match_button)
            time.sleep(random.uniform(1.5, 2.0))
        else:
            raise Exception("❌ Find a Match button not found!")

    def _scout_base_for_loot(self):
        """Analyze the current base for available loot."""
        logging.info("💰 Scouting base for loot...")
        loot = get_loot_amounts()
        if not loot:
            raise Exception("❌ Failed to detect loot amounts!")

        gold, elixir, dark_elixir = loot
        logging.info(f"Found: Gold={gold:,}, Elixir={elixir:,}, Dark Elixir={dark_elixir:,}")
        return gold, elixir, dark_elixir

    def _click_next_button(self):
        """Skip the current base and find another opponent."""
        logging.info("⏭️ Skipping base...")
        next_button = locate_image_on_screen('game_images/attack/next_button.png')
        if next_button:
            click_at(next_button)
            time.sleep(random.uniform(2.0, 2.5))
        else:
            raise Exception("❌ Next button not found!")

    def _detect_deployment_points(self):
        """Detect strategic points for troop deployment."""
        logging.info("🎯 Analyzing base for deployment points...")

        # Take screenshot and convert for OpenCV
        screenshot = pag.screenshot()
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Save original screenshot
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        original_path = os.path.join(self.debug_dir, f"original_{timestamp}.png")
        cv2.imwrite(original_path, image)

        # Get deployment points and debug images
        deployment_points, debug_image, debug_mask = self.boundary_detector.detect_boundary(image)

        # Save debug images
        debug_vis_path = os.path.join(self.debug_dir, f"detection_vis_{timestamp}.png")
        debug_mask_path = os.path.join(self.debug_dir, f"detection_mask_{timestamp}.png")
        cv2.imwrite(debug_vis_path, debug_image)
        cv2.imwrite(debug_mask_path, debug_mask)

        logging.info(f"📸 Debug images saved:\n"
                     f"  Original: {original_path}\n"
                     f"  Detection Visualization: {debug_vis_path}\n"
                     f"  Detection Mask: {debug_mask_path}")

        return deployment_points

    def _deploy_troops(self):
        """Deploy troops at strategic points around the base."""
        logging.info("⚔️ Deploying troops...")

        deployment_points = self._detect_deployment_points()

        if not deployment_points:
            logging.warning("⚠️ No deployment points detected! Using fallback strategy...")
            # You could implement a fallback deployment strategy here
            return

        # Select deployment points strategically
        num_points = min(len(deployment_points), 10)  # Deploy at max 10 points
        selected_points = random.sample(deployment_points, num_points)

        # Group points by side of base
        center_x = sum(x for x, y in selected_points) / len(selected_points)
        center_y = sum(y for x, y in selected_points) / len(selected_points)

        # Sort points by distance from center
        selected_points.sort(key=lambda p: ((p[0] - center_x) ** 2 + (p[1] - center_y) ** 2) ** 0.5)

        # Deploy troops at selected points
        for i, point in enumerate(selected_points):
            # Add small random offset for more natural deployment
            offset_x = random.randint(-15, 15)
            offset_y = random.randint(-15, 15)
            deploy_x = point[0] + offset_x
            deploy_y = point[1] + offset_y

            # Click to deploy troops
            pag.click(deploy_x, deploy_y)

            # Vary delay between deployments
            time.sleep(random.uniform(0.3, 0.7))

        logging.info(f"✅ Troops deployed at {num_points} strategic points")

    def analyze_base_colors(self):
        """Debug tool to analyze base colors."""
        logging.info("🎨 Starting color analysis mode...")
        screenshot = pag.screenshot()
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        self.boundary_detector.debug_color_values(image)

    def find_and_attack(self, max_searches=50):
        """Main function to find and attack a suitable base."""
        try:
            logging.info("🚀 Starting attack cycle...")

            # Step 1: Navigate to attack screen
            self._click_attack_button()
            self._click_find_match_button()

            # Step 2: Search for suitable base
            searches = 0
            while searches < max_searches:
                searches += 1
                logging.info(f"\n🔄 Search attempt {searches}/{max_searches}")

                # Scout current base
                gold, elixir, dark_elixir = self._scout_base_for_loot()

                # Check if base meets our criteria
                if (gold >= self.gold_threshold and
                        elixir >= self.elixir_threshold and
                        dark_elixir >= self.dark_elixir_threshold):

                    logging.info("🎯 Suitable base found! Starting attack...")
                    self._deploy_troops()
                    logging.info("⚔️ Attack completed!")
                    break
                else:
                    if searches < max_searches:
                        self._click_next_button()
                    else:
                        logging.warning("❌ Max searches reached without finding suitable base")

        except Exception as e:
            logging.error(f"❌ Error during attack cycle: {str(e)}")
            raise


def main():
    try:
        # Initialize attacker with custom thresholds
        attacker = Attacker(
            gold_threshold=10,  # Minimum gold to attack
            elixir_threshold=10,  # Minimum elixir to attack
            dark_elixir_threshold=10,  # Minimum dark elixir to attack
            debug_dir="debug_screenshots"
        )

        # Color analysis mode (uncomment to use)
        attacker.analyze_base_colors()

        # Start the attack cycle
        attacker.find_and_attack()

    except KeyboardInterrupt:
        logging.info("\n⌨️ Bot stopped by user")
    except Exception as e:
        logging.error(f"❌ Error in main: {str(e)}")


if __name__ == "__main__":
    main()