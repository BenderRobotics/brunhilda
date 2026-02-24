import re
from typing import Any, Dict, List


def parse_tags(description: str) -> Dict[str, str]:
    """
    Extracts tags from the test description.

    :param description: test description (docstring)
    :return: dictionary of tags, key is the tag name, value is the tag value
    """
    excluded_tags = ('steps', 'endsteps')
    tags = {}

    if description and isinstance(description, str):
        for line in description.splitlines():
            line = line.strip()

            if line.startswith('@'):
                pair = line.split(' ')
                tag = pair[0]
                tag = tag.strip('@').strip(':').lower()

                if tag not in excluded_tags:
                    if len(pair) > 1:
                        value = ' '.join(pair[1:])
                        value = value.split(',')
                    else:
                        value = ['']

                    tags[tag] = [v.strip('; ') for v in value]  # strip ; and space

    return tags


def parse_requirements(description: str) -> List[str]:
    """
    Extracts requirements from the test description.

    :param description: test description (docstring)
    :return: list of test requirements
    """
    specs = None

    if description and isinstance(description, str):
        for line in description.splitlines():
            specs = re.search(r'@spec[:\s]\s*\w.+', line.strip())

            if specs:
                break

    if specs is not None:
        specs = re.sub(r'@spec[:\s]s*', '', specs.group(0))
        specs = [' '.join(spec.split()) for spec in specs.split(',')]
    else:
        specs = ['-']

    return specs


def parse_steps(test_steps: List[Dict[str, Any]], description: str) -> List[Dict[str, Any]]:
    """
    Extracts test description without tags from the docstring.

    :param test_steps: list of executed steps
    :param description: test description (docstring)
    :return: list of parsed test steps enriched with execution results.
    """
    steps = []
    steps_active = False
    step_description_active = False
    step = None
    reg_step_description = re.compile(r'^\s*(?P<num>\d+)\)\s*>')
    reg_step_expectation = re.compile(r'^\s*>')

    if description and isinstance(description, str):
        for line in description.splitlines():
            if line.strip().startswith('@steps'):
                steps_active = True
            elif line.strip().startswith('@endsteps'):
                steps_active = False
            elif steps_active:
                # check if line stars with "1) >" (or other number)
                if reg_step_description.match(line):
                    if step:
                        steps.append(step)

                    step = {'number': 0, 'description': '', 'expectation': ''}
                    match_desc = reg_step_description.match(line)
                    step['number'] = int(match_desc.group('num'))
                    dynamic_spaces = ' ' * len(match_desc.group(0))
                    step['description'] = reg_step_description.sub(dynamic_spaces, line)
                    step['expectation'] = ''
                    step['result'] = ''
                    step['comment'] = ''
                    step['obtained'] = ''
                    step_description_active = True
                # this will happen only for invalid input, but cover the option to prevent errors
                elif step is None:
                    ...
                # check if line stars with "  >"
                elif reg_step_expectation.match(line):
                    step_description_active = False
                    match_exp = reg_step_expectation.match(line)
                    dynamic_spaces = ' ' * len(match_exp.group(0))
                    step['expectation'] = reg_step_expectation.sub(dynamic_spaces, line)
                # if still in description, append to description
                elif step_description_active:
                    step['description'] += '\n' + line
                # otherwise append to expectation
                elif step:
                    step['expectation'] += '\n' + line
    if step:
        steps.append(step)

    for test_step in test_steps:
        for i in range(len(steps)):
            if steps[i]['number'] == test_step['number']:
                steps[i]['result'] = test_step['result']
                steps[i]['comment'] = test_step['comment']
                steps[i]['obtained'] = test_step['obtained']

    return steps


def parse_description(description: str) -> str:
    """
    Extracts test description without tags from the docstring.

    :param description: test description (docstring)
    :return: description text stripped of tags and step blocks
    """
    lines = []
    block_active = False

    if description and isinstance(description, str):
        for line in description.splitlines():
            if not line.strip().startswith('@') and not block_active:
                lines.append(line)

            if line.strip().startswith('@steps'):
                block_active = True
            elif line.strip().startswith('@endsteps'):
                block_active = False

    return '\n'.join(lines)
