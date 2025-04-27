"""
# Public Fault Tree Analyser: cli.py

Command-line interface.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import argparse
import os
import shutil
import sys

from pfta._version import __version__
from pfta.core import FaultTree
from pfta.woe import FaultTreeTextException


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
    fault_tree_text_file_name = fault_tree_text_file.name
    fault_tree_text = fault_tree_text_file.read()

    try:
        fault_tree = FaultTree(fault_tree_text)
    except FaultTreeTextException as exception:
        line_number = exception.line_number
        message = exception.message
        explainer = exception.explainer

        line_parenthetical = f' (line {line_number})' if line_number else ''
        explainer_tail = f'\n\n{explainer}' if explainer else ''

        print(f'Error in `{fault_tree_text_file_name}`{line_parenthetical}: {message}{explainer_tail}', file=sys.stderr)
        sys.exit(1)

    model_table = fault_tree.compile_model_table()
    event_table = fault_tree.compile_event_table()
    gate_table = fault_tree.compile_gate_table()
    cut_set_table_from_gate_id = fault_tree.compile_cut_set_tables()
    # TODO: figure_from_id

    output_directory_name = f'{fault_tree_text_file_name}.out'
    cut_sets_directory_name = f'{output_directory_name}/cut-sets'
    # TODO: figures_directory_name

    mkdir_robust(output_directory_name)
    mkdir_robust(cut_sets_directory_name)

    model_table.write_tsv(f'{output_directory_name}/models.tsv')
    event_table.write_tsv(f'{output_directory_name}/events.tsv')
    gate_table.write_tsv(f'{output_directory_name}/gates.tsv')

    for gate_id, cut_set_table in cut_set_table_from_gate_id.items():
        cut_set_table.write_tsv(f'{cut_sets_directory_name}/{gate_id}.tsv')

    # TODO: other writes


if __name__ == '__main__':
    main()
