from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal, TypeAlias, Union

from pydantic import BaseModel, Extra, Field, validator

if TYPE_CHECKING:
    from pydantic.main import ModelMetaclass

    from ph_rando.shuffler._shuffler import Node


class BaseCheck(BaseModel):
    name: str = Field(..., description='The name of the item check')
    contents: str = Field(..., description='The item that this check contains')

    def __hash__(self) -> int:
        return id(self)

    @validator('contents')
    def check_if_item_is_valid(cls, v: str) -> str:
        """
        Ensure that this check's `contents` is set to a valid item.

        It'd be nice to have this be a JSON-Schema level check instead of a pydantic validator,
        but to do that, we need to dynamically generate an `Enum` with all possible item values
        using the ITEMS dict in patcher._items.py. As part of that, we would want to use pydantic's
        `use_enum_values` setting for the model, but mypy doesn't support it currently:
        https://github.com/pydantic/pydantic/issues/3809 and reports type errors all over the
        place if it's used. If this is ever fixed, it should be changed.
        """
        from ph_rando.patcher._items import ITEMS

        assert v in ITEMS
        return v


class Chest(BaseCheck):
    type: Literal['chest']
    zmb_file_path: str = Field(..., description='File path to the zmb the chest is on')
    zmb_mapobject_index: int = Field(..., description='Index of the chest in the defined zmb file')


class Mail(BaseCheck):
    type: Literal['mail']
    # TODO: what info is needed for patcher?


class Tree(BaseCheck):
    type: Literal['tree']
    zmb_file_path: str = Field(..., description='File path to the zmb the tree is on')
    zmb_mapobject_index: int = Field(
        ..., description='Index of the tree object in the defined zmb file'
    )


class Event(BaseCheck):
    type: Literal['event']
    bmg_file_path: str = Field(..., description='File path to the bmg the instruction is on')
    bmg_instruction_index: int = Field(
        ..., description='Index of the instruction in the defined bmg file'
    )


class IslandShop(BaseCheck):
    type: Literal['island_shop']
    overlay: int = Field(..., description='The code overlay this shop item is on')
    overlay_offset: str = Field(..., description='Hex offset from overlay to the shop item')


class Freestanding(BaseCheck):
    type: Literal['freestanding']
    # TODO: add other fields that are needed


class OnEnemy(BaseCheck):
    type: Literal['on_enemy']
    # TODO: what other fields are needed? Can this be replaced by Freestanding?


class SalvageTreasure(BaseCheck):
    type: Literal['salvage_treasure']
    zmb_file_path: str = Field(..., description='File path to the zmb the chest is on')
    zmb_actor_index: int = Field(
        ..., description='Index of the chest in the NPCA section of the zmb file'
    )


class DigSpot(BaseCheck):
    type: Literal['dig_spot']
    zmb_file_path: str = Field(..., description='File path to the zmb the chest is on')
    zmb_actor_index: int = Field(
        ..., description='Index of the chest in the NPCA section of the zmb file'
    )


class MinigameRewardChest(BaseCheck):
    type: Literal['minigame_reward_chest']
    # TODO: what other fields are needed?


Check: TypeAlias = (
    Chest
    | Event
    | IslandShop
    | Tree
    | Freestanding
    | OnEnemy
    | SalvageTreasure
    | DigSpot
    | MinigameRewardChest
    | Mail
)


def validate_check_type() -> None:
    """
    Ensure that the `Check` type alias includes all of the subclasses of `BaseCheck`.
    """

    def get_all_subclasses(cls: ModelMetaclass) -> list[ModelMetaclass]:
        """Recursively fetch all descendents of a class."""
        all_subclasses: list[ModelMetaclass] = []
        for subclass in cls.__subclasses__():
            all_subclasses.extend([subclass] + get_all_subclasses(subclass))
        return all_subclasses

    assert Check == Union[*[subclass for subclass in get_all_subclasses(BaseCheck)]]


validate_check_type()


class Exit(BaseModel):
    name: str = Field(..., description='The name of this exit')
    entrance: str = Field(..., description='The `entrance` or `door` where this exit leads.')


class Enemy(BaseModel):
    name: str = Field(..., description='The name of the referenced `enemy` in the .logic file.')
    type: str = Field(
        ..., description='The type of the enemy. Should map to an entry in `shuffler/enemies.json`.'
    )


class Room(BaseModel):
    class Config:
        extra = Extra.allow

    name: str = Field(..., description='The name of the room')
    chests: list[Annotated[Check, Field(discriminator='type')]] = Field(
        [],
        description='Item checks that can be made in this room',
        unique_items=True,
    )
    exits: list[Exit] = Field(
        [],
        description='All `exits` in this room that lead to an `entrance` in another room',
        unique_items=True,
    )
    enemies: list[Enemy] = Field(
        [],
        description='All enemies in this room',
        unique_items=True,
    )

    @validator('chests', 'exits', 'enemies')
    def name_uniqueness_check(cls, v: list[Check | Exit | Enemy]) -> list[Check | Exit | Enemy]:
        names_set = {item.name for item in v}
        if len(names_set) != len(v):
            from collections import defaultdict

            name_buckets: defaultdict[str, int] = defaultdict(int)
            for item in v:
                name_buckets[item.name] += 1
                if name_buckets[item.name] > 1:
                    raise ValueError(f'{type(item)} {item.name}: names must be unique!')
        return v

    @validator('exits')
    def entrance_uniqueness_check(cls, v: list[Exit]) -> list[Exit]:
        entrances_set = {item.entrance for item in v}
        if len(entrances_set) != len(v):
            from collections import defaultdict

            entrance_buckets: defaultdict[str, int] = defaultdict(int)
            for item in v:
                entrance_buckets[item.entrance] += 1
                if entrance_buckets[item.entrance] > 1:
                    raise ValueError(
                        f'Exit {item.name} contains more than one entrance {item.entrance}'
                    )
        return v

    # Note: pydantic ignores instance variables beginning with an underscore,
    # so we use that here. Nodes are not parsed by pydantic; they are populated
    # when the .logic files are parsed, i.e. after the initial aux data parsing.
    _nodes: list[Node]

    @property
    def nodes(self) -> list[Node]:
        if not hasattr(self, '_nodes'):
            self._nodes = []
        return self._nodes


class Area(BaseModel):
    name: str = Field(..., description='The name of the area')
    rooms: list[Room] = Field(
        ..., description='All of the rooms inside this area', min_items=1, unique_items=True
    )

    def json(self, *args: Any, **kwargs: Any) -> str:
        return super().json(*args, exclude={'rooms': {'__all__': {'nodes', '_nodes'}}}, **kwargs)


if __name__ == '__main__':
    json_schema = Area.schema_json(indent=2)
    with open(Path(__file__).parent / 'aux_schema.json', 'w') as fd:
        fd.write(json_schema + '\n')
