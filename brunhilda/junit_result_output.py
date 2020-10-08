import os
import jinja2
import colorama
import datetime
from docutils.core import publish_parts

class JUnitResultOutput():
    def print(self, testresult):
        path = os.path.join(os.path.dirname(__file__), 'templates', 'template.junit.jinja2')

        with open(path, encoding="utf-8") as f:
            template = jinja2.Template(f.read())

        template.globals['now'] = datetime.datetime.utcnow
        rendered = template.render(data=testresult)
        return rendered
