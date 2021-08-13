from .html_output import HtmlOutput

class HtmlIndexOutput(HtmlOutput):
    """
    """

    def print(self, outputs, paths):
        """
        Prints index with all outputs

        :param outputs: list of the generated outputs
        :return: HTML string
        :rtype: str
        """
        template = self.load_template('index.html.jinja2')
        rendered = template.render(outputs=outputs, paths=paths)
        return rendered
