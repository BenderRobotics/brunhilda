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
                                 name='system',
                                 dut='MMI2',
                                 extra_data_output="dev/extra")

    loader = brunhilda.BRunhildaTestLoader()
    suite = loader.discover('.', pattern='test*.py', top_level_dir=None, tag_filter=None)
    result = runner.run(suite)
    runner.save_issues(result, 'issues.yaml')
    runner.save_tests(result, 'tests.yaml')
    runner.save_junit_report(result, 'report.junit')
    runner.save_html_report(result, 'report.html')

    reporter = brunhilda.reporter.Reporter(requirements=['L55'])
    reporter.load_tests('tests.yaml')
    reporter.load_issues('issues.yaml')
    reporter.justify_tests()
    reporter.print_issue_list('issues.html')
    reporter.print_test_plan('plan.html')
    reporter.print_requirements_summary('requirements.html')
    reporter.print_test_summary('tests.html')
    reporter.print_index('index.html')
