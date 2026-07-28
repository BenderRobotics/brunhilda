import pytest

from brunhilda.data import RequirementsResultSummary, Summary, TestsResultsSummary


class TestTestResultsSummary:

    def test_initialization(self):
        summary = TestsResultsSummary(
            passed=10,
            failed=2,
            errored=1,
            skipped=5,
            justified=1,
            expected_failures=1,
            unexpected_successes=0,
            not_executed=0
        )
        assert summary.passed == 10
        assert summary.failed == 2
        assert summary.total == 20
        assert summary.errored == 1
        assert summary.skipped == 5
        assert summary.justified == 1
        assert summary.expected_failures == 1
        assert summary.unexpected_successes == 0
        assert summary.not_executed == 0

    def test_percentages_calculation(self):
        summary = TestsResultsSummary(
            passed=50,
            failed=18,
            errored=10,
            skipped=9,
            justified=5,
            expected_failures=4,
            unexpected_successes=1,
            not_executed=3,
        )

        assert summary.total == 100
        assert summary.pct_passed == 50.0
        assert summary.pct_failed == 18.0
        assert summary.pct_errored == 10.0
        assert summary.pct_skipped == 9.0
        assert summary.pct_justified == 5.0
        assert summary.pct_expected_failures == 4.0
        assert summary.pct_unexpected_successes == 1.0
        assert summary.pct_not_executed == 3.0

    def test_percentages_division_by_zero(self):
        summary = TestsResultsSummary(0, 0, 0, 0, 0, 0, 0, 0)

        assert summary.total == 0
        assert summary.pct_passed == 0.0
        assert summary.pct_failed == 0.0
        assert summary.pct_errored == 0.0
        assert summary.pct_justified == 0.0

    @pytest.mark.parametrize(
        'input_str, field_to_increment',
        [
            ('PASSED', 'passed'),
            ('passed', 'passed'),
            ('FAILED', 'failed'),
            ('ERRORED', 'errored'),
            ('SKIPPED', 'skipped'),
            ('JUSTIFIED', 'justified'),
            ('EXPECTED-FAILURE', 'expected_failures'),
            ('expected failure', 'expected_failures'),
            ('expected_failure', 'expected_failures'),
            ('UNEXPECTED-SUCCESS', 'unexpected_successes'),
            ('unexpected success', 'unexpected_successes'),
            ('NOT-EXECUTED', 'not_executed'),
            ('unknown', ValueError),  # Test error raise
        ]
    )
    def test_add_results(self, input_str, field_to_increment):
        summary = TestsResultsSummary(0, 0, 0, 0, 0, 0, 0, 0)

        if isinstance(field_to_increment, str):
            # Calls __add__ (with + operator)
            summary + input_str

            assert getattr(summary, field_to_increment) == 1
            assert summary.total == 1
        else:
            with pytest.raises(ValueError):
                summary + input_str

    def test_add_chaining(self):
        summary = TestsResultsSummary(0, 0, 0, 0, 0, 0, 0, 0)

        (summary + 'PASSED' + 'FAILED' + 'PASSED')

        assert summary.passed == 2
        assert summary.failed == 1
        assert summary.total == 3


