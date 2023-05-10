import os
import re
import yaml
import simplejson as json

from doorstop import Item
from natsort import natsorted
from typing import Dict, List, Optional, Union, Tuple, Sequence

from .data import Summary
from .rel_path import rel_path
from .html_test_summary_output import HtmlTestSummaryOutput
from .html_req_summary_output import HtmlReqSummaryOutput
from .html_test_plan_output import HtmlTestPlanOutput
from .html_index_output import HtmlIndexOutput
from .html_issue_list_output import HtmlIssueListOutput
from .html_feature_summary_output import HtmlFeatureSummaryOutput
from .html_user_stories_summary import HtmlUserStoriesSummaryOutput


class Reporter:
    def __init__(self, requirements: List[str] = [], user_data: Dict[str, str] = {}, user_stories: List[Item] = [] ) -> None:
        self._outputs = []
        self._requirements = requirements
        self._user_stories = user_stories
        self._tests: Dict = {}
        self._issues: Dict = {}
        self._features: Optional[Dict] = None
        self._issue_list_path: Optional[str] = None
        self._feature_list_path: Optional[str] = None
        self._test_plan_paths = {'_': ''}
        self._user_data = user_data

    def _load(self, path: str) -> Dict:
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
                    justifications = [] # list of justifications - there can be several failures in one test
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

    def load_tests(self, path: str) -> None:
        """
        Loads serialized tests file

        :param path: path to the file
        """
        self._tests[path] = self._load(path)

    def load_issues(self, path: str) -> None:
        """
        Loads serialized issues file

        :param path: path to the file
        """
        self._issues[path] = self._load(path)

    def load_features(self, path: str) -> None:
        """
        Loads serialized feature list

        :param path: path to the file
        """
        self._features = self._load(path)

    def _write_file(self, name: str, path: str, content: str) -> None:
        """
        Writes content to the given filename

        :param filename: name of the file
        :param content: content of the file
        """
        dir_name = os.path.dirname(os.path.abspath(path))

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        self._outputs.append((name, path))
        print(f"... created output {path}")

    def _collect_requirements(self, testsuite: Dict) -> List[str]:
        """
        Collects all requirements mentioned in the testsuite

        :param testsuite: testsuite to process
        """
        requirements = set()

        # extract all requirements from the test-suite mentions
        for test_run in testsuite.values():
            for test in test_run:
                for req in test['requirements']:
                    requirements.add(req)

        # add requirements from the full list of requirements if they are not already in there
        for req in self._requirements:
            if not any(r.startswith(req) for r in requirements):
                requirements.add(req)

        return natsorted(list(requirements),
                         key=lambda req: ' '.join((f'{chunk:>010}' for chunk in re.split(r'-|_|\s', req))))

    def _collect_summary(self, testsuite: Dict) -> Summary:
        """
        Collects summary about the testsuite

        :param testsuite: testsuite to process
        """
        summary = Summary()

        for test_run in testsuite.values():
            for test in test_run:
                level = test['level']
                result = test['result'].strip().upper()
                summary.results += result

                if level not in summary.levels:
                    summary.levels[level] = {
                        'execution': {},
                        'tests': 0
                    }

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

    def print_requirements_summary(self, path: str, name: str = 'Requirements Coverage Summary',
                                   preamble: Union[Sequence[str], str, None] = None) -> None:
        """
        Prints requirements summary report.

        :param path: where to store the output file
        :param name: name of the produced report used in title
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        formater = HtmlReqSummaryOutput(preamble=preamble)
        issue_list_path = rel_path(path, self._issue_list_path) if (self._issue_list_path is not None) else None
        test_plan_paths = {level: rel_path(path, plan_path) for level, plan_path in self._test_plan_paths.items()}

        output = formater.print(name=name,
                                testsuite=self._tests,
                                requirements=self._collect_requirements(self._tests),
                                summary=self._collect_summary(self._tests),
                                issue_list_path=issue_list_path,
                                test_plan_paths=test_plan_paths,
                                user_data=self._user_data)
        self._write_file(name, path, output)

    def print_user_stories_summary(self, path: str, name: str = 'User stories Coverage Summary',
                                   preamble: Union[Sequence[str], str, None] = None) -> None:
        """
        Prints user stories summary report from list of doorstop user stories.

        :param path: where to store the output file
        :param name: name of the produced report used in title
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        formater = HtmlUserStoriesSummaryOutput(preamble=preamble)
        issue_list_path = rel_path(path, self._issue_list_path) if (self._issue_list_path is not None) else None
        test_plan_paths = {level: rel_path(path, plan_path) for level, plan_path in self._test_plan_paths.items()}

        output = formater.print(name=name,
                                testsuite=self._tests,
                                user_stories=self._user_stories,
                                summary=self._collect_summary(self._tests),
                                issue_list_path=issue_list_path,
                                test_plan_paths=test_plan_paths,
                                user_data=self._user_data)
        self._write_file(name, path, output)

    def print_test_summary(self, path: str, name: str = 'Test Summary Report',
                           preamble: Union[Sequence[str], str, None] = None) -> None:
        """
        Prints test summary report.

        :param path: where to store the output file
        :param name: name of the produced report used in title
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        formater = HtmlTestSummaryOutput(preamble=preamble)
        issue_list_path = rel_path(path, self._issue_list_path) if (self._issue_list_path is not None) else None
        test_plan_paths = {level: rel_path(path, plan_path) for level, plan_path in self._test_plan_paths.items()}

        output = formater.print(name=name,
                                testsuite=self._tests,
                                requirements=self._collect_requirements(self._tests),
                                summary=self._collect_summary(self._tests),
                                issue_list_path=issue_list_path,
                                test_plan_paths=test_plan_paths,
                                user_data=self._user_data)
        self._write_file(name, path, output)

    def print_test_plan(self, path: str, name: str = 'Test Plan', preamble: Union[Sequence[str], str, None] = None,
                        level: Union[Tuple[str, ...], str, None] = None) -> None:
        """
        Prints test summary plan.formater

        :param path: where to store the output file
        :param name: name of the produced report used in title
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        :param level: level to filter the tests
        """
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

    def print_issue_list(self, path: str, name: str = 'List of Issues', preamble: Union[Sequence[str], str, None] = None) -> None:
        """
        Prints list of issues with justifications.

        :param path: path where the file shall be created
        :param name: name of the output file
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        self._issue_list_path = path
        formater = HtmlIssueListOutput(preamble=preamble, path=path)
        output = formater.print(name=name, issues=self._issues, user_data=self._user_data)
        self._write_file(name, path, output)

    def print_feature_summary(self, path: str, name: str = 'Summary of Features', preamble: Union[Sequence[str], str, None] = None) -> None:
        """
        Prints summary of features with related tests

        :param path: path where the file shall be created
        :param name: name of the output file
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        self._feature_list_path = path
        formater = HtmlFeatureSummaryOutput(preamble=preamble, path=path)
        test_plan_paths = {level: rel_path(path, plan_path) for level, plan_path in self._test_plan_paths.items()}
        output = formater.print(name=name, features=self._features, testsuite=self._tests, test_plan_paths=test_plan_paths)
        self._write_file(name, path, output)

    def print_index(self, path: str, name: str = 'Index', preamble: Union[Sequence[str], str, None] = None) -> None:
        """
        Prints index file for the generated files

        :param path: path where the file shall be created
        :param name: name of the output file
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        """
        formater = HtmlIndexOutput(preamble=preamble)
        file_list = []

        for file_name, file_path in self._outputs:
            file_list.append((file_name, rel_path(path, file_path)))

        output = formater.print(name, file_list)
        self._write_file(name, path, output)
