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
                       html_output="report.html",
                       junit_output="report.xml",
                       issues_output="issues.yaml",
                       tests_output="tests.yaml",
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
        self.html_output = html_output
        self.junit_output = junit_output
        self.issues_output = issues_output
        self.tests_output = tests_output
        self.extra_data_output = extra_data_output

    def _makeResult(self):
        return BRunhildaTestResult(self.stream,
                                   self.descriptions,
                                   self.verbosity,
                                   self.name,
                                   self.dut,
                                   extra_data_path=self.extra_data_output,
                                   user_data=self.user_data)

    def run(self, suite: TestSuite):
        """
        Run the given test case or test suite, prints the JUnit and HTML
        reports if requested.
        """
        result = super().run(suite)

        # print reports
        for path, Printer in ((self.html_output, HtmlResultOutput),
                              (self.junit_output, JUnitResultOutput)):
            if path:
                result.print(Printer(), path)

        # serialize for post-processing
        result.serialize_issues(self.issues_output)
        result.serialize_tests(self.tests_output)
        return result
