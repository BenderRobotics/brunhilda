import re
import operator
from typing import (Sequence, Dict, Callable)


def _num_compare(tag_values: Sequence[str], expression: str, operator: Callable):
    try:
        lh = eval_time(tag_values[0])
        rh = eval_time(expression)
        condition = operator(lh, rh)
        return condition and (len(tag_values) == 1)
    except (ValueError, IndexError):
        return False


def eval_time(expression: str) -> float:
    """
    Parses given time expresion into float value in seconds

    Supported symbols are:
    - s, sec, second, seconds
    - m, min, minute, minutes
    - h, hour, hours
    - d, day, days

    Examples:
    - 1h 1m 1s -> 3661
    - 2 hours 2 minutes 2 seconds -> 7322

    :param expression: expression to be parsed
    :return: seconds
    """
    expression = expression.lower().replace(' ', '')
    times = {
        r'(d(ays?)?)': '*24*60*60+',
        r'(h(ours?)?)': '*60*60+',
        r'(m(in(utes?)?)?)': '*60+',
        r'(s(ec(onds?)?)?)': '+',
    }

    if not expression:
        raise ValueError('Empty string can not be parsed to time value.')

    for pattern, value in times.items():
        match = re.match(r'.*\d+\.?\d*' + pattern + r'.*', expression, re.IGNORECASE)

        if match:
            expression = expression.replace(match.group(1), value)

    chunks = [c for c in expression.split('+') if c]
    sum_ = 0

    for chunk in chunks:
        value = 1.0

        for v in chunk.split('*'):
            if v:
                value *= float(v)

        sum_ += value

    return sum_


def equal(tag_values: Sequence[str], value: str):
    return (len(tag_values) == 1) and (value == tag_values[0])


def not_equal(tag_values: Sequence[str], value: str):
    return (len(tag_values) == 1) and (value != tag_values[0])


def contains(tag_values: Sequence[str], value: str):
    return value in tag_values


def not_contains(tag_values: Sequence[str], value: str):
    return value not in tag_values


def gt(tag_values: Sequence[str], value: str):
    return _num_compare(tag_values, value, operator.gt)


def ge(tag_values: Sequence[str], value: str):
    return _num_compare(tag_values, value, operator.ge)


def lt(tag_values: Sequence[str], value: str):
    return _num_compare(tag_values, value, operator.lt)


def le(tag_values: Sequence[str], value: str):
    return _num_compare(tag_values, value, operator.le)


def eval_condition(condition: str, tags: Dict[str, Sequence[str]]):
    """
    Evaluates logical operators in the condition.

    :param condition: string filter condition
    :param tags: dictionary of tags
    :return: True if the condition is satisfied with the given tag.
    """
    OPERATORS = {
        '==': equal,
        '!=': not_equal,
        '=~': contains,
        '!~': not_contains,
        '>=': ge,
        '<=': le,
        '>': gt,
        '<': lt,
    }

    condition = condition.strip()

    if condition.startswith('@'):
        return condition.strip('@') in tags
    elif condition.startswith('!'):
        return condition.strip('!') not in tags
    else:
        for op, func in OPERATORS.items():
            if op in condition:
                tag, value = condition.split(op)
                tag = tag.strip()
                value = value.strip()

                if tag in tags:
                    return func(tags[tag], value)
                else:
                    return False

        raise ValueError(f'Invalid operator in condition "{condition}".')


def eval_and(condition: str, tags: Dict[str, Sequence[str]]):
    """
    Evaluates AND logical operation in the condition.

    :param condition: string filter condition
    :param tags: dictionary of tags
    :return: True if the condition is satisfied with the given tag.
    """
    chunks = condition.split('&&')
    result = True

    for c in chunks:
        result = operator.and_(result, eval_condition(c, tags))

    return result


def eval_or(condition: str, tags: Dict[str, Sequence[str]]):
    """
    Evaluates OR logical operation in the condition.

    :param condition: string filter condition
    :param tags: dictionary of tags
    :return: True if the condition is satisfied with the given tag.
    """
    chunks = condition.split('||')
    result = False

    for c in chunks:
        result = operator.or_(result, eval_and(c, tags))

    return result


def eval_tags(condition: str, tags: Dict[str, Sequence[str]]):
    """
    Checks if given tags matches the set tag_filter

    - tag1==A strict equality/match - test must be tagged by tag1 and it must
              contain only the one value A (does not allow other values to be
              present)
    - tag1!=A strict inequality/mismatch - test must be tagged by tag1 and it
              must not contain the one value A (does not allow other values to
              be present)
    - tag1=~A contains - test must be tagged by tag1 and it must contain at
              least the one value A (allows other values to be present)
    - tag1!~A does not contain - test must be tagged by tag1 and it must not
              contain the value A (allows other values to be present)
    - @tag1 is tagged - test is tagged with tag1
    - !tag1 is not tagged test is not tagged tag1
    - tag1>=A greater than or equal to - test must be tagged by tag1 its numeric
              value must not be lower than A
    - tag1>A greater than - test must be tagged by tag1 its numeric value must
             be greater than A
    - tag1<=A lower than or equal to - test must be tagged by tag1 its numeric
              value must not be greater than A
    - tag1<A lower than - test must be tagged by tag1 its numeric value must
             be lower than A

    Logical operations:

    - || - OR operation (one of condition satisfied)
    - && - AND operation (both conditions satisfied)

    Examples

    - tag1=~A && @tag2 - tag1 contains A and tag2 is present

    :param condition: string filter condition
    :param tags: dictionary of tags
    :return: True if the tags matching filter, False if not
    """
    return eval_or(condition, tags)
