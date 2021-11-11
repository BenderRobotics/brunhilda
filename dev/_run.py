import brunhilda
import os
import sys

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
                                 name="system",
                                 html_preamble="dev/report.intro.html",
                                 html_output="dev/report.html",
                                 junit_output="dev/report.xml",
                                 traceability_output="dev/traceability.html",
                                 req_summary_output="dev/req-summary.html",
                                 test_summary_preamble="dev/test-summary.intro.html",
                                 test_summary_output="dev/test-summary.html",
                                 test_plan_preamble="dev/test-plan.intro.html",
                                 test_plan_output="dev/test-plan.html",
                                 requirements_list=['L10', 'L11', 'L12', 'C05'])

    loader = brunhilda.BRunhildaTestLoader()
    suite = loader.discover('.')
    runner.run(suite)
