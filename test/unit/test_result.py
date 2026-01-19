import io
import sys
import unittest
from unittest.mock import MagicMock, patch

import pytest

import brunhilda.result as target_module
from brunhilda.result import BRunhildaTestResult, CatchedStream, yaml_str_presenter


@pytest.fixture
def mock_dependencies(mocker):
    # Mock Summary class
    mock_summary = MagicMock()
    mock_summary.result = 'PASSED'
    mock_summary.results = ''
    mocker.patch.object(target_module, 'Summary', return_value=mock_summary)

    # Functions mock parser
    mocker.patch.object(target_module, 'parse_description', return_value='Parsed Desc')
    mocker.patch.object(target_module, 'parse_requirements', return_value={'REQ-1'})
    mocker.patch.object(target_module, 'parse_steps', return_value=[])
    mocker.patch.object(target_module, 'parse_tags', return_value={'tag': 'val'})
    mocker.patch.object(target_module, 'rel_path', side_effect=lambda b, t: f'rel/{t}')


@pytest.fixture
def result_instance(mock_dependencies):
    stream = io.StringIO()
    BRunhildaTestResult._renderers = None
    runner = BRunhildaTestResult(
        stream=stream, descriptions=True, verbosity=1, name='TestRun', dut='Device1', extra_data_path='/tmp/extra'
    )
    return runner


@pytest.fixture
def dummy_test_case():

    class DummyTest(unittest.TestCase):

        def test_dummy(self):
            """Dummy docstring"""
            pass

    return DummyTest('test_dummy')


# --- Tests yaml_str_presenter ---


def test_yaml_str_presenter():
    dumper = MagicMock()

    yaml_str_presenter(dumper, 'hello')
    dumper.represent_scalar.assert_called_with('tag:yaml.org,2002:str', 'hello')

    yaml_str_presenter(dumper, 'line1\nline2')
    dumper.represent_scalar.assert_called_with('tag:yaml.org,2002:str', 'line1\nline2', style='|')


# --- Test CatchedStream ---


class TestCatchedStream:

    def test_write_dual(self):
        stream = io.StringIO()
        buffer = io.StringIO()
        catched = CatchedStream(stream, buffer)

        catched.write('test')

        assert stream.getvalue() == 'test'
        assert buffer.getvalue() == 'test'

    def test_writeln_dual(self):
        stream = io.StringIO()
        buffer = io.StringIO()
        catched = CatchedStream(stream, buffer)

        catched.writeln('line')

        expected = 'line\n'
        assert stream.getvalue() == expected
        assert buffer.getvalue() == expected

    def test_writeln_empty(self):
        stream = io.StringIO()
        buffer = io.StringIO()
        catched = CatchedStream(stream, buffer)

        catched.writeln()
        assert stream.getvalue() == ''
        assert buffer.getvalue() == '\n'

    def test_getattr(self):
        stream = io.StringIO()
        buffer = io.StringIO()
        catched = CatchedStream(stream, buffer)

        catched.write('abc')
        assert catched.getvalue() == 'abc'

    def test_getattr_forbidden(self):
        stream = io.StringIO()
        buffer = io.StringIO()
        catched = CatchedStream(stream, buffer)

        with pytest.raises(AttributeError):
            _ = catched.__getstate__


# --- Tests BRunhildaTestResult ---


