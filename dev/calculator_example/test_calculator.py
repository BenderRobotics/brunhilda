import unittest
from calculator import add, subtract, multiply

class TestCalculator(unittest.TestCase):
    """
    Test suite for verifying basic calculator operations.
    This class serves as a demonstration for the BRunhilda reporter.
    """

    def test_addition_basic(self):
        """
        @test-id: CALC-ADD-01
        @name: Basic Addition Test
        @maintainer: Test Engineer
        @execution: automatic
        @priority: high
        @covering: REQ_01

        Verifies that the add function correctly sums two positive integers.

        @steps
        1) > Call the add function with parameters 10 and 20.
           > The result is equal to 30.
        2) > Verify the return value type.
           > The result is an instance of integer.
        @endsteps
        """
        result = add(10, 20)
        self.assertEqual(result, 30)
        self.assertIsInstance(result, int)

    def test_subtraction_with_line_blocks(self):
        """
        @test-id: CALC-SUB-01
        @name: Complex Subtraction Test
        @priority: mid
        @exec-time: 2s

        This test uses Line Blocks to provide detailed formatting for conditions.

        @steps
        1) > | Set the first operand to 100.
             | Set the second operand to 40.
           > The difference is calculated correctly as 60.
        2) > Perform subtraction in reverse order (40 - 100).
           > | The result must be a negative value.
             | Specifically, the value should be -60.
        @endsteps
        """
        self.assertEqual(subtract(100, 40), 60)
        self.assertEqual(subtract(40, 100), -60)

    def test_multiply_dynamic_reporting(self):
        """
        @test-id: CALC-MUL-01
        @name: Multiplication with Dynamic Reporting
        @priority: low

        Demonstrates how to push execution details into the HTML report at runtime.

        @steps
        1) > Multiply 5 by 5.
           > The result is 25.
        @endsteps
        """
        a, b = 5, 5
        result = multiply(a, b)

        # Appending execution details directly into the BRunhilda report
        self.steps.append({
            'number': 1,
            'obtained': f'multiply({a}, {b}) produced {result}',
            'comment': 'Calculation performed on local CPU successfully.',
            'result': 'PASSED' if result == 25 else 'FAILED'
        })

        self.assertEqual(result, 25)