class TestRequirementsResultSummary:

    def test_initialization(self):
        summary = RequirementsResultSummary(
            passed=10,
            failed=2,
            errored=1,
            skipped=5,
            justified=1,
            expected_failures=1,
            unexpected_successes=0,
            not_executed=0,
            not_covered=5,
            out_of_scope=15
        )
        assert summary.passed == 10
        assert summary.failed == 2
        assert summary.total == 40
        assert summary.errored == 1
        assert summary.skipped == 5
        assert summary.justified == 1
        assert summary.expected_failures == 1
        assert summary.unexpected_successes == 0
        assert summary.not_executed == 0
        assert summary.not_covered == 5
        assert summary.out_of_scope == 15

    def test_percentages_calculation(self):
        summary = RequirementsResultSummary(
            passed=50,
            failed=18,
            errored=10,
            skipped=9,
            justified=5,
            expected_failures=4,
            unexpected_successes=1,
            not_executed=1,
            not_covered=1,
            out_of_scope=1
        )

        assert summary.total == 100
        assert summary.pct_passed == 50.0
        assert summary.pct_failed == 18.0
        assert summary.pct_errored == 10.0
        assert summary.pct_skipped == 9.0
        assert summary.pct_justified == 5.0
        assert summary.pct_expected_failures == 4.0
        assert summary.pct_unexpected_successes == 1.0
        assert summary.pct_not_executed == 1.0
        assert summary.pct_not_covered == 1.0
        assert summary.pct_out_of_scope == 1.0

    def test_percentages_division_by_zero(self):
        summary = RequirementsResultSummary(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        assert summary.total == 0
        assert summary.pct_passed == 0.0
        assert summary.pct_failed == 0.0
        assert summary.pct_errored == 0.0
        assert summary.pct_justified == 0.0
        assert summary.pct_not_covered == 0.0
        assert summary.pct_out_of_scope == 0.0

    @pytest.mark.parametrize(
        'input_str, field_to_increment',
        [
            ('PASSED', 'passed'),
            ('passed', 'passed'),
            ('FAILED', 'failed'),
            ('ERRORED', 'errored'),
            ('SKIPPED', 'skipped'),
            ('JUSTIFIED', 'justified'),
            ('EXPECTED-FAILURE', 'expected_failures'),
            ('expected failure', 'expected_failures'),
            ('expected_failure', 'expected_failures'),
            ('UNEXPECTED-SUCCESS', 'unexpected_successes'),
            ('unexpected success', 'unexpected_successes'),
            ('NOT-EXECUTED', 'not_executed'),
            ('NOT-COVERED', 'not_covered'),
            ('not_covered', 'not_covered'),
            ('out of scope', 'out_of_scope'),
            ('OUT-OF-SCOPE', 'out_of_scope'),
            ('unknown', ValueError),  # Test error raise
        ]
    )
    def test_add_results(self, input_str, field_to_increment):
        summary = RequirementsResultSummary(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        if isinstance(field_to_increment, str):
            # Calls __add__ (with + operator)
            summary + input_str

            assert getattr(summary, field_to_increment) == 1
            assert summary.total == 1
        else:
            with pytest.raises(ValueError):
                summary + input_str

    def test_add_chaining(self):
        summary = RequirementsResultSummary(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        (summary + 'PASSED' + 'FAILED' + 'PASSED' + 'OUT-OF-SCOPE')

        assert summary.passed == 2
        assert summary.failed == 1
        assert summary.out_of_scope == 1
        assert summary.total == 4


class TestSummary:

    def test_init(self):
        s = Summary()
        assert isinstance(s.results, TestsResultsSummary)
        assert s.results.total == 0
        assert s.execution == {}
        assert s.levels == {}

    @pytest.mark.parametrize(
        'counts, expected_result', [
            ({
                'errored': 1,
                'passed': 100,
                'failed': 50
            }, 'ERRORED'),
            ({
                'failed': 1,
                'passed': 100,
                'skipped': 50
            }, 'FAILED'),
            ({
                'unexpected_successes': 1,
                'passed': 100
            }, 'FAILED'),
            ({
                'passed': 1,
                'skipped': 10
            }, 'PASSED'),
            ({
                'justified': 1,
                'skipped': 10
            }, 'PASSED'),
            ({
                'expected_failures': 1
            }, 'PASSED'),
            ({
                'skipped': 5
            }, 'SKIPPED'),
            ({}, 'NOT-EXECUTED'),
            ({
                'not_executed': 5
            }, 'NOT-EXECUTED'),
        ]
    )
    def test_overall_result_logic(self, counts, expected_result):
        """
        Sets the counters in ResultsSummary and verifies what summary.result returns.
        """
        s = Summary()

        for field, value in counts.items():
            setattr(s.results, field, value)

        assert s.result == expected_result
