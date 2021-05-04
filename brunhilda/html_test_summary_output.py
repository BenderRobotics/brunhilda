from .html_output import HtmlOutput

class HtmlTestSummaryOutput(HtmlOutput):
    """
    """

    def print(self, env_info, user_data, trace_matrix, total):
        """
        Prints test summary to HTML document.

        :param trace_matrix: BRunhilda trace matrix from the test run
        :return: HTML string
        :rtype: str
        """
        template = self.load_template('summary-test.html.jinja2')
        rendered = template.render(env_info=env_info,
                                   user_data=user_data,
                                   tests=trace_matrix,
                                   total=total)
        return rendered
