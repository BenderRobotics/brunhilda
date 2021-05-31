from .html_output import HtmlOutput

class HtmlTestPlanOutput(HtmlOutput):
    def print(self, env_info, user_data, tests, manual_execution):
        """
        Prints test plan to HTML document.

        :param tests: BRunhilda test result from the test run,
        :return: HTML string
        :rtype: str
        """
        template = self.load_template('test-plan.html.jinja2')

        for test in tests:
            if 'description' in test:
                test['description'] = self._format_doc(test['description'])

            if 'steps' in test:
                for i, step in enumerate(test['steps']):
                    test['steps'][i]['description'] = self._format_doc(step['description'])
                    test['steps'][i]['expectation'] = self._format_doc(step['expectation'])

        rendered = template.render(preamble=self._include_preamble,
                                   env_info=env_info,
                                   user_data=user_data,
                                   tests=tests,
                                   manual_execution=manual_execution)
        return rendered
