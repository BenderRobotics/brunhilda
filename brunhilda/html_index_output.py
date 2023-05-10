from typing import List, Union, Tuple
from .html_output import HtmlOutput

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
        rendered = template.render(name=name, outputs=outputs, preamble=self._include_preamble)
        return rendered
