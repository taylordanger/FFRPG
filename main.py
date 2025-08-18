import os
import random
import time
from typing import Dict, List, Tuple
import tkinter as tk
from tkinter import ttk


class FFRPG:
    def __init__(self):
        self.player = Player("FishMan MckFriendly", 0, 0)
        self.grid_size = 10
        self.fishfinder_grid = self.create_empty_grid_ff()
        self.overhead_grid = self.create_empty_grid_OH()
        self.current_rod = None
        self.current_leader = None
        self.current_fly = None
        self.current_location = None
        
    def create_empty_grid_OH(self):
        grid = []
        for _ in range(self.grid_size):
            grid.append(['0'] * self.grid_size)
        return grid
    
    def create_empty_grid_ff(self):
        # Use 0 for water, . for land
        grid = []
        for _ in range(self.grid_size):
            grid.append(['0'] * self.grid_size)
        return grid
    
    def generate_location(self, location_type):
        # Reset grids
        self.fishfinder_grid = self.create_empty_grid_ff()
        self.overhead_grid = self.create_empty_grid_OH()

        # Generate land features based on location type
        if location_type == "river":
            self._generate_river()
        elif location_type == "lake":
            self._generate_lake()
        elif location_type == "stream":
            self._generate_stream()
        
        # Copy to overhead view
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                self.overhead_grid[y][x] = self.create_empty_grid_OH()[y][x]
                
        
        self.current_location = location_type

    def generate_fish(self):
        # Generate fish in the fishfinder grid
        for _ in range(random.randint(5, 10)):
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            self.fishfinder_grid[y][x] = 'F'

    def _generate_river(self):
        # Create river banks (land)
        for y in range(self.grid_size):
            # Left bank
            for x in range(random.randint(1, 3)):
                self.fishfinder_grid[y][x] = '.'
            
            # Right bank
            for x in range(self.grid_size - random.randint(1, 3), self.grid_size):
                self.fishfinder_grid[y][x] = '.'
    
    def _generate_lake(self):
        # Create shoreline
        for y in range(self.grid_size):
            if y < 2 or y > self.grid_size - 3:
                # Top and bottom shorelines
                for x in range(self.grid_size):
                    if random.random() < 0.7:
                        self.fishfinder_grid[y][x] = '.'
    
    def _generate_stream(self):
        # Create meandering path
        center_x = self.grid_size // 2
        for y in range(self.grid_size):
            center_x += random.randint(-1, 1)
            center_x = max(3, min(center_x, self.grid_size - 4))  # Keep in bounds
            
            # Stream width varies between 3-5 cells
            width = random.randint(3, 5)
            left_bank = center_x - width // 2
            right_bank = center_x + width // 2
            
            # Mark banks as land
            for x in range(self.grid_size):
                if x < left_bank or x > right_bank:
                    self.fishfinder_grid[y][x] = '.'
    
    def display_game(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Top border and header
        print("#" * 83)
        print(" " * 32 + "FFRPG:FlyFlishingRPG")
        print("#" * 83)
        
        # Player info and equipment
        print(f"Fisherman: {self.player.name}" + " " * 10 + 
              f"Flyrod: {self.current_rod or ''}" + " " * 18 + 
              f"Fly: {self.current_fly or ''}")
        
        print(f"lvl: {self.player.level} xp: {self.player.xp:06d} total fish: {len(self.player.catch_record)}" + " " * 6 +
              f"Leader: {self.current_leader or ''}" + " " * 18 + 
              f"Location: {self.current_location or ''}")
        
        print("-" * 83)
        
        # Grid headers
        print("---------------fishfinder----------------|---------------OverHead--------------------")
        print(" " * 40 + "|")
        
        # Column labels
        print("      a  b  c  d  e  f  g  h  i  j       |            a  b  c  d  e  f  g  h  i  j")
        
        # Display both grids side by side
        for y in range(self.grid_size):
            # Left grid (fishfinder)
            left_row = f"    {y+1} "
            for x in range(self.grid_size):
                left_row += f"{self.fishfinder_grid[y][x]}  "
            
            # Right grid (overhead)
            right_row = f"          {y+1} "
            for x in range(self.grid_size):
                right_row += f"{self.overhead_grid[y][x]}  "
            
            print(f"{left_row}      |{right_row}")
        
        print("\n" + "#" * 83)
    
    def build_leader(self):
        print("\nBuild Your Leader")
        print("-" * 30)
        
        # Leader line options
        line_types = ["Fluorocarbon", "Monofilament", "Braided"]
        print("\nSelect leader line type:")
        for i, line in enumerate(line_types, 1):
            print(f"{i}. {line}")
        
        line_choice = input("Enter choice (1-3): ")
        try:
            line_type = line_types[int(line_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Using Monofilament.")
            line_type = "Monofilament"
        
        # Leader tippet diameter
        diameters = ["7X (2.0kg)", "6X (2.5kg)", "5X (3.0kg)", "4X (3.5kg)", "3X (4.5kg)", "2X (6.0kg)", "1X (7.0kg)", "0X (8.0kg)"]
        print("\nSelect tippet diameter:")
        for i, dia in enumerate(diameters, 1):
            print(f"{i}. {dia}")
        
        dia_choice = input("Enter choice (1-8): ")
        try:
            diameter = diameters[int(dia_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Using 5X.")
            diameter = "5X (3.0kg)"
        
        # Leader length
        length = input("\nEnter leader length in feet (7-12): ")
        try:
            length = int(length)
            if length < 7 or length > 12:
                print("Invalid length. Using 9 feet.")
                length = 9
        except ValueError:
            print("Invalid input. Using 9 feet.")
            length = 9
        
        # Create the leader
        self.current_leader = Leader(line_type, diameter, length)
        print(f"\nLeader built: {line_type}, {diameter}, {length} feet")
        input("Press Enter to continue...")
    
    def build_rod(self):
        print("\nBuild Your Fly Rod")
        print("-" * 30)
        
        # Rod length options
        lengths = [7, 8, 9, 10]
        print("\nSelect rod length (feet):")
        for i, length in enumerate(lengths, 1):
            print(f"{i}. {length}'")
        
        length_choice = input("Enter choice (1-4): ")
        try:
            rod_length = lengths[int(length_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Using 9 feet.")
            rod_length = 9
        
        # Rod weight options
        weights = [3, 4, 5, 6, 7, 8]
        print("\nSelect rod weight:")
        for i, weight in enumerate(weights, 1):
            print(f"{i}. {weight}-weight")
        
        weight_choice = input("Enter choice (1-6): ")
        try:
            rod_weight = weights[int(weight_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Using 5-weight.")
            rod_weight = 5
        
        # Rod material
        materials = ["Graphite", "Fiberglass", "Bamboo"]
        print("\nSelect rod material:")
        for i, material in enumerate(materials, 1):
            print(f"{i}. {material}")
        
        material_choice = input("Enter choice (1-3): ")
        try:
            rod_material = materials[int(material_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Using Graphite.")
            rod_material = "Graphite"
        
        # Create the rod
        self.current_rod = FlyRod(rod_length, rod_weight, rod_material)
        print(f"\nRod built: {rod_length}' {rod_weight}-weight {rod_material}")
        input("Press Enter to continue...")
    
    def build_fly(self):
        print("\nSelect Your Fly")
        print("-" * 30)
        
        # Fly categories
        categories = ["Dry Flies", "Wet Flies", "Nymphs", "Streamers"]
        print("\nSelect fly category:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        
        cat_choice = input("Enter choice (1-4): ")
        try:
            category = categories[int(cat_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Using Dry Flies.")
            category = "Dry Flies"
        
        # Specific fly patterns based on category
        fly_patterns = {
            "Dry Flies": ["Adams", "Elk Hair Caddis", "Parachute Hopper", "Royal Wulff"],
            "Wet Flies": ["Partridge & Orange", "Soft Hackle Hare's Ear", "Tellico Nymph"],
            "Nymphs": ["Pheasant Tail", "Gold-Ribbed Hare's Ear", "Zebra Midge", "Copper John"],
            "Streamers": ["Woolly Bugger", "Clouser Minnow", "Muddler Minnow", "Zonker"]
        }
        
        print(f"\nSelect {category} pattern:")
        patterns = fly_patterns[category]
        for i, pattern in enumerate(patterns, 1):
            print(f"{i}. {pattern}")
        
        pattern_choice = input(f"Enter choice (1-{len(patterns)}): ")
        try:
            pattern = patterns[int(pattern_choice) - 1]
        except (ValueError, IndexError):
            print(f"Invalid choice. Using {patterns[0]}.")
            pattern = patterns[0]
        
        # Fly size
        sizes = [22, 20, 18, 16, 14, 12, 10, 8, 6, 4]
        print("\nSelect fly size:")
        for i, size in enumerate(sizes, 1):
            print(f"{i}. Size {size}")
        
        size_choice = input("Enter choice (1-10): ")
        try:
            size = sizes[int(size_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Using size 16.")
            size = 16
        
        # Create the fly
        self.current_fly = Fly(pattern, category, size)
        print(f"\nFly selected: {pattern}, Size {size}")
        input("Press Enter to continue...")
    
    def select_location(self):
        print("\nSelect Fishing Location")
        print("-" * 30)
        
        locations = ["Mountain Stream", "River Bend", "Alpine Lake", "Coastal Estuary"]
        print("\nAvailable locations:")
        for i, location in enumerate(locations, 1):
            print(f"{i}. {location}")
        
        choice = input("Enter choice (1-4): ")
        try:
            location = locations[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Selecting Mountain Stream.")
            location = "Mountain Stream"
        
        # Generate the location grid
        location_type = "river"
        if "Stream" in location:
            location_type = "stream"
        elif "Lake" in location:
            location_type = "lake"
        
        self.generate_location(location_type)
        self.current_location = location
        print(f"\nLocation set to: {location}")
        input("Press Enter to continue...")
    
    def start_fishing(self):
        if not self.current_rod:
            print("\nYou need to build a rod first!")
            input("Press Enter to continue...")
            return
            
        if not self.current_leader:
            print("\nYou need to build a leader first!")
            input("Press Enter to continue...")
            return
            
        if not self.current_fly:
            print("\nYou need to select a fly first!")
            input("Press Enter to continue...")
            return
            
        if not self.current_location:
            print("\nYou need to select a location first!")
            input("Press Enter to continue...")
            return
        
        print("\nStarting to fish...")
        print("Select a grid position to cast to (e.g., b3):")
        
        cast_position = input("> ").strip().lower()
        if len(cast_position) != 2 or not cast_position[0].isalpha() or not cast_position[1].isdigit():
            print("Invalid position format. Use letter+number (e.g., b3)")
            input("Press Enter to try again...")
            return
        
        col = ord(cast_position[0]) - ord('a')
        row = int(cast_position[1]) - 1
        
        if col < 0 or col >= self.grid_size or row < 0 or row >= self.grid_size:
            print("Position out of bounds!")
            input("Press Enter to try again...")
            return
        
        if self.fishfinder_grid[row][col] == '.':
            print("You can't cast onto land!")
            input("Press Enter to try again...")
            return
        
        # Show the cast on the overhead view
        self.overhead_grid[row][col] = 'X'
        self.display_game()
        
        print("\nCasting...")
        time.sleep(1)
        
        # Determine if there's a bite
        bite_chance = random.random()
        if bite_chance > 0.7:  # 30% chance of a bite
            self._fish_on(row, col)
        else:
            print("No bites. Try casting again or change your approach.")
            input("Press Enter to continue...")
    
    def _fish_on(self, row, col):
        print("\nFISH ON!")
        
        # Determine fish species based on location
        fish_types = {
            "Mountain Stream": ["Brook Trout", "Rainbow Trout", "Brown Trout"],
            "River Bend": ["Brown Trout", "Rainbow Trout", "Smallmouth Bass"],
            "Alpine Lake": ["Lake Trout", "Arctic Char", "Grayling"],
            "Coastal Estuary": ["Striped Bass", "Sea-run Cutthroat", "Salmon"]
        }
        
        location_fish = fish_types.get(self.current_location, ["Generic Fish"])
        fish_species = random.choice(location_fish)
        
        # Determine fish size
        min_size = 6
        max_size = 24
        
        # Adjust based on rod and leader match
        if self.current_rod.weight == 3 and "Trout" in fish_species:
            max_size = 18  # Lighter rod better for smaller fish
        elif self.current_rod.weight >= 7 and "Bass" in fish_species:
            min_size = 10  # Heavier rod better for larger fish
        
        size = random.randint(min_size, max_size)
        
        print(f"\nIt's a {size}-inch {fish_species}!")
        
        # Simple fighting mechanic
        fight_rounds = 3
        successful_rounds = 0
        
        for round in range(fight_rounds):
            print(f"\nRound {round+1} of the fight")
            print("1. Apply steady pressure")
            print("2. Give it some line")
            print("3. Pull hard")
            
            action = input("Choose your action (1-3): ")
            
            # Simplified logic - different actions work better for different situations
            fish_action = random.randint(1, 3)
            
            if (action == "1" and fish_action == 1) or \
               (action == "2" and fish_action == 3) or \
               (action == "3" and fish_action == 2):
                print("Good choice! You maintain control of the fish.")
                successful_rounds += 1
            else:
                print("The fish is fighting hard!")
        
        # Determine if fish is landed
        if successful_rounds >= 2:
            print(f"\nSuccess! You landed the {size}-inch {fish_species}!")
            self.player.add_catch(fish_species, size)
            self.player.add_xp(size * 10)  # XP based on fish size
        else:
            print("\nThe fish got away at the last moment!")
        
        input("Press Enter to continue...")
    
    def main_menu(self):
        while True:
            self.display_game()
            
            print("\nMain Menu:")
            print("1. Build Leader")
            print("2. Build Rod")
            print("3. Select Fly")
            print("4. Select Location")
            print("5. Start Fishing")
            print("6. View Catch Record")
            print("7. Save Game")
            print("8. Quit")
            
            choice = input("\nEnter choice (1-8): ")
            
            if choice == "1":
                self.build_leader()
            elif choice == "2":
                self.build_rod()
            elif choice == "3":
                self.build_fly()
            elif choice == "4":
                self.select_location()
            elif choice == "5":
                self.start_fishing()
            elif choice == "6":
                self.view_catch_record()
            elif choice == "7":
                self.save_game()
            elif choice == "8":
                if input("Are you sure you want to quit? (y/n): ").lower() == 'y':
                    print("Thanks for playing FFRPG!")
                    break
    
    def view_catch_record(self):
        print("\nCatch Record")
        print("-" * 30)
        
        if not self.player.catch_record:
            print("No fish caught yet.")
        else:
            for i, (fish, size) in enumerate(self.player.catch_record, 1):
                print(f"{i}. {size}-inch {fish}")
        
        input("\nPress Enter to continue...")
    
    def save_game(self):
        print("\nSaving game...")
        # In a real implementation, this would save to a file
        print("Game saved!")
        input("\nPress Enter to continue...")


class Player:
    def __init__(self, name, level, xp):
        self.name = name
        self.level = level
        self.xp = xp
        self.catch_record = []  # List of (species, size) tuples
    
    def add_catch(self, species, size):
        self.catch_record.append((species, size))
    
    def add_xp(self, amount):
        self.xp += amount
        
        # Simple leveling system
        new_level = self.xp // 1000
        if new_level > self.level:
            self.level = new_level
            print(f"\nLevel Up! You are now level {self.level}")


class Leader:
    def __init__(self, material, tippet, length):
        self.material = material
        self.tippet = tippet
        self.length = length
    
    def __str__(self):
        return f"{self.length}' {self.material} {self.tippet}"


class FlyRod:
    def __init__(self, length, weight, material):
        self.length = length
        self.weight = weight
        self.material = material
    
    def __str__(self):
        return f"{self.length}' {self.weight}wt {self.material}"


class Fly:
    def __init__(self, pattern, category, size):
        self.pattern = pattern
        self.category = category
        self.size = size
    
    def __str__(self):
        return f"{self.pattern} (#{self.size})"


if __name__ == "__main__":
    game = FFRPG()
    game.main_menu()
