import io
import os
import sys
import time
import yaml
import simplejson as json
import base64
import socket
import pprint
import datetime
import platform
import colorama
import unittest
from io import BytesIO
from PIL import Image

from copy import deepcopy
from typing import List

from .rel_path import rel_path
from .data import (Summary, Result)
from .parser import (parse_tags, parse_description, parse_requirements, parse_steps)

__unittest = True


PASSED = 'PASSED'
FAILED = 'FAILED'
ERRORED = 'ERRORED'
SKIPPED = 'SKIPPED'
JUSTIFIED = 'JUSTIFIED'
EXPECTED_FAILURE = 'EXPECTED-FAILURE'
UNEXPECTED_SUCCESS = 'UNEXPECTED-SUCCESS'
EMPTY = 'EMPTY'    # for test case without test


def yaml_str_presenter(dumper, text):
    """Custom string presenter to dump multiline strings nicely"""
    try:
        if len(text.splitlines()) > 1:
            return dumper.represent_scalar('tag:yaml.org,2002:str', text, style='|')
    except TypeError:
        return dumper.represent_scalar('tag:yaml.org,2002:str', text)

    return dumper.represent_scalar('tag:yaml.org,2002:str', text)


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
            if hasattr(self.stream, 'writeln'):
                self.stream.writeln(arg)
            else:
                self.stream.write(arg)
                self.stream.write('\n')
        except Exception:
            pass


