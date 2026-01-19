import pytest

from brunhilda.outputs.html_feature_summary_output import HtmlFeatureSummaryOutput


@pytest.mark.parametrize(
    'test_input, expected_result', [
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED',
                'UNEXPECTED-SUCCESS', 'ERRORED', 'PASSED'
            ], 'ERRORED'
        ),
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED',
                'UNEXPECTED-SUCCESS', 'PASSED', 'UNEXPECTED-SUCCESS'
            ], 'UNEXPECTED-SUCCESS'
        ),
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED', 'JUSTIFIED',
                'PASSED', 'FAILED'
            ], 'FAILED'
        ),
        (
            ['EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'EXPECTED-FAILURE'
            ], 'EXPECTED-FAILURE'
        ),
        (['SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED'], 'SKIPPED'),
        (
            ['JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'
            ], 'JUSTIFIED'
        ),
        (['PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'], 'PASSED'),
    ]
)
def test_strict_policy(test_input, expected_result):
    assert HtmlFeatureSummaryOutput()._strict_policy(test_input) == expected_result


@pytest.mark.parametrize(
    'test_input, expected_result', [
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED',
                'UNEXPECTED-SUCCESS', 'ERRORED', 'PASSED'
            ], 'FAILED'
        ),
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED',
                'UNEXPECTED-SUCCESS', 'PASSED', 'UNEXPECTED-SUCCESS'
            ], 'FAILED'
        ),
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED', 'JUSTIFIED',
                'PASSED', 'FAILED'
            ], 'FAILED'
        ),
        (
            ['EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'EXPECTED-FAILURE'
            ], 'FAILED'
        ),
        (['SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED'], 'PASSED'),
        (
            ['JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'
            ], 'PASSED'
        ),
        (['PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'], 'PASSED'),
        (['PASSED', 'PASSED', 'PASSED', 'JUSTIFIED', 'SKIPPED', 'PASSED', 'JUSTIFIED'], 'PASSED'),
    ]
)
def test_all_pass_policy(test_input, expected_result):
    assert HtmlFeatureSummaryOutput()._all_pass_policy(test_input) == expected_result


@pytest.mark.parametrize(
    'test_input, expected_result', [
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED',
                'UNEXPECTED-SUCCESS', 'ERRORED', 'PASSED'
            ], 'PASSED'
        ),
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED',
                'UNEXPECTED-SUCCESS', 'PASSED', 'UNEXPECTED-SUCCESS'
            ], 'PASSED'
        ),
        (['UNEXPECTED-SUCCESS', 'EXPECTED-FAILURE', 'JUSTIFIED', 'FAILED', 'SKIPPED'], 'FAILED'),
        (['JUSTIFIED', 'SKIPPED', 'FAILED', 'ERRORED', 'JUSTIFIED', 'JUSTIFIED', 'ERRORED', 'FAILED'], 'FAILED'),
        (['PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'], 'PASSED'),
    ]
)
def testone_pass(test_input, expected_result):
    assert HtmlFeatureSummaryOutput()._one_pass_policy(test_input) == expected_result


@pytest.mark.parametrize(
    'test_input, expected_result', [
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED',
                'UNEXPECTED-SUCCESS', 'ERRORED', 'PASSED'
            ], 'FAILED'
        ),
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'EXPECTED-FAILURE', 'SKIPPED', 'UNEXPECTED-SUCCESS',
                'PASSED', 'UNEXPECTED-SUCCESS'
            ], 'PASSED'
        ),
        (['SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED', 'SKIPPED'], 'FAILED'),
        (
            ['JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'
            ], 'PASSED'
        ),
        (['PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'ERRORED'], 'FAILED'),
        (['PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'FAILED'], 'FAILED'),
    ]
)
def test_lenient_policy(test_input, expected_result):
    assert HtmlFeatureSummaryOutput()._lenient_policy(test_input) == expected_result


@pytest.mark.parametrize(
    'test_input, expected_result', [
        (
            [
                'JUSTIFIED', 'JUSTIFIED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'UNEXPECTED-SUCCESS',
                'ERRORED'
            ], 'JUSTIFIED'
        ),
        (
            [
                'JUSTIFIED', 'SKIPPED', 'ERRORED', 'ERRORED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED',
                'UNEXPECTED-SUCCESS', 'PASSED', 'UNEXPECTED-SUCCESS'
            ], 'ERRORED'
        ),
        (
            [
                'JUSTIFIED', 'SKIPPED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED', 'JUSTIFIED',
                'PASSED', 'FAILED', 'FAILED'
            ], 'FAILED'
        ),
        (['EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'ERRORED', 'FAILED'], 'EXPECTED-FAILURE'),
        (['SKIPPED', 'PASSED', 'PASSED', 'SKIPPED', 'PASSED', 'SKIPPED', 'SKIPPED'], 'SKIPPED'),
        (
            ['JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'
            ], 'PASSED'
        ),
        (['PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'], 'PASSED'),
        (['JUSTIFIED', 'SKIPPED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'UNEXPECTED-SUCCESS', 'ERRORED'], 'ERRORED'),
        (['JUSTIFIED', 'SKIPPED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'UNEXPECTED-SUCCESS'], 'UNEXPECTED-SUCCESS'),
        (['JUSTIFIED', 'SKIPPED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE'], 'FAILED'),
        (['JUSTIFIED', 'SKIPPED', 'PASSED', 'EXPECTED-FAILURE'], 'EXPECTED-FAILURE'),
        (['JUSTIFIED', 'SKIPPED', 'PASSED'], 'SKIPPED'),
        (['JUSTIFIED', 'PASSED'], 'JUSTIFIED'),
        (['PASSED'], 'PASSED'),
    ]
)
def test_majority_policy(test_input, expected_result):
    assert HtmlFeatureSummaryOutput()._majority_policy(test_input) == expected_result


@pytest.mark.parametrize(
    'test_input, expected_result', [
        (
            [
                'JUSTIFIED', 'SKIPPED', 'ERRORED', 'ERRORED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED',
                'UNEXPECTED-SUCCESS', 'PASSED', 'UNEXPECTED-SUCCESS'
            ], 'FAILED'
        ),
        (
            [
                'PASSED', 'PASSED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'FAILED', 'PASSED', 'PASSED',
                'PASSED'
            ], 'FAILED'
        ),
        (['EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'EXPECTED-FAILURE', 'ERRORED', 'FAILED'], 'FAILED'),
        (
            ['JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'JUSTIFIED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'
            ], 'PASSED'
        ),
        (['PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED'], 'PASSED'),
    ]
)
def test_threshold_policy(test_input, expected_result):
    assert HtmlFeatureSummaryOutput()._threshold_policy(test_input) == expected_result


@pytest.mark.parametrize(
    'test_input, expected_result', [
        (
            [
                'JUSTIFIED', 'JUSTIFIED', 'PASSED', 'PASSED', 'FAILED', 'EXPECTED-FAILURE', 'UNEXPECTED-SUCCESS',
                'ERRORED'
            ], 'ERRORED'
        ),
        ([], 'NOT-EXECUTED'),
    ]
)
def test_result(test_input, expected_result):
    assert HtmlFeatureSummaryOutput()._result(test_input) == expected_result
