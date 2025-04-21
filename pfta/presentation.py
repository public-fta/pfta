"""
# Public Fault Tree Analyser: presentation.py

Presentational classes.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import csv
import os

from pfta.common import natural_repr


class Table:
    def __init__(self, headings: list[str], data: list[list]):
        self.headings = headings
        self.data = data

    def __repr__(self):
        return natural_repr(self)

    def write_tsv(self, file_name: str):
        with open(file_name, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter='\t', lineterminator=os.linesep)
            writer.writerow(self.headings)
            writer.writerows(self.data)
