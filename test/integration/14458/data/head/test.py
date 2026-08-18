"""
This module isn't testing anything, it's used for testing BRunhilda's test execution.
This test is executed via BRunhilda runner, its output is used for reports generation and the reports are tested.
"""
import unittest


class TestCase(unittest.TestCase):

    def test(self):
        """
        @test-id: test-01
        @name: Verification of subtests justification
        @maintainer: John Doe
        @execution: automatic
        @exec-time: 1
        @covering:
        @environment:
        @priority: mid
        @variants:
        @status:
        @spec: REQ-001
        @disabled-modules:
        """
        for i in range(4):
            with self.subTest(i=i):
                if i < 3:
                    self.assertEqual(1, 1, 'This will pass.')
                else:
                    self.assertEqual(1, 2, 'This will fail.')
