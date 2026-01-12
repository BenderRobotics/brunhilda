from typing import List, Tuple, Union

from .html_output import HtmlOutput

try:
    from ..__version__ import version as brunhilda_version
except ImportError:
    brunhilda_version = 'unknown'


class HtmlIndexOutput(HtmlOutput):
    """
    Generates an HTML index page listing all created output reports.

    This class creates a navigation hub (index.html) containing links to
    other generated artifacts (like test reports, feature summaries, etc.).
    """

    def print(self, name: str, outputs: List[Tuple]) -> str:
        """
        Prints index with all outputs

        :param name: name of the generated report
        :param outputs: list of the generated outputs in a format [(path, title), ...]
        :return: HTML string
        """
        template = self.load_template('index.html.jinja2')
        rendered = template.render(
            name=name, outputs=outputs, brunhilda_version=brunhilda_version, preamble=self._include_preamble
        )
        return rendered
