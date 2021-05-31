from copy import deepcopy

from .html_output import HtmlOutput

class HtmlReqSummaryOutput(HtmlOutput):
    """
    """

    def print(self, env_info, user_data, trace_matrix):
        """
        Prints requirements summary to HTML document.

        :param trace_matrix: BRunhilda trace matrix from the test run
        :return: HTML string
        :rtype: str
        """
        # rewind the matrix to the perspective of the requirements
        requirements = []
        requirement_tags = set()

        for test in trace_matrix:
            for tag in test['requirements']:
                requirement_tags.add(tag)

        for tag in sorted(requirement_tags):
            tests = []
            passed = 0

            for test in trace_matrix:
                if tag in test['requirements']:
                    tests.append(deepcopy(test))

            for test in tests:
                if test['result'].lower() == 'passed':
                    passed += 1

                test['coverage_ratio'] = 1 / len(tests)

            test_pass_ratio = passed / len(tests) if len(tests) != 0 else 0
            requirements.append({
                'requirement_id': tag,
                'tests': tests,
                'test_pass_ratio': test_pass_ratio,
            })

        template = self.load_template('summary-req.html.jinja2')
        rendered = template.render(preamble=self._include_preamble,
                                   env_info=env_info,
                                   user_data=user_data,
                                   requirements=requirements)
        return rendered
