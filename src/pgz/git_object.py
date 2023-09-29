import hashlib
import pathlib
import zlib

from . import types
from . import lib


def from_sha(gitdir: pathlib.Path, sha: str) -> types.GitObject:
    object_path = gitdir / 'objects' / sha[:2] / sha[2:]

    return from_bytes(zlib.decompress(object_path.read_bytes()))


def from_path(path: pathlib.Path) -> types.GitObject:
    data = path.read_bytes()

    return from_bytes(data)


def from_bytes(raw: bytes) -> types.GitObject:
    type_end = raw.find(b' ')
    size_end = raw.find(b'\x00')

    file_type_ = raw[:type_end].decode()
    type_ = types.GitObjectTypeEnum.from_str(file_type_)
    if not type_:
        raise Exception(f'Unknown object type: {file_type_}')

    size = int(raw[type_end + 1:size_end].decode())
    if size != len(raw) - size_end - 1:
        raise Exception('Malformed object {sha}: bad length')

    data = raw[size_end + 1:]

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
