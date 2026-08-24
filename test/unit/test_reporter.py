import json
from datetime import datetime
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
        assert stored_data[0]['test_id_with_level'] == 'T1_1'


def test_load_tests_multiple(reporter):
    """Test loading multiple test files input."""
    data1 = {'tests': [{'test_id': 'T1', 'level': 1, 'result': 'PASSED'}]}
    data2 = {'tests': [{'test_id': 'T2', 'level': 2, 'result': 'EMPTY'}]}

    with patch.object(reporter, '_load', side_effect=[data1, data2]) as mock_load:
        reporter.load_tests('run1.json', 'rep1.html', 'run2.json', 'rep2.html')

        assert mock_load.call_count == 2
        mock_load.assert_has_calls([call('run1.json'), call('run2.json')])

        assert reporter._tests['run1.json'][0]['test_id_with_level'] == 'T1_1'
        assert reporter._tests['run2.json'][0]['test_id_with_level'] == 'T2_2'
        assert reporter._tests['run2.json'][0]['result'] == 'NOT-EXECUTED'


# --- Testing _load datetime parsing ---


def test_load_json_datetime_parsing(reporter):
    """Test that _load correctly parses datetime strings from JSON into datetime objects."""
    mock_json_content = json.dumps(
        {
            'env_info': {
                'timestamp_start': '2026-05-27 09:53:02.787515'
            },
            'normal_text': 'This is just a normal string'
        }
    )

    with patch('builtins.open', mock_open(read_data=mock_json_content)):
        result = reporter._load('fake_path/run.json')

    parsed_date = result['env_info']['timestamp_start']
    assert isinstance(parsed_date, datetime)

    assert parsed_date == datetime(2026, 5, 27, 9, 53, 2, 787515)

    assert result['normal_text'] == 'This is just a normal string'


def test_load_yaml_datetime_parsing(reporter):
    """Test that _load correctly parses datetime strings from YAML into datetime objects."""
    mock_yaml_content = """
    env_info:
        timestamp_start: 2026-05-27 09:53:02.787515
    normal_text: This is just a normal string
    """

    with patch('builtins.open', mock_open(read_data=mock_yaml_content)):
        result = reporter._load('fake_path/run.yaml')

    parsed_date = result['env_info']['timestamp_start']
    assert isinstance(parsed_date, datetime)

    assert parsed_date == datetime(2026, 5, 27, 9, 53, 2, 787515)

    assert result['normal_text'] == 'This is just a normal string'


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


def _subtest_scenario_tests() -> dict:
    tests = {
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
                    'result': 'ERRORED',
                    'comment': 'Some comment',
                    'bug_id': [],
                    'subtests':
                        [
                            {
                                'id': "TestCase1.test_02_subtest (i=0, j=0, bc='9.1.2')",
                                'result': 'FAILED',
                                'num': 1
                            }, {
                                'id': "TestCase1.test_02_subtest (i=1, j=2, bc='9.1.2')",
                                'result': 'PASSED',
                                'num': 2
                            }, {
                                'id': "TestCase1.test_02_subtest (i=2, j=3, bc='9.1.2')",
                                'result': 'ERRORED',
                                'num': 3
                            }, {
                                'id': "TestCase1.test_02_subtest (i=2, j=3, bc='9.1.2')",
                                'result': 'FAILED',
                                'num': 4
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
                }, {
                    'test_id': 'TestCase1.test_04_subtest',
                    'level': 'system',
                    'result': 'ERRORED',
                    'comment': 'Some comment',
                    'bug_id': [],
                    'subtests':
                        [
                            {
                                'id': "TestCase1.test_04_subtest (i=0, j=0, bc='9.1.2')",
                                'result': 'FAILED',
                                'num': 1
                            }, {
                                'id': "TestCase1.test_04_subtest (i=1, j=2, bc='9.1.2')",
                                'result': 'PASSED',
                                'num': 2
                            }, {
                                'id': "TestCase1.test_04_subtest (i=2, j=3, bc='9.1.2')",
                                'result': 'ERRORED',
                                'num': 3
                            }, {
                                'id': "TestCase1.test_04_subtest (i=2, j=3, bc='9.1.2')",
                                'result': 'FAILED',
                                'num': 4
                            }
                        ],
                    'tags': {}
                }
            ]
    }

    return tests


