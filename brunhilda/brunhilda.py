import os
import sys
import unittest

from .result import BRunhildaTestResult
from .html_result_output import HtmlResultOutput
from .junit_result_output import JUnitResultOutput
from .html_trace_output import HtmlTraceOutput
from .html_test_summary_output import HtmlTestSummaryOutput
from .html_req_summary_output import HtmlReqSummaryOutput
from .html_test_plan_output import HtmlTestPlanOutput
from .html_index_output import HtmlIndexOutput

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
                       html_preamble=None,
                       html_output="report.html",
                       junit_output="report.xml",
                       traceability_output="traceability.html",
                       req_summary_preamble=None,
                       req_summary_output="req-summary.html",
                       test_summary_preamble=None,
                       test_summary_output="test-summary.html",
                       test_plan_preamble=None,
                       test_plan_output="test-plan.html",
                       user_data=None,
                       requirements_list=[],
                       tag_filter={}):
        super().__init__(stream=stream,
                         descriptions=descriptions,
                         verbosity=verbosity,
                         failfast=failfast,
                         buffer=buffer,
                         warnings=warnings)
        self.name = name
        self.user_data = user_data
        self.html_preamble = html_preamble
        self.html_output = html_output
        self.junit_output = junit_output
        self.traceability_output = traceability_output
        self.req_summary_preamble = req_summary_preamble
        self.req_summary_output = req_summary_output
        self.test_summary_preamble = test_summary_preamble
        self.test_summary_output = test_summary_output
        self.test_plan_preamble = test_plan_preamble
        self.test_plan_output = test_plan_output
        self.requirements_list = requirements_list
        self.tag_filter = tag_filter

    def _makeResult(self):
        return BRunhildaTestResult(self.stream,
                                   self.descriptions,
                                   self.verbosity,
                                   self.name,
                                   user_data=self.user_data)

    @classmethod
    def test_iter(cls, suite):
        """
        Iterate through test suites, and yield individual tests
        """
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                for t in cls.test_iter(test):
                    yield t
            else:
                yield test

    def filter_by_tags(self, tags):
        """
        Checks if given tags matches the set tag_filter

        :param dict tags: parsed tags from the description
        :return: True if the tags matching filter, False if not
        """
        if self.tag_filter is not None:
            for tag, value in self.tag_filter.items():
                if (tag not in tags) or ((tag in tags) and (value not in tags[tag])):
                    return False

        return True

    def filter_tests(self, testlist):
        """
        Filters tests based on the _tag_filter

        :param testlist: list of tests
        :return: filtered test suite
        """
        suite = unittest.TestSuite()

        for test in self.test_iter(testlist):
            docstring = getattr(test, test._testMethodName).__doc__
            tags = BRunhildaTestResult.parseTags(docstring)

            if self.filter_by_tags(tags):
                suite.addTest(test)

        return suite

    def run(self, testlist):
        suite = self.filter_tests(testlist)
        result = super().run(suite)

        result.paths = {
            'test_record': os.path.split(self.html_output)[-1],
            'requirements_summary': os.path.split(self.req_summary_output)[-1],
            'test_summary': os.path.split(self.test_summary_output)[-1],
            'test_plan': os.path.split(self.test_plan_output)[-1]
        }

        if self.test_plan_output is not None:
            result.printTestPlan(HtmlTestPlanOutput(preamble=self.test_plan_preamble), self.test_plan_output)

        if hasattr(result, "print"):
            result.print(HtmlResultOutput(preamble=self.html_preamble), self.html_output)
            result.print(JUnitResultOutput(), self.junit_output)

        if self.traceability_output is not None:
            result.printTraceability(HtmlTraceOutput(), self.traceability_output)

        if self.test_summary_output is not None:
            result.printTestSummary(HtmlTestSummaryOutput(preamble=self.test_summary_preamble), self.test_summary_output)

        if self.req_summary_output is not None:
            result.printRequirementsSummary(HtmlReqSummaryOutput(preamble=self.req_summary_preamble),
                                            self.req_summary_output, self.requirements_list)

        index_path = os.path.join(os.path.dirname(self.html_output), 'index.html')
        result.printIndex(HtmlIndexOutput(), index_path)

        return result
