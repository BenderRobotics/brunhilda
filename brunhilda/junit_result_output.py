import copy
from brunhilda.output import Output
from .output import Output


class JUnitResultOutput(Output):
   def _format_terminal(self, text):
        """
        Removes colorama terminal output control sequence from the text
        """
        CSI = '\033['   # this is start of the ASCII escape sequences
        start = 0

        while start >= 0:
            pos = text.find(CSI, start)     # nex loc of the CSI
            end = text.find('m', pos) + 1   # CSI ends with 'm'
            esc = text[pos:end]             # whole escape sequence, e.g. '\033[30m' for BACK
            text = text.replace(esc, '')
            start = pos

        return text

   def print(self, env_info, user_data, result, summary, manual_execution):
      result = copy.deepcopy(result)

      for case in sorted(result['testcases'].values(), key=lambda item: item['id']):
         for test in case['tests']:
            if 'output' in test:
               test['output'] = self._format_terminal(test['output'])
            if 'errors' in test:
               test['errors'] = [self._format_terminal(err) for err in test['errors']]

      template = self.load_template('template.junit.jinja2')
      rendered = template.render(env_info=env_info,
                                 user_data=user_data,
                                 result=result,
                                 summary=summary,
                                 manual_execution=manual_execution)
      return rendered
