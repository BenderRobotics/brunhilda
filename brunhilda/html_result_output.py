import copy
from typing import Dict

from .data import Summary
from .html_output import HtmlOutput

class HtmlResultOutput(HtmlOutput):
    def print(self, env_info: Dict, user_data: Dict, result, summary: Summary):
        """
        Prints test result to HTML document.

        :param env_info: environment info dictionary
        :param user_data: user data dictionary
        :param result: BRunhilda test result from the test run
        :param summary: BRunhilda test result summary
        :return: HTML string
        :rtype: str
        """
        result = copy.deepcopy(result)

        for case in sorted(result['testcases'].values(), key=lambda item: item['id']):
            if 'description' in case:
                case['description'] = self._format_doc(case['description'])

            for test in case['tests']:
                if 'description' in test:
                    test['description'] = self._format_doc(test['description'])
                if 'output' in test:
                    test['output'] = self._format_terminal(test['output'])
                    test['output'] = self._format_logging(test['output'])
                if 'errors' in test:
                    test['errors'] = [self._format_terminal(err) for err in test['errors']]
                if 'steps' in test:
                    for i, step in enumerate(test['steps']):
                        test['steps'][i]['description'] = self._format_doc(step['description'])
                        test['steps'][i]['expectation'] = self._format_doc(step['expectation'])

        template = self.load_template('template.html.jinja2')
        rendered = template.render(preamble=self._include_preamble,
                                   env_info=env_info,
                                   user_data=user_data,
                                   result=result,
                                   summary=summary,
                                   document_path=self.path)
        return rendered
