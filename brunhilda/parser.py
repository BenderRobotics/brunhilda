import re

def parse_tags(description):
    """
    Extracts tags from the test description.

    :param str description: test description (docstring)
    :return: dictionary of tags, key is the tag name, value is the tag value
    :rtype: Dict[str, str]
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


def parse_requirements(description):
    """
    Extracts requirements from the test description.

    :param str description: test description (docstring)
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


def parse_steps(test_steps, description):
    """
    Extracts test description without tags from the docstring.

    :param str description: test description (docstring)
    """
    steps = []
    steps_active = False
    step_description_active = False
    step = None
    reg_step_description = re.compile(r'^\s*(?P<num>\d+)\)\s*>')
    reg_step_expectation = re.compile(r'^\s*>')
    indent_spaces = '            '

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
                    step['number'] = int(reg_step_description.match(line).group('num'))
                    step['description'] = reg_step_description.sub(indent_spaces, line)
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
                    step['expectation'] = reg_step_expectation.sub(indent_spaces, line)
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


def parse_description(description):
    """
    Extracts test description without tags from the docstring.

    :param str description: test description (docstring)
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
