from brunhilda.output import Output
from .output import Output


class JUnitResultOutput(Output):
   def print(self, env_info, user_data, result):
        template = self.load_template('template.junit.jinja2')
        rendered = template.render(env_info=env_info, user_data=user_data, result=result)
        return rendered
