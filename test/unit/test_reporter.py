from unittest.mock import MagicMock, call, mock_open, patch

import pytest

from brunhilda.reporter import Reporter


@pytest.fixture
def reporter():
    """Returns a fresh Reporter instance for each test."""
    return Reporter()


# --- Testing Initialization ---


def test_init_defaults(reporter):
    assert reporter._requirements == {}
    assert reporter._outputs == []
    assert reporter._tests == {}
    assert reporter._test_plan_paths == {'_': ''}


# --- Testing internal _load method ---


def test_load_json(reporter):
    """Test that _load correctly handles JSON files."""
    mock_content = {'key': 'value'}
    with patch('builtins.open', mock_open(read_data='data'), create=True), \
         patch('simplejson.load', return_value=mock_content) as mock_json:

        result = reporter._load('data.json')
        assert result == mock_content
        mock_json.assert_called_once()


def test_load_yaml(reporter):
    """Test that _load correctly handles YAML files."""
    mock_content = {'key': 'value'}
    with patch('builtins.open', mock_open(read_data='data'), create=True), \
         patch('yaml.safe_load', return_value=mock_content) as mock_yaml:

        result = reporter._load('data.yaml')
        assert result == mock_content
        mock_yaml.assert_called_once()


def test_load_unsupported(reporter):
    """Test that _load raises ValueError for unknown file extensions."""
    with pytest.raises(ValueError, match='Unsupported file type'):
        with patch('builtins.open', mock_open(), create=True):
            reporter._load('data.txt')


# --- Testing load_tests ---


def test_load_tests(reporter):
    """Test loading a single test file input."""
    path = 'tests/run.json'
    report = 'reports/run.html'

    mock_test_data = {'tests': [{'test_id': 'T1', 'level': 1, 'result': 'PASSED'}]}

    with patch.object(reporter, '_load', return_value=mock_test_data) as mock_load:
        reporter.load_tests(path, report)

        mock_load.assert_called_once_with(path)

        stored_data = reporter._tests[path]
        assert len(stored_data) == 1
        assert stored_data[0]['html_report_path'] == report
        assert stored_data[0]['test_id_with_level'] == 'T11'


def test_load_tests_multiple(reporter):
    """Test loading multiple test files input."""
    data1 = {'tests': [{'test_id': 'T1', 'level': 1, 'result': 'PASSED'}]}
    data2 = {'tests': [{'test_id': 'T2', 'level': 2, 'result': 'EMPTY'}]}

    with patch.object(reporter, '_load', side_effect=[data1, data2]) as mock_load:
        reporter.load_tests('run1.json', 'rep1.html', 'run2.json', 'rep2.html')

        assert mock_load.call_count == 2
        mock_load.assert_has_calls([call('run1.json'), call('run2.json')])

        assert reporter._tests['run1.json'][0]['test_id_with_level'] == 'T11'
        assert reporter._tests['run2.json'][0]['test_id_with_level'] == 'T22'
        assert reporter._tests['run2.json'][0]['result'] == 'NOT-EXECUTED'


# --- Testing load_issues ---


def test_load_issues_single_path(reporter):
    """Test loading a single issues file input as a string."""

    path = 'data/issues.json'
    mock_data = {'failures': [], 'errors': []}

    with patch.object(reporter, '_load', return_value=mock_data) as mock_load:

        reporter.load_issues(path)

        mock_load.assert_called_once_with(path)

        assert path in reporter._issues
        assert reporter._issues[path] == mock_data


def test_load_issues_multiple_paths(reporter):
    """Test loading multiple issues files input."""
    data1 = {'errors': [], 'failures': [{'bug-id': 'issue1', 'comment': ''}]}
    data2 = {'errors': [], 'failures': [{'bug-id': 'issue2', 'comment': ''}]}

    with patch.object(reporter, '_load', side_effect=[data1, data2]) as mock_load:

        reporter.load_issues('data/issues_part1.json', 'data/issues_part2.json')

        assert mock_load.call_count == 2
        mock_load.assert_has_calls([call('data/issues_part1.json'), call('data/issues_part2.json')])

        assert reporter._issues['data/issues_part1.json'] == data1
        assert reporter._issues['data/issues_part2.json'] == data2


