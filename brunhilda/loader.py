import unittest
from .parser import parse_tags
from .tag_filter import eval_tags


def iter_suite(suite: unittest.TestSuite):
    """
    Iterate through test suites, and yield individual tests
    """
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            for t in iter_suite(test):
                yield t
        else:
            yield test


class BRunhildaTestLoader:
    def discover(self, start_dir, pattern='test*.py', top_level_dir=None, tag_filter=None):
        """Find and return all test modules from the specified start
        directory, recursing into subdirectories to find them and return all
        tests found within them. Only test files that match the pattern will
        be loaded. (Using shell style pattern matching.)

        All test modules must be importable from the top level of the project.
        If the start directory is not the top level directory then the top
        level directory must be specified separately.

        If a test package name (directory with '__init__.py') matches the
        pattern then the package will be checked for a 'load_tests' function. If
        this exists then it will be called with (loader, tests, pattern) unless
        the package has already had load_tests called from the same discovery
        invocation, in which case the package module object is not scanned for
        tests - this ensures that when a package uses discover to further
        discover child tests that infinite recursion does not happen.

        If load_tests exists then discovery does *not* recurse into the package,
        load_tests is responsible for loading all tests in the package.

        The pattern is deliberately not stored as a loader attribute so that
        packages can continue discovery themselves. top_level_dir is stored so
        load_tests does not need to pass this argument in to loader.discover().

        Paths are sorted before being imported to ensure reproducible execution
        order even on filesystems with non-alphabetical ordering like ext3/4.
        """
        patterns = pattern.split(',')
        tests = unittest.TestSuite()

        for pattern in patterns:
            suite = unittest.defaultTestLoader.discover(start_dir, pattern.strip(), top_level_dir)

            for test in iter_suite(suite):
                if tag_filter is None:
                    tests.addTest(test)
                else:
                    docstring = getattr(test, test._testMethodName).__doc__
                    tags = parse_tags(docstring)

                    if eval_tags(tag_filter, tags):
                        tests.addTest(test)

        # this ugly thing is added for the compatibility with Brest which expects suite in the suite
        suite = unittest.TestSuite(tests=[tests])
        return unittest.TestSuite(tests=[suite])

    def _filter_by_tags(self, conditions, tags):
        """
        Checks if given tags matches the set tag_filter

        :param dict tags: parsed tags from the description
        :return: True if the tags matching filter, False if not
        """
        if conditions is not None:
            for tag, value in conditions.items():
                if (tag not in tags) or ((tag in tags) and (value not in tags[tag])):
                    return False

        return True
