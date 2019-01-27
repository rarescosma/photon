#!/usr/bin/env python3.7
from collections import defaultdict
from hashlib import md5
from operator import attrgetter
from pathlib import Path
from typing import Callable, Dict, Iterable, List

import click


@click.group()
def cli():
    """Photo name matcher."""


@cli.command()
@click.argument(
    'from_path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
)
@click.argument(
    'to_path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
)
def match(from_path: str, to_path: str):
    from_map = _file_map(_scan_dir(Path(from_path)))
    to_map = _file_map(_scan_dir(Path(to_path)))

    name_matches = set(from_map) & set(to_map)

    for m in name_matches:
        for h, files in _file_map(
                from_map[m] + to_map[m],
                identify=_hash
        ).items():
            if len(files) > 1:
                rep = "\t".join(str(f) for f in files)
                print(f'{rep}\t{h}')


def _scan_dir(d: Path) -> Iterable[Path]:
    return (f for f in d.rglob('*') if f.is_file())


def _file_map(
        files: Iterable[Path],
        identify: Callable[[Path], str] = attrgetter('name')
) -> Dict[str, List[Path]]:
    res = defaultdict(list)
    for f in files:
        res[identify(f)].append(f)
    return res


def _hash(file: Path) -> str:
    return md5(file.read_bytes()).hexdigest()


if __name__ == '__main__':
    cli()
