from .html_output import HtmlOutput

class HtmlTestSummaryOutput(HtmlOutput):
    """
    """

    def print(self, env_info, user_data, tests, summary):
        """
        Prints test summary to HTML document.

        :param tests: BRunhilda tests sequence from the test run
        :return: HTML string
        :rtype: str
        """
        template = self.load_template('summary-test.html.jinja2')
        rendered = template.render(preamble=self._include_preamble,
                                   env_info=env_info,
                                   user_data=user_data,
                                   tests=tests,
                                   summary=summary)
        return rendered
