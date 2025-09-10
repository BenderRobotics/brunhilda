from copy import deepcopy
from enum import Enum
from typing import Callable, Dict, List, Optional, OrderedDict, Union

from .data import Summary
from .html_output import HtmlOutput


class FeatureCoveragePolicy(Enum):
    """
    Enum defining policies for feature coverage evaluation.
    """
    STRICT = 'strict'
    MAJORITY = 'majority'
    THRESHOLD = 'threshold'
    LENIENT = 'lenient'
    ALL_PASS = 'all-pass'
    ONE_PASS = 'one-pass'


class HtmlFeatureSummaryOutput(HtmlOutput):
    """
    """

    def _flatten_tests(self, testsuite: Dict) -> List:
        """
        Converts test-suite into list of tests.

        If there are sub-tests in the test, it puts individual sub-tests to the list.
        :param testsuite: testsuite
        :return: list of tests
        """
        flat_tests = []

        for test_run in testsuite.values():
            for test in test_run:
                test_ = deepcopy(test)
                test_['parameters'] = {}
                test_['subtest_id'] = ''
                test_['subtests'] = []

                if 'subtests' in test and test['subtests']:
                    for subtest in test['subtests']:
                        subtest_ = deepcopy(test_)

                        if ('parameters' in subtest) and subtest['parameters']:
                            parameters = subtest['parameters']
                            subtest_['parameters'] = parameters
                            subtest_['subtest_id'] = ','.join(
                                f'{parameter}:{value}' for parameter, value in parameters.items()
                            )

                        subtest_['result'] = subtest['result']
                        subtest_['subtests'] = []  # clear the subtests, now the test is the subtest actually
                        flat_tests.append(subtest_)
                else:
                    flat_tests.append(test_)

        return flat_tests

    def _covers_param(self, test: Dict, parameter: str, values: List[str]) -> bool:
        """
        Test if the test parameters contains parameter with the given value or value wildcard matches the value in the test.

        :param test: test
        :param parameter: name of the parameter
        :param values: list of parameter values
        :return: Test result - True or False
        """
        if (parameter in test['parameters']):
            if str(test['parameters'][parameter]) in values:
                return True
            elif any(value.endswith('*') and test['parameters'][parameter].startswith(value[:-1]) for value in values):
                return True

        return False

    def _strict_policy(self, results: List[str]) -> str:
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

    def _all_pass_policy(self, results: List[str]) -> str:
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

    def _one_pass_policy(self, results: List[str]) -> str:
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

    def _lenient_policy(self, results: List[str]) -> str:
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

    def _majority_policy(self, results: List[str]) -> str:
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

    def _threshold_policy(self, results: List[str]) -> str:
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

    def _result(
        self,
        results: List[str],
        policy: Union[FeatureCoveragePolicy, Callable[[List[str]], str]] = FeatureCoveragePolicy.STRICT
    ) -> str:
        """
        Evaluates feature results by given policy.

        :param results: list of test results
        :param policy: evaluation policy
        :return: feature result in string
        """
        if callable(policy):
            return policy(results)

        if not results:
            return 'EMPTY'

        if policy == FeatureCoveragePolicy.STRICT:
            res = self._strict_policy(results)
        elif policy == FeatureCoveragePolicy.ALL_PASS:
            res = self._all_pass_policy(results)
        elif policy == FeatureCoveragePolicy.ONE_PASS:
            res = self._one_pass_policy(results)
        elif policy == FeatureCoveragePolicy.LENIENT:
            res = self._lenient_policy(results)
        elif policy == FeatureCoveragePolicy.MAJORITY:
            res = self._majority_policy(results)
        elif policy == FeatureCoveragePolicy.THRESHOLD:
            res = self._threshold_policy(results)
        else:
            raise ValueError('Undefined feature coverage policy selected.')

        return res

    def print(
        self,
        name: str,
        features: Dict,
        testsuite: Dict,
        test_plan_paths: Optional[Dict[str, str]] = None,
        feature_coverage_policy: Union[FeatureCoveragePolicy, Callable[[List[str]], str]] = FeatureCoveragePolicy.STRICT
    ) -> str:
        """
        Prints summary of features to HTML document.

        :param name: name of the generated report
        :param features: collected features
        :param testsuite: suite of the executed tests
        :param test_plan_path: path to the test plans
        :return: HTML string
        :rtype: str
        """
        entries = OrderedDict()
        all_tests = self._flatten_tests(testsuite)
        unlinked_tests = deepcopy(all_tests)
        summary = Summary()

        for group in features:
            entries[group] = []
            for feature_group in features[group]:
                for feature_name in feature_group:
                    requirement_tests = {}
                    order = feature_group[feature_name]['order']
                    links = feature_group[feature_name]['link']
                    links = {
                        k.rstrip('_'): v for k, v in links.items()
                    }  # Remove bypassing character for backward compatibility
                    entry = {'group': group, 'name': feature_name, 'order': order, 'result': '', 'links': {}}
                    feature_results = []

                    for link in links:
                        params = links[link]
                        entry['links'][link] = {}

                        for index, test in enumerate(all_tests):
                            test_case_id = test['test_id'] + test['subtest_id']

                            for requirement in test['requirements']:
                                # Get only important part of the requirement (INTF_001.1 (indirect) -> INTF_001.1) and remove bypassing character for backward compatibility
                                shortened_requirement = requirement.split()[0].rstrip('_')

                                if shortened_requirement not in requirement_tests:
                                    requirement_tests[shortened_requirement] = []

                                if link == shortened_requirement and (
                                    test_case_id not in requirement_tests[shortened_requirement]
                                ):
                                    if params:
                                        for parameter in params:
                                            test_group = test['test_id'] + f' {parameter}:{params[parameter]}'

                                            if test_group not in entry['links'][link]:
                                                entry['links'][link][test_group] = {
                                                    'tests': [],
                                                    'level': test['level'],
                                                    'results': set(),
                                                }

                                            if self._covers_param(test, parameter, params[parameter]):
                                                test_case = deepcopy(test)
                                                requirement_tests[shortened_requirement].append(test_case_id)
                                                if test_case not in entry['links'][link][test_group]['tests']:
                                                    entry['links'][link][test_group]['tests'].append(test_case)
                                                    entry['links'][link][test_group]['results'].add(test_case['result'])
                                                    feature_results.append(test_case['result'])
                                                unlinked_tests[index] = None
                                    else:
                                        test_group = test['test_id']

                                        if test_group not in entry['links'][link]:
                                            entry['links'][link][test_group] = {
                                                'tests': [],
                                                'level': test['level'],
                                                'results': set(),
                                            }

                                        test_case = deepcopy(test)
                                        requirement_tests[shortened_requirement].append(test_case_id)
                                        if test_case not in entry['links'][link][test_group]['tests']:
                                            entry['links'][link][test_group]['tests'].append(test_case)
                                            entry['links'][link][test_group]['results'].add(test_case['result'])
                                            feature_results.append(test_case['result'])
                                        unlinked_tests[index] = None

                    entry['result'] = self._result(feature_results, feature_coverage_policy).lower()
                    summary.results += self._result(feature_results, feature_coverage_policy)
                    entries[group].append(entry)

        # remove empty test groups
        for group in entries:
            for entry in entries[group]:
                for link in entry['links']:
                    for test_group in list(entry['links'][link].keys()):
                        if not entry['links'][link][test_group]['tests'] and len(entry['links'][link]) > 1:
                            del entry['links'][link][test_group]
                        else:
                            # for features test cases we do not want to use policy
                            entry['links'][link][test_group]['result'] = self._result(
                                entry['links'][link][test_group]['results']
                            ).lower()

        # add not linked tests refereeing to empty feature
        unlinked_tests = list(filter(lambda test: test is not None, unlinked_tests))
        # entries['Not linked'] = [{'group': '', 'name': '', 'order': '', 'links': {'': unlinked_tests}}]

        template = self.load_template('summary-features.html.jinja2')
        rendered = template.render(
            name=name,
            preamble=self._include_preamble,
            features=entries,
            summary=summary,
            test_plan_paths=test_plan_paths
        )
        return rendered
