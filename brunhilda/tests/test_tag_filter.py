import pytest
from .. import tag_filter


@pytest.mark.parametrize('test_input, expected_result', [
    ('1', 1),
    ('1s', 1),
    (' 1 s ', 1),
    ('1 sec', 1),
    ('1second', 1),
    ('5.5second', 5.5),
    ('2m', 2 * 60),
    ('10m3s', 603),
    ('1.5min', 90),
    ('3 minutes', 180),
    ('3 minutes 5s ', 185),
    ('3 min 0sec ', 180),
    ('1h', 3600),
    ('2h3m2s ', 7382),
    ('1 hour 5 s ', 3605),
    ('2.5 hours 5 s ', 9005),
    ('24s 1d', 86424),
])
def test_tag_filter_eval_time(test_input, expected_result):
    assert tag_filter.eval_time(test_input) == pytest.approx(expected_result)


@pytest.mark.parametrize('value, tag, expected_result', [
    ('a', ['a'], True),
    ('a', ['b'], False),
    ('a', [], False),
    ('a', ['a', 'b'], False),
])
def test_tag_filter_equal(tag, value, expected_result):
    assert tag_filter.equal(tag, value) == expected_result


@pytest.mark.parametrize('value, tag, expected_result', [
    ('a', ['a'], False),
    ('a', ['b'], True),
    ('a', [], False),
    ('a', ['a', 'b'], False),
])
def test_tag_filter_not_equal(tag, value, expected_result):
    assert tag_filter.not_equal(tag, value) == expected_result


@pytest.mark.parametrize('value, tag, expected_result', [
    ('a', ['a'], True),
    ('a', ['b'], False),
    ('a', [], False),
    ('a', ['a', 'b'], True),
])
def test_tag_filter_contains(tag, value, expected_result):
    assert tag_filter.contains(tag, value) == expected_result


@pytest.mark.parametrize('value, tag, expected_result', [
    ('a', ['a'], False),
    ('a', ['b'], True),
    ('a', [], True),
    ('a', ['a', 'b'], False),
])
def test_tag_filter_not_contains(tag, value, expected_result):
    assert tag_filter.not_contains(tag, value) == expected_result


@pytest.mark.parametrize('value, tag, expected_result', [
    ('2.0', ['1'], False),
    ('1.5', ['1'], False),
    ('1h', ['60m'], False),
    ('1', ['1'], False),
    ('0', ['1'], True),
    ('2', ['1', '2'], False),
    ('a', ['1'], False),
    ('1', ['a'], False),
    ('1', [' '], False),
    ('1', [], False),
])
def test_tag_filter_gt(tag, value, expected_result):
    assert tag_filter.gt(tag, value) == expected_result


@pytest.mark.parametrize('value, tag, expected_result', [
    ('2.0', ['1'], False),
    ('1.5', ['1'], False),
    ('1h', ['60m'], True),
    ('1', ['1'], True),
    ('0', ['1'], True),
    ('2', ['1', '2'], False),
    ('a', ['1'], False),
    ('1', ['a'], False),
    ('1', [' '], False),
    ('1', [], False),
])
def test_tag_filter_ge(tag, value, expected_result):
    assert tag_filter.ge(tag, value) == expected_result


@pytest.mark.parametrize('value, tag, expected_result', [
    ('2.0', ['1'], True),
    ('1.5', ['1'], True),
    ('1h', ['60m'], False),
    ('1', ['1'], False),
    ('0', ['1'], False),
    ('2', ['1', '2'], False),
    ('a', ['1'], False),
    ('1', ['a'], False),
    ('1', [' '], False),
    ('1', [], False),
])
def test_tag_filter_lt(tag, value, expected_result):
    assert tag_filter.lt(tag, value) == expected_result


@pytest.mark.parametrize('value, tag, expected_result', [
    ('2.0', ['1'], True),
    ('1.5', ['1'], True),
    ('1h', ['60m'], True),
    ('1', ['1'], True),
    ('0', ['1'], False),
    ('2', ['1', '2'], False),
    ('a', ['1'], False),
    ('1', ['a'], False),
    ('1', [' '], False),
    ('1', [], False),
])
def test_tag_filter_le(tag, value, expected_result):
    assert tag_filter.le(tag, value) == expected_result


TAGS = {
    'A': ['a', 'b', 'c'],
    'B': ['b'],
    'C': ['c'],
    'D': ['10s'],
    'E': ['5s'],
    'F': [],
    'G': [' '],
}


@pytest.mark.parametrize('condition, expected_result', [
    ('@A', True),
    ('@B', True),
    ('@Z', False),
    ('!A', False),
    ('!B', False),
    ('!Z', True),
    ('A==c', False),
    ('B==b', True),
    ('B==c', False),
    ('Z==c', False),
    ('A!=c', False),
    ('B!=b', False),
    ('B!=c', True),
    ('Z!=c', False),
    ('A=~c', True),
    ('A=~d', False),
    ('B=~b', True),
    ('B=~c', False),
    ('Z=~c', False),
    ('A!~c', False),
    ('A!~d', True),
    ('B!~b', False),
    ('B!~c', True),
    ('Z!~c', False),
    ('D>5s', True),
    ('D>20s', False),
    ('F>1', False),
    ('D>=10s', True),
    ('D>=20s', False),
    ('D<5s', False),
    ('D<20s', True),
    ('D<=10s', True),
    ('D<=20s', True),
    ('F<=5s', False),
    ('G<=5s', False),
])
def test_tag_filter_eval_condition(condition, expected_result):
    assert tag_filter.eval_condition(condition, TAGS) == expected_result


@pytest.mark.parametrize('condition, expected_result', [
    ('@A', True),
    ('@A && @B', True),
    ('@A && @B && @Z', False),
    ('@A && @B && !Z', True),
    ('B==b && A=~c', True),
    ('Z=~c && D>=10s', False),
    ('D<20s && D>=10s', True),
])
def test_tag_filter_eval_and(condition, expected_result):
    assert tag_filter.eval_and(condition, TAGS) == expected_result


@pytest.mark.parametrize('condition, expected_result', [
    ('@A', True),
    ('@A || @B', True),
    ('@A || @B || @Z', True),
    ('@A || @B || !Z', True),
    ('B==b || A=~c', True),
    ('Z=~c || D>=10s', True),
    ('D<20s || D>=10s', True),
    ('@X || @Y || @Z', False),
    ('B==x || B==y', False),
])
def test_tag_filter_eval_or(condition, expected_result):
    assert tag_filter.eval_or(condition, TAGS) == expected_result


@pytest.mark.parametrize('condition, expected_result', [
    ('@A', True),
    ('A == a && B == b || E >= 5s', True),
    ('A == a && B == b || E < 5s', False),
])
def test_tag_filter_eval_tags(condition, expected_result):
    assert tag_filter.eval_tags(condition, TAGS) == expected_result
