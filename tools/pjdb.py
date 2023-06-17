#! /usr/bin/env python3
#
# pjdb.py - JSON-ify pacman databases.
#
# (C) 2021 Richard Neumann <mail at richard dash neumann period de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""JSON-ify pacman database."""

from datetime import datetime
from json import dumps
from pathlib import Path
from subprocess import CompletedProcess, run
from tempfile import TemporaryDirectory
from typing import Iterator, Union


DESCFILE = 'desc'
INT_KEYS = {'%BUILDDATE%', '%CSIZE%', '%ISIZE%'}
LIST_KEYS = {'%DEPENDS%', '%MAKEDEPENDS%', '%OPTDEPENDS%'}
LIST_SEP = '\n'
ITEM_SEP = '\n\n'
KEY_VALUE_SEP = '\n'
TAR = '/usr/bin/tar'
KeyValuePair = tuple[str, Union[str, int]]
PackageDescription = tuple[str, KeyValuePair]


class Pjdb:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)

    def _tar_xf(self, tarfile: Path, directory: Path) -> CompletedProcess:
        """Workaround for missing zstd support in Python's tar library."""

        return run([TAR, 'xf', str(tarfile), '-C', str(directory)], check=True)

    def kv_from_str(self, text: str) -> Iterator[KeyValuePair]:
        """Yields key / value pairs from a string."""

        for item in text.split(ITEM_SEP):
            if not item.strip():
                continue

            key, value = item.split(KEY_VALUE_SEP, maxsplit=1)

            if key in INT_KEYS:
                value = int(value)
            elif key in LIST_KEYS:
                value = value.split(LIST_SEP)

            yield (key.replace('%', '').lower(), value)

    def kv_from_file(self, filename: Path) -> Iterator[KeyValuePair]:
        """Yields key / value pairs from a file."""

        with filename.open('r') as file:
            yield from self.kv_from_str(file.read())

    def pkg_from_dir(self, dirname: Path) -> PackageDescription:
        """Reads package information from a package directory."""

        return (dirname.name, dict(self.kv_from_file(dirname / DESCFILE)))

    def pkgs_from_dir(self, dirname: Path) -> Iterator[PackageDescription]:
        """Yields package descriptions."""

        for pkgdir in dirname.iterdir():
            yield self.pkg_from_dir(pkgdir)

    def pkgs_from_db(self) -> dict:
        """Yields package descriptions from a database file."""

        with TemporaryDirectory() as tmpd:
            tmpd = Path(tmpd)
            self._tar_xf(self.db_path, tmpd)
            return dict(self.pkgs_from_dir(tmpd))

    def to_json(self) -> str:
        """Converts pacman database to JSON format."""

        return dumps(self.pkgs_from_db(), indent=2)
