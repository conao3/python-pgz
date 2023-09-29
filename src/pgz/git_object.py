import hashlib
import pathlib
from typing import Any
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

    if type_ == types.GitObjectTypeEnum.BLOB:
        return types.GitObjectBlob(type_=type_, blob=data)
    elif type_ == types.GitObjectTypeEnum.TREE:
        return parse_tree(data)
    elif type_ == types.GitObjectTypeEnum.COMMIT:
        return parse_commit(data)
    elif type_ == types.GitObjectTypeEnum.TAG:
        return parse_tag(data)

    raise Exception(f'Unknown object type: {type_}')


def parse_key_value_list_with_message(raw: bytes) -> dict[str, bytes]:
    res: dict[str, bytes] = {}

    while (space_pos := raw.find(b' ')) < (newline_pos := raw.find(b'\n')):
        key = raw[:space_pos].decode()
        value = raw[space_pos + 1:newline_pos]

        res[key] = value
        raw = raw[newline_pos + 1:]

    res['message'] = raw[1:]

    return res


def serialize_key_value_list_with_message(data: dict[str, Any]) -> bytes:
    res = b''

    for key, value in data.items():
        if key == 'message':
            continue

        if isinstance(value, str):
            value = value.encode()
        res += key.encode() + b' ' + value + b'\n'

    res += b'\n'
    res += data['message']

    return res


def parse_commit(raw: bytes) -> types.GitObjectCommit:
    body = parse_key_value_list_with_message(raw)

    return types.GitObjectCommit.model_validate(
        body |
        {
            "tree": body['tree'].decode(),
            "parent": body.get('parent') and body['parent'].decode(),
            "author": body['author'],
            "committer": body['committer'],
        } |
        {
            "type_": types.GitObjectTypeEnum.COMMIT,
            "data": raw,
        }
    )


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

    return types.GitObjectTree(type_=types.GitObjectTypeEnum.TREE, items=items)


def parse_tag(raw: bytes) -> types.GitObjectTag:
    body = parse_key_value_list_with_message(raw)

    return types.GitObjectTag.model_validate(
        body |
        {
            "type": body['type'].decode(),
            "tag": body['tag'].decode(),
            "tagger": body['tagger'],
        } |
        {
            "type_": types.GitObjectTypeEnum.TAG,
            "data": raw,
        }
    )


def prettify(obj: types.GitObject) -> bytes:
    if isinstance(obj, types.GitObjectBlob):
        return obj.blob

    elif isinstance(obj, types.GitObjectCommit):
        data = obj.model_dump()
        data.pop('type_')
        return serialize_key_value_list_with_message(data)

    elif isinstance(obj, types.GitObjectTree):
        res = b''
        type_mapping = {
            '04': 'tree',
            '10': 'blob',
            '12': 'blob',
            '16': 'commit',
        }
        for item in obj.items:
            type_ = type_mapping.get(item.mode[:2])
            if not type_:
                raise Exception(f'Unknown mode: {item.mode}')
            res += f'{item.mode} {type_} {item.sha}\t{item.path}\n'.encode()

        return res

    elif isinstance(obj, types.GitObjectTag):
        data = obj.model_dump()
        data.pop('type_')
        return serialize_key_value_list_with_message(data)

    raise Exception(f'Unknown object type: {obj.type_}')


def serialize(obj: types.GitObject) -> bytes:
    if isinstance(obj, types.GitObjectBlob):
        return obj.blob

    elif isinstance(obj, types.GitObjectCommit):
        data = obj.model_dump()
        data.pop('type_')
        return serialize_key_value_list_with_message(data)

    elif isinstance(obj, types.GitObjectTree):
        res = b''

        for item in obj.items:
            res += item.mode.encode() + b' ' + item.path.encode() + b'\x00' + bytes.fromhex(item.sha)

        return res

    elif isinstance(obj, types.GitObjectTag):
        data = obj.model_dump()
        data.pop('type_')
        return serialize_key_value_list_with_message(data)

    raise Exception(f'Unknown object type: {obj.type_}')


def hash_(obj: types.GitObject) -> tuple[str, bytes]:
    data = serialize(obj)
    raw = f'{obj.type_.name.lower()} {len(data)}\x00'.encode() + data

    return hashlib.sha1(raw).hexdigest(), data


def write_(obj: types.GitObject, gitdir: pathlib.Path) -> tuple[str, pathlib.Path]:
    sha, data = hash_(obj)
    filepath = lib.get_or_create_repo_file(gitdir, f'objects/{sha[:2]}/{sha[2:]}')

    raw = f'{obj.type_.name.lower()} {len(data)}\x00'.encode() + data
    filepath.write_bytes(zlib.compress(raw))

    return sha, filepath
