from collections import defaultdict, deque
from copy import deepcopy
import logging
import random
from typing import Self

from ordered_set import OrderedSet

from ph_rando.common import ShufflerAuxData
from ph_rando.shuffler._parser import (
    Edge,
    Node,
    annotate_logic,
    connect_mail_nodes,
    connect_rooms,
    connect_shop_nodes,
    parse_aux_data,
)
from ph_rando.shuffler.aux_models import Check, Item

logger = logging.getLogger(__name__)

DUNGEON_REWARD_CHECKS: dict[str, str] = {
    'BlaazBossRoom.Main.SpiritOfPower': 'PowerSpirit',
    'CyclokBossRoom.Main.SpiritOfWisdom': 'WisdomSpirit',
    'CraykBossRoom.Main.SpiritOfCourage': 'CourageSpirit',
    'GoronTemple.CrimsonineRoom.Crimsonine': 'Crimsonine',
    'IceTemple.AzurineRoom.Azurine': 'Azurine',
    'MutohTemple.B4.Aquanine': 'Aquanine',
}

IMPORTANT_ITEMS: set[str] = {
    # Progression items
    'Bombchus',
    'Bombs',
    'Boomerang',
    'Bow',
    'Cannon',
    'CycloneSlate',
    'FishingRod',
    'GrapplingHook',
    'Hammer',
    'KingKey',
    'GhostKey',
    'ProgressiveSword',
    'PhantomHourglass',
    'RegalNecklace',
    'SalvageArm',
    'Shovel',
    'SunKey',
    'Shield',
    'JolenesLetter',
    # Sea charts
    'NESeaChart',
    'NWSeaChart',
    'SESeaChart',
    'SWSeaChart',
    # Gems
    'PowerGem',
    'WisdomGem',
    'CourageGem',
    # Spirit upgrades
    'PowerSpiritLv1'
    'WisdomSpiritLv1'
    'CourageSpiritLv1'
    'PowerSpiritLv2'
    'WisdomSpiritLv2'
    'CourageSpiritLv2',
    # Trading quest items
    'Kaleidoscope',
    'WoodHeart',
    'GuardNotebook',
    'HeroNewClothes',
    # Treasure maps
    'TreasureMapSW1',
    'TreasureMapSW2',
    'TreasureMapSW3',
    'TreasureMapSW4',
    'TreasureMapSW5',
    'TreasureMapSW6',
    'TreasureMapSW7',
    'TreasureMapNW1',
    'TreasureMapNW2',
    'TreasureMapNW3',
    'TreasureMapNW4',
    'TreasureMapNW5',
    'TreasureMapNW6',
    'TreasureMapNW7',
    'TreasureMapNW8',
    'TreasureMapSE1',
    'TreasureMapSE2',
    'TreasureMapSE3',
    'TreasureMapSE4',
    'TreasureMapSE5',
    'TreasureMapSE6',
    'TreasureMapSE7',
    'TreasureMapSE8',
    'TreasureMapNE1',
    'TreasureMapNE2',
    'TreasureMapNE3',
    'TreasureMapNE4',
    'TreasureMapNE5',
    'TreasureMapNE6',
    'TreasureMapNE7',
    'TreasureMapNE8',
}


class AssumedFillFailed(Exception):
    pass


