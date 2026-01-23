from enum import Enum
from typing import Callable, List, Union

__all__ = ['CoveragePolicy', 'evaluate_result']


class CoveragePolicy(Enum):
    """
    Enum defining policies for feature coverage evaluation.
    """
    STRICT = 'strict'
    MAJORITY = 'majority'
    THRESHOLD = 'threshold'
    LENIENT = 'lenient'
    ALL_PASS = 'all-pass'
    ONE_PASS = 'one-pass'


def _strict_policy(results: List[str]) -> str:
    """
    STRICT feature coverage policy.
    Evaluates results according to strict priority order. The first one to match will determine the outcome.

    :param results: list of tests results
    :return: feature result in string
    """
    if any(r == 'ERRORED' for r in results):
        res = 'ERRORED'
    elif any(r == 'UNEXPECTED-SUCCESS' for r in results):
        res = 'UNEXPECTED-SUCCESS'
    elif any(r == 'FAILED' for r in results):
        res = 'FAILED'
    elif all(r == 'EXPECTED-FAILURE' for r in results):
        res = 'EXPECTED-FAILURE'
    elif all(r == 'SKIPPED' for r in results):
        res = 'SKIPPED'
    elif any(r == 'JUSTIFIED' for r in results):
        res = 'JUSTIFIED'
    else:
        res = 'PASSED'

    return res


def _all_pass_policy(results: List[str]) -> str:
    """
    ALL_PASS feature coverage policy.
    Feature is PASSED only if all results are PASSED, SKIPPED or JUSTIFIED, otherwise feature is FAILED.

    :param results: list of tests results
    :return: feature result in string
    """
    if all(r in ['PASSED', 'SKIPPED', 'JUSTIFIED'] for r in results):
        res = 'PASSED'
    else:
        res = 'FAILED'

    return res


def _one_pass_policy(results: List[str]) -> str:
    """
    ONE_PASS feature coverage policy.
    Feature is PASSED if at least one result is PASSED, otherwise feature is FAILED.

    :param results: list of tests results
    :return: feature result in string
    """
    if any(r == 'PASSED' for r in results):
        res = 'PASSED'
    else:
        res = 'FAILED'

    return res


def _lenient_policy(results: List[str]) -> str:
    """
    LENIENT feature coverage policy.
    Feature is PASSED if at least one result is PASSED and there aren't any FAILED or ERRORED results.

    :param results: list of tests results
    :return: feature result in string
    """
    if any(r == 'PASSED' for r in results) and not any(r in ('FAILED', 'ERRORED') for r in results):
        res = 'PASSED'
    else:
        res = 'FAILED'

    return res


def _majority_policy(results: List[str]) -> str:
    """
    MAJORITY feature coverage policy.
    Feature is result as same as the most common result. In case of tie, the dict sort decides.

    :param results: list of tests results
    :return: feature result in string
    """
    majority = {
        'ERRORED': results.count('ERRORED'),
        'UNEXPECTED-SUCCESS': results.count('UNEXPECTED-SUCCESS'),
        'FAILED': results.count('FAILED'),
        'EXPECTED-FAILURE': results.count('EXPECTED-FAILURE'),
        'SKIPPED': results.count('SKIPPED'),
        'JUSTIFIED': results.count('JUSTIFIED'),
        'PASSED': results.count('PASSED'),
    }
    return max(majority, key=majority.get)


def _threshold_policy(results: List[str]) -> str:
    """
    MAJORITY feature coverage policy.
    Feature is PASSED if share of PASSED result is equal or greater than 80 %. Otherwise feature result is FAILED.
    If all tests are SKIPPED, feature result is SKIPPED.

    :param results: list of tests results
    :return: feature result in string
    """
    pass_ratio = results.count('PASSED') / len(results)

    if all(r == 'SKIPPED' for r in results):
        res = 'SKIPPED'
    elif pass_ratio >= 0.8:
        res = 'PASSED'
    else:
        res = 'FAILED'

    return res


def evaluate_result(
    results: List[str], policy: Union[CoveragePolicy, Callable[[List[str]], str]] = CoveragePolicy.STRICT
) -> str:
    """
    Evaluates results by given policy.

    :param results: list of test results
    :param policy: evaluation policy
    :return: feature/requirement result in string
    """
    if callable(policy):
        return policy(results)

    if not results:
        return 'NOT-EXECUTED'

    if policy == CoveragePolicy.STRICT:
        res = _strict_policy(results)
    elif policy == CoveragePolicy.ALL_PASS:
        res = _all_pass_policy(results)
    elif policy == CoveragePolicy.ONE_PASS:
        res = _one_pass_policy(results)
    elif policy == CoveragePolicy.LENIENT:
        res = _lenient_policy(results)
    elif policy == CoveragePolicy.MAJORITY:
        res = _majority_policy(results)
    elif policy == CoveragePolicy.THRESHOLD:
        res = _threshold_policy(results)
    else:
        raise ValueError('Undefined feature coverage policy selected.')

    return res
