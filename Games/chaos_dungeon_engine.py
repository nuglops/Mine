#!/usr/bin/env python3
"""
Chaos Dungeon — Single-file Comedy RPG Engine
Save as: chaos_dungeon_engine.py
Run: python chaos_dungeon_engine.py

Features:
- Single-file, modular design (functions as "engine" hooks)
- Replayable with multiple endings
- Random room generator
- Stupid-but-functional combat system with stats
- Blobbo companion that evolves (and gets worse)
- ASCII art title and sound-effect stubs
- Plenty of places to drop your own rooms, enemies, and endings
"""

import random
import sys
import time

# ---------------------------
# Utility / Presentation
# ---------------------------
def slow_print(text, delay=0.02):
    """Optional flourished printing (can be turned off by setting delay=0)."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        if delay:
            time.sleep(delay)
    print()

def play_sound(effect_name):
    """Stub for 'sound effects' — replace with audio calls if desired."""
    print(f"*sound effect: {effect_name}*")

def ascii_title():
    print(r"""
   ____ _   _    _    ____   ___   ____  
  / ___| | | |  / \  |  _ \ / _ \ / ___| 
 | |   | |_| | / _ \ | | | | | | | |     
 | |___|  _  |/ ___ \| |_| | |_| | |___  
  \____|_| |_/_/   \_\____/ \___/ \____| 
        CHAOS DUNGEON – PYTHON EDITION
    """)
    print("Welcome to the engine. Tip: press Ctrl+C to quit at any time.\n")

# ---------------------------
# Game Data (customize me)
# ---------------------------

ROOMS = [
    "a room filled with inflatable ducks slowly bouncing into each other.",
    "a tiny chamber where a mime is trapped inside an invisible box… and he’s furious.",
    "a hallway where every torch whispers your name in a sultry voice.",
    "a cavern with a vending machine that only sells disappointment.",
    "a library where all the books scream when opened.",
    "a room full of goblins arguing about cryptocurrency.",
    "a pit where frogs perform slam poetry about heartbreak.",
    "a room containing a single chair, but Blobbo glares at it suspiciously."
]

COMPANION_DIALOGUE = [
    "“Hi! I am Blobbo, destroyer of nothing in particular!”",
    "“I once lost a staring contest to a potato.”",
    "“Warning: I am extremely unhelpful.”",
    "“I offer zero emotional support.”"
]

BLOBBO_ADVICE = [
    "“Always scream at spiders. They respect dominance.”",
    "“If something tries to eat you, just politely decline.”",
    "“Never trust a chair. They’re always just *sitting* there.”",
    "“If we die, can I have your socks?”"
]

SILLY_ENEMIES = [
    {"name": "Angry Goose", "health": 10, "attack": 3},
    {"name": "Passive-Aggressive Slime", "health": 8, "attack": 2},
    {"name": "Hyped-Up Squirrel", "health": 6, "attack": 4},
    {"name": "Disgruntled Lobster", "health": 12, "attack": 3},
]

ENDINGS = [
    ("You walk away from the dungeon, burrito crumbs trailing behind you.", "neutral"),
    ("You were defeated by something profoundly stupid.", "bad"),
    ("You convinced a noodle wyrm to open a noodle restaurant instead of eating you.", "good"),
    ("Blobbo evolved into an eldritch soup god and politely asked you to leave.", "weird")
]

# ---------------------------
# Engine Core: Entities
# ---------------------------
def create_player():
    return {"health": 20, "attack": 5, "name": "You", "inventory": ["half-eaten burrito"]}

def create_blobbo():
    # form = 1 (baby blobbo) -> higher numbers = worse & stronger
    return {"name": "Blobbo", "form": 1, "attack": 2}

# ---------------------------
# Blobbo evolution system
# ---------------------------
def blobbo_evolve(blobbo):
    blobbo["form"] += 1
    form = blobbo["form"]

    if form == 2:
        slow_print("\nBlobbo begins vibrating violently...")
        slow_print("Blobbo evolved into **Blobbo Supreme**, now 20% more unhinged.")
        blobbo["attack"] = 4

    elif form == 3:
        slow_print("\nBlobbo is glowing. This seems bad.")
        slow_print("Blobbo evolved into **Mega Blobbo**, radiating chaotic energy.")
        blobbo["attack"] = 6

    elif form >= 4:
        slow_print("\nOh no. Blobbo is levitating.")
        slow_print("Blobbo evolved into **Eldritch Blobbo**, whispering forbidden soup recipes.")
        blobbo["attack"] = 8

# ---------------------------
# Encounters: battle and events
# ---------------------------
def silly_enemy_encounter(player, blobbo):
    enemy = random.choice([dict(e) for e in SILLY_ENEMIES])  # copy to avoid mutation
    slow_print(f"\nA wild {enemy['name']} appears! (HP: {enemy['health']}, ATK: {enemy['attack']})", 0.01)
    play_sound("enemy_appearance")

    while enemy["health"] > 0 and player["health"] > 0:
        print(f"\nYour HP: {player['health']}   Blobbo(form {blobbo['form']}) ATK: {blobbo['attack']}")
        action = input("Fight (f) / Blobbo tries (b) / Use item (i) : ").lower().strip()

        if action == "f":
            enemy["health"] -= player["attack"]
            slow_print(f"You bonk the {enemy['name']} for {player['attack']} damage! It has {max(enemy['health'],0)} HP left.")
        elif action == "b":
            enemy["health"] -= blobbo["attack"]
            slow_print(f"Blobbo flops into the {enemy['name']} and deals {blobbo['attack']} damage.")
        elif action == "i":
            if player["inventory"]:
                item = player["inventory"].pop(0)
                slow_print(f"You use {item}. It… mostly helps your dignity. +3 HP")
                player["health"] += 3
            else:
                slow_print("You have nothing useful. Blobbo suggests staring dramatically.")
        else:
            slow_print("Confused actions lead to chaotic outcomes: you trip over a thought and lose 1 HP.")
            player["health"] -= 1

        # Enemy strikes back if alive
        if enemy["health"] > 0:
            player["health"] -= enemy["attack"]
            slow_print(f"The {enemy['name']} hits back for {enemy['attack']} damage! You now have {max(player['health'],0)} HP.")

    if player["health"] <= 0:
        slow_print("\nYou collapse dramatically. The dungeon is mildly inconvenienced.")
        play_sound("player_death")
        return False  # player died

    slow_print(f"\nYou defeated the {enemy['name']}! Blobbo cheers awkwardly.")
    play_sound("enemy_defeat")
    # Blobbo evolves after victory
    blobbo_evolve(blobbo)
    return True

# ---------------------------
# Random rooms generator
# ---------------------------
def random_room_sequence(player, blobbo):
    slow_print("\nBlobbo: 'Welp, time to wander deeper! What’s the worst that could happen?'")
    steps = 0
    while True:
        enter = input("\nEnter the next room? (y/n): ").lower().strip()
        if enter != "y":
            slow_print("\nBlobbo: 'Retreat? Cowardice is a valid strategy. I respect it.'")
            return "retreat"  # returns reason to trigger next stage (e.g. boss)

        steps += 1
        slow_print("\nYou step forward and the dungeon shifts around you...")
        slow_print("You enter: " + random.choice(ROOMS))
        print(random.choice([
            "Blobbo gasps dramatically.",
            "Blobbo boos loudly.",
            "Blobbo tries to fight the air.",
            "Blobbo whispers, 'This place has bad vibes.'",
            "Blobbo starts humming ominously.",
            "Blobbo hides behind your ankle."
        ]))

        # Random chance of enemy encounter
        if random.random() < 0.35:  # 35% chance
            survived = silly_enemy_encounter(player, blobbo)
            if not survived:
                return "dead"
        # Random chance of bizarre item find
        if random.random() < 0.25:
            item = random.choice(["rubber chicken", "sock of ambiguity", "mystery key"])
            player["inventory"].append(item)
            slow_print(f"You found a {item}! Blobbo judges it immediately.")

        # After a bunch of rooms there's a chance dungeon clamps shut and forces finale
        if steps >= 4 and random.random() < 0.25:
            slow_print("\nThe dungeon hums… something in the depths has noticed you.")
            return "force_boss"

# ---------------------------
# Boss battle: The Great Noodle Wyrm
# ---------------------------
def noodle_wyrm_battle(player, blobbo):
    slow_print("\nThe dungeon rumbles... The walls peel away like wet stickers.")
    slow_print("Blobbo: 'Uh oh. I think we triggered the finale.'")
    slow_print("\nA gigantic swirling vortex of spaghetti rises before you!")
    slow_print("It screeches: 'I AM THE GREAT NOODLE WYRM, DEVOURER OF CARBS!'")
    play_sound("boss_theme")

    wyrm_hp = 30
    while wyrm_hp > 0 and player["health"] > 0:
        action = input("\nDo you (a) attack, (b) throw your burrito, (c) let Blobbo handle it, (d) try diplomacy? ").lower().strip()
        if action == "a":
            damage = player["attack"]
            wyrm_hp -= damage
            slow_print(f"You punch noodles for {damage} damage. Wyrm HP: {max(wyrm_hp,0)}")
            play_sound("punch_noodles")
        elif action == "b":
            if "half-eaten burrito" in player["inventory"]:
                player["inventory"].remove("half-eaten burrito")
                slow_print("You hurl your half-eaten burrito with the force of a thousand regrets.")
                slow_print("The Noodle Wyrm devours it… then instantly falls asleep.")
                play_sound("snore")
                return "wyrm_asleep"
            else:
                slow_print("You have no burrito. Blobbo sniffs the air sadly.")
                player["health"] -= 2
        elif action == "c":
            slow_print("Blobbo steps forward confidently.")
            slow_print("Blobbo: 'Stand back. I was born for this… I think.'")
            slow_print("Blobbo challenges the Wyrm to a staring contest.")
            # Blobbo has a probabilistic effect based on form
            chance = 0.4 + 0.15 * (blobbo["form"] - 1)
            if random.random() < chance:
                slow_print("The Wyrm loses. Instantly. Noodles wilt everywhere.")
                play_sound("victory_barf")
                return "blobbo_stare_win"
            else:
                slow_print("The Wyrm blinks and flails. You take 4 damage.")
                player["health"] -= 4
        elif action == "d":
            slow_print("You try diplomacy. You wax philosophical about carbohydrates.")
            if random.random() < 0.5:
                slow_print("The Wyrm seems moved. 'No more eating today,' it says, and wanders off.")
                return "diplomacy_success"
            else:
                slow_print("The Wyrm is unimpressed and slaps you with al dente fury.")
                player["health"] -= 6
        else:
            slow_print("Confusion. You slip on a noodle and lose 1 HP.")
            player["health"] -= 1

        # Wyrm attacks occasionally
        if wyrm_hp > 0:
            slow_print("The Wyrm lunges and smacks you with a saucy tail.")
            player["health"] -= 3
            slow_print(f"You have {max(player['health'],0)} HP left.")

    if player["health"] <= 0:
        slow_print("\nYou have been reduced to a puddle of regret and parmesan.")
        return "dead"

    slow_print("\nThe Noodle Wyrm retreats in confusion. You win by baffling it.")
    return "wyrm_defeated"

# ---------------------------
# Endings & Replay
# ---------------------------
def ending_screen(reason_key):
    # Map reason string to an ending message
    mapping = {
        "retreat": ENDINGS[0][0],
        "dead": ENDINGS[1][0],
        "wyrm_asleep": ENDINGS[2][0],
        "blobbo_stare_win": ENDINGS[3][0],
        "diplomacy_success": "You and the Wyrm open a small noodle bistro together. Business is okay.",
        "wyrm_defeated": "You defeated the Wyrm through sheer nonsense and questionable bravery. The court of carbs is baffled."
    }
    message = mapping.get(reason_key, "You escaped in an oddly unsatisfying manner.")
    slow_print("\n===== CHAOS DUNGEON ENDING =====")
    slow_print(message)
    slow_print("Blobbo: 'Wow. Choices were made.'")
    slow_print("===============================\n")

# ---------------------------
# Intro & Companion
# ---------------------------
def game_intro():
    ascii_title()
    slow_print("You wake up wearing mismatched socks and holding a mysterious half-eaten burrito.\n")
    slow_print("Two doors wobble in front of you like they're trying to vibe to music only they can hear.\n")
    choice = input("Do you pick door (1) or door (2)? ").strip()
    if choice == "1":
        slow_print(random.choice([
            "A raccoon in a wizard robe challenges you to rock-paper-scissors.",
            "A time-traveling potato appears and demands tax documents.",
            "A chicken riding a Roomba zooms past, screaming 'THE PROPHECY!'",
            "You fall into a pit of marshmallows. They are sentient. They judge you."
        ]))
    else:
        slow_print(random.choice([
            "A disco-ball golem asks if you know how to dance the forbidden tango.",
            "A goblin gives you a motivational speech about personal growth.",
            "A swarm of bees forms into the shape of a middle finger.",
            "You meet a ghost who's mad because someone ate his leftovers."
        ]))

    slow_print("\nAs the weirdness settles, a small blob creature oozes out of your burrito.")
    slow_print(random.choice(COMPANION_DIALOGUE))
    slow_print("\nBlobbo tries to climb onto your shoulder but falls off immediately for no reason.")
    input("\nBlobbo stares at you intensely. Press ENTER to receive unwanted advice...")
    slow_print(random.choice(BLOBBO_ADVICE))

# ---------------------------
# Main game flow (ties engine together)
# ---------------------------
def play_one_run():
    player = create_player()
    blobbo = create_blobbo()

    # initial state
    game_intro()

    # Give the player's inventory the burrito (we keep it simple)
    if "half-eaten burrito" not in player["inventory"]:
        player["inventory"].insert(0, "half-eaten burrito")

    # Random rooms / wandering
    result = random_room_sequence(player, blobbo)
    if result == "dead":
        ending_screen("dead")
        return

    # If the player retreated or dungeon forced boss, go to boss
    slow_print("\nThe dungeon pulls you toward a final confrontation…")
    boss_result = noodle_wyrm_battle(player, blobbo)

    # Final handling / endings
    if boss_result == "dead":
        ending_screen("dead")
    elif boss_result == "wyrm_asleep":
        ending_screen("wyrm_asleep")
    elif boss_result == "blobbo_stare_win":
        ending_screen("blobbo_stare_win")
    elif boss_result == "diplomacy_success":
        ending_screen("diplomacy_success")
    elif boss_result == "wyrm_defeated":
        ending_screen("wyrm_defeated")
    else:
        ending_screen("retreat")

# ---------------------------
# Reusable Engine Hooks (for you)
# ---------------------------
# If you want to use this file as an engine in other scripts, call `play_one_run()`.
# You can override data by importing and changing ROOM, ENEMY, etc., or extend functions:
# - Add new rooms to ROOMS
# - Add enemies to SILLY_ENEMIES
# - Modify blobbo_evolve() to change evolution behavior
# - Replace play_sound() with real audio playing implementation

# ---------------------------
# CLI / Replay loop
# ---------------------------
def main():
    try:
        while True:
            play_one_run()
            again = input("\nPlay again? (y/n): ").lower().strip()
            if again != "y":
                slow_print("\nThanks for playing Chaos Dungeon! Farewell, brave burrito-bearer.")
                break
            else:
                slow_print("\n--- RESTARTING THE CHAOS ---\n")
    except KeyboardInterrupt:
        slow_print("\n\nSession ended. Blobbo politely waves its appendage. Goodbye!")

if __name__ == "__main__":
    main()
