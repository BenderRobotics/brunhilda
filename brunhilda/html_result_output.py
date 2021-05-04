import copy

from .html_output import HtmlOutput

class HtmlResultOutput(HtmlOutput):
    def print(self, env_info, user_data, result):
        """
        Prints test result to HTML document.

        :param result: BRunhilda test result from the test run,
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

        template = self.load_template('template.html.jinja2')
        rendered = template.render(env_info=env_info, user_data=user_data, result=result)
        return rendered
