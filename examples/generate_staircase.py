import inspect
import os


DEPTH = 20


def fault_tree_properties_text():
    return '\n'.join([
        '- times: nan',
        '- tolerance: 5e-3',
    ])


def model_text():
    return '\n'.join([
        'Model: MODEL',
        '- model_type: Fixed',
        '- probability: 0.1',
        '- intensity: 0',
    ])


def base_event_text():
    return '\n'.join([
        'Event: BASE',
        '- model: MODEL',
    ])


def and_child_text(level):
    return '\n'.join([
        f'Event: AND_CHILD_{level}',
        f'- model: MODEL',
    ])


def or_child_text(level):
    return '\n'.join([
        f'Event: OR_CHILD_{level}',
        f'- model: MODEL',
    ])


def and_gate_text(level):
    return '\n'.join([
        f'Gate: AND_GATE_{level}',
        f'- type: AND',
        f'- inputs: AND_CHILD_{level}, OR_GATE_{level}',
    ])


def or_gate_text(level):
    return '\n'.join([
        f'Gate: OR_GATE_{level}',
        f'- type: OR',
        f'- inputs: OR_CHILD_{level}, {f"AND_GATE_{level + 1}" if level < DEPTH - 1 else "BASE"}',
    ])



def main():
    fault_tree_text = '\n'.join([
        '# Procedurally generated from `generate_staircase.py`.',
        '',
        '',
        fault_tree_properties_text(),
        '',
        '',
        model_text(),
        '',
        '',
        base_event_text(),
        '',
        '',
        '\n\n'.join(and_child_text(level) for level in range(DEPTH)),
        '',
        '',
        '\n\n'.join(or_child_text(level) for level in range(DEPTH)),
        '',
        '',
        '\n\n'.join(and_gate_text(level) for level in range(DEPTH)),
        '',
        '',
        '\n\n'.join(or_gate_text(level) for level in range(DEPTH)),
        '',
    ])

    examples_directory = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda: 0)))
    with open(f'{examples_directory}/staircase.txt', 'w', encoding='utf-8') as file:
        file.write(fault_tree_text)


if __name__ == '__main__':
    main()
