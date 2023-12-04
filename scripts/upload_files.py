import json
import os
from os import path
from sys import argv

from ampy.files import Files
from ampy.pyboard import Pyboard
from python_minifier import minify

from resolve_deps import find_deps

device = argv[3] if len(argv) >= 4 else '/dev/ttyUSB0'
filesystem = Files(Pyboard(device, baudrate=115200, rawdelay=0))

filemap_path = '.cache/filemap.json'


def load_filemap():
    if not path.exists(filemap_path):
        return {}

    try:
        return json.load(open(filemap_path, 'r'))
    except ValueError:
        return {}


def save_filemap():
    if not path.exists('.cache'):
        os.mkdir('.cache')

    json.dump(filemap, open(filemap_path, 'w'))


filemap = load_filemap()


def ensure_dir(file: str):
    dirs = file.split(os.sep)[:-1]
    current = ''

    for entry in dirs:
        current += os.sep + entry
        filesystem.mkdir(current, exists_okay=True)


def is_debug():
    return os.environ.get('DEBUG', '')


def upload(local: str, remote: str):
    mtime = int(path.getmtime(local) * 1000)

    if filemap.get(local, 0) == mtime and not is_debug():
        print(f'{local} -> {remote} (skip)')
        return

    filemap[local] = mtime

    if local.endswith('.py'):
        with open(local, 'r') as fp:
            if is_debug():
                content = fp.read().encode()
            else:
                content = minify(fp.read(), local).encode()
    else:
        with open(local, 'rb') as fp:
            content = fp.read()

    print(f'{local} -> {remote} ({len(content) / 1024:.2f}KB)')

    ensure_dir(remote)
    filesystem.put(remote, content)


def main():
    deps = [argv[1]] + find_deps(argv[1])

    print(f'Uploading {len(deps)} files to {device}:')

    for local in deps:
        remote = path.relpath(local, argv[2])
        upload(local, remote)

    save_filemap()


if __name__ == '__main__':
    if len(argv) < 3:
        print(f'Usage: python {path.basename(__file__)} <index> <base> [device]')
        exit()

    main()
