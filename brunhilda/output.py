import os
import jinja2
import datetime


class Output():
    def load_template(self, template):
        """
        Prints testresult to HTML document.

        :param testresult: BRunhilda test result from the test run,
        :return: HTML string
        :rtype: str
        """
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        template_path = os.path.join(template_dir, template)

        with open(template_path, encoding='utf-8') as f:
            template_str = f.read()

        environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                         trim_blocks=True,
                                         lstrip_blocks=True)
        template = environment.from_string(template_str)
        template.globals['now'] = datetime.datetime.now
        return template
