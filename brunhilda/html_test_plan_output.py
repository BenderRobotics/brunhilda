from copy import deepcopy
from typing import Dict, Optional, Tuple
from .html_output import HtmlOutput

class HtmlTestPlanOutput(HtmlOutput):
    def print(self, name: str,
                    testsuite: Dict,
                    levels: Optional[Tuple[str, ...]],
                    user_data: Dict[str, str] = None) -> str:
        """
        Prints test plan to HTML document.

        :param name: name of the output report
        :param testsuite: BRunhilda test suite,
        :param user_data: additional data passed by a user
        :return: HTML string
        """
        template = self.load_template('test-plan.html.jinja2')
        entries = []

        for tests in testsuite.values():
            for test in tests:
                if (levels is None) or (test['level'] in levels):
                    if 'description' in test:
                        test['description'] = self._format_doc(test['description'])

                    if 'steps' in test:
                        for i, step in enumerate(test['steps']):
                            test['steps'][i]['description'] = self._format_doc(step['description'])
                            test['steps'][i]['expectation'] = self._format_doc(step['expectation'])

                    entries.append(deepcopy(test))

        rendered = template.render(name=name,
                                   preamble=self._include_preamble,
                                   tests=entries,
                                   user_data=user_data)
        return rendered
