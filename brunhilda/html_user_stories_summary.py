from copy import deepcopy
from doorstop import Item
from typing import Dict, List, Optional

from .data import Summary
from .html_output import HtmlOutput


class HtmlUserStoriesSummaryOutput(HtmlOutput):
    """
    This class creates a HTML output for user stories created by doorstop package.
    """

    def print(self, name: str,
                    testsuite: Dict,
                    user_stories: List[Item],
                    summary: Summary,
                    issue_list_path: Optional[str] = None,
                    test_plan_paths: Optional[Dict[str, str]] = None,
                    user_data: Dict[str, str] = None) -> str:
        """
        Prints user stories summary to HTML document. User stories are expected to be in doorstop format.

        :param name: name of the generated report
        :param testsuite: suite of the executed tests
        :param user_stories: list of all user stories
        :param summary: summary for the test suite
        :param issue_list_path: path to the issue list
        :param test_plan_path: path to the issue list
        :param user_data: additional data passed by a user
        :return: HTML string
        :rtype: str
        """
        entries = list()
        groups = list()

        for user_story in user_stories:

            if not isinstance(user_story, Item):
                raise ValueError("User story is not object of doorstop item.")

            tests_coverage = list()

            req_id = user_story.get("uid").value
            header = user_story.get("header")
            text = user_story.get("text")
            for test_run in testsuite.values():
                for test in test_run:
                    if req_id in test['requirements']:
                        tests_coverage.append(deepcopy(test))

            if header not in groups:
                groups.append(header)

            if user_story.get("enabled"):
                status = "ACTIVE"
            else:
                status = "INACTIVE"

            entries.append({
                'status': status,
                'name': req_id,
                'level': header,
                'story': text,
                'tests': tests_coverage,
            })

        template = self.load_template('summary-user-stories.html.jinja2')
        rendered = template.render(name=name,
                                   preamble=self._include_preamble,
                                   user_stories=entries,
                                   summary=summary,
                                   groups=groups,
                                   issue_list_path=issue_list_path,
                                   test_plan_paths=test_plan_paths,
                                   user_data=user_data)

        return rendered

