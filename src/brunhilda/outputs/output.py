import datetime
import os
import urllib.parse

import jinja2

from ..rel_path import rel_path


def _quote_path(path: str) -> str:
    """
    Quotes given path to be useable as browser URL

    :param path: path to be queted
    :return: queted path
    """
    path = path.replace('\\', '/')
    return urllib.parse.quote(path)


class Output:

    def load_template(self, template: str) -> jinja2.Template:
        """
        Loads a Jinja2 template from the templates directory.

        :param template: filename of the template
        :return: Jinja2 Template object
        """
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        template_path = os.path.join(template_dir, template)

        with open(template_path, encoding='utf-8') as f:
            template_str = f.read()

        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True
        )
        template = environment.from_string(template_str)
        template.globals['now'] = datetime.datetime.now  # pass func short-hand to the template
        template.globals['rel_path'] = rel_path  # pass func short-hand for relative paths
        template.globals['join_path'] = os.path.join  # pass func short-hand for path join func
        template.globals['dir_path'] = os.path.dirname  # pass func short-hand for dirname func
        template.globals['quote'] = _quote_path
        return template
