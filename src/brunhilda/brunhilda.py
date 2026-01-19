import sys
import unittest
from pathlib import Path
from typing import Dict, Union
from unittest import TextTestResult
from unittest.case import TestCase
from unittest.suite import TestSuite

from .loader import iter_suite
from .outputs.html_result_output import HtmlResultOutput
from .outputs.junit_result_output import JUnitResultOutput
from .result import NOT_EXECUTED, BRunhildaTestResult

__unittest = True


class BRunhilda(unittest.TextTestRunner):
    """
    A test runner class that displays results in textual form.
    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """

    def __init__(
        self,
        stream=sys.stderr,
        descriptions=True,
        verbosity=1,
        failfast=False,
        buffer=False,
        warnings=None,
        name='',
        dut='',
        extra_data_output='extra',
        user_data=None
    ):
        super().__init__(
            stream=stream,
            descriptions=descriptions,
            verbosity=verbosity,
            failfast=failfast,
            buffer=buffer,
            warnings=warnings
        )
        self._name = name
        self._dut = dut
        self._user_data = user_data
        self._extra_data_output = extra_data_output

    @property
    def name(self) -> str:
        return self._name

    @property
    def dut(self) -> str:
        return self._dut

    @property
    def user_data(self) -> Dict[str, str]:
        return self._user_data

    @property
    def extra_data_output(self) -> str:
        return self._extra_data_output

    def run(self, test: Union[TestSuite, TestCase]) -> BRunhildaTestResult:
        """
        Run the given test case or test suite.

        :param test: test suite or case to be run
        :return: test result
        """
        return super().run(test)  # type: ignore

    def dryrun(self, suite: TestSuite) -> BRunhildaTestResult:
        """
        Executes a dry run of the test suite. Creates the same artifacts as a normal run but without
        actually executing the tests.

        :param suite: test suite
        :return: test result
        """
        result = self._makeResult()
        result.startTestRun()

        for test in iter_suite(suite):
            result.startTest(test)
            result._last_result = NOT_EXECUTED  # override since we do not execute the test
            result.stopTest(test)

        result.stopTestRun()
        return result

    def _makeResult(self) -> BRunhildaTestResult:
        """
        Overridden method for creating test result.

        :return: formated test result
        """
        return BRunhildaTestResult(
            self.stream,
            self.descriptions,
            self.verbosity,
            self._name,
            self._dut,
            extra_data_path=self._extra_data_output,
            user_data=self._user_data
        )

    def save_html_report(self, result: BRunhildaTestResult, output_path: Union[str, Path]):
        """
        Prints the HTML report of the result.

        :param result: result whose report will be printed
        :param output_path: printed report path
        """
        try:
            result.print(HtmlResultOutput(), str(output_path))
        except Exception as ex:
            print(ex)

    def save_junit_report(self, result: BRunhildaTestResult, output_path: Union[str, Path]):
        """
        Prints the jUnit report of the result.

        :param result: result whose report will be printed
        :param output_path: printed report path
        """
        try:
            result.print(JUnitResultOutput(), str(output_path))
        except Exception as ex:
            print(ex)

    def save_issues(self, result: BRunhildaTestResult, output_path: Union[str, Path]):
        """
        Serializes issues from the result.

        :param result: result whose report will be printed
        :param output_path: printed file path
        """
        try:
            result.serialize_issues(str(output_path))
        except Exception as ex:
            print(ex)

    def save_tests(self, result: BRunhildaTestResult, output_path: Union[str, Path]):
        """
        Serializes executed tests from the result.

        :param result: result whose report will be printed
        :param output_path: printed file path
        """
        try:
            result.serialize_tests(str(output_path))
        except Exception as ex:
            print(ex)