def _subtest_scenario_issues(with_num: bool) -> dict:
    issues = {
        'issues.json':
            {
                'run': {
                    'level': 'system',
                    'dut': 'MMI2'
                },
                'errors':
                    [
                        {
                            'test': 'TestCase1.test_02_subtest',
                            'sub-test': "TestCase1.test_02_subtest (i=2, j=3, bc='9.1.2')",
                            'result': 'ERRORED',
                            'justified': '',
                            'comment': '',
                            'bug-id': '',
                            'extra': []
                        }, {
                            'test': 'TestCase1.test_04_subtest',
                            'sub-test': "TestCase1.test_04_subtest (i=2, j=3, bc='9.1.2')",
                            'result': 'ERRORED',
                            'justified': 'yes',
                            'comment': '',
                            'bug-id': '',
                            'extra': []
                        }
                    ],
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
                            'test': 'TestCase1.test_02_subtest',
                            'sub-test': "TestCase1.test_02_subtest (i=2, j=3, bc='9.1.2')",
                            'result': 'FAILED',
                            'justified': 'YES',
                            'comment': '',
                            'bug-id': '321',
                            'extra': []
                        }, {
                            'test': 'TestCase1.test_03_error',
                            'sub-test': None,
                            'result': 'ERRORED',
                            'justified': '',
                            'comment': 'New error',
                            'bug-id': '',
                            'extra': []
                        }, {
                            'test': 'TestCase1.test_04_subtest',
                            'sub-test': "TestCase1.test_04_subtest (i=0, j=0, bc='9.1.2')",
                            'result': 'FAILED',
                            'justified': '',
                            'comment': '',
                            'bug-id': '',
                            'extra': []
                        }, {
                            'test': 'TestCase1.test_04_subtest',
                            'sub-test': "TestCase1.test_04_subtest (i=2, j=3, bc='9.1.2')",
                            'result': 'FAILED',
                            'justified': '',
                            'comment': '',
                            'bug-id': '',
                            'extra': []
                        }
                    ]
            }
    }

    nums = [3, 3, 1, 4, 1, 4]

    if with_num:
        for issue in issues['issues.json']['errors'] + issues['issues.json']['failures']:
            if issue['sub-test'] is not None:
                issue['num'] = nums.pop(0)

    return issues


@pytest.mark.parametrize('with_num', [True, False], ids=['num-key', 'subtest-indices'])
def test_justify_tests(reporter, with_num):
    reporter._tests = _subtest_scenario_tests()
    reporter._issues = _subtest_scenario_issues(with_num=with_num)

    reporter.justify_tests()

    tests = reporter._tests['tests.json']
    test_A = tests[0]
    test_B = tests[1]
    test_C = tests[2]
    test_D = tests[3]

    assert test_A['result'] == 'JUSTIFIED'
    assert 'Known HW error' in test_A['issues_details'][0]['comment']
    assert '123' in test_A['issues_details'][0]['bug_id']

    assert test_B['subtests'][0]['result'] == 'JUSTIFIED'
    assert test_B['subtests'][1]['result'] == 'PASSED'
    assert test_B['subtests'][2]['result'] == 'ERRORED'
    assert test_B['subtests'][3]['result'] == 'JUSTIFIED'
    assert test_B['result'] == 'ERRORED'
    assert 'Some comment' in test_B['test_comment']
    assert 'Subtest fail' in test_B['issues_details'][1]['comment']
    assert 'comment' not in test_B['issues_details'][2]
    assert '456' in test_B['issues_details'][1]['bug_id']

    assert test_C['result'] == 'ERRORED'
    assert 'New error' in test_C['issues_details'][0]['comment']

    # Check test result reevaluation after subtets justification
    assert test_D['result'] == 'FAILED'


def test_justify_tests_generates_bug_html(reporter):
    """Test that justify_tests generates bug_html_link alongside bug_id."""
    reporter._bug_trackers = [
        {
            'url': 'https://redmine.company.com/issues/%BUGID%',
            'log_regex': '#(\\d+)',
            'log_link_regex': None
        }
    ]

    reporter._tests = {
        'tests.json':
            [
                {
                    'test_id': 'TestCase1.test_01',
                    'level': 'system',
                    'result': 'FAILED',
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
                    'level': 'system'
                },
                'errors': [],
                'failures':
                    [
                        {
                            'test': 'TestCase1.test_01',
                            'sub-test': None,
                            'result': 'FAILED',
                            'justified': 'yes',
                            'comment': 'Known issue',
                            'bug-id': '#123',
                            'extra': []
                        }
                    ]
            }
    }

    reporter.justify_tests()

    issue_detail = reporter._tests['tests.json'][0]['issues_details'][0]

    assert issue_detail['bug_id'] == '#123'

    assert issue_detail['bug_html_link'] == '<a href="https://redmine.company.com/issues/123" target="_blank">#123</a>'


# --- Testing load_bugtraq ---


def test_load_bugtraq_success(reporter):
    """Test that load_bugtraq correctly parses INI, cleans backslashes, and ignores % interpolation."""
    mock_ini_content = (
        '[bugtraq "redmine"]\n'
        'url = https://redmine.company.com/issues/%BUGID%\n'
        'loglinkregex = "#\\\\d+"\n'
        'logregex = \\\\d+\n'
    )

    with patch('builtins.open', mock_open(read_data=mock_ini_content), create=True):
        reporter.load_bugtraq('.bugtraq')

    assert len(reporter._bug_trackers) == 1
    tracker = reporter._bug_trackers[0]
    assert tracker['url'] == 'https://redmine.company.com/issues/%BUGID%'
    assert tracker['log_regex'] == '\\d+'
    assert tracker['log_link_regex'] == '#\\d+'


