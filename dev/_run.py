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
    suite = loader.discover('dev', pattern='test*.py', top_level_dir=None, tag_filter=None)
    result = runner.run(suite)
    runner.save_issues(result, 'dev/issues.yaml')
    runner.save_tests(result, 'dev/tests.yaml')
    #runner.save_junit_report(result, 'dev/report.junit')
    runner.save_html_report(result, 'dev/report.html')

    reporter = brunhilda.reporter.Reporter()
    #reporter.load_tests('dev/tests-system.json')
    #reporter.load_tests('dev/tests-integration.json')
    #reporter.load_tests('dev/tests-visual.json')
    #reporter.load_tests('dev/tests-system.yaml')
    #reporter.load_tests('dev/tests-visual.yaml')
    reporter.load_tests('dev/tests.yaml', 'dev/report.html')
    reporter.load_issues('dev/issues.yaml')
    reporter.load_features('dev/features.yaml')
    reporter.justify_tests()
    reporter.print_test_plan('dev/plan.html')
    reporter.print_issue_list('dev/issues.html')
    reporter.print_requirements_summary('dev/requirements.html')
    reporter.print_test_summary('dev/tests.html')
    reporter.print_feature_summary('dev/features.html')
    reporter.print_index('dev/index.html')
