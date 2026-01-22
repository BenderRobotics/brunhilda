from dataclasses import dataclass

try:
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal

Result = Literal['PASSED', 'FAILED', 'ERRORED', 'JUSTIFIED', 'SKIPPED', 'UNEXPECTED-SUCCESS', 'EXPECTED-FAILURE',
                 'NOT-EXECUTED']


@dataclass(eq=True, unsafe_hash=True)
class ResultsSummary:
    """
    Dataclass representing summary of results.

    Contains number of passed, failed, ... tests.
    """
    passed: int
    failed: int
    errored: int
    skipped: int
    justified: int
    expected_failures: int
    unexpected_successes: int
    not_executed: int
    out_of_scope: int

    @property
    def total(self) -> int:
        return (
            self.passed + self.failed + self.errored + self.skipped + self.justified + self.expected_failures +
            self.unexpected_successes + self.not_executed + self.out_of_scope
        )

    @property
    def pct_passed(self) -> float:
        return (self.passed / self.total * 100.0) if (self.total != 0) else 0.0

    @property
    def pct_failed(self) -> float:
        return (self.failed / self.total * 100.0) if (self.total != 0) else 0.0

    @property
    def pct_errored(self) -> float:
        return (self.errored / self.total * 100.0) if (self.total != 0) else 0.0

    @property
    def pct_skipped(self) -> float:
        return (self.skipped / self.total * 100.0) if (self.total != 0) else 0.0

    @property
    def pct_justified(self) -> float:
        return (self.justified / self.total * 100.0) if (self.total != 0) else 0.0

    @property
    def pct_expected_failures(self) -> float:
        return (self.expected_failures / self.total * 100.0) if (self.total != 0) else 0.0

    @property
    def pct_unexpected_successes(self) -> float:
        return (self.unexpected_successes / self.total * 100.0) if (self.total != 0) else 0.0

    @property
    def pct_not_executed(self) -> float:
        return (self.not_executed / self.total * 100.0) if (self.total != 0) else 0.0

    @property
    def pct_out_of_scope(self) -> float:
        return (self.out_of_scope / self.total * 100.0) if (self.total != 0) else 0.0

    def __add__(self, result: Result):
        """
        Add result to summary.

        :param result: result that will be add to summary
        """
        result = str(result).upper().replace(' ', '-').replace('_', '-').strip()

        if result == 'PASSED':
            self.passed += 1
        elif result == 'ERRORED':
            self.errored += 1
        elif result == 'FAILED':
            self.failed += 1
        elif result == 'JUSTIFIED':
            self.justified += 1
        elif result == 'SKIPPED':
            self.skipped += 1
        elif result == 'EXPECTED-FAILURE':
            self.expected_failures += 1
        elif result == 'UNEXPECTED-SUCCESS':
            self.unexpected_successes += 1
        elif result in ['NOT-EXECUTED', 'EMPTY']:
            self.not_executed += 1
        elif result == 'OUT-OF-SCOPE':
            self.out_of_scope += 1
        else:
            raise ValueError(f'Unknown result "{result}".')

        return self


class Summary:
    """
    Class representing summary of test run.
    """

    def __init__(self):
        self.results = ResultsSummary(0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.execution = {}
        self.levels = {}

    @property
    def result(self) -> Result:
        if self.results.errored > 0:
            # if there is at least one error -> error
            return 'ERRORED'
        elif (self.results.failed > 0) or (self.results.unexpected_successes > 0):
            # if there is at least one fail or unexpected success and no error -> fail
            return 'FAILED'
        elif (self.results.passed > 0) or (self.results.justified > 0) or (self.results.expected_failures > 0):
            # otherwise if there are passed, justified or expected failures -> passed
            return 'PASSED'
        elif self.results.skipped > 0:
            return 'SKIPPED'
        else:
            return 'NOT-EXECUTED'
