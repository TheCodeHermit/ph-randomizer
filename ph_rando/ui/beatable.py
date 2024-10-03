#why is round crystal avaliable as salvage??? that doesnt work right? and force gems?
#do you need the sw seachart, that is the question
#can you go around the back way if you have the nw sea chart
#do you really need the phantom sword to fight bellum?

import json
import sys
from . import fakecli

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

HeroNewClothes = False
JolenesLetter = False
Kaleidoscope = False
WoodHeart = False
GuardNotebook =False


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

def gemDeDupe(GemArg):
    var_1 = 0
    GemNum = 1
    for index in entries:
        if entries[var_1] == GemArg:
            entries[var_1] = GemArg + str(GemNum)
            GemNum+=1
            var_1+=1
        else:
            var_1 += 1

file_path = /home/ubuntu/test1/spoiler.json

entries, seed_entry = extract_bottom_level_entries(file_path)

#renaming duplicates
gemDeDupe("PowerGem")
gemDeDupe("WisdomGem")
gemDeDupe("CourageGem")



inventory = []
powerGems =[]
wisdomGems = []
courageGems = []
damage = ["progressiveSword","Hammer","GrappleHook","Bow","Bombs","Bomchus"]
#always accessible from beginning
inventory.append(entries[45])    #WoodenShield
inventory.append(entries[46])    #QuiverUpgrade
inventory.append(entries[63])    #Chest at the summit
inventory.append(entries[79])    #Chest  after jumping with the cucco
inventory.append(entries[83])    #Roll into the highest tree
inventory.append(entries[86])    #Remove rocks from Lapelli's yard
inventory.append(entries[89])    #PowerGem
inventory.append(entries[91])    #Count the trees
inventory.append(entries[242])   #Linebeck's chest
inventory.append(entries[243])   #Sea chart chest
inventory.append(entries[257])   #Get the Phantom Hourglass

'''def chest_emulator():
    #if "ProgressiveSword" in inventory:
        
    if "Shovel" in inventory:
        inventory.append(entries[64]) #Dig the grass near the Temple Entrance
        inventory.append(entries[67]) #Dig the mark (In astrids basement)

    if "GrapplingHook" in inventory:
        inventory.append(entries[62]) #Chest on the small northern island (Ember Isle)

    if "Cannon" in inventory: #need to find out if can go the back way through the nw sea chart
        #and then for return to molida when to kill the monster thingy
        #after salvage arm or after sun crest collection, or after sun crest salvage??
        inventory.append(entries[58]) #Chest on main island (Spirit)



        inventory = list(set(inventory))
        if sum(1 for item in inventory if 'PowerGem' in item) > 9:
            inventory.append(entries[52]) #Gather 10 Power Gems
            if sum(1 for item in inventory if 'PowerGem' in item) > 19:
                inventory.append(entries[53]) #Gather 20 Power Gems
        if sum(1 for item in inventory if 'WisdomGem' in item) > 9:
            inventory.append(entries[54]) #Gather 10 Wisdom Gems
            if sum(1 for item in inventory if 'WisdomGem' in item) > 19:
                inventory.append(entries[55]) #Gather 20 Wisdom Gems
        if sum(1 for item in inventory if 'CourageGem' in item) > 9:
            inventory.append(entries[56]) #Gather 10 Courage Gems
            if sum(1 for item in inventory if 'CourageGem' in item) > 19:
                inventory.append(entries[57]) #Gather 20 Courage Gems



    if "NWSeaChart" in inventory:
            
            if "Shovel" in inventory:
                
            if "GrapplingHook" in inventory:

            if "Cannon" in inventory:

    if "SESeaChart" in inventory:
            
            if "Shovel" in inventory:
                
            if "GrapplingHook" in inventory:

            if "Cannon" in inventory:

                if "NESeaChart" in inventory:

                    if "Shovel" in inventory:
                
                    if "GrapplingHook" in inventory:

                    if "Cannon" in inventory:


'''
    #if bool(set(damage) & set(inventory)): 
        
    


if NWSeaChart in inventory:
    for entry in inventory:
        print(entry)
    print("Completable")
    sys.exit(seed_entry)

for entry in inventory:
    print(entry)
print("Womp womp "+ seed_entry)
fakecli.randomizer_cli()

    







