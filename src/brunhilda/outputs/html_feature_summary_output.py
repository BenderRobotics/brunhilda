from copy import copy, deepcopy
from typing import Callable, Dict, List, Optional, OrderedDict, Union

from tqdm import tqdm

from ..data import RequirementsResultSummary
from ..policies import CoveragePolicy, evaluate_result
from .html_output import HtmlOutput

try:
    from ..__version__ import version as brunhilda_version
except ImportError:
    brunhilda_version = 'unknown'


class HtmlFeatureSummaryOutput(HtmlOutput):
    """
    Generates an HTML report summarizing feature coverage based on test results.

    This class processes the test suite to link individual tests (and subtests)
    to specific features or requirements. It evaluates the overall result of each
    feature group using a specified `FeatureCoveragePolicy` (e.g., STRICT, MAJORITY).
    """

    TQDM_BAR_FORMAT = '    - {desc:<36}: {percentage:3.0f}% |{bar}| {n_fmt}/{total_fmt}'

    def _flatten_tests(self, testsuite: Dict, disable_progress_bar: bool) -> List:
        """
        Converts test-suite into list of tests.

        If there are sub-tests in the test, it puts individual sub-tests to the list.

        :param testsuite: testsuite dict
        :param disable_progress_bar: if True progress bars will be disabled
        :return: list of tests
        """
        flat_tests = []

        total_tests = sum(len(test_run) for test_run in testsuite.values())

        with tqdm(
            total=total_tests,
            desc='flattening test cases',
            unit='test',
            disable=disable_progress_bar,
            dynamic_ncols=True,
            colour='#3498db',
            bar_format=self.TQDM_BAR_FORMAT
        ) as pbar:
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
                                parameters_string = [
                                    f"{key}='{value}'" if isinstance(value, str) else f'{key}={value}'
                                    for key, value in parameters.items()
                                ]

                                for issue_detail in subtest_['issues_details']:
                                    if all(param in issue_detail['link'] for param in parameters_string):
                                        subtest_['issues_details'] = [issue_detail]
                                        break

                            subtest_['result'] = subtest['result']
                            subtest_['subtests'] = []  # clear the subtests, now the test is the subtest actually
                            flat_tests.append(subtest_)
                    else:
                        flat_tests.append(test_)

                    pbar.update(1)

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

    def print(
        self,
        name: str,
        features: Dict,
        testsuite: Dict,
        test_plan_paths: Optional[Dict[str, str]] = None,
        issue_list_path: Optional[str] = None,
        evaluation_policy: Union[CoveragePolicy, Callable[[List[str]], str]] = CoveragePolicy.STRICT,
        disable_progress_bars: bool = True
    ) -> str:
        """
        Prints summary of features to HTML document.

        :param name: name of the generated report
        :param features: collected features
        :param testsuite: suite of the executed tests
        :param test_plan_path: path to the test plans
        :param evaluation_policy: evaluation policy
        :param disable_progress_bars: if True progress bars will be disabled
        :return: HTML string
        """
        entries = OrderedDict()
        all_tests = self._flatten_tests(testsuite, disable_progress_bars)
        feature_results_summary = RequirementsResultSummary()

        # Map req to tests
        req_to_tests = {}
        for index, test in enumerate(
            tqdm(
                all_tests,
                desc='indexing requirements',
                unit='sub test',
                disable=disable_progress_bars,
                dynamic_ncols=True,
                colour='#1abc9c',
                bar_format=self.TQDM_BAR_FORMAT
            )
        ):
            test_case_id = test['test_id_with_level'] + test['subtest_id']

            seen_reqs_in_test = set()
            for requirement in test.get('requirements', []):
                # Get only important part of the requirement (INTF_001.1 (indirect) -> INTF_001.1) and remove bypassing character for backward compatibility
                shortened_requirement = requirement.split()[0].rstrip('_')

                if shortened_requirement not in seen_reqs_in_test:
                    seen_reqs_in_test.add(shortened_requirement)
                    if shortened_requirement not in req_to_tests:
                        req_to_tests[shortened_requirement] = []
                    req_to_tests[shortened_requirement].append((index, test, test_case_id))

        total_features = sum(len(feature_group) for group in features for feature_group in features[group])

        with tqdm(
            total=total_features,
            desc='linking tests & evaluating features',
            unit='feature',
            disable=disable_progress_bars,
            dynamic_ncols=True,
            colour='#f39c12',
            bar_format=self.TQDM_BAR_FORMAT
        ) as pbar:
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

                            if link not in requirement_tests:
                                requirement_tests[link] = set()

                            matching_tests = req_to_tests.get(link, [])

                            for index, test, test_case_id in matching_tests:
                                if test_case_id not in requirement_tests[link]:
                                    if params:
                                        for parameter in params:
                                            test_group = test['test_id'] + f' {parameter}:{params[parameter]}'

                                            if test_group not in entry['links'][link]:
                                                entry['links'][link][test_group] = {
                                                    'tests': [],
                                                    'level': test['level'],
                                                    'results': [],
                                                    'seen_tests': set(),
                                                }

                                            if self._covers_param(test, parameter, params[parameter]):
                                                test_case = copy(test)
                                                requirement_tests[link].add(test_case_id)
                                                if test_case_id not in entry['links'][link][test_group]['seen_tests']:
                                                    entry['links'][link][test_group]['tests'].append(test_case)
                                                    entry['links'][link][test_group]['results'].append(
                                                        test_case['result']
                                                    )
                                                    entry['links'][link][test_group]['seen_tests'].add(test_case_id)
                                                    feature_results.append(test_case['result'])
                                    else:
                                        test_group = test['test_id_with_level']

                                        if test_group not in entry['links'][link]:
                                            entry['links'][link][test_group] = {
                                                'tests': [],
                                                'level': test['level'],
                                                'results': [],
                                                'seen_tests': set(),
                                            }

                                        test_case = copy(test)
                                        requirement_tests[link].add(test_case_id)
                                        if test_case_id not in entry['links'][link][test_group]['seen_tests']:
                                            entry['links'][link][test_group]['tests'].append(test_case)
                                            entry['links'][link][test_group]['results'].append(test_case['result'])
                                            entry['links'][link][test_group]['seen_tests'].add(test_case_id)
                                            feature_results.append(test_case['result'])

                        if feature_group[feature_name]['oos']:
                            result = 'OUT-OF-SCOPE'
                        elif not feature_results:
                            result = 'NOT-COVERED'
                        elif all(r.upper() == 'NOT-EXECUTED' for r in feature_results):
                            result = 'NOT-EXECUTED'
                        else:
                            result = evaluate_result(feature_results, evaluation_policy)

                        entry['result'] = result.lower()
                        feature_results_summary += result
                        entries[group].append(entry)

                        pbar.update(1)

        total_entries = sum(len(entries[group]) for group in entries)

        with tqdm(
            total=total_entries,
            desc='evaluating feature groups',
            unit='group',
            disable=disable_progress_bars,
            dynamic_ncols=True,
            colour='#2ecc71',
            bar_format=self.TQDM_BAR_FORMAT
        ) as pbar:
            # remove empty test groups and evaluate test groups results
            for group in entries:
                for entry in entries[group]:
                    for link in entry['links']:
                        for test_group in list(entry['links'][link].keys()):
                            test_group_dict = entry['links'][link][test_group]
                            if not test_group_dict['tests'] and len(entry['links'][link]) > 1:
                                del entry['links'][link][test_group]
                            else:
                                if test_group_dict['results']:
                                    test_group_dict['result'] = evaluate_result(
                                        test_group_dict['results'], evaluation_policy
                                    )

                    pbar.update(1)

        template = self.load_template('summary-features.html.jinja2')
        rendered = template.render(
            name=name,
            preamble=self._include_preamble,
            features=entries,
            feature_results_summary=feature_results_summary,
            test_plan_paths=test_plan_paths,
            issue_list_path=issue_list_path,
            brunhilda_version=brunhilda_version
        )
        return rendered
