from pathlib import Path

from pydantic import BaseModel, Field, validator


class Setting(BaseModel):
    name: str
    description: str | None
    flag: bool | None
    options: list[str] | None
    supported: bool = Field(default=True)

    @validator('options')
    def ensure_values_or_flag(cls, v: list[str] | None, values: dict):
        if not ('options' in values or 'flag' in values):
            raise ValueError(f'Invalid setting {values["name"]} - require "options" or "flag".')
        if 'options' in values and 'flag' in values:
            raise ValueError(
                f'Invalid setting {values["name"]} - has both'
                '"options" or "flag", only one allowed.'
            )
        return v


class Settings(BaseModel):
    settings: list[Setting]


if __name__ == '__main__':
    json_schema = Settings.schema_json(indent=2)
    with open(Path(__file__).parent / 'settings_schema.json', 'w') as fd:
        fd.write(json_schema + '\n')
