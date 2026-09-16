"""
This module isn't testing anything, it's used for testing BRunhilda's test execution.
This test is executed via BRunhilda runner, its output is used for reports generation and the reports are tested.
"""
import unittest


class TestCase(unittest.TestCase):

    def test_01_all_passed(self):
        """
        @test-id: test-01
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                self.assertTrue(True)

    def test_02_middle_one_failed(self):
        """
        @test-id: test-02
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 5:
                    self.assertTrue(False)
                else:
                    self.assertTrue(True)

    def test_03_last_failed(self):
        """
        @test-id: test-03
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 9:
                    self.assertTrue(False)
                else:
                    self.assertTrue(True)

    def test_04_middle_one_errored(self):
        """
        @test-id: test-04
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 5:
                    raise RuntimeError()
                else:
                    self.assertTrue(True)

    def test_05_last_errored(self):
        """
        @test-id: test-05
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 9:
                    raise RuntimeError()
                else:
                    self.assertTrue(True)

    def test_06_middle_errored_last_failed(self):
        """
        @test-id: test-06
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 5:
                    raise RuntimeError()
                elif i == 9:
                    self.assertTrue(False)
                else:
                    self.assertTrue(True)

    def test_07_middle_failed_last_errored(self):
        """
        @test-id: test-07
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 9:
                    raise RuntimeError()
                elif i == 5:
                    self.assertTrue(False)
                else:
                    self.assertTrue(True)

    def test_08_middle_justified_last_errored(self):
        """
        @test-id: test-08
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 9:
                    raise RuntimeError()
                elif i == 5:
                    self.assertTrue(False)
                else:
                    self.assertTrue(True)

    def test_09_middle_errored_last_justified(self):
        """
        @test-id: test-09
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 5:
                    raise RuntimeError()
                elif i == 9:
                    self.assertTrue(False)
                else:
                    self.assertTrue(True)

    def test_10_middle_justified_last_failed(self):
        """
        @test-id: test-10
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 9:
                    self.assertTrue(False)
                elif i == 5:
                    self.assertTrue(False)
                else:
                    self.assertTrue(True)

    def test_11_middle_failed_last_justified(self):
        """
        @test-id: test-11
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 9:
                    self.assertTrue(False)
                elif i == 5:
                    self.assertTrue(False)
                else:
                    self.assertTrue(True)

    def test_12_all_failed_justified(self):
        """
        @test-id: test-12
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 9:
                    self.assertTrue(False)
                elif i == 5:
                    self.assertTrue(False)
                else:
                    self.assertTrue(True)

    @unittest.expectedFailure
    def test_13_unexpected_success(self):
        """
        @test-id: test-13
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        self.assertTrue(True)

    @unittest.expectedFailure
    def test_14_expected_failure(self):
        """
        @test-id: test-14
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        self.assertTrue(False)

    @unittest.skip
    def test_15_skip(self):
        """
        @test-id: test-15
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        self.assertTrue(True)

    def test_16_one_skipped(self):
        """
        @test-id: test-16
        @maintainer: John Doe
        @execution: automatic
        @covering:
        @spec: REQ-001
        """
        for i in range(10):
            with self.subTest(i=i):
                if i == 9:
                    self.skipTest('Skip')
                else:
                    self.assertTrue(True)
