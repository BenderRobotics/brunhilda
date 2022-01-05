import sys
import unittest

from typing import cast
from unittest.suite import TestSuite

from .result import BRunhildaTestResult
from .html_result_output import HtmlResultOutput
from .junit_result_output import JUnitResultOutput

__unittest = True


class BRunhilda(unittest.TextTestRunner):
    """
    A test runner class that displays results in textual form.
    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """

    def __init__(self, stream=sys.stderr,
                       descriptions=True,
                       verbosity=1,
                       failfast=False,
                       buffer=False,
                       warnings=None,
                       name="",
                       dut="",
                       extra_data_output="extra",
                       user_data=None):
        super().__init__(stream=stream,
                         descriptions=descriptions,
                         verbosity=verbosity,
                         failfast=failfast,
                         buffer=buffer,
                         warnings=warnings)
        self.name = name
        self.dut = dut
        self.user_data = user_data
        self.extra_data_output = extra_data_output

    def _makeResult(self):
        return BRunhildaTestResult(self.stream,
                                   self.descriptions,
                                   self.verbosity,
                                   self.name,
                                   self.dut,
                                   extra_data_path=self.extra_data_output,
                                   user_data=self.user_data)

    def save_html_report(self, result, output_path):
        """
        Prints the HTML report of the last result
        """
        try:
            result.print(HtmlResultOutput(), output_path)
        except Exception as ex:
            print(ex)

    def save_junit_report(self, result, output_path):
        """
        Prints the jUnit report of the last result
        """
        try:
            result.print(JUnitResultOutput(), output_path)
        except Exception as ex:
            print(ex)

    def save_issues(self, result, output_path):
        """
        Serializes issues from the last result.
        """
        try:
            result.serialize_issues(output_path)
        except Exception as ex:
            print(ex)

    def save_tests(self, result, output_path):
        """
        Serializes executed tests from the last result.
        """
        try:
            result.serialize_tests(output_path)
        except Exception as ex:
            print(ex)