import unittest
import brunhilda
import os
import sys
import logging
import colorama
import time
import ddt
import lorem
from PIL import Image, ImageDraw

colorama.init()


@ddt.ddt
class TestCase1(unittest.TestCase):
    """
    This is a test case description. It can contain subset of RST formating.

    Also *italics*, **bold**, ``monospace`` ... inline formating is supported.

    But *.bin or *.hex is OK!

    Lists
    =========

    1. numbers

    A. upper-case letters

    a. lower-case letters

    I. upper-case roman numerals

    i. lower-case roman numerals

    (1) numbers again

    1) and again

    * a bullet point
    * list with many
    * items

    Level 1
    =========

    Folowed by an paragraph.

    Second level
    ------------

    Also here has to be some text.

    Or more levels of headings
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tables are also supported:

    +---------------------+---------+---+
    |1                    |        2| 3 |
    +---------------------+---------+---+

    +------------+------------+-----------+
    | Header 1   | Header 2   | Header 3  |
    +============+============+===========+
    | body row 1 | column 2   | column 3  |
    +------------+------------+-----------+
    | body row 2 | Cells may span columns.|
    +------------+------------+-----------+
    | body row 3 | Cells may  | - Cells   |
    +------------+ span rows. | - contain |
    | body row 4 |            | - blocks. |
    +------------+------------+-----------+

    .. list-table:: Frozen Delights!
       :widths: 15 10 30
       :header-rows: 1

       * - Treat
         - Quantity
         - Description
       * - Albatross
         - 2.99
         - On a stick!
       * - Crunchy Frog
         - 1.49
         - If we took the bones out, it wouldn't be
           crunchy, now would it?
       * - Gannet Ripple
         - 1.99
         - On a stick!

    .. list-table:: Title
       :widths: 25 25 50
       :header-rows: 1

       * - Heading row 1, column 1
         - Heading row 1, column 2
         - Heading row 1, column 3
       * - Row 1, column 1
         -
         - Row 1, column 3
       * - Row 2, column 1
         - Row 2, column 2
         - Row 2, column 3
    """

    def test_00_pass(self):
        """
        @test-id:       ST_FW_002
        @author:        Jan Hrbacek
        @execution:     automatic
        @exec-time:     150s
        @covering:      REQ_SYS_FW_001, REQ_SYS_FW_002
        @environment:   ENV_002
        @priority:      high
        @variants:      MMI_TGL_001, MMI_TGL_002;
        @status:        new
        @spec:          L11 4.4
        @tp:            TP07.1

        But *.bin or *.hex is OK!
        Verifies normal execution of the scheduled program.

        @steps
        1) >  Set ``{user_permission}`` to 3 (installer). When the test step description
              is too long, it is possible to split in multiple lines. It is possible to
              use RS inside of these

              - including
              - lists
           > ``{user_permission} == 3``
        2) > Set {tm_user_permission_user} to 20.
           > {tm_user_permission} == 20. When the test step description
             is too long, it is possible to split in multiple lines.
        3) > Enter and activate test run A.1.1.
           > A.1.1 BC is active BC
        @endsteps
        """
        print("Stupid print")
        FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=FORMAT)
        log = logging.getLogger("")
        log.setLevel(0)
        log.debug("debug message")
        log.info("info message")
        log.warning("very warning message")
        log.error("error message")
        log.critical("critical message")
        time.sleep(0.2)
        self.assertEqual(1, 1, "Message")

    def test_01_fail(self):
        """
        @ref ST01.1
        @spec REQ_SYS_001, REQ_SYS_002, REQ_SYS_003

        Verifies normal execution of the scheduled program.

        1) Generates schedule program with random values and times,
        2) Write program to MMI.
        3) Set MMI date-time before the first program action time.
        4) Write A
        5) Verify value of the schedule timer action target to be a previous scheduled value.
        6) Verify value of the schedule timer action target to be a new scheduled value.

        - a
        - b
        - c
        - d
        """
        import colorama
        from colorama import Fore, Back, Style
        colorama.init()

        # Set the color semi-permanently
        print(Fore.CYAN)
        print("Text will continue to be cyan")
        print("until it is reset or changed")
        print(Style.RESET_ALL)

        # Colorize a single line and then reset
        print(Fore.RED + 'You can colorize a single line.' + Style.RESET_ALL)

        # Colorize a single word in the output
        print('Or a single ' + Back.GREEN + 'words' + Style.RESET_ALL + ' can be highlighted')

        # Combine foreground and background color
        print(Fore.BLUE + Back.WHITE)
        print('Foreground, background, and styles can be combined')
        print("==========            ")

        print(Style.RESET_ALL)
        print('If unsure, reset everything back to normal.')

        print(Fore.RED + 'some red text')
        print(Back.GREEN + 'and with a green background' + Back.RESET)
        print(Style.DIM + 'and in dim text' + Fore.RESET)
        print('still dim but normal color')
        print(Style.RESET_ALL)
        print('back to normal now')

        img = Image.new('RGB', (1600, 1000), color = (73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((30, 30), "PIL image", fill=(255, 255, 0))

        self.extra.append(img.copy())

        img2 = Image.new('RGB', (1600, 1000), color = (0, 200, 137))
        d = ImageDraw.Draw(img2)
        d.text((30, 30), "PIL image 2", fill=(255, 255, 0))

        self.extra.append(img2.copy())

        self.extra.append(lorem.paragraph())

        self.extra.append({"dictionary": 1, "can": "be", "used": {"as": "well"}})
        self.extra.append(['or', 'list', 'of', 'items'])

        self.assertEqual(1, 2, "Message")

    def test_02_subtest(self):
        """
        @ref ST01.1, ST01.2
        @spec REQ_SYS_001, REQ_SYS_002, REQ_SYS_003

        Verifies normal execution of the scheduled program.

        1) Generates schedule program with random values and times,
        2) Write program to MMI.
        3) Set MMI date-time before the first program action time.
        4) Write A
        5) Verify value of the schedule timer action target to be a previous scheduled value.
        6) Verify value of the schedule timer action target to be a new scheduled value.

        Repeat steps 3–6 for entire progam.
        """
        for i in range(10):
            with self.subTest(i=i, j=i*2, bc="9.1.2") as subtest:
                print(lorem.sentence())
                if i == 4:
                    self.skipTest("Because 4")
                elif i % 2 == 0:
                    img = Image.new('RGB', (1600, 1000), color = (0, 128, 180))
                    d = ImageDraw.Draw(img)
                    d.text((30, 30), f"Image {i}", fill=(255, 255, 0))
                    self.extra.append(img.copy())
                    raise AssertionError(img.copy())

                self.assertEqual(1, 1 / (i % 3) , "Message")

    def test_03_error(self):
        """
        @ref ST01.1, ST01.3

        Verifies normal execution of the scheduled program.

        1) Generates schedule program with random values and times,
        2) Write program to MMI.
        3) Set MMI date-time before the first program action time.
        4) Verify value of the schedule timer action target to be a previous scheduled value.
        5) Wait for time pass over the action time.
        6) Verify value of the schedule timer action target to be a new scheduled value.

        Repeat steps 3 – 6 for entire progam.
        """
        self.assertTrue(1 / 0, "Message")

    def test_04_skip(self):
        """
        @ref ST01.4

        Verifies normal execution of the scheduled program.

        1) Generates schedule program with random values and times,
        2) Write program to MMI.
        3) Set MMI date-time before the first program action time.
        4) Verify value of the schedule timer action target to be a previous scheduled value.
        5) Wait for time pass over the action time.
        6) Verify value of the schedule timer action target to be a new scheduled value.

        Repeat steps 3 – 6 for entire progam.
        """
        self.skipTest("Because we can")

    @unittest.skip("Because of decorator")
    def test_05_skip_decorator(self):
        """
        @ref ST01.1
        @spec REQ_SYS_004

        Verifies normal execution of the scheduled program.

        1) Generates schedule program with random values and times,
        2) Write program to MMI.
        3) Set MMI date-time before the first program action time.
        4) Verify value of the schedule timer action target to be a previous scheduled value.
        5) Wait for time pass over the action time.
        6) Verify value of the schedule timer action target to be a new scheduled value.

        Repeat steps 3 – 6 for entire progam.
        """
        self.assertTrue(True)

    @unittest.expectedFailure
    def test_06_expected_failure(self):
        """
        """
        self.assertTrue(False)

    @unittest.expectedFailure
    def test_07_unexpected_sucess(self):
        self.assertTrue(True)

    def test_08_exception_args(self):
        img = Image.new('RGB', (1600, 1000), color = (0, 128, 180))
        raise AssertionError(img.copy())

    @ddt.data(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    def test_09_ddt(self, param):
        """
        @ref ST01.1
        @spec REQ_SYS_004, REQ_SYS_005, REQ_SYS_006, REQ_SYS_007

        """
        self.assertIn(param, [2, 5, 7])


class TestCaseA(unittest.TestCase):
    """
    This is a test case description. longish explanation: returns the square of a: :math:`a^2`
    """
    def test_0A_pass(self):
        """
        Some test from A
        """
        self.assertTrue(True)


if __name__ == '__main__':
    information = {
        "Firmware version": os.getenv('VER_FW', '-') + " (bootloader " + os.getenv('VER_BL', '-') + ")",
        "Tag": os.getenv('CI_COMMIT_TAG', '-'),
        "Branch": os.getenv('CI_COMMIT_BRANCH', '-'),
        "Commit ID": os.getenv('CI_COMMIT_SHA', '-'),
        "Execution": "automated" if 'CI' in os.environ else "manual",
        "Triggered by": os.getenv('CI_PIPELINE_SOURCE', '-'),
        "Runner": os.getenv('CI_RUNNER_DESCRIPTION', '-'),
        "Runner ID": os.getenv('CI_RUNNER_ID', '-'),
        "Job ID": os.getenv('CI_JOB_ID', '-'),
        "Job name": os.getenv('CI_JOB_NAME', '-'),
        "Job stage": os.getenv('CI_JOB_STAGE', '-'),
        "Pipeline": os.getenv('CI_PIPELINE_IID', '-'),
        "Project": os.getenv('CI_PROJECT_ID', '-'),
        "Project name": os.getenv('CI_PROJECT_NAME', '-')
    }
    runner = brunhilda.BRunhilda(user_data=information,
                                 verbosity=3,
                                 stream=sys.stdout,
                                 html_output="dev/report.html",
                                 junit_output="dev/report.xml",
                                 traceability_output="dev/traceability.html",
                                 req_summary_output="dev/req-summary.html",
                                 test_summary_output="dev/test-summary.html",
                                 test_plan_output="dev/test-plan.html",
                                 manual_execution=True)
    unittest.main(testRunner=runner)

# @}
