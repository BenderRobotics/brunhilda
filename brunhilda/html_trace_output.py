import os
import jinja2
import datetime
import copy

class HtmlTraceOutput():
    """
    """

    def print(self, refs, trace_matrix):
        """
        Prints testresult to HTML document.

        :param trace_matrix: BRunhilda trace matrix from the test run
        :return: HTML string
        :rtype: str
        """
        path = os.path.join(os.path.dirname(__file__), 'templates', 'trace.html.jinja2')

        with open(path, encoding="utf-8") as f:
            template = jinja2.Template(f.read())

        template.globals['now'] = datetime.datetime.now
        rendered = template.render(refs=refs, tests=trace_matrix)
        return rendered
