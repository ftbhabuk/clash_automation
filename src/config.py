# Define image paths and cooldowns
IMAGE_PATHS = {
    'collectors': {
        'gold': 'game_images/collectors/full_gold.png',
        'elixir': 'game_images/collectors/full_elixir.png',
        # 'dark_elixir': 'game_images/collectors/full_dark_elixir.png'
    },
    'training': {
        'open_training_menu': 'game_images/training/open_training_menu.png',  # Step 1
        'train_army_button': 'game_images/training/train_army_button.png',  # Step 2
        'close_training_menu': 'game_images/training/close_button.png',  # Close
        'queue_full_message': 'game_images/training/queue_full.png',
        'quick_train_button': 'game_images/training/quick_train.png',
        'quick_train_army1': 'game_images/training/quick_train_army1.png',
        'troops': {
            'barbarian': 'game_images/training/troops/barbarian.png',
            'archer': 'game_images/training/troops/archer.png',
            'giant': 'game_images/training/troops/giant.png',
            'goblin': 'game_images/training/troops/goblin.png',
            # Add more troops as needed
        }
    },
    'attack': {
        'attack_button': 'game_images/attack/attack_button.png',  # Home village attack button
        'find_match': 'game_images/attack/find_match.png',  # Find a match button
        'next_button': 'game_images/attack/next_button.png',  # Next button during scouting
        'troop_deployment_area': 'game_images/attack/troop_deployment_area.png',  # Deployment area
        'return_home': 'game_images/attack/return_home.png',
    },

    'upgrade': {
        'builder_icon': 'game_images/upgrade/builder_icon.png'
    },
    'resources': {
        'gold': 'game_images/resources/gold_icon.png',
        'elixir': 'game_images/resources/elixir_icon.png',
    }

}

COOLDOWNS = {
    'collection': 300,  # 5 minutes
    'training': 60  # 1 minute
}
