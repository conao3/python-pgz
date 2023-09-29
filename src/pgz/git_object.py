import hashlib
import pathlib
from typing import Optional
import zlib

from . import types
from . import lib


def from_sha(gitdir: pathlib.Path, type_: Optional[types.GitObjectTypeEnum], sha: str) -> types.GitObject:
    object_path = gitdir / 'objects' / sha[:2] / sha[2:]

    with object_path.open('rb') as f:
        raw = zlib.decompress(f.read())

    type_end = raw.find(b' ')
    size_end = raw.find(b'\x00')

    file_type_ = raw[:type_end].decode()
    if type_:
        if file_type_ != type_.name:
            raise Exception(f'Object {sha} is of type {file_type_}, not {type_}')
        obj_type = type_
    else:
        obj_type = types.GitObjectTypeEnum.from_str(file_type_)
        if not obj_type:
            raise Exception(f'Unknown object type: {file_type_}')

    size = int(raw[type_end + 1:size_end].decode())
    if size != len(raw) - size_end - 1:
        raise Exception('Malformed object {sha}: bad length')

    data = raw[size_end + 1:]

    return types.GitObject(type_=obj_type, data=data)


def from_path(type_: types.GitObjectTypeEnum, path: pathlib.Path) -> types.GitObject:
    data = path.read_bytes()

    return types.GitObject(type_=type_, data=data)


def obj_hash(obj: types.GitObject) -> str:
    raw = f'{obj.type_.name.lower()} {len(obj.data)}\x00'.encode() + obj.data

    return hashlib.sha1(raw).hexdigest()


def write_obj(obj: types.GitObject, gitdir: pathlib.Path) -> pathlib.Path:
    sha = obj_hash(obj)
    filepath = lib.create_repo_file(gitdir, f'objects/{sha[:2]}/{sha[2:]}')

    raw = f'{obj.type_.name.lower()} {len(obj.data)}\x00'.encode() + obj.data
    filepath.write_bytes(zlib.compress(raw))

    return filepath
