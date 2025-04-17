"""
# Public Fault Tree Analyser: cli.py

Command-line interface.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import argparse

from pfta._version import __version__


def parse_cli_arguments():
    parser = argparse.ArgumentParser(description='Perform a fault tree analysis.')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'{parser.prog} version {__version__}',
    )

    return parser.parse_args()


def main():
    arguments = parse_cli_arguments()


if __name__ == '__main__':
    main()
