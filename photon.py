#!/usr/bin/env python3.7
"""Dead-simple tool for matching photos by name and hash."""
from collections import defaultdict
from functools import partial
from hashlib import md5
from operator import attrgetter
from pathlib import Path
from typing import (
    Callable, Dict, Hashable, Iterable, List, NamedTuple, Tuple, TypeVar,
)

import click

A = TypeVar('A')
K = TypeVar('K', bound=Hashable)
PathGroup = Dict[str, List[Path]]
Match = NamedTuple('Match', [('orig', Path), ('dupe', Path), ('md5', str)])

existing_dir = partial(
    click.argument,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
)


@click.group()
def cli():
    """Photo name matcher."""


@cli.command()
@existing_dir('from_dir')
@existing_dir('to_dir')
def match(from_dir: str, to_dir: str):
    """Find duplicates."""
    for m in set(_match(Path(from_dir), Path(to_dir))):
        print('\t'.join([str(m.orig), str(m.dupe), m.md5]))


def _match(from_path: Path, to_path: Path) -> Iterable[Match]:
    """Find duplicates in to_path relative to from_path."""
    from_map: PathGroup = _group_by(set(_scan_dir(from_path)))
    to_map: PathGroup = _group_by(set(_scan_dir(to_path)))

    name_matches = set(from_map) & set(to_map)

    for m in name_matches:
        for h, fs in _group_by(from_map[m] + to_map[m], identify=_hash).items():
            dupes, orig = _split(fs, lambda f: _is_ancestor(to_path, f))
            if orig:
                orig_min = min(orig, key=lambda x: str(x.resolve()))
                yield from (Match(orig=orig_min, dupe=d, md5=h) for d in dupes)


def _group_by(
        xs: Iterable[A],
        identify: Callable[[A], K] = attrgetter('name')
) -> Dict[K, List[A]]:
    """Group xs by an identifier function."""
    res: Dict[K, List[A]] = defaultdict(list)
    for x in xs:
        res[identify(x)].append(x)
    return res


def _split(xs: Iterable[A], p: Callable[[A], bool]) -> Tuple[List[A], List[A]]:
    """Split iterable by predicate into tuple of matching, non-matching."""
    grouped = _group_by(xs, p)
    return grouped.get(True, []), grouped.get(False, [])


def _scan_dir(d: Path) -> Iterable[Path]:
    """Generate all file paths under d."""
    return (f for f in d.rglob('*') if f.is_file() and not f.is_symlink())


def _hash(file: Path) -> str:
    """Compute the MD5 digest of a file."""
    return md5(file.read_bytes()).hexdigest()


def _is_ancestor(d: Path, f: Path) -> bool:
    """True if d is an ancestor of f."""
    return str(f.resolve()).startswith(str(d.resolve()))


if __name__ == '__main__':
    cli()
