import os
import random
import time
from typing import Dict, List, Optional
from grid_system import FishingGrid

class FFRPGGgame:
    """main game class"""

def __init__(self):
    self.player = None
    self.current_location = None
    self.weather = None
    self.tod = self.get_time()
    self.game_running = False
    self.grid = FishingGrid(size=10)
    self.current_rod


def initialize_game(self):
    """init new game"""
    print("#" * 60)
    print("Welcome to FFRPG - The Ultimate FlyFishing Experience")
    print("#" * 60)
    self.player = self.choose_character()
    """each character class is a separate thing"""
    self.current_location = self.select_location()
    self.weather = self.check_weather()
    self.tod = self.get_time()
    self.game_runnning = True

def choose_character(pick_A):
    """create new character"""
    print("Character Creation, Who are you?")
    print("--" * 60)
    name = input("Enter your name, angler: ")
    print("--" * 60)
    print("\n Pick one of these that speaks to you: ")
    print("\n1. Outlaw, \n2. Explorer,\n3. Sage,\n4.  Waste-of-Rod,")
    pick_A = input()

    def character(self):

    


    for attribute in ("Casting","Patience","Observation","Knowledge","Endurance"):
        while True:
            try:
                value = int(input(f"{attribute} ({points_available} points remaining: "))
                if 0 <= value <= points_available:
                    attributes[attribute.lower()] = value
                    remaining_points -= value
                    break
                else:
                    print(f"Please enter a value between 0 amd {points_available}")
            except ValueError:
                print("Please enter a valid number, come on...")

    return pick_A(name, attributes)


def select_location(self):
    """sets location for the player which brings environment variables"""
    print()