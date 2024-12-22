import logging
import time
import random
from src.resource_collector import ResourceCollector
from src.troop_trainer import TroopTrainer

# Configure logging
def setup_logging():
    logging.basicConfig(
        filename='automation.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Logging setup complete.")

# main.py
def main():
    print("🎮 Clash of Clans Automation Starting...")
    setup_logging()

    collector = ResourceCollector()
    trainer = TroopTrainer()

    troops_to_train = [
        ('barbarian', 5),
        # ('archer', 3)
    ]

    print("\n⚠️ Make sure you have:")
    print("1. Game window open and visible")
    print("2. All required screenshots in place")
    print("3. Correct troop training images in game_images/training/troops/")
    input("\n▶️ Press Enter to start (then quickly click on the game window)...")
    time.sleep(3)

    cycle_count = 1
    try:
        while True:
            print(f"\n📍 Starting cycle #{cycle_count}")

            collector.collect_resources()
            time.sleep(random.uniform(0.5, 1.0))  # Faster delay

            trainer.train_troops(troops_to_train)

            wait_time = random.uniform(2.0, 3.0)  # Shorter wait between cycles
            print(f"\n⏳ Waiting {wait_time:.1f} seconds before next cycle...")
            time.sleep(wait_time)

            cycle_count += 1

    except KeyboardInterrupt:
        print("\n🛑 Stopping automation - User interrupted")
        logging.info("Automation stopped by user")
    except Exception as e:
        print(f"\n❌ Error during automation: {str(e)}")
        logging.error(f"Automation error: {str(e)}")


if __name__ == "__main__":
    main()
