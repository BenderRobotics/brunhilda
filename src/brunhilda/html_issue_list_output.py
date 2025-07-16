from typing import Dict, Optional

from .html_output import HtmlOutput


class HtmlIssueListOutput(HtmlOutput):

    def print(
        self,
        name: str,
        issues: Dict,
        test_plan_paths: Optional[Dict[str, str]] = None,
        user_data: Dict[str, str] = None
    ):
        """
        Prints issue list

        :param name: name of the generated report file
        :param issues: BRunhilda issues
        :param user_data: additional data passed by a user
        :return: HTML string
        :rtype: str
        """
        template = self.load_template('issue-list.html.jinja2')
        rendered = template.render(
            name=name,
            preamble=self._include_preamble,
            reports=issues,
            user_data=user_data,
            test_plan_paths=test_plan_paths,
            document_path=self.path
        )
        return rendered
