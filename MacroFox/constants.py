# constants.py

MATERIALS = [
    "Sprinkler_Builder", "Gumdrops", "Coconut", "Stinger", "Snowflake", "Jelly_Beans",
    "Red_Extract", "Blue_Extract", "Glitter", "Glue", "Oil", "Enzymes", "Tropical_Drink",
    "Purple_Potion", "Super_Smoothie", "Marshmallow_Bee", "Magic_Bean"
]

MATERIAL_INFO = {
    "Blue_Extract": "Grants x1.25 Blue Pollen for 10 minutes.",
    "Cloud_Vial": "Summons a Cloud in the field you're standing in. Lasts for 3 minutes.",
    "Coconut": "Drops a huge Coconut into the field. Catch it to convert pollen to Honey Tokens.",
    "Enzymes": "Grants +10% Instant Conversion and x1.25 Conversion Rate for 10 minutes.",
    "Glitter": "Boosts the field you're standing in, granting +100% pollen for 15 minutes.",
    "Glue": "Grants x1.25 Bee Gather Pollen and Tools for 10 minutes.",
    "Gumdrops": "Use while standing in a field to cover flowers in goo. Goo grants bonus honey.",
    "Jelly_Beans": "Scatters various buff-granting beans on nearby flowers. Works best when shared.",
    "Magic_Bean": "Plants a random Sprout in the field you're standing in.",
    "Marshmallow_Bee": "50% White Pollen, +50% Capacity, and +250% Conversion Rate for 30 minutes.",
    "Micro-Converter": "Instantly converts all Pollen in your bag to Honey.",
    "Oil": "Grants x1.2 Bee and Player Movespeed for 10 minutes.",
    "Purple_Potion": "Grants x1.25 Capacity, x1.25 Convert Rate At Hive, x1.5 Red Pollen, x1.5 Blue Pollen, x1.3 Bee Gather Pollen, and x1.3 Pollen From Tools for 15 minutes.",
    "Red_Extract": "Grants x1.25 Red Pollen for 10 minutes.",
    "Snowflake": "Sends a cool, soothing breeze to all the players on the server (Melts after Beesmas!)",
    "Sprinkler_Builder": "Use while standing in flowers to place a Sprinkler.",
    "Stinger": "Grants your bees x1.5 attack for 30 seconds.",
    "Super_Smoothie": "Grants x1.5 Capacity, x1.6 Red Pollen, x1.6 Blue Pollen, x1.6 White Pollen, x1.4 Bee Gather Pollen, x1.4 Pollen From Tools, x2 Convert Rate, x1.5 Convert Rate At Hive, +12% Instant Conversion, +7% Critical Chance, x1.25 Bee Movespeed, and x1.25 Player Movespeed for 20 minutes.",
    "Tropical_Drink": "Grants x1.25 White Pollen and +5% Critical Chance for 10 minutes.",
}

MATERIAL_TIMER = {
    "Blue_Extract": 600,
    "Cloud_Vial": 180,
    "Coconut": 1,
    "Enzymes": 600,
    "Glitter": 910,
    "Glue": 600,
    "Gumdrops": 1,
    "Jelly_Beans": 45,
    "Magic_Bean": 1,
    "Marshmallow_Bee": 1800,
    "Micro-Converter": 15,
    "Oil": 600,
    "Purple_Potion": 900,
    "Red_Extract": 600,
    "Snowflake": 1,
    "Sprinkler_Builder": 5,
    "Stinger": 10,
    "Super_Smoothie": 1200,
    "Tropical_Drink": 600,
}

PRESETS = {
    "Boost": ["Sprinkler_Builder", "Stinger", "Coconut", "Jelly_Beans", "Gumdrops", "Super_Smoothie", "Glitter"],
}

THEMES = {
    "light": {
        "BG": "#FFFFFF",
        "PANEL": "#F0F0F0",
        "SLOT_BG": "#E0E0E0",
        "FONT": "#212121",
        "PRIMARY": "#2196F3",
        "SUCCESS": "#73C277",
        "DANGER": "#F55A4E",
        "WARNING": "#FFC107",
        "HINT": "#616161",
        "THEME_MODE": "light",
    },
    "dark": {
        "BG": "#121212",
        "PANEL": "#1E1E1E",
        "SLOT_BG": "#2A2A2A",
        "FONT": "#E0E0E0",
        "PRIMARY": "#4CAF50",
        "SUCCESS": "#66BB6A",
        "DANGER": "#EF5350",
        "WARNING": "#FFA726",
        "HINT": "#9E9E9E",
        "THEME_MODE": "dark",
    },
    "nothing": {
        "BG": "#000000",
        "PANEL": "#111111",
        "SLOT_BG": "#222222",
        "FONT": "#FFFFFF",
        "PRIMARY": "#D71922",
        "SUCCESS": "#2ECC71",
        "DANGER": "#E74C3C",
        "WARNING": "#F39C12",
        "HINT": "#AAAAAA",
        "THEME_MODE": "dark",
    },
    "pinky": {
        "BG": "#FFF9FB",
        "PANEL": "#FFE8F0",
        "SLOT_BG": "#FFDDEA",
        "FONT": "#C2185B",
        "PRIMARY": "#F06292",
        "SUCCESS": "#81C784",
        "DANGER": "#F48FB1",
        "WARNING": "#FFCC80",
        "HINT": "#CE93D8",
        "THEME_MODE": "light",
    },
}

APP_VERSION = "v1.2"
UPDATE_LOG = [
    "Updated Setting menu to add sliders",
    "App was separated into several .py files instead of one main.py",
    "Added Hotkeys to run / pause / stop",
    "WIP (unreleased). Precision Buff detection",
    #"Nope not yet (WIP).  ̶P̶r̶e̶c̶i̶s̶i̶o̶n̶ ̶B̶u̶f̶f̶ ̶D̶e̶t̶e̶c̶t̶i̶o̶n̶:̶ ̶Y̶o̶u̶ ̶w̶i̶l̶l̶ ̶b̶e̶ ̶n̶o̶t̶i̶f̶i̶e̶d̶ ̶w̶i̶t̶h̶ ̶a̶ ̶s̶o̶u̶n̶d̶ ̶i̶f̶ ̶y̶o̶u̶ ̶a̶r̶e̶ ̶r̶u̶n̶n̶i̶n̶g̶ ̶o̶u̶t̶ ̶o̶f̶ ̶y̶o̶u̶ ̶p̶r̶e̶c̶i̶s̶e̶ ̶b̶o̶o̶s̶t̶.̶ ̶N̶o̶ ̶n̶e̶e̶d̶ ̶t̶o̶ ̶c̶h̶e̶c̶k̶ ̶y̶o̶u̶r̶ ̶p̶r̶e̶c̶i̶s̶i̶o̶n̶ ̶b̶o̶o̶s̶t̶ ̶a̶n̶y̶m̶o̶r̶e̶!̶",
    ]
APP_TIPS = [
    "🚫 Long-press slot to clear",
    "💡 Single-click slot to disable it",
    "🔊 Make sure to turn on sounds, when you play with Precision Detector",
    "⌨️ Hotkeys: F1=Start, F2=Pause/Resume, F3=Stop",
    "📁 All save files are stored at \nC:\\Documents\\MacroFox"
]

BORDER_RADIUS = 6