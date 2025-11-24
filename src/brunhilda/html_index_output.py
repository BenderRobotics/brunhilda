from typing import List, Tuple, Union

from .html_output import HtmlOutput

try:
    from .__version__ import version as brunhilda_version
except ImportError:
    brunhilda_version = 'unknown'


class HtmlIndexOutput(HtmlOutput):
    """
    """

    def print(self, name: str, outputs: List[Tuple], preamble: Union[List[str], str, None] = None) -> str:
        """
        Prints index with all outputs

        :param name: name of the generated report
        :param outputs: list of the generated outputs in a format [(path, title), ...]
        :param preamble: path or multiple paths to the HTML document to be used as a document preamble
        :return: HTML string
        """
        template = self.load_template('index.html.jinja2')
        rendered = template.render(
            name=name, outputs=outputs, brunhilda_version=brunhilda_version, preamble=self._include_preamble
        )
        return rendered