class Shuffler:
    def __init__(
        self: Self,
        seed: str,
        starting_node_name: str = 'Mercay.OutsideOshus.Outside',
    ) -> None:
        random.seed(seed)

        self.aux_data = parse_aux_data()
        annotate_logic(areas=self.aux_data.areas)
        connect_rooms(self.aux_data.areas)
        connect_mail_nodes(self.aux_data.areas)
        connect_shop_nodes(self.aux_data.areas)

        self.starting_node = [
            node
            for area in self.aux_data.areas
            for room in area.rooms
            for node in room.nodes
            if node.name == starting_node_name
        ][0]

    def generate(self: Self) -> ShufflerAuxData:
        while True:
            aux_data_backup = deepcopy(self.aux_data)

            # Copy all items to a list and set all checks to null
            item_pool: list[Item] = []
            for area in self.aux_data.areas:
                for room in area.rooms:
                    for check in room.chests:
                        item = check.contents

                        # Append area name for keys, so that we know where we can place
                        # it later on.
                        if item.name == 'SmallKey':
                            item.name += f'_{area.name}'

                        item_pool.append(item)
                        check.contents = None  # type: ignore

            # Shuffle the item pool
            random.shuffle(item_pool)

            try:
                self._place_dungeon_rewards(item_pool)
                self._place_boss_keys(item_pool)
                self._place_small_keys(item_pool)
                self._place_important_items(item_pool)
                self._place_rest_of_items(item_pool)
                break
            except AssumedFillFailed:
                self.aux_data = aux_data_backup
                logging.info('Assumed fill failed! Trying again...\n')
                continue

        return self.aux_data

    def _place_item(
        self: Self,
        item: Item,
        remaining_item_pool: list[Item],
        candidates: OrderedSet[Check] | None = None,
        use_logic: bool = True,
    ) -> None:
        """
        Places the given item in a location. Set `use_logic` to False to ignore logic
        and place the item in a completely random empty location.
        """
        reachable_null_checks: dict[Check, str] = {}

        if use_logic:
            # Figure out what nodes are accessible
            reachable_nodes = self.assumed_search(remaining_item_pool)

            for node in reachable_nodes:
                for check in node.checks:
                    if candidates is not None and check not in candidates:
                        continue
                    if check.contents is None:
                        reachable_null_checks[check] = node.name

        else:
            for area in self.aux_data.areas:
                for room in area.rooms:
                    for node in room.nodes:
                        for check in node.checks:
                            if check.contents is None:
                                reachable_null_checks[check] = node.name

        locations = list(reachable_null_checks.keys())
        if len(locations) == 0:
            raise AssumedFillFailed()

        # Place the current item into a random location
        r = locations[random.randint(0, max(0, len(reachable_null_checks) - 1))]
        r.contents = item

        logger.info(f'Placed {item.name} at {reachable_null_checks[r]}')

    def _place_dungeon_rewards(self: Self, item_pool: list[Item]) -> None:
        dungeon_reward_pool = [item for item in item_pool if item in DUNGEON_REWARD_CHECKS.values()]
        for item in dungeon_reward_pool:
            possible_checks: OrderedSet[Check] = OrderedSet(
                [
                    check
                    for area in self.aux_data.areas
                    for room in area.rooms
                    for node in room.nodes
                    for check in node.checks
                    if f'{node.area.name}.{node.room.name}.{check.name}' in DUNGEON_REWARD_CHECKS
                ]
            )
            item_pool.remove(item)
            self._place_item(item, item_pool, possible_checks)

    def _place_boss_keys(self: Self, item_pool: list[Item]) -> None:
        """Place all boss keys in `item_pool`."""
        key_pool = [item for item in item_pool if item.name.startswith('BossKey')]
        for item in key_pool:
            possible_checks: OrderedSet[Check] = OrderedSet(
                [
                    check
                    for area in self.aux_data.areas
                    for room in area.rooms
                    for node in room.nodes
                    for check in node.checks
                    if node.area.name == item.name[7:]
                ]
            )
            item_pool.remove(item)
            self._place_item(item, item_pool, possible_checks)

    def _place_small_keys(self: Self, item_pool: list[Item]) -> None:
        """Place all small keys in `item_pool`."""
        key_pool = [item for item in item_pool if item.name.startswith('SmallKey_')]
        for item in key_pool:
            possible_checks: OrderedSet[Check] = OrderedSet(
                [
                    check
                    for area in self.aux_data.areas
                    for room in area.rooms
                    for node in room.nodes
                    for check in node.checks
                    if node.area.name == item.name[9:]
                ]
            )
            item_pool.remove(item)
            item.name = item.name[: item.name.index('_')]
            self._place_item(item, item_pool, possible_checks)

    def _place_important_items(self: Self, item_pool: list[Item]) -> None:
        """Place all "important" items in the given item_pool."""
        important_items = [item for item in item_pool if item.name in IMPORTANT_ITEMS]
        for item in important_items:
            item_pool.remove(item)
            self._place_item(item, item_pool)

    def _place_rest_of_items(self: Self, item_pool: list[Item]) -> None:
        """Place all items remaining in item_pool."""
        for item in item_pool:
            self._place_item(item, item_pool, use_logic=False)
        item_pool.clear()

    def search(
        self: Self,
        items: list[Item],
        flags: set[str],
        states: set[str],
    ) -> OrderedSet[Node]:
        reachable_nodes: OrderedSet[Node] = OrderedSet()

        queue: deque[Node] = deque([self.starting_node])

        # Mapping to keep track of the state of `locks` (unlocked vs locked)
        locks: dict[str, bool] = {}

        visited_nodes: set[Node] = {self.starting_node}

        while len(queue) > 0:
            # Mapping to keep track of edges that contain an `open` descriptor, but are
            # otherwise traversable
            edges_with_locked_door: dict[str, list[Edge]] = defaultdict(list)
            while len(queue) > 0:
                r = queue.popleft()
                for edge in r.edges:
                    target = edge.dest

                    requirements_met = edge.is_traversable(
                        [i.name for i in items], flags, states, self.aux_data
                    )

                    if requirements_met and target not in visited_nodes:
                        if edge.locked_door:
                            edges_with_locked_door[edge.src.area.name].append(edge)
                        else:
                            queue.append(target)
                            visited_nodes.add(target)
                reachable_nodes.add(r)

            # Calculate key counts for each area
            keys: dict[str, int] = defaultdict(int)
            for item in items:
                if item.name.startswith('SmallKey_'):
                    area_name = item.name[9:]
                    keys[area_name] += 1

            # Record any newly-reachable locked doors
            for node in reachable_nodes:
                if not node.lock:
                    continue
                full_lock_name = '.'.join([node.area.name, node.room.name, node.lock])
                if full_lock_name in locks:
                    continue
                locks[full_lock_name] = False

            # Figure out which doors we can unlock, and mark
            # them as "unlocked" + update key counts
            for area_name, edges in edges_with_locked_door.items():
                doors_to_unlock = {e.locked_door for e in edges}
                if keys[area_name] >= len(doors_to_unlock):
                    keys[area_name] -= len(doors_to_unlock)
                    for door in doors_to_unlock:
                        assert door is not None
                        locks[door] = True

            for edges in edges_with_locked_door.values():
                for edge in edges:
                    assert edge.locked_door is not None
                    if locks.get(edge.locked_door):
                        queue.append(edge.dest)
                        visited_nodes.add(edge.dest)

        return reachable_nodes

    def assumed_search(self: Self, items: list[Item], area: str | None = None) -> OrderedSet[Node]:
        # Used to keep track of what checks/flags we've encountered
        completed_checks: set[Check] = set()

        flags: set[str] = set()
        items = deepcopy(items)  # make copy of items so we don't mutate the original list
        states: set[str] = {state for item in items for state in item.states}

        while True:
            reachable_nodes = self.search(items, flags, states)
            if area is not None:
                reachable_nodes = OrderedSet(
                    [node for node in reachable_nodes if node.area.name == area]
                )
            found_new_items = False

            for node in reachable_nodes:
                for check in node.checks:
                    if check.contents and check not in completed_checks:
                        item = check.contents
                        # If this is a small key, append the area name to it
                        # so that we can tell what dungeon it goes to.
                        if item.name == 'SmallKey':
                            item.name += f'_{node.area.name}'
                        items.append(item)
                        states.update(item.states)
                        found_new_items = True
                        completed_checks.add(check)
                for flag in node.flags:
                    if flag not in flags:
                        flags.add(flag)
                        found_new_items = True
                for state in node.states_gained:
                    states.add(state)
                for state in node.states_lost:
                    if state in states:
                        states.remove(state)

            if not found_new_items:
                break

        return reachable_nodes
