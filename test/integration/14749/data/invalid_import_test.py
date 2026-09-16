import unittest

import a_module_that_does_not_exist  # the whole point of this file


class TestBad(unittest.TestCase):

    def test_something(self):
        """
        @environment: ENV_A
        """