class TestBRunhildaTestResult:

    def test_init(self, result_instance):
        assert result_instance.name == 'TestRun'
        assert result_instance.dut == 'Device1'
        assert result_instance.stream_buffer is not None
        assert isinstance(result_instance.stream, CatchedStream)

    def test_start_stop_test(self, result_instance, dummy_test_case):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result_instance.startTest(dummy_test_case)
            assert isinstance(sys.stdout, CatchedStream)
            assert hasattr(dummy_test_case, 'extra')
            assert hasattr(dummy_test_case, 'steps')

            time_start = result_instance.test_start_time

            result_instance.stopTest(dummy_test_case)
            assert sys.stdout is not isinstance(sys.stdout, CatchedStream)

            case_name = 'DummyTest'
            assert len(result_instance.results['testcases'][case_name]['tests']) == 1
            assert result_instance.num_tests == 1

    def test_add_success(self, result_instance, dummy_test_case):
        result_instance.startTest(dummy_test_case)
        result_instance.addSuccess(dummy_test_case)
        result_instance.stopTest(dummy_test_case)

        stats = result_instance.results['testcases']['DummyTest']
        assert stats['passed'] == 1
        assert stats['result'] == 'PASSED'

    def test_add_failure_with_exception(self, result_instance, dummy_test_case):
        result_instance.startTest(dummy_test_case)

        try:
            assert 1 == 2, 'Error'
        except AssertionError:
            err = sys.exc_info()
            result_instance.addFailure(dummy_test_case, err)

        result_instance.stopTest(dummy_test_case)

        stats = result_instance.results['testcases']['DummyTest']
        assert stats['failed'] == 1
        assert stats['result'] == 'FAILED'

        assert len(result_instance._issues['failures']) == 1
        assert 'AssertionError' in result_instance._issues['failures'][0]['message']

    def test_add_error_with_image(self, result_instance, dummy_test_case, mocker):
        result_instance.startTest(dummy_test_case)

        # Mock _render_img to return fake image for any arg
        mocker.patch.object(result_instance, '_render_img', return_value=(b'fake_img', 'image/png'))

        try:
            # Simulate exception which holds image in args
            raise RuntimeError('ImageError')
        except RuntimeError:
            err = sys.exc_info()
            result_instance.addError(dummy_test_case, err)

        assert len(dummy_test_case.extra) > 0
        assert dummy_test_case.extra[0]['value'] == 'ImageError'

        result_instance.stopTest(dummy_test_case)
        stats = result_instance.results['testcases']['DummyTest']
        assert stats['errored'] == 1

    def test_add_subtest(self, result_instance, dummy_test_case):
        result_instance.startTest(dummy_test_case)

        subtest = unittest.TestCase()
        subtest.params = {'param': 1}
        subtest._testMethodName = 'test_dummy'

        result_instance.addSubTest(dummy_test_case, subtest, None)
        assert len(result_instance.subtests) == 1
        assert result_instance.subtests[0]['result'] == 'PASSED'

        try:
            raise AssertionError('SubFail')
        except AssertionError:
            err = sys.exc_info()
            result_instance.addSubTest(dummy_test_case, subtest, err)

        assert len(result_instance.subtests) == 2
        assert result_instance.subtests[1]['result'] == 'FAILED'
        assert result_instance._last_result == 'FAILED'

        result_instance.stopTest(dummy_test_case)

    def test_add_skip(self, result_instance, dummy_test_case):
        result_instance.startTest(dummy_test_case)
        result_instance.addSkip(dummy_test_case, 'Reason')
        result_instance.stopTest(dummy_test_case)

        stats = result_instance.results['testcases']['DummyTest']
        assert stats['skipped'] == 1
        assert result_instance.skip_reason == 'Reason'

    def test_render_img_pil(self, result_instance):
        # Mock PIL Image object
        mock_pil_image = MagicMock()
        mock_pil_image.size = (100, 100)
        mock_pil_image.save = MagicMock()

        with patch('io.BytesIO') as mock_io:
            mock_io.return_value.getvalue.return_value = b'encoded_bytes'

            res = result_instance._render_img(mock_pil_image)

            assert res is not None
            assert res[0] == b'encoded_bytes'
            assert res[1] == 'image/jpeg'

    def test_store_img(self, result_instance, mocker):
        # Mock os.makedirs and os.path.exists
        mocker.patch('os.makedirs')
        mocker.patch('os.path.exists', return_value=False)
        mocker.patch('os.path.isfile', return_value=False)

        # Mock PIL.Image.open
        mock_pil_open = mocker.patch('PIL.Image.open')
        mock_img_obj = MagicMock()
        mock_pil_open.return_value = mock_img_obj

        img_bytes = b'fake_bytes'
        path = result_instance._store_img('screenshot.png', img_bytes)

        assert '/tmp/extra' in path
        assert path.endswith('.jpg')
        mock_img_obj.save.assert_called_once()

    def test_serialize_methods(self, result_instance, mocker):
        mock_write = mocker.patch.object(result_instance, '_write_file')

        data = {'key': 'value'}

        # JSON
        result_instance._serialize(data, 'output.json')
        mock_write.assert_called()
        args, _ = mock_write.call_args
        assert args[0] == 'output.json'
        assert '"key": "value"' in args[1]

        # YAML
        result_instance._serialize(data, 'output.yaml')
        mock_write.assert_called()
