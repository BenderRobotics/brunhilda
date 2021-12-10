from copy import deepcopy
from typing import Dict, List, Optional

from .data import Summary
from .html_output import HtmlOutput


class HtmlReqSummaryOutput(HtmlOutput):
    """
    """

    def print(self, name: str,
                    testsuite: Dict,
                    requirements: List[str],
                    summary: Summary,
                    issue_list_path: Optional[str] = None,
                    test_plan_paths: Optional[Dict[str, str]] = None,
                    user_data: Dict[str, str] = None) -> str:
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
        :rtype: str
        """
        entries = []
        count = 0

        for requirement in requirements:
            levels = {}
            passed = 0
            count = 0

            for test_run in testsuite.values():
                for test in test_run:
                    if ('requirements' in test) and (requirement in test['requirements']):
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

            entries.append({
                'name': requirement,
                'levels': levels,
                'count': count,
                'pass_ratio': (passed / count) * 100 if (count != 0) else 0,
            })

        template = self.load_template('summary-req.html.jinja2')
        rendered = template.render(name=name,
                                   preamble=self._include_preamble,
                                   summary=summary,
                                   requirements=entries,
                                   issue_list_path=issue_list_path,
                                   test_plan_paths=test_plan_paths,
                                   user_data=user_data)
        return rendered
