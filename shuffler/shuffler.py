import json
import logging
from parser import Descriptor, Edge, Node, parse
from pathlib import Path
from random import randint
import sys
from typing import Any

import click

logging.basicConfig(level=logging.INFO)

END_NODE = "Mercay.AboveMercayTown.Island"  # Name of node that player must reach to beat the game

# Global variables
visited_nodes: set[str]  # Tracks "visited" nodes to avoid infinite recursion
nodes: list[Node]  # List of nodes that make up the world graph
edges: dict[str, list[Edge]]  # List of edges that connect nodes. Maps node names to edges.
inventory: list[str]


def load_aux_data(directory: Path):
    # Find all aux data files in the given directory
    aux_files = list(directory.rglob("*.json"))

    areas: list[dict] = []
    for file in aux_files:
        with open(file, "r") as fd:
            areas.append(json.load(fd))
    return areas


def randomize_aux_data(aux_data_directory: Path):
    """
    Return aux data for the logic with the item locations randomized.

    Note: the item locations are *not* guaranteed (and are unlikely) to be logic-compliant.
    This function just performs a "dumb" shuffle and returns the results.

    Params:
        aux_data_directory: Directory that contains the initial aux data
    """
    areas = load_aux_data(aux_data_directory)
    areas = [areas[0]]  # TODO: for now, just shuffle Mercay

    # List of every item in the game
    chest_items: list[str] = []

    # Record all items in the game
    for area in areas:
        for room in area["rooms"]:
            if "chests" in room:
                for chest in room["chests"]:
                    chest_items.append(chest["contents"])

    # Randomize the items
    for area in areas:
        for room in area["rooms"]:
            if "chests" in room:
                for chest in room["chests"]:
                    chest["contents"] = chest_items.pop(randint(0, len(chest_items) - 1))
    return areas


def edge_is_traversable(edge: Edge):
    """Determine if this edge is traversable given the current state of the game."""
    # TODO: implement this
    match edge.constraints:
        case "item Sword":
            return "oshus_sword" in inventory
        case "(item Bombs | item Bombchus)":
            return "bombs" in inventory or "bombchus" in inventory
        case "item Bow":
            return "bow" in inventory
        case "item Boomerang":
            return "boomerang" in inventory
        case "flag BridgeRepaired":
            return True  # TODO: for now, assume bridge is always repaired
    return False


def get_chest_contents(chest_name: str, area_aux_data: dict[Any, Any]) -> str:
    for room in area_aux_data["rooms"]:
        if "chests" in room:
            for chest in room["chests"]:
                if chest["name"] == chest_name:
                    return chest["contents"]
    raise Exception(f"{chest_name} not found in the given aux data.")


def traverse_graph(node: Node, area_aux_data: dict[Any, Any], visited_rooms: set[str]):
    """
    Traverse the graph (i.e. the nodes and edges) of the current room, starting at `node`.

    Params:
        `node`: The node to start the traversal at
        `area_aux_data`: The aux data for the current area.
        `visited_rooms`: Rooms that have been visited already in this traversal.
                         Note that this is not a global variable, since we only want to limit rooms
                         visited in the _current_ traversal. Future traversals may need to revisit
                         this room to reach new nodes that were previously inaccessible.

    Returns:
        `True` if the `END_NODE` was reached, `False` otherwise.
    """
    global nodes, edges, visited_nodes, inventory
    logging.debug(node.name)

    if node.name == END_NODE:
        return True

    doors_to_enter: list[str] = []
    visited_nodes.add(node.name)  # Acknowledge this node as "visited"

    # For the current node, find all chests + "collect" their items and note every door so
    # we can go through them later
    for node_info in node.contents:
        if node_info.type == Descriptor.CHEST.value:
            inventory.append(get_chest_contents(node_info.data, area_aux_data))
        elif node_info.type in (
            Descriptor.DOOR.value,
            Descriptor.ENTRANCE.value,
            Descriptor.EXIT.value,
        ):
            full_room_name = node_info.data
            # Get "path" to node, including Area and Room, if they're not included
            if len(full_room_name.split(".")) == 2:
                full_room_name = f"{node.area}.{full_room_name}"
            elif len(full_room_name.split(".")) == 1:
                full_room_name = f"{node.area}.{node.room}.{full_room_name}"

            if full_room_name not in visited_rooms:
                doors_to_enter.append(full_room_name)
                visited_rooms.add(full_room_name)

    # Check which edges are traversable and do so if they are
    for edge in edges[node.name]:
        if edge.dest.name in visited_nodes:
            continue
        if edge_is_traversable(edge):
            logging.debug(f"{edge.source.name} -> {edge.dest.name}")
            if traverse_graph(edge.dest, area_aux_data, visited_rooms):
                return True

    # Go through each door and traverse each of their room graphs
    for door_name in doors_to_enter:
        door_name = door_name.split(".")[-1]  # Remove area and room if they are specified
        for room in area_aux_data["rooms"]:
            if node.room == room["name"]:
                for door in room["doors"]:
                    if door["name"] == door_name:
                        for other_node in nodes:
                            # TODO: this only supports links with format `room.node`.
                            if door["link"] in [".".join([other_node.room, other_node.node])]:
                                logging.debug(f"{node.name} -> {other_node.name}")
                                if traverse_graph(other_node, area_aux_data, visited_rooms):
                                    return True
    return False


@click.command()
@click.option(
    "-a",
    "--aux-data-directory",
    required=True,
    type=str,
    help="File path to directory that contains aux data.",
)
@click.option(
    "-o",
    "--output",
    default=None,
    type=str,
    help="Path to save randomized aux data to.",
)
def shuffler(aux_data_directory: str, output: str | None):
    global nodes, edges, visited_nodes, inventory

    nodes, edges = parse()

    # Starting node is Mercay outside of Oshus's house.
    # This would need to be randomized to support entrance rando
    starting_node = [node for node in nodes if node.name == "Mercay.OutsideOshus.Outside"][0]

    # Begin the random fill algorithm.
    # The program will generate a completely random seed without using logic.
    # It will then attempt to traverse the seed's world graph. If it fails to reach the node
    # required to beat the game, it will generate another seed and check it again. This repeats
    # until a valid seed is generated.
    # TODO: we'll want to instead use the assumed fill algorithm eventually, but this naive
    # approach is sufficient for now.
    tries = 0
    while True:
        tries += 1
        # Initialize global variables
        visited_nodes = set()  # Tracks "visited" nodes to avoid infinite recursion
        inventory = []

        areas = randomize_aux_data(Path(aux_data_directory))
        area = areas[0]  # TODO: for now, just shuffle Mercay
        if traverse_graph(starting_node, area, set()):
            break

    logging.debug(f"{tries} tries were needed to get a valid seed.")

    if output == "--":
        print(json.dumps(areas), file=sys.stdout)
    elif output is not None:
        with open(output, "w") as fd:
            fd.write(json.dumps(areas))

    return areas


if __name__ == "__main__":
    shuffler()
