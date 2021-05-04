import io
import os
import re
import sys
import time
import base64
import socket
import pprint
import datetime
import platform
import colorama
import unittest

__unittest = True

PASSED = 'PASSED'
FAILED = 'FAILED'
ERRORED = 'ERRORED'
SKIPPED = 'SKIPPED'
EXPECTED_FAILURE = 'EXPECTED FAILURE'
UNEXPECTED_SUCCESS = 'UNEXPECTED SUCCESS'
EMPTY = 'EMPTY'    # for test case without test


class CatchedStream():
    """
    Adds additional shared buffer stream to the given stream allowing
    to catch all stream outputs in the chronological order.
    """

    def __init__(self, stream, buffer):
        """
        :param stream: stream to catch
        :param buffer: instance of the buffer stream
        """
        self._buffer = buffer
        self.stream = stream

    def __getattr__(self, attr):
        """
        Allowes to act transparently as a stream substitution.
        """
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream, attr)

    def write(self, arg):
        """
        All stream writes are also written to the shared buffer.
        """
        self._buffer.write(arg)
        return self.stream.write(arg)

    def writeln(self, arg=None):
        """
        Original test runner uses custom decorator with `writeln` method,
        we have to implemented as well to keep compatible interface.
        """
        if arg:
            self._buffer.write(arg)
        self._buffer.write('\n')

        try:
            return self.stream.writeln(arg)
        except Exception:
            pass


