#are upgrades progressive?
#why is round crystal avaliable as salvage??? that doesnt work right? and force gems?
#do you need the sw seachart, that is the question
#can you go around the back way if you have the nw sea chart

import json
import sys

#inventory
NWSeaChart = False
SESeaChart = False
NESeaChart = False

CourageGem = 0
PowerGem = 0
WisdomGem = 0

Sword = False
Shovel = False
Bow = False
Bombs = False
Bomchus = False
Boomerang = False
Hammer = False
GrapplingHook = False

Cannon = False
FishingRod = False
SalvageArm = False
CycloneSlate = False

SunKey = False
KingKey = False
GhostKey = False
RegalNecklace = False
PhantomHourglass = False
PhantomBlade = False

PowerSpirit = False
WidsdomSpirit = False
CourageSpirit = False
Aquanine = False
Crimsonine = False
Azurine = False

HeroNewClothes = Fase
JolenesLetter = False
Kaleidoscope = False
WoodHeart = False
GuardNotebook


def extract_bottom_level_entries(file_path):
    # Load the JSON data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)

    bottom_level_entries = []
    current_seed_entry = data.get("seed")

    # Recursive function to traverse the JSON structure
    def traverse(node):

        if isinstance(node, dict):

            # Check if it's a bottom-level dictionary (no further nesting)
            if all(not isinstance(v, dict) for v in node.values()):
                for value in node.values():
                    bottom_level_entries.append(value)  # Add only the value
            else:
                # Recursively traverse each value
                for value in node.values():
                    traverse(value)

    # Start traversing from the 'items' key
    if 'items' in data:
        traverse(data['items'])

    return bottom_level_entries, current_seed_entry

# Example usage
file_path = r"C:\Users\James.Broadhead\3D Objects\spoilerlog.json"

entries, seed_entry = extract_bottom_level_entries(file_path)

print("\nCurrent seed entry:")
print(seed_entry)

inventory = []
damage = ["progressiveSword","Hammer","GrappleHook","Bow","Bombs","Bomchus"]
#always accessible from beginning
inventory.append(entries[45])
inventory.append(entries[46])
inventory.append(entries[63])
inventory.append(entries[79])
inventory.append(entries[82])
#is this accessible without salvage arm? inventory.append(entries[83])
inventory.append(entries[86])
inventory.append(entries[89])
inventory.append(entries[91])
inventory.append(entries[242])
inventory.append(entries[243])
inventory.append(entries[257])

i = 1
while i > 0:
    if bool(set(damage) & set(inventory)): 
        #can you kill fire bats without boomerang? inventory.append(entries[168])
        print("damage")
        sys.exit("Found Damage")
    i -=1
else:
    for entry in inventory:
        print(entry)


    







