import time
import random
import logging
import colorama
from colorama import Fore, Style
import keyboard
from src.attack import Attacker  # Your attack module
from src.resource_collector import ResourceCollector  # Resource collection module
from src.troop_trainer import TroopTrainer  # Troop training module

# Global variable to track the automation state
stop_automation = False


def setup_logging():
    colorama.init()

    class ColorFormatter(logging.Formatter):
        def format(self, record):
            if record.levelname == 'INFO':
                record.msg = f"{Fore.GREEN}{record.msg}{Style.RESET_ALL}"
            elif record.levelname == 'WARNING':
                record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
            elif record.levelname == 'ERROR':
                record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
            return super().format(record)

    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter('%(asctime)s - %(levelname)s - %(message)s'))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.FileHandler('automation.log', encoding='utf-8'), handler]
    )
    logging.info("Logging setup complete.")


def stop_on_q_key(event):
    """
    Callback function to stop automation when 'q' is pressed.
    """
    global stop_automation
    if event.name == 'q':
        stop_automation = True
        print("\nStopping automation - Q pressed")
        logging.info("Automation stopped by user (Q key)")


def main():
    global stop_automation
    print("Clash of Clans Automation Starting...")
    setup_logging()

    try:
        collector = ResourceCollector()
        trainer = TroopTrainer()

        gold_threshold = 20
        elixir_threshold = 20
        dark_elixir_threshold = 0
        attacker = Attacker(gold_threshold, elixir_threshold, dark_elixir_threshold)

        troops_to_train = [
            ('barbarian', 50),
        ]

        print("\nMake sure you have:")
        print("1. Game window open and visible")
        print("2. All required screenshots in place")
        print("3. Correct troop training images")
        print("\nPress 'q' at any time to stop the automation")
        input("\nPress Enter to start (then quickly click game window)...")
        time.sleep(3)

        # Hook the keyboard listener for the 'q' key
        keyboard.on_press(stop_on_q_key)

        cycle_count = 1
        while not stop_automation:
            print(f"\nStarting cycle #{cycle_count}")
            try:
                # Collect resources
                collector.collect_resources()
                time.sleep(random.uniform(0.5, 1.0))

                # Train troops
                trainer.train_troops(troops_to_train)
                time.sleep(random.uniform(0.5, 1.0))

                # Find and attack
                attacker.find_and_attack()

                # Wait for a random delay between cycles
                wait_time = random.uniform(2.0, 3.0)
                print(f"\nWaiting {wait_time:.1f} seconds before next cycle...")
                time.sleep(wait_time)
                cycle_count += 1

            except Exception as e:
                print(f"\nError in cycle #{cycle_count}: {str(e)}")
                logging.error(f"Error in cycle #{cycle_count}: {str(e)}")
                time.sleep(5)
                continue

    except Exception as e:
        print(f"\nError during automation: {str(e)}")
        logging.error(f"Automation error: {str(e)}")

    finally:
        # Unhook the keyboard listener
        keyboard.unhook_all()
        print("Automation has been stopped.")


if __name__ == "__main__":
    main()
