import random
import time
import os 

def clear_screen(): # <<<< REPLACE THIS FUNCTION
    """Clears the terminal screen."""
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux (os.name is 'posix')
    else:
        _ = os.system('clear')


# --- Helper Functions ---
def print_slow(text, delay=0.03):
    """Prints text slowly, as if typed."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


# --- Game Classes ---
class Character:
    def __init__(self, name, hp, attack, defense=0):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack_power = attack
        self.defense = defense

    def is_alive(self):
        return self.hp > 0

    def attack(self, target):
        damage = self.attack_power - target.defense
        if damage < 0:
            damage = 0 # Cannot heal with an attack
        target.hp -= damage
        print_slow(f"{self.name} attacks {target.name} for {damage} damage!")
        if not target.is_alive():
            print_slow(f"{target.name} has been defeated!")
        return damage

    def show_stats(self):
        print_slow(f"--- {self.name} ---")
        print_slow(f"HP: {self.hp}/{self.max_hp}")
        print_slow(f"Attack: {self.attack_power}")
        print_slow(f"Defense: {self.defense}")
        print_slow("-----------------")

class Player(Character):
    def __init__(self, name, hp, attack, defense=0):
        super().__init__(name, hp, attack, defense)
        self.inventory = []
        self.current_room = None
        self.xp = 0
        self.level = 1

    def add_item(self, item_name):
        self.inventory.append(item_name)
        print_slow(f"{item_name} added to inventory.")

    def has_item(self, item_name):
        return item_name in self.inventory

    def use_item(self, item_name):
        if item_name == "health potion":
            if self.has_item("health potion"):
                heal_amount = 20
                self.hp = min(self.max_hp, self.hp + heal_amount)
                self.inventory.remove("health potion")
                print_slow(f"You used a health potion and healed {heal_amount} HP.")
                self.show_stats()
            else:
                print_slow("You don't have any health potions.")
        else:
            print_slow(f"You can't use {item_name} like that.")

    def gain_xp(self, amount):
        self.xp += amount
        print_slow(f"You gained {amount} XP!")
        # Simple leveling: 100 XP to level up
        if self.xp >= 100 * self.level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp = 0 # Reset XP for next level or carry over self.xp -= 100 * (self.level -1)
        self.max_hp += 10
        self.hp = self.max_hp # Full heal on level up
        self.attack_power += 2
        self.defense +=1
        print_slow(f"Congratulations! You reached Level {self.level}!")
        print_slow("Your stats have increased!")
        self.show_stats()


class Enemy(Character):
    def __init__(self, name, hp, attack, defense=0, xp_reward=10, drops=None):
        super().__init__(name, hp, attack, defense)
        self.xp_reward = xp_reward
        self.drops = drops if drops else [] # e.g., ["health potion"]

# --- Room/Level Definition ---
class Room:
    def __init__(self, name, description, enemy=None, item_to_find=None, requires_item=None):
        self.name = name
        self.description = description
        self.enemy = enemy # Enemy object or None
        self.item_to_find = item_to_find # Item name string or None
        self.item_found = False # Track if item in this room has been taken
        self.exits = {} # e.g., {"north": room_object, "south": room_object_2}
        self.requires_item = requires_item # e.g., "key" to enter

    def add_exit(self, direction, room):
        self.exits[direction.lower()] = room

    def describe(self):
        clear_screen()
        print_slow(f"\n--- {self.name} ---")
        print_slow(self.description)
        if self.enemy and self.enemy.is_alive():
            print_slow(f"A wild {self.enemy.name} blocks your path!")
        elif self.item_to_find and not self.item_found:
            print_slow(f"You see a {self.item_to_find} here.")
        print_slow("Exits: " + ", ".join(self.exits.keys()))

# --- Game Setup ---
def setup_game():
    # Create Player
    player_name = input("Enter your hero's name: ")
    player = Player(player_name, hp=50, attack=10, defense=2)

    # Create Enemies
    goblin = Enemy("Goblin", hp=20, attack=5, defense=1, xp_reward=20, drops=["health potion"])
    orc = Enemy("Orc Grunt", hp=40, attack=8, defense=3, xp_reward=50)
    troll_guard = Enemy("Troll Guard", hp=70, attack=12, defense=5, xp_reward=80, drops=["rusty key"])
    dragon_boss = Enemy("Red Dragon", hp=150, attack=20, defense=8, xp_reward=200)

    # Create Rooms
    village = Room("Quiet Village", "A peaceful village, though strangely quiet. The path north leads to the forest.")
    forest_entrance = Room("Forest Entrance", "The trees loom ominously. You hear rustling deeper in.", enemy=goblin)
    deep_forest = Room("Deep Forest", "It's dark and damp. An orc is patrolling here.", enemy=orc, item_to_find="health potion")
    cave_mouth = Room("Cave Mouth", "A dark cave entrance. A sturdy-looking Troll guards it.", enemy=troll_guard, requires_item=None) # No item required to initially see the troll
    treasure_chamber = Room("Treasure Chamber", "A hoard of glittering gold... and a massive Red Dragon!", enemy=dragon_boss)
    victory_hall = Room("Victory Hall", "The dragon is slain! You are a true hero!")

    # Link Rooms (Exits)
    village.add_exit("north", forest_entrance)

    forest_entrance.add_exit("south", village)
    forest_entrance.add_exit("east", deep_forest)

    deep_forest.add_exit("west", forest_entrance)
    deep_forest.add_exit("north", cave_mouth)

    cave_mouth.add_exit("south", deep_forest)
    # The exit to treasure_chamber will be conditional on having the 'rusty key'

    player.current_room = village
    return player

# --- Combat Function ---
def combat(player, enemy):
    print_slow(f"\n--- COMBAT START: {player.name} vs {enemy.name} ---")
    enemy.show_stats() # Show enemy stats at start of combat

    while player.is_alive() and enemy.is_alive():
        player.show_stats()
        action = input("Choose action: [A]ttack, [U]se item, [R]un: ").lower()

        if action == 'a':
            player.attack(enemy)
            if enemy.is_alive():
                enemy.attack(player)
        elif action == 'u':
            if player.inventory:
                print("Your inventory:", ", ".join(player.inventory))
                item_to_use = input("Which item to use? (Type name or 'cancel'): ").lower()
                if item_to_use != 'cancel':
                    player.use_item(item_to_use)
                    # Enemy still gets a turn if player used an item
                    if enemy.is_alive():
                        enemy.attack(player)
            else:
                print_slow("Your inventory is empty.")
                # Penalty: enemy still attacks if you fumbled with empty inventory
                if enemy.is_alive():
                     enemy.attack(player)
        elif action == 'r':
            if random.random() < 0.5: # 50% chance to escape
                print_slow("You successfully fled!")
                return "fled"
            else:
                print_slow("You failed to escape!")
                enemy.attack(player)
        else:
            print_slow("Invalid action. Try again.")
            # Penalty: enemy attacks if you enter invalid command
            if enemy.is_alive():
                 enemy.attack(player)

        if not player.is_alive():
            print_slow("You have been defeated... Game Over.")
            return "player_dead"
        if not enemy.is_alive():
            print_slow(f"{enemy.name} was vanquished!")
            player.gain_xp(enemy.xp_reward)
            for item in enemy.drops:
                player.add_item(item)
            return "enemy_dead"
    return "error" # Should not happen

# --- Main Game Loop ---
def game_loop(player):
    print_slow("Welcome to the Simple RPG Adventure!", delay=0.05)
    print_slow("Type 'help' for commands.", delay=0.05)

    while player.is_alive():
        current_room = player.current_room
        current_room.describe()

        # Handle combat if an enemy is present and alive
        if current_room.enemy and current_room.enemy.is_alive():
            combat_result = combat(player, current_room.enemy)
            if combat_result == "player_dead":
                break # Exit game loop
            elif combat_result == "enemy_dead":
                current_room.enemy = None # Enemy is now gone from this room
                # Special condition for Troll Guard dropping key for Treasure Chamber
                if current_room.name == "Cave Mouth" and not player.has_item("rusty key"):
                    # The Troll Guard drops the key, which is handled by enemy.drops
                    # Now we can add the exit if the key was indeed dropped and picked up.
                    if player.has_item("rusty key"):
                         print_slow("The Troll dropped a 'rusty key'! It might unlock something...")
                         current_room.add_exit("enter chamber", treasure_chamber) # Dynamically add exit
                continue # Re-describe room now that enemy is gone
            elif combat_result == "fled":
                # If fled, player might move back. For simplicity, stay in room but re-describe.
                # A more complex system could move player to previous room.
                continue

        # Check for win condition
        if current_room.name == "Victory Hall":
            print_slow("\nCONGRATULATIONS! You have completed the game!")
            break

        command = input("\nWhat do you do? (e.g., 'go north', 'look', 'get item', 'inventory', 'stats', 'help', 'quit'): ").lower().split()

        if not command:
            continue

        action = command[0]

        if action == "quit":
            print_slow("Thanks for playing!")
            break
        elif action == "help":
            print_slow("\n--- Available Commands ---")
            print_slow("go [direction]  - Move to another room (e.g., 'go north')")
            print_slow("look            - Describe the current room again")
            print_slow("get [item name] - Pick up an item (e.g., 'get health potion')")
            print_slow("inventory       - Show your inventory")
            print_slow("use [item name] - Use an item from your inventory (e.g., 'use health potion')")
            print_slow("stats           - Show your current stats")
            print_slow("quit            - Exit the game")
        elif action == "look":
            continue # Loop will re-describe
        elif action == "stats":
            player.show_stats()
        elif action == "inventory":
            if player.inventory:
                print_slow("Your inventory: " + ", ".join(player.inventory))
            else:
                print_slow("Your inventory is empty.")
        elif action == "use":
            if len(command) > 1:
                item_to_use = " ".join(command[1:])
                player.use_item(item_to_use)
            else:
                print_slow("Use what?")

        elif action == "get":
            if len(command) > 1:
                item_name_parts = command[1:]
                item_to_get = " ".join(item_name_parts)
                if current_room.item_to_find == item_to_get and not current_room.item_found:
                    player.add_item(item_to_get)
                    current_room.item_found = True
                    current_room.item_to_find = None # Item is gone from room
                elif current_room.item_found and current_room.item_to_find is None: # check if item was already taken
                    print_slow(f"There is no {item_to_get} here to get, or it's already taken.")
                else:
                    print_slow(f"There is no {item_to_get} here.")
            else:
                print_slow("Get what?")

        elif action == "go":
            if len(command) > 1:
                direction = command[1]
                if direction in current_room.exits:
                    next_room = current_room.exits[direction]
                    # Check if the next room requires an item
                    if next_room.requires_item and not player.has_item(next_room.requires_item):
                        print_slow(f"You need a '{next_room.requires_item}' to go that way.")
                    else:
                        player.current_room = next_room
                        # Special condition for entering Victory Hall
                        if next_room.name == "Treasure Chamber" and next_room.enemy is None: # Dragon defeated
                            player.current_room = victory_hall # Automatically move to victory
                # Special dynamic exit for treasure chamber
                elif direction == "enter" and "chamber" in command and current_room.name == "Cave Mouth":
                    if player.has_item("rusty key"):
                        if "enter chamber" in current_room.exits: # Check if exit was added
                            player.current_room = current_room.exits["enter chamber"]
                        else: # This case should ideally not be hit if logic is correct
                            print_slow("You try the key, but the way is not yet open...")
                    else:
                        print_slow("The way is barred. You might need something to open it.")
                else:
                    print_slow(f"You can't go {direction} from here.")
            else:
                print_slow("Go where?")
        else:
            print_slow("Unknown command. Type 'help' for a list of commands.")

        time.sleep(0.5) # Small delay to make reading easier

    if not player.is_alive():
        print_slow("\n--- GAME OVER ---", delay=0.05)

# --- Start the Game ---
if __name__ == "__main__":
    player_character = setup_game()
    game_loop(player_character)