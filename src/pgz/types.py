from __future__ import annotations
import enum
from typing import Optional

import pydantic


class GitObjectTypeEnum(enum.Enum):
    COMMIT = enum.auto()
    TREE = enum.auto()
    TAG = enum.auto()
    BLOB = enum.auto()

    @classmethod
    def from_str(cls, arg: str) -> Optional['GitObjectTypeEnum']:
        mapping = {
            'COMMIT': GitObjectTypeEnum.COMMIT,
            'TREE': GitObjectTypeEnum.TREE,
            'TAG': GitObjectTypeEnum.TAG,
            'BLOB': GitObjectTypeEnum.BLOB,
        }

        return mapping.get(arg.upper())


class GitObject(pydantic.BaseModel):
    type_: GitObjectTypeEnum
    data: bytes
