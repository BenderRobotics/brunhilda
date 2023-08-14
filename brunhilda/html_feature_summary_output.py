from copy import deepcopy
from typing import Dict, Optional, OrderedDict, List, Set

from .html_output import HtmlOutput
from .data import Summary

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
                            subtest_['subtest_id'] = ','.join(f'{parameter}:{value}' for parameter, value in parameters.items())

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

    def _result(self, results: Set[str]) -> str:
        if not results:
            res = 'EMPTY'
        elif any(r == 'ERRORED' for r in results):
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

    def print(self, name: str,
                    features: Dict,
                    testsuite: Dict,
                    test_plan_paths: Optional[Dict[str, str]] = None) -> str:
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
                    entry = {'group': group, 'name': feature_name, 'order': order, 'result': '', 'links': {}}
                    feature_results = set()

                    for link in links:
                        params = links[link]
                        entry['links'][link] = {}

                        for index, test in enumerate(all_tests):
                            test_case_id = test['test_id'] + test['subtest_id']

                            for requirement in test['requirements']:
                                if requirement not in requirement_tests:
                                    requirement_tests[requirement] = []

                                if requirement.startswith(link) and (test_case_id not in requirement_tests[requirement]):
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
                                                requirement_tests[requirement].append(test_case_id)
                                                if test_case not in entry['links'][link][test_group]['tests']:
                                                    entry['links'][link][test_group]['tests'].append(test_case)
                                                    entry['links'][link][test_group]['results'].add(test_case['result'])
                                                    feature_results.add(test_case['result'])
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
                                        requirement_tests[requirement].append(test_case_id)
                                        if test_case not in entry['links'][link][test_group]['tests']:
                                            entry['links'][link][test_group]['tests'].append(test_case)
                                            entry['links'][link][test_group]['results'].add(test_case['result'])
                                            feature_results.add(test_case['result'])
                                        unlinked_tests[index] = None



                    entry['result'] = self._result(feature_results).lower()
                    summary.results += self._result(feature_results)
                    entries[group].append(entry)

        # remove empty test groups
        for group in entries:
            for entry in entries[group]:
                for link in entry['links']:
                    for test_group in list(entry['links'][link].keys()):
                        if not entry['links'][link][test_group]['tests'] and len(entry['links'][link]) > 1:
                            del entry['links'][link][test_group]
                        else:
                            entry['links'][link][test_group]['result'] = self._result(entry['links'][link][test_group]['results']).lower()

        # add not linked tests refereeing to empty feature
        unlinked_tests = list(filter(lambda test: test is not None, unlinked_tests))
        # entries['Not linked'] = [{'group': '', 'name': '', 'order': '', 'links': {'': unlinked_tests}}]

        template = self.load_template('summary-features.html.jinja2')
        rendered = template.render(name=name,
                                   preamble=self._include_preamble,
                                   features=entries,
                                   summary=summary,
                                   test_plan_paths=test_plan_paths)
        return rendered
