import ast
import re
import tokenize
from os import path
from sys import argv


def is_local(file: str, module: str):
    parts = module.split('.')
    parts[-1] += '.py'

    filename = path.join(path.dirname(file), *parts)

    if path.exists(filename):
        return filename

    return False


def find_import_deps(file: str, deps: set[str]):
    with open(file, 'r') as fp:
        ast_tree = ast.parse(fp.read())

    for node in ast.walk(ast_tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if module := is_local(file, name.name):
                    deps.add(module)
                    find_import_deps(module, deps)
                    find_marked_deps(module, deps)

        if isinstance(node, ast.ImportFrom) and (module := is_local(file, node.module)):
            deps.add(module)
            find_import_deps(module, deps)
            find_marked_deps(module, deps)


def find_marked_deps(file: str, deps: set[str]):
    dirname = path.dirname(file)

    fp = open(file, 'rb')
    tokens = tokenize.tokenize(fp.readline)

    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue

        if match := re.search('^# depends:(.+)', token.string.strip()):
            deps.add(path.join(dirname, match.group(1)))


def find_deps(file: str) -> list[str]:
    deps = set()

    find_import_deps(file, deps)
    find_marked_deps(file, deps)

    return list(deps)


if __name__ == '__main__':
    if len(argv) == 1:
        print(f'Usage: python {path.basename(__file__)} <file>')
        exit()

    for dep in find_deps(argv[1]):
        print(f'{dep} ({path.getsize(dep) / 1024:.2f}KB)')