def test_load_bugtraq_with_projects(reporter):
    """Test that %PROJECT% macro is expanded into a non-capturing regex group."""
    mock_ini_content = (
        '[bugtraq "jira-al4"]\n'
        'projects = A4MMI4, A4MMI\n'
        'url = https://company.atlassian.net/browse/%BUGID%\n'
        'logregex = %PROJECT%-\\\\d+\n'
    )

    with patch('builtins.open', mock_open(read_data=mock_ini_content), create=True):
        reporter.load_bugtraq('.bugtraq')

    assert len(reporter._bug_trackers) == 1
    tracker = reporter._bug_trackers[0]
    assert tracker['log_regex'] == '(?:A4MMI4|A4MMI)-\\d+'
    assert tracker['log_link_regex'] is None


def test_load_bugtraq_missing_mandatory(reporter):
    """Test that sections missing mandatory fields (like logregex) are skipped."""
    mock_ini_content = ('[bugtraq "broken"]\n'
                        'url = https://jira.company.com/browse/%BUGID%\n')

    with patch('builtins.open', mock_open(read_data=mock_ini_content), create=True):
        reporter.load_bugtraq('.bugtraq')

    assert len(reporter._bug_trackers) == 0


def test_load_bugtraq_multiple_trackers(reporter):
    """Test that load_bugtraq correctly parses multiple distinct tracker sections from a single file."""
    mock_ini_content = (
        '[bugtraq "redmine"]\n'
        'url = https://redmine.company.com/issues/%BUGID%\n'
        'logregex = #(\\\\d+)\n\n'
        '[bugtraq "jira-al4"]\n'
        'projects = A4MMI4, AL4MMI\n'
        'url = https://company.atlassian.net/browse/%BUGID%\n'
        'logregex = %PROJECT%-\\\\d+\n'
    )

    with patch('builtins.open', mock_open(read_data=mock_ini_content), create=True):
        reporter.load_bugtraq('.bugtraq')

    assert len(reporter._bug_trackers) == 2

    redmine_tracker = reporter._bug_trackers[0]
    assert redmine_tracker['url'] == 'https://redmine.company.com/issues/%BUGID%'
    assert redmine_tracker['log_regex'] == '#(\\d+)'

    jira_tracker = reporter._bug_trackers[1]
    assert jira_tracker['url'] == 'https://company.atlassian.net/browse/%BUGID%'
    assert jira_tracker['log_regex'] == '(?:A4MMI4|AL4MMI)-\\d+'


# --- Testing internal _apply_bugtraq method ---


def test_apply_bugtraq_no_trackers(reporter):
    """Test that _apply_bugtraq returns the original text if no trackers are loaded."""
    text = 'Fixes #123'
    assert reporter._apply_bugtraq(text) == text


def test_apply_bugtraq_with_capturing_groups(reporter):
    """Test configuration using capturing groups."""
    reporter._bug_trackers = [
        {
            'url': 'https://redmine.company.com/issues/%BUGID%',
            'log_regex': '#(\\d+)',
            'log_link_regex': None
        }
    ]

    result = reporter._apply_bugtraq('Fixed #12345 in code')
    expected = 'Fixed <a href="https://redmine.company.com/issues/12345" target="_blank">#12345</a> in code'
    assert result == expected


def test_apply_bugtraq_with_project_macro(reporter):
    """Test tracking where the project key is part of the URL id."""
    reporter._bug_trackers = [
        {
            'url': 'https://company.atlassian.net/browse/%BUGID%',
            'log_regex': '(?:A4MMI4|A4MMI)-\\d+',
            'log_link_regex': None
        }
    ]

    result = reporter._apply_bugtraq('See A4MMI-789 for details')
    expected = 'See <a href="https://company.atlassian.net/browse/A4MMI-789" target="_blank">A4MMI-789</a> for details'
    assert result == expected


def test_apply_bugtraq_with_log_link_regex(reporter):
    """Test that log_link_regex isolates the text (e.g. #12345) and log_regex extracts the ID (12345)."""
    reporter._bug_trackers = [
        {
            'url': 'https://redmine.company.com/issues/%BUGID%',
            'log_regex': '\\d+',
            'log_link_regex': '#\\d+'
        }
    ]

    input_text = 'Fixes #12345 and ignores normal number 456'

    expected_html = 'Fixes <a href="https://redmine.company.com/issues/12345" target="_blank">#12345</a> and ignores normal number 456'

    assert reporter._apply_bugtraq(input_text) == expected_html
