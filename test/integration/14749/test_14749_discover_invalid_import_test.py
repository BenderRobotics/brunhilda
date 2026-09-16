from pathlib import Path

from brunhilda import BRunhildaTestLoader
from brunhilda.loader import iter_suite

DATA_FOLDER = Path(__file__).parent / 'data'


def test_discover_invalid_module_import():
    """
    GIVEN two modules with unit tests, one of them have invalid import
    WHEN loading unit tests via BRunhildaTestLoader
    THEN unit tests from both modules should be discovered
    """
    for tag_filter in (None, 'environment==ENV_A'):
        suite = BRunhildaTestLoader().discover(DATA_FOLDER, pattern='*.py', tag_filter=tag_filter)
        found = [type(test).__name__ for test in iter_suite(suite)]

        assert len(found) == 2
        assert sum(n == '_FailedTest' for n in found) == 1
