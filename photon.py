#!/usr/bin/env python3.7
"""Dead-simple tool for matching photos by name and hash."""
import os
import string
import sys
from collections import defaultdict
from functools import partial, wraps
from hashlib import md5
from operator import attrgetter
from pathlib import Path
from random import choices
from typing import (
    Any, Callable, Dict, Hashable, Iterable, List, NamedTuple, Tuple, TypeVar,
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


def effect(f: Callable) -> Callable:
    """Stigmatize side effects."""
    @wraps(f)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        return f(*args, **kwargs)
    return wrapped


@cli.command()
@existing_dir('from_dir')
@existing_dir('to_dir')
def match(from_dir: str, to_dir: str):
    """Find duplicates."""
    for m in set(_match(Path(from_dir), Path(to_dir))):
        print('\t'.join([str(m.orig), str(m.dupe), m.md5]))


@cli.command()
@existing_dir('from_dir')
@existing_dir('to_dir')
def dedupe(from_dir: str, to_dir: str):
    """Deduplicate using symlinks."""
    for m in set(_match(Path(from_dir), Path(to_dir))):
        print(f'{str(m.dupe)} -> {str(m.orig)}', file=sys.__stderr__)
        _atomic_link(m.dupe, to_file=m.orig)


def _match(from_path: Path, to_path: Path) -> Iterable[Match]:
    """Find duplicates in to_path relative to from_path."""
    name_key = attrgetter('name')
    from_map: PathGroup = _group_by(set(_scan_dir(from_path)), key=name_key)
    to_map: PathGroup = _group_by(set(_scan_dir(to_path)), key=name_key)

    name_matches = set(from_map) & set(to_map)

    for m in name_matches:
        for h, fs in _group_by(from_map[m] + to_map[m], key=_hash).items():
            dupes, orig = _split(fs, lambda f: _is_ancestor(to_path, f))
            if orig:
                orig_min = min(orig, key=lambda x: str(x.resolve()))
                yield from (Match(orig=orig_min, dupe=d, md5=h) for d in dupes)


def _group_by(xs: Iterable[A], key: Callable[[A], K]) -> Dict[K, List[A]]:
    """Group xs by the result of the key function."""
    res: Dict[K, List[A]] = defaultdict(list)
    for x in xs:
        res[key(x)].append(x)
    return res


def _split(xs: Iterable[A], p: Callable[[A], bool]) -> Tuple[List[A], List[A]]:
    """Split iterable by predicate into tuple of matching, non-matching."""
    grouped = _group_by(xs, p)
    return grouped.get(True, []), grouped.get(False, [])


@effect
def _scan_dir(d: Path) -> Iterable[Path]:
    """Generate all file paths under d."""
    return (f for f in d.rglob('*') if f.is_file() and not f.is_symlink())


def _hash(file: Path) -> str:
    """Compute the MD5 digest of a file."""
    return md5(file.read_bytes()).hexdigest()


def _is_ancestor(d: Path, f: Path) -> bool:
    """True if d is an ancestor of f."""
    return str(f.resolve()).startswith(str(d.resolve()))


@effect
def _atomic_link(from_file: Path, to_file: Path) -> None:
    """Create a relative symlink from_file to_file."""
    tmp = Path(from_file.stem + _random_str())
    tmp.symlink_to(_relative(from_file, to_file))
    tmp.rename(from_file)


def _relative(from_file: Path, to_file: Path) -> str:
    """Get the relative path from_file to_file."""
    return os.path.relpath(str(to_file), str(from_file.parent))


@effect
def _random_str(n: int = 12) -> str:
    """Generate a random string on length n."""
    return ''.join(choices(string.ascii_uppercase + string.digits, k=n))


if __name__ == '__main__':
    cli()
