# Brunhilda project changelog

## [Unreleased]

### 🪄 Added

### 🐛 Fixed

- Fix fixed header overlapping target elements when scrolling to anchors (refs [#14560](https://redmine.benderrobotics.com/issues/14560))
- Fix TOC overlap by Home button in Features Summary (refs [#14461](https://redmine.benderrobotics.com/issues/14461))

### 🏗️ Changed

- Move result icon in front test name in Features Summary (refs [#14476](https://redmine.benderrobotics.com/issues/14476))

### 🗑️ Removed

- Remove confusing stats from Features Summary printing progress bar (refs [#14483](https://redmine.benderrobotics.com/issues/14483))

## 2.9.1 (2026-08-25)

- Add backward compatibility for older versions execution outputs (refs [#14458](https://redmine.benderrobotics.com/issues/14458), [#14471](https://redmine.benderrobotics.com/issues/14471), [#14479](https://redmine.benderrobotics.com/issues/14479))
- Add BRunhilda version to execution outputs (refs [#14491](https://redmine.benderrobotics.com/issues/14491))
- Add link to issue list from features summary (refs [#14463](https://redmine.benderrobotics.com/issues/14463))
- Add setup of integration tests (refs [#14492](https://redmine.benderrobotics.com/issues/14492))
- Fix execution distribution and levels graphs protting in Test Run Report (refs [#14495](https://redmine.benderrobotics.com/issues/14495))
- Fix navigation panel links in features summary (refs [#14274](https://redmine.benderrobotics.com/issues/14274))
- Fix test result reevaluation after subtests justification (refs [#14489](https://redmine.benderrobotics.com/issues/14489))

## 2.9.0 (2026-07-29)

- Improve Test summary charts naming (refs [#14264](https://redmine.benderrobotics.com/issues/14264))
- Improve Features and Requirements summary charts naming (refs [#14276](https://redmine.benderrobotics.com/issues/14276))
- Add showing all non-zero chart segments in legend (refs [#14267](https://redmine.benderrobotics.com/issues/14267))
- Fix filtering by level in Requirements cummary (refs [#14268](https://redmine.benderrobotics.com/issues/14268))
- Add percentage to chart legend (refs [#14265](https://redmine.benderrobotics.com/issues/14265))
- Remove number of Not Executed subtests from summary table (refs [#14235](https://redmine.benderrobotics.com/issues/14235))
- Change color of chart label to black (refs [#14236](https://redmine.benderrobotics.com/issues/14236))
- Fix test result in Features summary (refs [#14269](https://redmine.benderrobotics.com/issues/14269))
- Add test name as test heading ID in test plan (refs [#14258](https://redmine.benderrobotics.com/issues/14258))
- Improve subtests justification (refs [#14249](https://redmine.benderrobotics.com/issues/14249))
- Improve responsiveness of features summary (refs [#14266](https://redmine.benderrobotics.com/issues/14266), [#14272](https://redmine.benderrobotics.com/issues/14272))
- Fix TOC links in features summary (refs [#14274](https://redmine.benderrobotics.com/issues/14274))
- Rearrange charts in test summary (refs [#14238](https://redmine.benderrobotics.com/issues/14238))
- Fix inconsistent column width in Requirements summary table (refs [#14273](https://redmine.benderrobotics.com/issues/14273))
- Change Not Executed test result icon (refs [#14270](https://redmine.benderrobotics.com/issues/14270))
- Add Not Executed result to features and requirements (refs [#14275](https://redmine.benderrobotics.com/issues/14275))

## 2.8.1 (2026-06-30)

- Remove test record links leading to nowehere from the issue list when the path to HTML file is not provided (refs [#14208](https://redmine.benderrobotics.com/issues/14208))
- Optimize line breaks in sub-tests table details to prevent table overflow (refs [#14170](https://redmine.benderrobotics.com/issues/14170))
- Add legend to test suite execution graph (refs [#14234](https://redmine.benderrobotics.com/issues/14234))
- Fix justification for multiple sub-tests having same parameters (refs [#14241](https://redmine.benderrobotics.com/issues/14241))
- Change color used in reports for the `OUT-OF-SCOPE` state to prevent confusion with `PASSED` state (refs [#14248](https://redmine.benderrobotics.com/issues/14248))

## 2.8.0 (2026-06-18)

- Added Test Record table width optimization (refs [#13922](https://redmine.benderrobotics.com/issues/13922))
- Fixed datetime parsing from JSON file (refs [#13986](https://redmine.benderrobotics.com/issues/13986))
- Added subtest stats into Test Summary summary table (refs [#13940](https://redmine.benderrobotics.com/issues/13940))
- Optimized printing Summary of Features report (refs [#13946](https://redmine.benderrobotics.com/issues/13946))
- Added bugtraq file support for bug IDs links (refs [#13941](https://redmine.benderrobotics.com/issues/13941))
- Added extended filtering options (refs [#13839](https://redmine.benderrobotics.com/issues/13839))
- Added guide for report producer (refs [#13710](https://redmine.benderrobotics.com/issues/13710))

## 2.7.0 (2026-04-28)

- Added guide for report readers (refs [#13710](https://redmine.benderrobotics.com/issues/13710))
- Added requirement result in Requirement Summary (refs [#12918](https://redmine.benderrobotics.com/issues/12918))
- Added Out of Scope requirement state (refs [#12917](https://redmine.benderrobotics.com/issues/12917))
- Added Not Executed test result (refs [#12919](https://redmine.benderrobotics.com/issues/12919))
- Added prevention for loading tests after justification (refs [#13386](https://redmine.benderrobotics.com/issues/13386))
- Added justified Test Record regeneration (refs [#13388](https://redmine.benderrobotics.com/issues/13388))
- Added support for newline in issue comment section (refs [#13637](https://redmine.benderrobotics.com/issues/13637))
- Added subtest stats into Test Record summary table (refs [#13385](https://redmine.benderrobotics.com/issues/13385))
- Added order to bug IDs and comments in Test Summary (refs [#13636](https://redmine.benderrobotics.com/issues/13636))
- Updated charts colors (refs [#13173](https://redmine.benderrobotics.com/issues/13173))
- Fixed cell alignment in Requirement Summary table (refs [#13173](https://redmine.benderrobotics.com/issues/13173))
- Fixed parsing of line blocks in steps description (refs [#13244](https://redmine.benderrobotics.com/issues/13244))
- Fixed resizing cells (refs [#13172](https://redmine.benderrobotics.com/issues/13172), [#13173](https://redmine.benderrobotics.com/issues/13173))
- Fixed erroring subtests after errored subtest (refs [#13597](https://redmine.benderrobotics.com/issues/13597))
- Removed Test Record link if no HTML provided (refs [#13182](https://redmine.benderrobotics.com/issues/13182))

## 2.6.1 (2026-01-21)

- Added backward compatibility for loading test files created with versions prior to 2.6.0 (refs [#13181](https://redmine.benderrobotics.com/issues/13181)).
- Fixed the parsing of line blocks in step descriptions (refs [#13244](https://redmine.benderrobotics.com/issues/13244)).
- Colors for unknown categories in charts are now selected in a reproducible order from a defined list (refs [#13173](https://redmine.benderrobotics.com/issues/13173)).
- Fixed filtering in the requirements summary report (refs [#13173](https://redmine.benderrobotics.com/issues/13173)).
- Fixed cell resizing in the test summary (refs [#13173](https://redmine.benderrobotics.com/issues/13173), [#13172](https://redmine.benderrobotics.com/issues/13172)).
- Improved the performance of test summary loading ([#13172](https://redmine.benderrobotics.com/issues/13172)).
- Removed the link to the test report if no HTML is provided during report creation (refs [#13182](https://redmine.benderrobotics.com/issues/13182)).

## 2.6.0 (2026-01-21)

- Added version of BRunhilda to generated files (refs [#12690](https://redmine.benderrobotics.com/issues/12690))
- Added possibility to link custom files to the index page (refs [#12691](https://redmine.benderrobotics.com/issues/12691))
- Added sub-tests detailed info into test record view (refs [#12689](https://redmine.benderrobotics.com/issues/12689))
- Added ability to show multiple version of the same suite at a time (refs [#12692](https://redmine.benderrobotics.com/issues/12692))
- Added run info to tests output (refs [#12882](https://redmine.benderrobotics.com/issues/12882))
- Added coverage html report to CI artifacts (refs [#12882](https://redmine.benderrobotics.com/issues/12882))
- Adjusted issue list table cell spanning (refs [#12693](https://redmine.benderrobotics.com/issues/12693))
- Updated project structure (refs [#12882](https://redmine.benderrobotics.com/issues/12882))
- Removed leftover trace output (refs [#12882](https://redmine.benderrobotics.com/issues/12882))
- Updated load issues and tests methods (refs [#12882](https://redmine.benderrobotics.com/issues/12882))
- Changed unforced public attributes to readonly (refs [#12882](https://redmine.benderrobotics.com/issues/12882))
- Improved type hints (refs [#12882](https://redmine.benderrobotics.com/issues/12882))
- Updated docstring code documentation (refs [#12882](https://redmine.benderrobotics.com/issues/12882))
- Extended unit tests coverage (refs [#12882](https://redmine.benderrobotics.com/issues/12882))
- Fixed test details opening by clicking on test line (refs [#13017](https://redmine.benderrobotics.com/issues/13017))
- Fixed sub-test row height limit (refs [#13018](https://redmine.benderrobotics.com/issues/13018))

## 2.5.0 (2025-11-06)

- Added pyyaml to install_requires dependencies (refs [#7560](https://redmine.benderrobotics.com/issues/7560))
- Added link to index page to all reports (refs [#11707](https://redmine.benderrobotics.com/issues/11707))
- Added link between summary report and test result (refs [#11708](https://redmine.benderrobotics.com/issues/11708))
- Added link between issue list and test result (refs [#11709](https://redmine.benderrobotics.com/issues/11709))
- Added test ID column to test summary (refs [#7562](https://redmine.benderrobotics.com/issues/7562))
- Added custom color palette support (refs [#11902](https://redmine.benderrobotics.com/issues/11902))
- Added shortcut for closing all details (refs [#12082](https://redmine.benderrobotics.com/issues/12082))
- Added support for multi paragraph entries (refs [#12083](https://redmine.benderrobotics.com/issues/12083))
- Added support for custom coverage policy (refs [#12081](https://redmine.benderrobotics.com/issues/12081))
- Moved home link button to right top corner, update button style (refs [#11707](https://redmine.benderrobotics.com/issues/11707))
- Updated package structure to use pyproject.toml (refs [#11792](https://redmine.benderrobotics.com/issues/11792))
- Improved width and maximum height of narrow table cells in reports (refs [#11793](https://redmine.benderrobotics.com/issues/11793))
- Improved readability of cells in reports (refs [#11793](https://redmine.benderrobotics.com/issues/11793))
- Changed doorstop user story feature to optional (refs [#7560](https://redmine.benderrobotics.com/issues/7560), [#6890](https://redmine.benderrobotics.com/issues/6890))
- Fixed HTML code in error message (refs [#10824](https://redmine.benderrobotics.com/issues/10824))
- Fixed reference matching (refs [#12043](https://redmine.benderrobotics.com/issues/12043))
- Fixed duplicate references in feature summary (refs [#7561](https://redmine.benderrobotics.com/issues/7561))
- Fixed counting of skipped tests
- Fixed missing errors_strings field of test result object

## 2.4.0 (2023-05-10)

- Added support to use multiple files as a document preamble (refs [#7022](https://redmine.benderrobotics.com/issues/7022)).
- Fix CSS for test-steps result table column.
- Fixed numpy version required for doorstop (refs [#6890](https://redmine.benderrobotics.com/issues/6890)).

## 2.3.4 (2023-02-03)

- Added support for doorstop requirements management (refs [#5559](https://redmine.benderrobotics.com/issues/5559)).
- Added preamble to index page.

## 2.3.3 (2022-09-07)

- Use a different colour for passed and justified feature tests (refs [#6249](https://redmine.benderrobotics.com/issues/6249), CBTFM-560).
- Mention number of tests cases passed per feature (refs [#6249](https://redmine.benderrobotics.com/issues/6249), CBTFM-560).
- Fix incorrect justification of tests in features summary report (refs [#6230](https://redmine.benderrobotics.com/issues/6230)).

## 2.3.2 (2022-08-12)

- Use natural sort to sort requirements (refs [#6163](https://redmine.benderrobotics.com/issues/6163), CBTFM-560).

## 2.3.1 (2022-06-29)

- Use str as a default JSON serializer.
- Make JSON outputs pretty.
- Respect individual sub-tests results in feature list report.

## 2.3.0 (2022-06-03)

- Add option to build feature list based on YAML-defined features (refs [#5664](https://redmine.benderrobotics.com/issues/5664), CBTFM-446).

## 2.2.3 (2022-05-02)

- Removes image extra data from the result memory when they are stored to the disk (refs [#5280](https://redmine.benderrobotics.com/issues/5280)).

## 2.2.2 (2022-04-13)

- Added skip reason to the tests overview report (CBTFM-511).

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
