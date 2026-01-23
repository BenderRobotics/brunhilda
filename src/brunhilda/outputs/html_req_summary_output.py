from copy import deepcopy
from typing import Callable, Dict, List, Optional, Union

from ..data import ResultsSummary, Summary
from ..policies import CoveragePolicy, evaluate_result
from .html_output import HtmlOutput

try:
    from ..__version__ import version as brunhilda_version
except ImportError:
    brunhilda_version = 'unknown'


class HtmlReqSummaryOutput(HtmlOutput):
    """
    Generates an HTML report summarizing requirements.
    """

    def print(
        self,
        name: str,
        testsuite: Dict,
        requirements: List[str],
        summary: Summary,
        issue_list_path: Optional[str] = None,
        test_plan_paths: Optional[Dict[str, str]] = None,
        user_data: Dict[str, str] = None,
        evaluation_policy: Union[CoveragePolicy, Callable[[List[str]], str]] = CoveragePolicy.STRICT
    ) -> str:
        """
        Prints requirements summary to HTML document.

        :param name: name of the generated report
        :param testsuite: suite of the executed tests
        :param requirements: list of all requirements
        :param summary: summary for the test suite
        :param issue_list_path: path to the issue list
        :param test_plan_path: path to the issue list
        :param user_data: additional data passed by a user
        :return: HTML string
        """
        entries = []
        count = 0
        requirements_results = ResultsSummary(0, 0, 0, 0, 0, 0, 0, 0, 0)

        for requirement, data in requirements:
            levels = {}
            passed = 0
            count = 0
            req_tests_results = []

            for test_run in testsuite.values():
                for test in test_run:
                    if ('requirements' in test) and (requirement in test['requirements']):
                        req_tests_results.append(test['result'])
                        level = test['level']
                        result = test['result'].upper()
                        count += 1

                        if result in ('PASSED', 'JUSTIFIED'):
                            passed += 1

                        if level not in levels:
                            levels[level] = []

                        levels[level].append(deepcopy(test))

            for level in levels:
                for test in levels[level]:
                    test['coverage_ratio'] = (100 / count) if (count > 0) else 0

            if data is not None:
                requirement_result = 'OUT-OF-SCOPE'
                requirements_results += requirement_result
            elif requirement != '-':  # Exclude empty requirement from stats
                requirement_result = evaluate_result(req_tests_results, evaluation_policy)
                requirements_results += requirement_result
            else:
                requirement_result = ''

            entries.append(
                {
                    'name': requirement,
                    'levels': levels,
                    'count': count,
                    'pass_ratio': (passed / count) * 100 if (count != 0) else 0,
                    'out_of_scope': data,
                    'result': requirement_result
                }
            )

        template = self.load_template('summary-req.html.jinja2')
        rendered = template.render(
            name=name,
            preamble=self._include_preamble,
            summary=summary,
            requirements=entries,
            issue_list_path=issue_list_path,
            test_plan_paths=test_plan_paths,
            user_data=user_data,
            brunhilda_version=brunhilda_version,
            requirements_results=requirements_results,
            only_summary_functions=True
        )
        return rendered
