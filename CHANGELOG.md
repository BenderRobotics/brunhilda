# Brunhilda project changelog

## 2.2.1 (2022-03-15)

- Fixed linking issues to tests from different test levels (refs [#5619](https://redmine.benderrobotics.com/issues/5619)).
- Fixed exceptions in case that other object than test is raised as errored.

## 2.2.0 (2022-02-23)

- Add advanced tag-based filtering during test discovery (refs [#5525](https://redmine.benderrobotics.com/issues/5525)).
- Add dryrun functionality (refs [#5449](https://redmine.benderrobotics.com/issues/5449)).

## 2.1.2 (2022-02-15)

- Filled comment and bug ID columns in the summary report (refs [#5573](https://redmine.benderrobotics.com/issues/5573), CBTFM-433).
- Fixed CSS sizes of test header in the HTML test execution report.

## 2.1.1 (2022-01-12)

- Added quoting of the URL's in generated HTML's to prevent invalid links to referenced artifacts (refs [#5416](https://redmine.benderrobotics.com/issues/5416)).

## 2.1.0 (2022-01-07)

- Prevented collision in generated extra file names (refs [#5307](https://redmine.benderrobotics.com/issues/5307)).
- Fixed paths to the test plan in the test summary report (refs [#5416](https://redmine.benderrobotics.com/issues/5416)).
- Split artifacts generation process into dedicated functions - no longer part of the the test running.
- Improved report filtering function (refs [#5416](https://redmine.benderrobotics.com/issues/5416), CBTFM-394)
- Removed catch of the missing preamble error to stop reporting (refs [#5416](https://redmine.benderrobotics.com/issues/5416)).

## 2.0.2 (2021-12-23)

- Fixed processing of extra test data by additional check if test object contains extra data.
- Fixed saving of extra images with too long filename by limiting max length of the filename to 120 chars.

## 2.0.1 (2021-12-14)

- Fixed loader filtering by tags.
- Fixed invalid characters in the extra file name.
- Fixed extra image paths in the test execution report.

## 2.0.0 (2021-12-10)

- Used external images instead of embedded images in the HTML reports to reduce memory errors during test runs (refs [#5043](https://redmine.benderrobotics.com/issues/5043)).
- Majorly refactored to generate intermediate format used for post processing (refs [#5043](https://redmine.benderrobotics.com/issues/5043)).

## 1.3.1 (2021-12-10)

- Changed structure of the test-suite produced by loader to be complaint with Brest expectations (refs [#5043](https://redmine.benderrobotics.com/issues/5043), [#5364](https://redmine.benderrobotics.com/issues/5364)).

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
