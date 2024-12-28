import os
import cv2
import numpy as np
import pytesseract
import pyautogui as pag

# Ensure debug folder exists
DEBUG_FOLDER = "debug_screenshots"
os.makedirs(DEBUG_FOLDER, exist_ok=True)


def extract_resource_amount(region, resource_name="resource"):
    """
    Extract the resource amount using OCR from a specific region.
    """
    try:
        # Take a screenshot of the specified region
        screenshot = pag.screenshot(region=region)

        # Save the screenshot for debugging
        debug_path = os.path.join(DEBUG_FOLDER, f"{resource_name}_debug.png")
        screenshot.save(debug_path)
        print(f"Saved debug image for {resource_name} at {debug_path}")

        # Convert the screenshot to grayscale for OCR
        gray_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

        # Use pytesseract to extract text
        text = pytesseract.image_to_string(gray_image, config="--psm 7").strip()

        if text.isdigit():
            return int(text)
        else:
            print(f"Failed to parse resource amount from text: {text}")
            return 0
    except Exception as e:
        print(f"Error extracting resource amount: {str(e)}")
        return 0


def get_resources():
    """
    Identify and extract resources (gold and elixir) amounts.
    """
    # Define resource icons and approximate regions
    resources = {
        "gold": {"icon_path": IMAGE_PATHS['collectors']['gold'], "region": None},
        "elixir": {"icon_path": IMAGE_PATHS['collectors']['elixir'], "region": None},
    }

    # Locate resource icons and extend the region to include text
    for resource, data in resources.items():
        icon_path = data["icon_path"]
        print(f"Looking for {resource} icon at {icon_path}")

        # Locate icon on the screen
        icon_location = pag.locateOnScreen(icon_path, confidence=0.8)
        if icon_location:
            print(f"{resource.capitalize()} icon found at {icon_location}")
            x, y, w, h = icon_location
            data["region"] = (x + w, y, 150, h)  # Extend rightward to capture text
        else:
            print(f"Could not find {resource} icon on the screen.")
            resources[resource] = 0  # Default to 0 if not found
            continue

        # Extract resource amount using the extended region
        if data["region"]:
            resources[resource] = extract_resource_amount(data["region"], resource)
        else:
            resources[resource] = 0

    return resources
