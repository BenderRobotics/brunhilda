import sys
import unittest

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
                       html_output="report.html",
                       junit_output="report.xml",
                       user_data=None):
        super().__init__(stream=stream,
                         descriptions=descriptions,
                         verbosity=verbosity,
                         failfast=failfast,
                         buffer=buffer,
                         warnings=warnings)
        self.name = name
        self.user_data = user_data
        self.html_output = html_output
        self.junit_output = junit_output

    def _makeResult(self):
        return BRunhildaTestResult(self.stream, self.descriptions, self.verbosity, self.name, user_data=self.user_data)

    def run(self, test):
        result = super().run(test)

        if hasattr(result, "print"):
            result.print(HtmlResultOutput(), self.html_output)
            result.print(JUnitResultOutput(), self.junit_output)

        return result
