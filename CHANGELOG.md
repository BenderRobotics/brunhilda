# Brunhilda project changelog

## 1.3.0 (2021-12-01)

- Added BRunhilda loader with support to filter tests by tags (refs [#5175](https://redmine.benderrobotics.com/issues/5175)).

## 1.2.7 (2021-11-09)

- Fixed missing escaping of the failure text in JUnit output.

## 1.2.6 (2021-11-08)

- Change to use sub-test ID instead of the number in the reports for IDs.
- Fixed base64 image encoding in the HTML test report.
- Added support for the sub-test extra data including images.

## 1.2.5 (2021-10-22)

- Unified ID's of the tests in all generated HTML files.

## 1.2.4 (2021-10-22)

- Fixed issues in the test plan generated HTML code.
- Unified ID's of the test-plan test sections, added anchors for the test cases.

## 1.2.3 (2021-10-04)

- Distinguished between failure and error in JUnit report ([#5043](https://redmine.benderrobotics.com/issues/5043)).
- Added meta property with the test result to JUnit report ([#5043](https://redmine.benderrobotics.com/issues/5043)).

## 1.2.2 (2021-09-30)

- Improved readability of the report pre-formatted text by enabled scroll bars in HTML reports.
- Added tags to the JUnit XML report ([#5043](https://redmine.benderrobotics.com/issues/5043)).
- Sanitize quotes in JUnit XML report tag values ([#5043](https://redmine.benderrobotics.com/issues/5043)).
- Sanitize invalid chars for the XML report ([#5043](https://redmine.benderrobotics.com/issues/5043)).
- Added suite names to the reports ([#5043](https://redmine.benderrobotics.com/issues/5043)).

## 1.2.1 (2021-08-30)

- Added full list of requirements to the requirements summary report ([#4828](https://redmine.benderrobotics.com/issues/4828)).

## 1.2.0 (2021-08-18)

- Removed dependency to jQuery from static HTML reports.
- Added filling of test procedure steps ([#4814](https://redmine.benderrobotics.com/issues/4814)).
- Fixed key-press navigation in the test report.
- Generated index.html file for the created outputs.
- Fixed using spec tag instead of ref tag for the traceability generator.
- Removed manual execution option ([#4828](https://redmine.benderrobotics.com/issues/4828)).
- Added links from the summary report to the test plan ([#4828](https://redmine.benderrobotics.com/issues/4828)).
- Prevented division by zero in the template of the pass percentage.

## 1.1.3 (2021-07-29)

- Added option to include static preambles ([#4602](https://redmine.benderrobotics.com/issues/4602)).

## 1.1.2 (2021-05-25)

- Added test execution summary to the Test Summary output ([#4439](https://redmine.benderrobotics.com/issues/4439)).

## 1.1.1 (2021-05-25)

- Added explanation of the test summary test results in the HTML report.

## 1.1.0 (2021-05-20)

- Fixed JUnit XML output, escaped HTML in JUnit XML output, added test execution time information
  ([#4501](https://redmine.benderrobotics.com/issues/4501)).
- Added test plan output report ([#4437](https://redmine.benderrobotics.com/issues/4437)).
- Added test and requirements summary outputs ([#4439](https://redmine.benderrobotics.com/issues/4439)).

## 1.0.0 (2021-03-17)

- First stable version.
