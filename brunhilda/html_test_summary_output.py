from typing import Optional, Dict, List
from copy import deepcopy

from .data import Summary
from .html_output import HtmlOutput

class HtmlTestSummaryOutput(HtmlOutput):
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
        Prints test summary to HTML document.

        :param name: name of the produced file
        :param testsuite: BRunhilda tests
        :param summary: generated test summary
        :param issue_list_path: path to the issue list
        :param test_plan_paths: dict of paths to the level test plans
        :param user_data: additional data passed by a user
        :return: HTML string
        """
        entries = []

        for tests in testsuite.values():
            for test in tests:
                entries.append(deepcopy(test))

        template = self.load_template('summary-test.html.jinja2')
        rendered = template.render(name=name,
                                   preamble=self._include_preamble,
                                   tests=entries,
                                   requirements=requirements,
                                   summary=summary,
                                   issue_list_path=issue_list_path,
                                   test_plan_paths=test_plan_paths,
                                   user_data=user_data)
        return rendered