def test_load_issues_newline_update(reporter):
    """Tests load issues part, where comments newlines are updated."""
    data = {
        'errors':
            [
                {
                    'comment': ''
                }, {
                    'comment': ''
                }, {
                    'comment': 'First\nSecond'
                }, {
                    'comment': 'First\nSecond'
                }, {
                    'comment': 'Normal comment'
                }, {
                    'comment': 'Normal comment'
                }
            ],
        'failures':
            [
                {
                    'comment': ''
                }, {
                    'comment': ''
                }, {
                    'comment': 'First\nSecond'
                }, {
                    'comment': 'First\nSecond'
                }, {
                    'comment': 'Normal comment'
                }, {
                    'comment': 'Normal comment'
                }
            ]
    }
    path = 'data/issues.json'

    with patch.object(reporter, '_load', return_value=data) as mock_load:

        reporter.load_issues(path)

        mock_load.assert_called_once_with(path)

        assert path in reporter._issues
        print(reporter._issues[path])
        assert reporter._issues[path] == {
            'errors':
                [
                    {
                        'comment': ''
                    }, {
                        'comment': ''
                    }, {
                        'comment': 'First<br />Second'
                    }, {
                        'comment': 'First<br />Second'
                    }, {
                        'comment': 'Normal comment'
                    }, {
                        'comment': 'Normal comment'
                    }
                ],
            'failures':
                [
                    {
                        'comment': ''
                    }, {
                        'comment': ''
                    }, {
                        'comment': 'First<br />Second'
                    }, {
                        'comment': 'First<br />Second'
                    }, {
                        'comment': 'Normal comment'
                    }, {
                        'comment': 'Normal comment'
                    }
                ]
        }


# --- Testing justify_tests ---


def test_justify_tests(reporter):
    """Test the logic that matches issues to tests and updates results."""

    reporter._tests = {
        'tests.json':
            [
                {
                    'test_id': 'TestCase1.test_01_fail',
                    'level': 'system',
                    'result': 'FAILED',
                    'comment': '',
                    'bug_id': [],
                    'subtests': [],
                    'tags': {}
                }, {
                    'test_id': 'TestCase1.test_02_subtest',
                    'level': 'system',
                    'result': 'FAILED',
                    'comment': 'Some comment',
                    'bug_id': [],
                    'subtests':
                        [
                            {
                                'id': "TestCase1.test_02_subtest (i=0, j=0, bc='9.1.2')",
                                'result': 'FAILED'
                            }, {
                                'id': "TestCase1.test_02_subtest (i=1, j=2, bc='9.1.2')",
                                'result': 'PASSED'
                            }
                        ],
                    'tags': {}
                }, {
                    'test_id': 'TestCase1.test_03_error',
                    'level': 'system',
                    'result': 'ERRORED',
                    'comment': '',
                    'bug_id': [],
                    'subtests': [],
                    'tags': {}
                }
            ]
    }

    reporter._issues = {
        'issues.json':
            {
                'run': {
                    'level': 'system',
                    'dut': 'MMI2'
                },
                'errors': [],
                'failures':
                    [
                        {
                            'test': 'TestCase1.test_01_fail',
                            'sub-test': None,
                            'result': 'FAILED',
                            'justified': 'yes',
                            'comment': 'Known HW error',
                            'bug-id': '123',
                            'extra': []
                        }, {
                            'test': 'TestCase1.test_02_subtest',
                            'sub-test': "TestCase1.test_02_subtest (i=0, j=0, bc='9.1.2')",
                            'result': 'FAILED',
                            'justified': 'YES',
                            'comment': 'Subtest fail',
                            'bug-id': '456',
                            'extra': []
                        }, {
                            'test': 'TestCase1.test_03_error',
                            'sub-test': None,
                            'result': 'ERRORED',
                            'justified': '',
                            'comment': 'New error',
                            'bug-id': '',
                            'extra': []
                        }
                    ]
            }
    }

    reporter.justify_tests()

    tests = reporter._tests['tests.json']
    test_A = tests[0]
    test_B = tests[1]
    test_C = tests[2]

    assert test_A['result'] == 'JUSTIFIED'
    assert 'Known HW error' in test_A['comment']
    assert '123' in test_A['bug_id']

    assert test_B['subtests'][0]['result'] == 'JUSTIFIED'
    assert test_B['subtests'][1]['result'] == 'PASSED'
    assert test_B['result'] == 'JUSTIFIED'
    assert 'Some comment' in test_B['comment']
    assert 'Subtest fail' in test_B['comment']
    assert '456' in test_B['bug_id']

    assert test_C['result'] == 'ERRORED'
    assert 'New error' in test_C['comment']
