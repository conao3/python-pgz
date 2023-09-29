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

    if type_ == types.GitObjectTypeEnum.TREE:
        return parse_tree(data)

    return types.GitObject(type_=type_, data=data)


def parse_tree(raw: bytes) -> types.GitObjectTree:
    items: list[types.GitObjectTreeItem] = []

    while raw:
        mode_end = raw.find(b' ')
        path_end = raw.find(b'\x00')

        mode = raw[:mode_end].decode()
        mode = f'{mode:0>6}'  # pad 0 with right align
        path = raw[mode_end + 1:path_end].decode()
        sha = raw[path_end + 1:path_end + 21].hex()

        items.append(types.GitObjectTreeItem(mode=mode, path=path, sha=sha))

        raw = raw[path_end + 21:]

    return types.GitObjectTree(type_=types.GitObjectTypeEnum.TREE, data=raw, items=items)


def obj_hash(obj: types.GitObject) -> str:
    raw = f'{obj.type_.name.lower()} {len(obj.data)}\x00'.encode() + obj.data

    return hashlib.sha1(raw).hexdigest()


def write_obj(obj: types.GitObject, gitdir: pathlib.Path) -> pathlib.Path:
    sha = obj_hash(obj)
    filepath = lib.create_repo_file(gitdir, f'objects/{sha[:2]}/{sha[2:]}')

    raw = f'{obj.type_.name.lower()} {len(obj.data)}\x00'.encode() + obj.data
    filepath.write_bytes(zlib.compress(raw))

    return filepath