class BRunhildaTestResult(unittest.runner.TextTestResult):
    """
    Test result class produced by the BRunhilda test runner.
    """
    _renderers = None

    def __init__(self, stream, descriptions, verbosity, name="", user_data=None):
        super().__init__(stream, descriptions, verbosity)
        self.name = name
        self.user_data = user_data
        self.env_info = {
            'pyversion': sys.version,
            'system': platform.platform(),
            'hostname': socket.gethostname(),
            'name': self.name,
        }
        self.stream_buffer = io.StringIO()
        self.stream = CatchedStream(stream, self.stream_buffer)
        self._clean()

    def _clean(self):
        self._stdout_backup = None
        self._stderr_backup = None
        self.total_execution_time = 0   # time to execute all tests
        self.suite_execution_time = 0   # time to execute tests in current test case class
        self.num_suites = 0
        self.num_tests = 0
        self.num_success = 0
        self.num_skipped = 0
        self.num_failed = 0
        self.num_errored = 0
        self.trace_matrix = []
        self.requirements = set()
        self.results = {
            'total': {},
            'testcases': {},
        }

    @classmethod
    def _render_img(cls, img, fmt="jpg", height=612):
        """
        Tries to create renderers for OpenCV, PIL and PyPlot images.
        """
        if not cls._renderers:
            cls._renderers = []
            # Try to create OpenCV image renderer
            try:
                import cv2
                import numpy

                def render_opencv(img, fmt="jpg"):
                    if not isinstance(img, numpy.ndarray):
                        return None

                    if img.shape[0] > height:
                        width = int(img.shape[1] * (height / img.shape[0]))
                        img = cv2.resize(img.copy(), (width, height), interpolation=cv2.INTER_CUBIC)

                    # Remove alpha channel if present and target output is jpeg
                    if len(img.shape) == 3 and img.shape[2] == 4 and fmt in ("jpeg", "jpg"):
                        img = img[:, :, :3]

                    retval, buf = cv2.imencode(f".{fmt}", img)

                    if not retval:
                        return None

                    return buf, f"image/{fmt}"

                cls._renderers.append(render_opencv)
            except ImportError:
                pass

            # Try to create PIL image renderer
            try:
                from io import BytesIO
                from PIL import Image

                def render_pil(img, fmt="jpg"):
                    if not callable(getattr(img, "save", None)):
                        return None

                    output = BytesIO()
                    width, height = img.size

                    if height > height:
                        width = int(width * (height / height))
                        img = img.resize((width, height))

                    # if format is jpeg, convert to RGB to remove transparency
                    if fmt in ("jpeg", "jpg"):
                        img = img.convert('RGB')

                    # PIL needs JPEG, JPG is not enough
                    if fmt == "jpg":
                        fmt = "jpeg"

                    img.save(output, format=fmt)
                    contents = output.getvalue()
                    output.close()

                    return contents, f"image/{fmt}"

                cls._renderers.append(render_pil)
            except ImportError:
                pass

            # Try to create PyPlot image renderer
            try:
                from io import BytesIO

                def render_pyplot(img, fmt="png"):
                    if not callable(getattr(img, "savefig", None)):
                        return None

                    output = BytesIO()
                    img.savefig(output, format=fmt)
                    contents = output.getvalue()
                    output.close()

                    return contents, f"image/{fmt}"

                cls._renderers.append(render_pyplot)
            except ImportError:
                pass

        # Trying renderers one by one
        for renderer in cls._renderers:
            res = renderer(img, fmt)
            if res is not None:
                return res

    @property
    def result(self):
        """
        Returns result of the whole test run.
        """
        if self.num_errored > 0:
            return ERRORED
        elif self.num_failed > 0:
            return FAILED
        elif self.num_success > 0:
            return PASSED
        elif self.num_skipped > 0:
            return SKIPPED
        elif self.expectedFailures > 0:
            return EXPECTED_FAILURE
        else:
            return EMPTY

    def startTestRun(self):
        self._clean()
        self.last_result = ''
        self.run_start_timestamp = datetime.datetime.now()
        super().startTestRun()

    def stopTestRun(self):
        super().stopTestRun()
        self.run_finish_timestamp = datetime.datetime.now()
        self.env_info['timestamp_start'] = self.run_start_timestamp
        self.env_info['timestamp_finish'] = self.run_finish_timestamp

        self.results['total'] = {
            'tests': self.num_tests,
            'timestamp': datetime.datetime.now(),
            'time': self.total_execution_time,
            'passed': self.num_success,
            'skipped':  self.num_skipped,
            'failed': self.num_failed,
            'errored': self.num_errored,
            'expected_failures': len(self.expectedFailures),
            'unexpected_successes': len(self.unexpectedSuccesses),
            'result': self.result,
            'requirements': len([req for req in self.requirements if req != '-'])
        }

    def startTest(self, test):
        """
        This method is called before execution of the given test.
        """
        testcase_name = test.__class__.__name__
        # Check if the test case class name was already here,
        # if not we are starting execution of the new test case class.
        if testcase_name not in self.results['testcases']:
            self.results['testcases'][testcase_name] = {
                'timestamp': datetime.datetime.now(),
                'time': 0,
                'name': testcase_name,
                'description': self._parseDescription(test.__class__.__doc__),
                'id': self.num_suites,
                'tests': [],
                'passed': 0,
                'skipped': 0,
                'failed': 0,
                'errored': 0,
                'expected_failures': 0,
                'unexpected_successes': 0,
                'result': EMPTY
            }
            self.num_suites += 1
            self.suite_execution_time = 0

        self.test_start_time = time.perf_counter()
        self.errors_strings = []
        self.subtests = []
        self.skip_reason = ''
        self.last_result = PASSED
        # Hold reference to the stdout and stderr streams,
        # it has to be done now since super method can change
        # theses for buffering
        self._stdout_backup = sys.stdout
        self._stderr_backup = sys.stderr
        self.stream_buffer = io.StringIO()
        sys.stderr = CatchedStream(sys.stderr, self.stream_buffer)
        sys.stdout = CatchedStream(sys.stdout, self.stream_buffer)
        self.stream._buffer = self.stream_buffer
        test.extra = []
        super().startTest(test)

    def stopTest(self, test):
        """
        This method is called after execution of the given test
        """
        testcase_name = test.__class__.__name__
        self.test_execution_time = time.perf_counter() - self.test_start_time
        self.suite_execution_time += self.test_execution_time
        self.total_execution_time += self.test_execution_time
        self.num_tests += 1

        super().stopTest(test)

        self.stream_buffer.seek(0)
        # and restore original streams
        sys.stdout = self._stdout_backup
        sys.stderr = self._stderr_backup

        if self.last_result == PASSED:
            self.results['testcases'][testcase_name]['passed'] += 1
        elif self.last_result == SKIPPED:
            self.results['testcases'][testcase_name]['skipped'] += 1
        elif self.last_result == FAILED:
            self.results['testcases'][testcase_name]['failed'] += 1
        elif self.last_result == ERRORED:
            self.results['testcases'][testcase_name]['errored'] += 1
        elif self.last_result == EXPECTED_FAILURE:
            self.results['testcases'][testcase_name]['expected_failures'] += 1
        elif self.last_result == UNEXPECTED_SUCCESS:
            self.results['testcases'][testcase_name]['unexpected_successes'] += 1

        # over all test case result
        if self.results['testcases'][testcase_name]['errored'] != 0:
            self.results['testcases'][testcase_name]['result'] = ERRORED
        elif self.results['testcases'][testcase_name]['failed'] != 0:
            self.results['testcases'][testcase_name]['result'] = FAILED
        elif self.results['testcases'][testcase_name]['passed'] != 0:
            self.results['testcases'][testcase_name]['result'] = PASSED

        extra = None

        for ex in test.extra:
            if extra is None:
                extra = []

            img = self._render_img(ex)

            if isinstance(ex, str):
                extra.append({'type': 'text', 'value': ex})
            elif img is not None:
                extra.append({'type': img[1], 'value': base64.b64encode(img[0]).decode()})
            else:
                extra.append({'type': 'text', 'value': pprint.pformat(ex, indent=2, width=120)})

        self.results['testcases'][testcase_name]['time'] = self.suite_execution_time
        self.results['testcases'][testcase_name]['tests'].append({
            'subtests': self.subtests,
            'skip_reason': self.skip_reason,
            'id': self.num_tests,
            'name': test._testMethodName,
            'time': self.test_execution_time,
            'description': self._parseDescription(test._testMethodDoc),
            'result': self.last_result,
            'output': self.stream_buffer.read(),
            'errors': self.errors_strings,
            'extra': extra
        })

        if self.last_result == PASSED:
            self.num_success += 1
        elif self.last_result == FAILED:
            self.num_failed += 1
        elif self.last_result == ERRORED:
            self.num_errored += 1

        self.addToTrace(testcase_name, test._testMethodName, test._testMethodDoc, self.last_result)

    def addSuccess(self, test):
        """
        This method is called after successfull end of the test method.
        """
        super().addSuccess(test)

    def addError(self, test, err):
        """
        This method is called when error occurs.
        """
        super().addError(test, err)

        if err is not None:
            for ex in err[1].args:
                img = self._render_img(ex)
                if img is not None:
                    test.extra.append(ex)

        self.errors_strings.append(self._exc_info_to_string(err, test))
        self.last_result = ERRORED

    def addFailure(self, test, err):
        """
        This method is called upon assertion failure.
        """
        super().addFailure(test, err)

        if err is not None:
            for ex in err[1].args:
                img = self._render_img(ex)
                if img is not None:
                    test.extra.append(ex)

        self.errors_strings.append(self._exc_info_to_string(err, test))
        self.last_result = FAILED

    def addSubTest(self, test, subtest, err):
        """
        This method is called after sub-test is done.
        """
        extra = None

        if err is not None:
            for ex in err[1].args:
                if extra is None:
                    extra = []

                img = self._render_img(ex)

                if isinstance(ex, str):
                    extra.append({'type': 'text', 'value': ex})
                elif img is not None:
                    extra.append({'type': img[1], 'value': base64.b64encode(img[0]).decode()})
                else:
                    extra.append({'type': 'text', 'value': pprint.pformat(ex, indent=2, width=120)})

        self.subtests.append({
            'id': 1+len(self.subtests),
            'name': str(dict(subtest.params)),
            'result': PASSED,
            'extra': extra
        })

        # `err` contains info about errors and failures, if `None`, sub-test passed
        if err is not None:
            err_str = self._exc_info_to_string(err, test)
            self.subtests[-1]['error'] = err_str
            # Append error to list of errors, first line is the subtest name with black background.
            self.errors_strings.append(f'{colorama.Back.BLACK}{subtest}{colorama.Back.RESET}\n{err_str}')

            # Subtest errored if the exception is not a failure or derived exception
            if not issubclass(err[0], test.failureException):
                self.subtests[-1]['result'] = ERRORED
                self.last_result = ERRORED
            else:
                self.subtests[-1]['result'] = FAILED
                # We want to keep overall test result ERRORED if already set, ERRORED means that test is not working.
                if self.last_result != ERRORED:
                    self.last_result = FAILED

        super().addSubTest(test, subtest, err)

    def addSkip(self, test, reason):
        """
        This method is called after skip of the test.
        """
        super().addSkip(test, reason)
        # When sub test is skipped, this method is called as well, so only way how to
        # detect skipped sub tests is to check the test class.
        if isinstance(test, unittest.case._SubTest):
            self.subtests.append({
                'id': 1+len(self.subtests),
                'name': str(dict(test.params)),
                'result': SKIPPED,
                'reason': reason
            })
        else:
            self.num_skipped += 1
            self.last_result = SKIPPED
            self.skip_reason = reason

    def addExpectedFailure(self, test, err):
        """
        This method is called when test marked with @expectedFailure decorator fails.
        """
        super().addExpectedFailure(test, err)
        self.errors_strings.append(self._exc_info_to_string(err, test))
        self.last_result = EXPECTED_FAILURE

    def addUnexpectedSuccess(self, test):
        """
        This method is called when test marked with @expectedFailure decorator succeeds.
        """
        super().addUnexpectedSuccess(test)
        self.last_result = UNEXPECTED_SUCCESS

    def _parseReferences(self, description):
        """
        Extracts references from the test description.

        :param str description: test description (docstring)
        """
        refs = None

        if description and isinstance(description, str):
            for line in description.splitlines():
                refs = re.search(r'@ref[:\s]\s*\w.+', line.strip())

                if refs:
                    break

        if refs is not None:
            refs = re.sub(r'@ref[:\s]s*', '', refs.group(0))
            refs = [' '.join(ref.split()) for ref in refs.split(',')]
        else:
            refs = ['-']

        return refs

    def _parseRequirements(self, description):
        """
        Extracts requirements from the test description.

        :param str description: test description (docstring)
        """
        specs = None

        if description and isinstance(description, str):
            for line in description.splitlines():
                specs = re.search(r'@spec[:\s]\s*\w.+', line.strip())

                if specs:
                    break

        if specs is not None:
            specs = re.sub(r'@spec[:\s]s*', '', specs.group(0))
            specs = [' '.join(spec.split()) for spec in specs.split(',')]
        else:
            specs = ['-']

        return specs

    def _parseDescription(self, description):
        """
        Extracts test description without tags from the docstring.

        :param str description: test description (docstring)
        """
        lines = []

        if description and isinstance(description, str):
            for line in description.splitlines():
                if not line.strip().startswith('@'):
                    lines.append(line)

        return '\n'.join(lines)

    def addToTrace(self, testcase_name, test_name, description, result):
        """
        Adds executed test to the trace record

        :param str testcase_name: name of the test case class
        :param str test_name: name of the test method
        :param description: test docstring
        :param result: result of the test execution
        """
        references = self._parseReferences(description)
        requirements = self._parseRequirements(description)
        test_id = f'{testcase_name} {test_name}'

        self.requirements.update(requirements)
        self.trace_matrix.append({'case': testcase_name,
                                  'test': test_name,
                                  'result': result,
                                  'references': references,
                                  'requirements': requirements,
                                  'test_id': test_id})

    def _writeFile(self, filename, content):
        """
        Writes content to the given filename

        :param filename: name of the file
        :param content: content of the file
        """
        dir_name = os.path.dirname(os.path.abspath(filename))

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        with open(filename, 'w', encoding="utf-8") as f:
            f.write(content)

    def print(self, output_formater, path):
        """
        Prints test results with the given result output.
        """
        if path is not None:
            output = output_formater.print(self.env_info, self.user_data, self.results)
            self._writeFile(path, output)
            print(f"... created report {path}")

    def printTraceability(self, output_formater, path):
        """
        Prints test traceability report in a matrix form.

        :param output_formater: format to process the data
        :param path: where to store the output file
        """
        if path is not None:
            refs = []

            for test in self.trace_matrix:
                refs += test['references']

            refs = list(set(refs))
            refs.sort()

            for test in self.trace_matrix:
                test['ref_indexes'] = []

                for test_ref in test['references']:
                    test['ref_indexes'].append(refs.index(test_ref))

            output = output_formater.print(refs, self.trace_matrix)
            self._writeFile(path, output)
            print(f"... created traceability matrix {path}")

    def printTestSummary(self, output_formater, path):
        """
        Prints test summary report.

        :param output_formater: format to process the data
        :param path: where to store the output file
        """
        if path is not None:
            output = output_formater.print(self.env_info, self.user_data, self.trace_matrix,
                                           self.results['total'])
            self._writeFile(path, output)
            print(f"... created test summary {path}")

    def printRequirementsSummary(self, output_formater, path):
        """
        Prints requirements summary report.

        :param output_formater: format to process the data
        :param path: where to store the output file
        """
        if path is not None:
            output = output_formater.print(self.env_info, self.user_data, self.trace_matrix)
            self._writeFile(path, output)
            print(f"... created test summary {path}")