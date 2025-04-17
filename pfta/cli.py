"""
# Public Fault Tree Analyser: cli.py

Command-line interface.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import argparse
import os
import shutil

from pfta._version import __version__


def parse_cli_arguments():
    parser = argparse.ArgumentParser(description='Perform a fault tree analysis.')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'{parser.prog} version {__version__}',
    )
    parser.add_argument(
        'fault_tree_text_file',
        type=argparse.FileType('r'),
        help='fault tree text file; output is written to `{ft.txt}.out/`',
        metavar='ft.txt',
    )

    return parser.parse_args()


def mkdir_robust(directory_name: str):
    if os.path.isfile(directory_name):
        os.remove(directory_name)

    if os.path.isdir(directory_name):
        shutil.rmtree(directory_name)

    os.mkdir(directory_name)


def main():
    arguments = parse_cli_arguments()
    fault_tree_text_file = arguments.fault_tree_text_file

    # TODO: main fault tree computation

    output_directory_name = f'{fault_tree_text_file.name}.out'

    mkdir_robust(output_directory_name)

    # TODO: write output


if __name__ == '__main__':
    main()
