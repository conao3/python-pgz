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


class GitObjectBlob(GitObject):
    blob: bytes


class GitObjectCommit(GitObject):
    model_config = pydantic.ConfigDict(extra='allow')

    tree: str
    parent: Optional[str] = None
    author: bytes
    committer: bytes
    message: bytes


class GitObjectTreeItem(pydantic.BaseModel):
    mode: str
    path: str
    sha: str


class GitObjectTree(GitObject):
    items: list[GitObjectTreeItem]


class GitObjectTag(GitObject):
    model_config = pydantic.ConfigDict(extra='allow')

    object: str
    type: str
    tag: str
    tagger: bytes
    message: bytes
