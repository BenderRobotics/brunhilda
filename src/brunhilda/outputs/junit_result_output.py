import copy
import re
from typing import Any, Dict

from ..data import Summary
from .output import Output


class JUnitResultOutput(Output):
    """
    Generates test execution results in JUnit XML format.
    """

    def _format_terminal(self, text: str) -> str:
        """
        Removes colorama terminal output control sequence from the text

        :param text: input text containing potential terminal control sequences
        :return: cleaned text without formatting codes
        """
        CSI = '\033['  # this is start of the ASCII escape sequences
        start = 0

        while start >= 0:
            pos = text.find(CSI, start)  # nex loc of the CSI
            end = text.find('m', pos) + 1  # CSI ends with 'm'
            esc = text[pos:end]  # whole escape sequence, e.g. '\033[30m' for BACK
            text = text.replace(esc, '')
            start = pos

        return text

    def _sanitize_xml_text(self, text: str) -> str:
        """
        Replaces invalid XML characters with the '?'

        :param text: text to clean up
        :return: cleaned text
        """
        illegal_characters = [
            (0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F), (0x7F, 0x84), (0x86, 0x9F), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
            (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF),
            (0x6FFFE, 0x6FFFF), (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF),
            (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF), (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
            (0x10FFFE, 0x10FFFF)
        ]

        illegal_ranges = [fr'{chr(low)}-{chr(high)}' for (low, high) in illegal_characters]
        xml_illegal_character_regex = '[' + ''.join(illegal_ranges) + ']'
        text = re.sub(xml_illegal_character_regex, '?', text)
        return text

    def print(self, env_info: Dict, user_data: Dict[str, Any], result: Dict, summary: Summary) -> str:
        """
        Prints test result to JUnit XML.

        :param env_info: environment info dictionary
        :param user_data: user data dictionary
        :param result: test result from the test run
        :param summary: BRunhilda test result summary
        :return: JUnit XML string
        """
        result = copy.deepcopy(result)

        for case in sorted(result['testcases'].values(), key=lambda item: item['id']):
            for test in case['tests']:
                if 'output' in test:
                    test['output'] = self._format_terminal(test['output'])
                    test['output'] = self._sanitize_xml_text(test['output'])
                if 'errors' in test:
                    test['errors'] = [self._format_terminal(err) for err in test['errors']]
                    test['errors'] = [self._sanitize_xml_text(err) for err in test['errors']]

        template = self.load_template('template.junit.jinja2')
        rendered = template.render(env_info=env_info, user_data=user_data, result=result, summary=summary)
        return rendered
