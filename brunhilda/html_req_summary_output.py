from copy import deepcopy

from .html_output import HtmlOutput

class HtmlReqSummaryOutput(HtmlOutput):
    """
    """

    def _format_req(self, req_name):
        """
        Sorting function to be used to sort the requirements

        Splits the chunks in the requirement ID and adds padding to correctly sort
        chapters (e.g. 'L15 4.2' and 'L15 14.1').

        :param str req_name: name of the requirement
        :return: requirement name formated in a way supporting the sorting
        """
        input_chunks = [req_name]
        output_chunks = []

        for delimiter in (' ', '-', '.'):
            for c in input_chunks:
                output_chunks.extend(c.split(delimiter))

            input_chunks = deepcopy(output_chunks)
            output_chunks = []

        chunks = input_chunks

        for i, chunk in enumerate(chunks):
            # pad with zeros to length of 10
            chunks[i] = f'{chunk:>010}'

        return ' '.join(chunks)

    def print(self, env_info, user_data, trace_matrix, paths, requirements_list):
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

        # add requirements from the full list of requirements if they are not already in there
        for req in requirements_list:
            if not any(r.startswith(req) for r in requirement_tags):
                requirement_tags.add(req)

        for tag in sorted(requirement_tags, key=self._format_req):
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
                                   requirements=requirements,
                                   paths=paths)
        return rendered