class BRunhildaTestResult(unittest.runner.TextTestResult):
    """
    Test result class produced by the BRunhilda test runner.
    """
    _renderers = None
    EMBEDDED_IMAGES = False     #: controls embeding images as base64

    def __init__(self,
                 stream,
                 descriptions,
                 verbosity,
                 name='',
                 dut='',
                 extra_data_path='./extra',
                 user_data=None):
        super().__init__(stream, descriptions, verbosity)
        self.errors_strings = []
        self.stream_buffer = io.StringIO()
        self.stream = CatchedStream(stream, self.stream_buffer)
        self._tests = []
        self._issues = {}
        self._requirements = set()
        self.extra_data_path = extra_data_path
        self.last_result: Result = EMPTY
        self.name = name
        self.dut = dut
        self.user_data = user_data
        self.summary = Summary()
        self.env_info = {
            'pyversion': sys.version,
            'system': platform.platform(),
            'hostname': socket.gethostname(),
            'name': self.name,
        }
        self._clean()

    def _clean(self):
        self._stdout_backup = None
        self._stderr_backup = None
        self.total_execution_time = 0   # time to execute all tests
        self.suite_execution_time = 0   # time to execute tests in current test case class
        self.num_suites = 0
        self.num_tests = 0
        self.results = {
            'total': {},
            'testcases': {},
        }
        self._requirements.clear()
        self._tests.clear()
        self._issues = {'errors': [], 'failures': [], 'run': {}}
        self.summary = Summary()
        self.last_result = EMPTY
        self.run_start_timestamp = datetime.datetime.now()

    def _process_test_extra(self, test, test_id: str) -> None:
        """
        Process extra data of the given subtest and replaces it with the processed one.

        This is usefull when the extra data are images.

        :param test: test to be process
        :param test_id: id of the test
        """
        try:
            extra = self._process_extra_data(test.extra, test_id)
            del test.extra
            test.extra = extra
        except Exception:
            test.extra = []

    def _process_extra_data(self, extra: List, test_id: str) -> List:
        """
        Goes through the extra data list, renderers images to base64 or stores them to the filesystem.

        :param extra: extra data list
        :param test_id: ID of the current test
        :return: processed extra data
        """
        processed_extras = []

        for i, ex in enumerate(extra):
            img = self._render_img(ex)

            if isinstance(ex, str):
                processed_extras.append({'type': 'text', 'value': ex})
            elif img is not None:
                if self.EMBEDDED_IMAGES:
                    processed_extras.append({'type': img[1], 'value': base64.b64encode(img[0]).decode()})
                else:
                    path = self._store_img(test_id, img[0])
                    path = path.replace('\\', '/')
                    processed_extras.append({'type': 'image-reference', 'value': path})
            else:
                processed_extras.append({'type': 'text', 'value': pprint.pformat(ex, indent=2, width=120)})

        return processed_extras

    def _get_test_id(self, test):
        """
        Gets test ID in the unified format
        """
        test_id = test.id()
        return '.'.join(chunk for chunk in test_id.split('.') if chunk != test.__module__)

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

        return None

    def _store_img(self, filename, image):
        """
        Stores image into extra data folder as an jpeg file

        :param filename: name of the file
        :param image: image bytes
        """
        invalid_path_characters = ("'", '"', '/', '\\', '?', '<', '>', ':', '|', '*')

        try:
            if not os.path.exists(self.extra_data_path):
                os.makedirs(self.extra_data_path)

            for char in invalid_path_characters:
                filename = filename.replace(char, '')

            filename = filename[:120]   # limit to 120 characters
            num = 0
            save_path = None

            while (save_path is None) or os.path.isfile(save_path):
                num += 1
                save_path = os.path.join(self.extra_data_path, f'{filename}-{num:03}.jpg')

            im = Image.open(BytesIO(image))
            im.save(save_path, format='jpeg')
        except Exception:
            save_path = ''
        finally:
            return save_path

    @property
    def result(self):
        """
        Returns result of the whole test run.
        """
        return self.summary.result

    def startTestRun(self):
        self._clean()
        super().startTestRun()

    def stopTestRun(self):
        super().stopTestRun()
        self.run_finish_timestamp = datetime.datetime.now()
        self.env_info['timestamp_start'] = self.run_start_timestamp
        self.env_info['timestamp_finish'] = self.run_finish_timestamp
        self.env_info['execution_time'] = self.total_execution_time

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
                'description': parse_description(test.__class__.__doc__),
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
        test.steps = []
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

        test_id = self._get_test_id(test)
        self._process_test_extra(test, test_id)

        self.results['testcases'][testcase_name]['time'] = self.suite_execution_time
        self.results['testcases'][testcase_name]['tests'].append({
            'subtests': self.subtests,
            'skip_reason': self.skip_reason,
            'id': test_id,
            'name': test._testMethodName,
            'time': self.test_execution_time,
            'description': parse_description(test._testMethodDoc),
            'steps': parse_steps(test.steps, test._testMethodDoc),
            'tags': parse_tags(test._testMethodDoc),
            'result': self.last_result,
            'output': self.stream_buffer.read(),
            'errors': self.errors_strings,
            'extra': test.extra
        })

        self.summary.results += self.last_result

        self._record(testcase_name, test_id, test.steps, test._testMethodDoc,
                     self.last_result, self.skip_reason, self.subtests)

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

        try:
            if err is not None:
                for ex in err[1].args:
                    img = self._render_img(ex)

                    if img is not None:
                        test.extra.append(ex)

            test_id = self._get_test_id(test)
            self._process_test_extra(test, test_id)

            self._issues['errors'].append({
                'test': test_id,
                'sub-test': None,
                'result': ERRORED,
                'message': self._exc_info_to_string(err, test),
                'extra': test.extra,
                'bug-id': '',
                'comment': '',
                'justified': '',
                'tags': parse_tags(test._testMethodDoc)
            })
        except AttributeError:
            pass
        finally:
            self.errors_strings.append(self._exc_info_to_string(err, test))
            self.last_result = ERRORED

    def addFailure(self, test, err):
        """
        This method is called upon assertion failure.
        """
        super().addFailure(test, err)

        if err is not None:
            for ex in err[1].args:
                test.extra.append(ex)

        test_id = self._get_test_id(test)
        self._process_test_extra(test, test_id)

        self._issues['failures'].append({
            'test': test_id,
            'sub-test': None,
            'result': FAILED,
            'message': self._exc_info_to_string(err, test),
            'extra': test.extra,
            'bug-id': '',
            'comment': '',
            'justified': '',
            'tags': parse_tags(test._testMethodDoc)
        })
        self.errors_strings.append(self._exc_info_to_string(err, test))
        self.last_result = FAILED

    def addSubTest(self, test, subtest, err):
        """
        This method is called after sub-test is done.
        """
        if not hasattr(subtest, 'extra'):
            subtest.extra = []

        if err is not None:
            subtest.extra += list(err[1].args)

        test_id = self._get_test_id(test)
        subtest_id = subtest.id().lstrip(test.__module__ + '.')
        self._process_test_extra(subtest, subtest_id)

        self.subtests.append({
            'num': 1+len(self.subtests),
            'id': subtest_id,
            'name': str(dict(subtest.params)),
            'result': PASSED,
            'extra': subtest.extra,
            'parameters': dict(subtest.params),
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

            issue = {
                'test': test_id,
                'sub-test': subtest_id,
                'message': err_str,
                'extra': subtest.extra,
                'result': self.last_result,
                'bug-id': '',
                'comment': '',
                'justified': '',
                'tags': parse_tags(test._testMethodDoc)
            }

            self._issues['errors' if self.last_result == ERRORED else 'failures'].append(issue)

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
                'reason': reason,
                'parameters': dict(test.params),
            })
        else:
            self.skip_reason = reason
            self.last_result = SKIPPED

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

    def _record(self, testcase_name, test_id, test_steps, description, result, comment='', subtests=[]):
        """
        Adds executed test to the trace record

        :param str testcase_name: name of the test case class
        :param str test_name: name of the test method
        :param description: test docstring
        :param result: result of the test execution
        :param subtests: all subtests of this test
        """
        requirements = parse_requirements(description)
        tags = parse_tags(description)
        steps = parse_steps(test_steps, description)
        description = parse_description(description)

        self._requirements.update(requirements)
        self._tests.append({'case': testcase_name,
                            'result': result,
                            'tags': tags,
                            'description': description,
                            'steps': steps,
                            'requirements': requirements,
                            'test_id': test_id,
                            'comment': comment,
                            'level': self.name,
                            'subtests': deepcopy(subtests),})

    def _write_file(self, filename, content):
        """
        Writes content to the given filename

        :param filename: name of the file
        :param content: content of the file
        """
        dir_name = os.path.dirname(os.path.abspath(filename))

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(filename, 'w', encoding="utf-8") as f:
            f.write(content)

        print(f"... created output {filename}")

    def _serialize(self, content, filename):
        """
        Serializes given content into yaml/json file
        """
        if filename.lower().endswith(('yaml', 'yml')):
            yaml.add_representer(str, yaml_str_presenter)
            serialized = yaml.dump(content)
        elif filename.lower().endswith(('json')):
            serialized = json.dumps(content, default=str, sort_keys=True, indent=4)
        else:
            raise ValueError(f'Invalid filename {filename}, only JSON and YAML files are supported.')

        self._write_file(filename, serialized)

    def _issues_relative_to(self, base_path):
        """
        Modifies paths in the issues to be relative to the given filename

        :param base_path: new path to be used as a base path
        """
        issues = deepcopy(self._issues)

        for issue in issues['errors'] + issues['failures']:
            for extra in issue['extra']:
                if extra['type'] == 'image-reference':
                    extra['value'] = rel_path(base_path, extra['value'])

        return issues

    def serialize_issues(self, filename: str):
        """
        Serializes test result into yaml/json file

        :param filename: filename to put the serialized form into
        """
        self._issues['run'] = {
            'user data': self.user_data,
            'date-time': self.run_start_timestamp,
            'level': self.name,
            'dut': self.dut
        }

        issues = self._issues_relative_to(filename)
        self._serialize(issues, filename)

    def serialize_tests(self, filename: str):
        """
        Serializes executed tests

        :param filename: filename to put the serialized form into
        """
        self._serialize(self._tests, filename)

    def print(self, output_formater, filename):
        """
        Prints test results with the given result output.
        """
        if filename is not None:
            output_formater.path = filename
            output = output_formater.print(self.env_info, self.user_data, self.results, self.summary)
            self._write_file(filename, output)
