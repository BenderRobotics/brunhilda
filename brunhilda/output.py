import os
import jinja2
import datetime
import urllib.parse

from .rel_path import rel_path


def _quote_path(path):
    """
    Quotes given path to be useable as browser URL

    :param path: path to be queted
    :return: queted path
    """
    path = path.replace('\\', '/')
    return urllib.parse.quote(path)


class Output:
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
        template.globals['now'] = datetime.datetime.now # pass func short-hand to the template
        template.globals['rel_path'] = rel_path         # pass func short-hand for relative paths
        template.globals['join_path'] = os.path.join    # pass func short-hand for path join func
        template.globals['dir_path'] = os.path.dirname  # pass func short-hand for dirname func
        template.globals['quote'] = _quote_path
        return template
