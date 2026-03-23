import os
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union, overload

import simplejson as json
import yaml
from natsort import natsorted

from brunhilda.outputs.html_result_output import HtmlResultOutput

from .data import Summary
from .outputs.html_feature_summary_output import HtmlFeatureSummaryOutput
from .outputs.html_index_output import HtmlIndexOutput
from .outputs.html_issue_list_output import HtmlIssueListOutput
from .outputs.html_req_summary_output import HtmlReqSummaryOutput
from .outputs.html_test_plan_output import HtmlTestPlanOutput
from .outputs.html_test_summary_output import HtmlTestSummaryOutput
from .outputs.output import Output
from .policies import CoveragePolicy
from .rel_path import rel_path

try:
    from .__version__ import version as brunhilda_version
except ImportError:
    brunhilda_version = 'unknown'


class Reporter:

    def __init__(self, user_data: Dict[str, str] = {}, user_stories: List['doorstop.Item'] = []) -> None:
        self._outputs: List[Tuple[str, str, bool,
                                  bool]] = []  # Tuple contains name, path, is generated, is justified record
        self._user_stories = user_stories
        self._requirements: Dict[str, Optional[str]] = {}  # key: req_id, value: out of scope reason (None == in scope)
        self._tests: Dict = {}
        self._issues: Dict = {}
        self._features: Optional[Dict] = None
        self._issue_list_path: Optional[str] = None
        self._feature_list_path: Optional[str] = None
        self._test_plan_paths = {'_': ''}
        self._user_data = user_data
        self._justification_executed = False

    def _load(self, path: Union[str, Path]) -> Dict:
        """
        Load JSON or yaml file.

        :param path: path to the file being loaded
        :return: dictionary of values loaded from the file
        """
        path = str(path)
        print(f'... loading {path}')

        with open(path, 'r', encoding='utf-8') as f:
            if path.endswith(('yaml', 'yml')):
                content = yaml.safe_load(f)
            elif path.endswith(('json')):
                content = json.load(f)
            else:
                raise ValueError(f'Unsupported file type {path}')

            return content

    def justify_tests(self) -> None:
        """
        Updates loaded test with justifications.
        """
        # link with justification taken from issues
        if (self._issues is not None) and (self._tests is not None):
            for tests in self._tests.values():
                for test in tests:
                    justifications = []  # list of justifications - there can be several failures in one test
                    comments = set([test['comment']])
                    bug_ids = set()

                    for issues in self._issues.values():
                        if issues['run']['level'] == test['level']:
                            for issue in issues['errors'] + issues['failures']:
                                if issue['test'] == test['test_id']:
                                    justified = issue['justified'].lower().strip() == 'yes'
                                    justifications.append(justified)

                                    if issue['comment']:
                                        comments.add(issue['comment'])

                                    if issue['bug-id']:
                                        bug_ids.add(issue['bug-id'])

                                    for i, subtest in enumerate(test['subtests']):
                                        if subtest['id'] == issue['sub-test'] and justified:
                                            test['subtests'][i]['result'] = 'JUSTIFIED'
                                            break

                    if justifications and all(justifications):
                        test['result'] = 'JUSTIFIED'

                    test['comment'] = [comment for comment in comments if comment]
                    test['bug_id'] = list(bug_ids)

            self._justification_executed = True

    def _append_requirement(self, req_id: str, out_of_scope_reason: Optional[str] = None) -> None:
        """
        Append requirement to list of requirements.
        If it's duplicity, update out of scope state or do nothing.
        """
        # new requirement
        if req_id not in self._requirements:
            self._requirements[req_id] = out_of_scope_reason

        # requirement exists and we got new out of scope reason
        elif self._requirements.get(req_id) is None and out_of_scope_reason is not None:
            self._requirements[req_id] = out_of_scope_reason

    def load_requirements_list(self, requirements: List[str]) -> None:
        """
        Loads requirements.

        :param requirements: list of requirements
        """
        for req_id in requirements:
            self._append_requirement(req_id, None)

    def load_out_of_scope_requirements_list(self, requirements: List[str]) -> None:
        """
        Loads out of scope requirements.

        :param requirements: list of out of scope requirements
        """
        for req_id in requirements:
            self._append_requirement(req_id, '')  # requirement is out of scope, but reason is unknown

    def load_requirements(self, path: Union[str, Path]) -> None:
        """
        Loads requirements from file.

        :param path: path to requirements file
        """
        requirements = self._load(path)

        for req_id, data in requirements.items():
            reason = data['out-of-scope'] if 'out-of-scope' in data else None
            self._append_requirement(req_id, reason)

    @overload
    def load_tests(self, path: Union[str, Path], report_path: Union[str, Path] = '') -> None:
        ...

    @overload
    def load_tests(self, *args: Union[str, Path]) -> None:
        ...

    def load_tests(self, *args: Union[str, Path]) -> None:
        """
        Loads serialized tests file and store path to their html report

        Accepts variable number of arguments where:
        - Odd arguments (1st, 3rd...) are paths to test files.
        - Even arguments (2nd, 4th...) are paths to html reports.

        Example:
            load_tests("run1.json", "run1.html", "run2.json", "run2.html")

        :param path: path to the test file
        :param report_path: path to the test html report file
        """
        if self._justification_executed:
            raise RuntimeError('Another tests cannot be loaded after justification.')

        for i in range(0, len(args), 2):
            path = str(args[i])
            report_path = str(args[i + 1] if i + 1 < len(args) else '')

            tests_list = self._load(path)

            # Backward compatibility (old test artifacts were containing list of test result directly, now is the list wrapped as a 'tests' key dict value)
            if 'tests' in tests_list:
                tests_list = tests_list['tests']

            for test in tests_list:
                test['html_report_path'] = report_path
                # More unique ID for handling the running of a single test from multiple levels
                test['test_id_with_level'] = f"{test['test_id']}{test['level']}"

                # Backward compatibility (EMPTY result was replaced by NOT-EXECUTED)
                if test['result'] == 'EMPTY':
                    test['result'] = 'NOT-EXECUTED'

            self._tests[path] = tests_list

    @overload
    def load_issues(self, path: Union[str, Path]) -> None:
        ...

    @overload
    def load_issues(self, *paths: Union[str, Path]) -> None:
        ...

    def load_issues(self, *paths: Union[str, Path]) -> None:
        """
        Loads serialized issues file(s).

        Accepts variable number of paths as arguments.

        :param paths: path(s) to the file(s)
        """
        if self._justification_executed:
            raise RuntimeError('Another issues cannot be loaded after justification.')

        for path in paths:
            path = str(path)
            self._issues[path] = self._load(path)

    def load_features(self, path: Union[str, Path]) -> None:
        """
        Loads serialized feature list

        :param path: path to the file
        """
        features = self._load(path)
        for features_list in features.values():
            for feature in features_list:
                for feature_data in feature.values():
                    feature_out_of_scope = False
                    requirements = list(feature_data.get('link', {}).keys())
                    if requirements == []:
                        feature_out_of_scope = True
                    else:
                        for requirement in requirements:
                            if requirement in self._requirements.keys():
                                if self._requirements[requirement] is not None:
                                    feature_out_of_scope = True
                                else:
                                    feature_out_of_scope = False
                                    break
                            else:
                                feature_out_of_scope = False
                                break

                    feature_data['oos'] = feature_out_of_scope

        self._features = features

    def _write_file(self, name: str, path: str, content: str, is_justified_record=False) -> None:
        """
        Writes content to the given filename

        :param name: name of the file
        :param path: path to the file
        :param content: content of the file
        :param is_justified_report: defines if written file is regeneration of test record
        """
        dir_name = os.path.dirname(os.path.abspath(path))

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        self._outputs.append((name, path, True, is_justified_record))
        print(f'... created output {path}')

    def _collect_requirements(self, testsuite: Dict) -> List[Tuple[str, Optional[str]]]:
        """
        Collects all requirements mentioned in the testsuite

        :param testsuite: testsuite to process
        :return: list of collected requirements from test suite
        """
        requirements = set()

        # extract all requirements from the test-suite mentions
        for test_run in testsuite.values():
            for test in test_run:
                for req in test['requirements']:
                    requirements.add((req, None))

        # add requirements from the full list of requirements if they are not already in there
        for req, data in self._requirements.items():
            if not any(r[0].startswith(req) for r in requirements):
                requirements.add((req, data))

        return natsorted(
            list(requirements), key=lambda req: ' '.join((f'{chunk:>010}' for chunk in re.split(r'-|_|\s', req[0])))
        )

    def _collect_summary(self, testsuite: Dict) -> Summary:
        """
        Collects summary about the testsuite

        :param testsuite: testsuite to process
        :return: test suite summary
        """
        summary = Summary()

        for test_run in testsuite.values():
            for test in test_run:
                level = test['level']
                result = test['result'].strip().upper()
                summary.results += result

                if level not in summary.levels:
                    summary.levels[level] = {'execution': {}, 'tests': 0}

                summary.levels[level]['tests'] += 1

                if 'execution' in test['tags']:
                    for execution in test['tags']['execution']:
                        if execution not in summary.execution:
                            summary.execution[execution] = 0

                        if execution not in summary.levels[level]['execution']:
                            summary.levels[level]['execution'][execution] = 0

                        summary.execution[execution] += 1
                        summary.levels[level]['execution'][execution] += 1

        # add missing executions with 0 number of tests
        for execution in summary.execution:
            for level in summary.levels:
                if execution not in summary.levels[level]['execution']:
                    summary.levels[level]['execution'][execution] = 0

        return summary

    def _add_index_link(self, path: str) -> None:
        """
        Add link to index page into every generated file.

        :param path: index path
        """
        for _, file_path, is_generated, _ in self._outputs:
            if is_generated:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                content = content.replace('href="#index"', f'href="{ rel_path(file_path, path) }"')

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)

    def _add_test_run_report_path_to_issues(self) -> None:
        """
        Add key with test result html report path to every issue dict
        """
        test_name_to_html_report_path = {}
        for tests in self._tests.values():
            for test in tests:
                test_id = test['test_id_with_level']
                report_path = test['html_report_path']
                test_name_to_html_report_path[test_id] = rel_path(self._issue_list_path, report_path)

        for file_issues in self._issues.values():
            for result in ('errors', 'failures'):
                for issue in file_issues[result]:
                    test_id = f"{ issue['test'] }{ file_issues['run']['level'] }"
                    issue['html_report_path'] = test_name_to_html_report_path[test_id]

    def print_requirements_summary(
        self,
        path: Union[str, Path],
        name: str = 'Requirements Coverage Summary',
        preamble: Union[Sequence[str], str, None] = None,
        evaluation_policy: Union[CoveragePolicy, Callable[[List[str]], str]] = CoveragePolicy.STRICT
    ) -> None:
        """
        Prints requirements summary report.

        :param path: where to store the output file
        :param name: name of the produced report used in title
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        :param evaluation_policy: policy used for evaluating requirement result
        """
        path = str(path)
        formater = HtmlReqSummaryOutput(preamble=preamble)
        issue_list_path = rel_path(path, self._issue_list_path) if (self._issue_list_path is not None) else None
        test_plan_paths = {level: rel_path(path, plan_path) for level, plan_path in self._test_plan_paths.items()}

        output = formater.print(
            name=name,
            testsuite=self._tests,
            requirements=self._collect_requirements(self._tests),
            summary=self._collect_summary(self._tests),
            issue_list_path=issue_list_path,
            test_plan_paths=test_plan_paths,
            user_data=self._user_data,
            evaluation_policy=evaluation_policy
        )
        self._write_file(name, path, output)

    def print_user_stories_summary(
        self,
        path: Union[str, Path],
        name: str = 'User stories Coverage Summary',
        preamble: Union[Sequence[str], str, None] = None
    ) -> None:
        """
        Prints user stories summary report from list of doorstop user stories.

        :param path: where to store the output file
        :param name: name of the produced report used in title
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        try:
            from .outputs.html_user_stories_summary import HtmlUserStoriesSummaryOutput
        except ImportError as ex:
            raise ImportError(f'Missing pip dependencies. Reason: {ex}')

        path = str(path)
        formater = HtmlUserStoriesSummaryOutput(preamble=preamble)
        issue_list_path = rel_path(path, self._issue_list_path) if (self._issue_list_path is not None) else None
        test_plan_paths = {level: rel_path(path, plan_path) for level, plan_path in self._test_plan_paths.items()}

        output = formater.print(
            name=name,
            testsuite=self._tests,
            user_stories=self._user_stories,
            summary=self._collect_summary(self._tests),
            issue_list_path=issue_list_path,
            test_plan_paths=test_plan_paths,
            user_data=self._user_data
        )
        self._write_file(name, path, output)

    def print_test_summary(
        self,
        path: Union[str, Path],
        name: str = 'Test Summary Report',
        preamble: Union[Sequence[str], str, None] = None
    ) -> None:
        """
        Prints test summary report.

        :param path: where to store the output file
        :param name: name of the produced report used in title
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        path = str(path)
        formater = HtmlTestSummaryOutput(preamble=preamble)
        issue_list_path = rel_path(path, self._issue_list_path) if (self._issue_list_path is not None) else None
        test_plan_paths = {level: rel_path(path, plan_path) for level, plan_path in self._test_plan_paths.items()}

        # Update path to test run report to relative one
        updated_tests = {
            k: [
                {
                    **test, 'html_report_path':
                        rel_path(path, test['html_report_path']) if test['html_report_path'] != '' else ''
                } for test in tests
            ] for k, tests in self._tests.items()
        }

        output = formater.print(
            name=name,
            testsuite=updated_tests,
            summary=self._collect_summary(self._tests),
            issue_list_path=issue_list_path,
            test_plan_paths=test_plan_paths,
            user_data=self._user_data
        )
        self._write_file(name, path, output)

    def print_test_plan(
        self,
        path: Union[str, Path],
        name: str = 'Test Plan',
        preamble: Union[Sequence[str], str, None] = None,
        level: Union[Tuple[str, ...], str, None] = None
    ) -> None:
        """
        Prints test summary plan.formater

        :param path: where to store the output file
        :param name: name of the produced report used in title
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        :param level: level to filter the tests
        """
        path = str(path)

        if isinstance(level, (list, set, tuple, frozenset)):
            levels = level
        elif isinstance(level, str):
            levels = (level,)
        else:
            levels = None

        if levels is not None:
            for l in levels:
                self._test_plan_paths[l] = path
        else:
            self._test_plan_paths['_'] = path

        formater = HtmlTestPlanOutput(preamble=preamble, path=path)
        output = formater.print(name=name, testsuite=self._tests, levels=levels, user_data=self._user_data)
        self._write_file(name, path, output)

    def print_issue_list(
        self,
        path: Union[str, Path],
        name: str = 'List of Issues',
        preamble: Union[Sequence[str], str, None] = None
    ) -> None:
        """
        Prints list of issues with justifications.

        :param path: path where the file shall be created
        :param name: name of the output file
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        path = str(path)
        self._issue_list_path = path
        formater = HtmlIssueListOutput(preamble=preamble, path=path)
        self._add_test_run_report_path_to_issues()
        test_plan_paths = {level: rel_path(path, plan_path) for level, plan_path in self._test_plan_paths.items()}

        output = formater.print(
            name=name, issues=self._issues, test_plan_paths=test_plan_paths, user_data=self._user_data
        )
        self._write_file(name, path, output)

    def print_feature_summary(
        self,
        path: Union[str, Path],
        name: str = 'Summary of Features',
        preamble: Union[Sequence[str], str, None] = None,
        evaluation_policy: Union[CoveragePolicy, Callable[[List[str]], str]] = CoveragePolicy.STRICT
    ) -> None:
        """
        Prints summary of features with related tests

        :param path: path where the file shall be created
        :param name: name of the output file
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        :param evaluation_policy: policy used for evaluating feature result
        """
        path = str(path)
        self._feature_list_path = path
        formater = HtmlFeatureSummaryOutput(preamble=preamble, path=path)
        test_plan_paths = {level: rel_path(path, plan_path) for level, plan_path in self._test_plan_paths.items()}
        output = formater.print(
            name=name,
            features=self._features,
            testsuite=self._tests,
            test_plan_paths=test_plan_paths,
            evaluation_policy=evaluation_policy
        )
        self._write_file(name, path, output)

    def add_index_link(self, path: Union[str, Path], name: str) -> None:
        """
        Adds not generated file link to index page.

        :param path: path to the file
        :param name: name of the file that will be displayed on index page
        """
        path = str(path)
        self._outputs.append((name, path, False, False))
        print(f'... added index page file {path}')

    def print_index(
        self, path: Union[str, Path], name: str = 'Index', preamble: Union[Sequence[str], str, None] = None
    ) -> None:
        """
        Prints index file for the generated files

        :param path: path where the file shall be created
        :param name: name of the output file
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        path = str(path)
        formater = HtmlIndexOutput(preamble=preamble)
        file_list = []

        for file_name, file_path, _, is_justified_record in self._outputs:
            if not is_justified_record:
                file_list.append((file_name, rel_path(path, file_path)))

        output = formater.print(name, file_list)
        self._add_index_link(path)
        self._write_file(name, path, output)

    def print_justified_record(self, tests_path: str, output_path: str) -> None:
        """
        Regenerate test record with updated results after justification
        :param tests_path: path to json/yaml tests file
        :param output_path: path to regenerated file
        """
        if not tests_path in self._tests:
            raise RuntimeError(
                f"Given tests ({tests_path}) weren't loaded before justified record print. They must be loaded before this operation."
            )

        raw_data = self._load(tests_path)
        summary = Summary()

        for test in self._tests[tests_path]:
            summary.results += test['result']

        output = HtmlResultOutput(path=output_path)
        rendered = output.print(
            env_info=raw_data['run'].get('env-info', None),
            user_data=raw_data['run']['user-data'],
            result=self._prepare_test_data_for_template(self._tests[tests_path], raw_data),
            summary=summary,
            justified_record=True
        )

        self._write_file('', output_path, rendered, True)

        # Update tests link to html report
        for test in self._tests[tests_path]:
            test['html_report_path'] = output_path

    def _prepare_test_data_for_template(self, flat_data: list, raw_data: Dict):
        """
        Helper method to convert loaded tests into BRunhildaTestResult format
        Needed for correct parsing into HTML test record template

        :param flat_data: loaded test data from json/yaml file
        :param raw_data: raw data
        """
        converted_result = {'testcases': {}}
        case_id = 0  # unique ID in case raw_data doesn't contain 'test-cases'

        for test in flat_data:
            case_name = test['case']

            if case_name not in converted_result['testcases']:
                converted_result['testcases'][case_name] = {
                    'name': case_name,
                    'time': 0.0,  # will be retroactively adjusted
                    'description': '',  # will be retroactively adjusted
                    'tests': [],
                    'passed': 0,
                    'errored': 0,
                    'failed': 0,
                    'skipped': 0,
                    'justified': 0,
                    'not_executed': 0,
                    'expected_failures': 0,
                    'unexpected_successes': 0,
                    'id': case_id  # will be retroactively adjusted
                }
                case_id += 1

            ctx = converted_result['testcases'][case_name]

            raw_res = test.get('result', 'NOT-EXECUTED').upper()

            test_obj = {
                'name': test.get('test_id', 'unknown').split('.')[-1],
                'result': raw_res,
                'time': test.get('duration', 0.0),
                'skip_reason': test.get('comment')[0] if raw_res == 'SKIPPED' and test.get('comment') else '',
                'description': test.get('description', ''),
                'steps': test.get('steps', []),
                'subtests': test.get('subtests', []),
                'output': test.get('output', ''),
                'errors': test.get('errors', []),
                'extra': test.get('extra', [])
            }

            if test_obj['subtests']:
                stats = {}
                for st in test_obj['subtests']:
                    st_res = st.get('result', 'NOT-EXECUTED').lower()
                    stats[st_res] = stats.get(st_res, 0) + 1
                test_obj['subtests_stats'] = stats

            ctx['tests'].append(test_obj)

            if raw_res == 'PASSED':
                ctx['passed'] += 1
            elif raw_res == 'FAILED':
                ctx['failed'] += 1
            elif raw_res == 'ERRORED':
                ctx['errored'] += 1
            elif raw_res == 'SKIPPED':
                ctx['skipped'] += 1
            elif raw_res == 'EXPECTED-FAILURE':
                ctx['expected_failures'] += 1
            elif raw_res == 'UNEXPECTED-SUCCESS':
                ctx['unexpected_successes'] += 1
            elif raw_res == 'JUSTIFIED':
                ctx['justified'] += 1
            elif raw_res == 'NOT-EXECUTED':
                ctx['not_executed'] += 1

        if 'test-cases' in raw_data:
            # Update test cases description, ID and time from raw data
            for test_case in raw_data['test-cases']:
                if test_case['name'] in converted_result['testcases']:
                    converted_result['testcases'][test_case['name']]['description'] = test_case['description']
                    converted_result['testcases'][test_case['name']]['time'] = test_case['time']
                    converted_result['testcases'][test_case['name']]['id'] = test_case['id']

        return converted_result
