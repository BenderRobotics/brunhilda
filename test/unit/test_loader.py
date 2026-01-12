import unittest
from unittest.mock import MagicMock, patch

import pytest

from brunhilda.loader import BRunhildaTestLoader, iter_suite

# --- Helper classes for testing purpose ---


class SampleTest(unittest.TestCase):
    """Fake test case"""

    def test_dummy(self):
        """
        @priority: high
        """
        pass


class SampleTestNoDoc(unittest.TestCase):
    """Test without docstring"""

    def test_nodoc(self):
        pass


# --- Tests iter_suite ---


def test_iter_suite_flat():
    test1 = SampleTest('test_dummy')
    test2 = SampleTest('test_dummy')
    suite = unittest.TestSuite([test1, test2])

    result = list(iter_suite(suite))

    assert len(result) == 2
    assert test1 in result
    assert test2 in result


def test_iter_suite_nested():
    test1 = SampleTest('test_dummy')
    test2 = SampleTest('test_dummy')
    test3 = SampleTest('test_dummy')

    # Structure: Suite -> [test1, Suite -> [test2, test3]]
    inner_suite = unittest.TestSuite([test2, test3])
    outer_suite = unittest.TestSuite([test1, inner_suite])

    result = list(iter_suite(outer_suite))

    assert len(result) == 3
    assert test1 in result
    assert test2 in result
    assert test3 in result


# --- Tests BRunhildaTestLoader ---


class TestBRunhildaLoader:

    @pytest.fixture
    def loader(self):
        return BRunhildaTestLoader()

    @patch('unittest.defaultTestLoader.discover')
    def test_discover_basic_patterns(self, mock_discover, loader):
        """Tests if discover calls unittest laoder correctly for more patterns"""
        mock_discover.return_value = unittest.TestSuite()

        start_dir = './tests'
        pattern = 'test_a*.py, test_b*.py'

        loader.discover(start_dir, pattern=pattern)

        assert mock_discover.call_count == 2

        calls = mock_discover.call_args_list
        assert calls[0][0][1] == 'test_a*.py'
        assert calls[1][0][1] == 'test_b*.py'

    @patch('brunhilda.loader.eval_tags')
    @patch('brunhilda.loader.parse_tags')
    @patch('unittest.defaultTestLoader.discover')
    def test_discover_with_filtering_match(self, mock_discover, mock_parse, mock_eval, loader):
        """Tests tags filter - eval returns True"""
        test_case = SampleTest('test_dummy')
        suite = unittest.TestSuite([test_case])
        mock_discover.return_value = suite

        mock_parse.return_value = {'priority': ['high']}  # What parse_tags returns
        mock_eval.return_value = True  # What eval_tags returns

        result_suite = loader.discover('.', tag_filter='priority=high')

        outer_wrapper = list(result_suite)[0]
        inner_wrapper = list(outer_wrapper)[0]
        final_tests = list(inner_wrapper)

        assert len(final_tests) == 1
        assert final_tests[0] == test_case

        mock_parse.assert_called_once()
        mock_eval.assert_called_with('priority=high', {'priority': ['high']})

    @patch('brunhilda.loader.eval_tags')
    @patch('brunhilda.loader.parse_tags')
    @patch('unittest.defaultTestLoader.discover')
    def test_discover_with_filtering_no_match(self, mock_discover, mock_parse, mock_eval, loader):
        """Tests tags filter - eval returns False"""
        test_case = SampleTest('test_dummy')
        mock_discover.return_value = unittest.TestSuite([test_case])

        mock_parse.return_value = {'priority': ['low']}  # What parse_tags returns
        mock_eval.return_value = False  # What eval_tags returns

        result_suite = loader.discover('.', tag_filter='priority=high')

        outer_wrapper = list(result_suite)[0]
        inner_wrapper = list(outer_wrapper)[0]
        final_tests = list(inner_wrapper)

        assert len(final_tests) == 0

    @patch('unittest.defaultTestLoader.discover')
    def test_discover_no_filter(self, mock_discover, loader):
        """Tests tags filter - without tags"""
        test_case = SampleTest('test_dummy')
        mock_discover.return_value = unittest.TestSuite([test_case])

        result_suite = loader.discover('.', tag_filter=None)

        outer_wrapper = list(result_suite)[0]
        inner_wrapper = list(outer_wrapper)[0]
        final_tests = list(inner_wrapper)

        assert len(final_tests) == 1
        assert final_tests[0] == test_case

    @patch('unittest.defaultTestLoader.discover')
    def test_return_structure_compatibility(self, mock_discover, loader):
        """
        Verifies the specific (compatible) structure of the return value.
        """
        mock_discover.return_value = unittest.TestSuite()

        result = loader.discover('.')

        assert isinstance(result, unittest.TestSuite)

        content_level_1 = list(result)
        assert len(content_level_1) == 1
        assert isinstance(content_level_1[0], unittest.TestSuite)

        content_level_2 = list(content_level_1[0])
        assert len(content_level_2) == 1
        assert isinstance(content_level_2[0], unittest.TestSuite)
