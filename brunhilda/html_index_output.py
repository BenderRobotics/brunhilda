from typing import List, Tuple
from .html_output import HtmlOutput

class HtmlIndexOutput(HtmlOutput):
    """
    """

    def print(self, name: str, outputs: List[Tuple]) -> str:
        """
        Prints index with all outputs

        :param name: name of the generated report
        :param outputs: list of the generated outputs in a format [(path, title), ...]
        :return: HTML string
        """
        template = self.load_template('index.html.jinja2')
        rendered = template.render(name=name, outputs=outputs)
        return rendered
