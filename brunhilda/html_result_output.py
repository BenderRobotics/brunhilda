import copy

from .html_output import HtmlOutput

class HtmlResultOutput(HtmlOutput):
    def print(self, env_info, user_data, result, summary, manual_execution):
        """
        Prints test result to HTML document.

        :param result: BRunhilda test result from the test run,
        :param manual_execution: True - tests are executed manually and the report is filled by
                                 tester.
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
                                   manual_execution=manual_execution)
        return rendered
