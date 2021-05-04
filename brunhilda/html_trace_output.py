from .html_output import HtmlOutput

class HtmlTraceOutput(HtmlOutput):
    """
    """

    def print(self, refs, trace_matrix):
        """
        Prints test trace matrix to HTML document.

        :param trace_matrix: BRunhilda trace matrix from the test run
        :return: HTML string
        :rtype: str
        """
        template = self.load_template('trace.html.jinja2')
        rendered = template.render(refs=refs, tests=trace_matrix)
        return rendered
