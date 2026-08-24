# Producer Guide

This guide is intended for Producers (QA engineers and developers) who write test scripts and configure the BRunhilda engine. It explains how to instrument your Python tests with metadata, how to use the advanced test loader for filtering, and how to configure the reporter to aggregate results into consolidated dashboards.

This document describes step-by-step how to generate a test run report with added information.

- [Extended Test Docstring format](#extended-test-docstring-format)
  - [Tags Field](#tags-field)
  - [Description Field](#description-field)
  - [Steps Field](#steps-field)
  - [Extended Test Docstring Example](#extended-test-docstring-example)
  - [Docstring Formatting](#docstring-formatting)
  - [Execution details in test steps](#execution-details-in-test-steps)
- [Test Loader](#test-loader)
  - [Tag-based Test Filtering](#tag-based-test-filtering)
    - [Tag-based Test Filtering Examples](#tag-based-test-filtering-examples)
- [Test Runner](#test-runner)
  - [Standard Execution](#standard-execution)
  - [Dry run](#dry-run)
  - [Test Run Artifacts](#test-run-artifacts)
- [Test Execution Example](#test-execution-example)
- [Tests  Justification](#tests--justification)
- [Reporting](#reporting)
  - [Methods](#methods)
  - [Requirements File](#requirements-file)
  - [Features File](#features-file)
  - [Bugtraq File](#bugtraq-file)
  - [Evaluation Policy](#evaluation-policy)
    - [Custom Evaluation Policy](#custom-evaluation-policy)
    - [Evaluation Policy Example](#evaluation-policy-example)
  - [Custom Colors](#custom-colors)
  - [Doorstop Requirements](#doorstop-requirements)

## Extended Test Docstring format

As a first step, the user must define the tests themselves and add a docstring containing detailed information about the test in the machine readable form.

```python
def test_01(self):
    """
    {tags}

    {description}

    {steps}
    """
```

### Tags Field

`{tags}` field holds tagging information. Each tag consists of pair

```python
@name: value
```

Multiple values are expressed as a comma separated list.

```python
@name: value1, value2, value3
```

`name` can be any text starting with `@` and can not contain `:` character.

Tags representing the time may contain units. Following keywords are supported:

- `s`, `sec`, `second`, `seconds`
- `m`, `min`, `minute`, `minutes`
- `h`, `hour`, `hours`
- `d`, `day`, `days`

Sample:

- `1h 1m 1s` -> 3661
- `2 hours 2 minutes 2 seconds` -> 7322

Example:

```python
@execution: automatic
@exec-time: 46
@spec: requirement_156
@covering:
@environment: INT_ENV_MMI1, INT_ENV_MMI2, INT_ENV_VIRT
@priority: mid
```

> [!IMPORTANT]
> Some tags are highly recommended because they have an impact on reports generating:
>
> - `@spec` - used for linking test to requirement
> - `@execution` - used for *Tests Execution* graph in *Test Run Report* and *Test Summary Report*

### Description Field

`{description}` field holds general description of the test.

### Steps Field

`{steps}` field holds detailed description of the test sequence. This field starts with the `@steps` and ends with `@endsteps`. Each step in the sequence starts with the number `X)` (`1)`, `2)`, ...). First `>` character is followed by the step action description (what is done), second `>` character is followed by the step expectation description (what is checked).

Example:

```python
@steps
1) > Read value A.
   > Value A is equal to 5.
2) > Read value B.
   > Value B is less than 0.
3) > Read value C.
   > Value C is greater than 1.
@endsteps
```

This steps sequence is interpreted as a following table.

| Step | Description            | Expectation                |
|------|------------------------|----------------------------|
| 1    |  Read value A.         | Value A is equal to 5.     |
| 2    |  Read value B.         | Value B is less than 0.    |
| 3    |  Read value C.         | Value C is greater than 1. |

### Extended Test Docstring Example

```python
def test_01(self):
    """
    @test-id:
    @name: First test
    @maintainer: Pavel Kumpan
    @execution: automatic
    @exec-time: 46
    @spec: requirement_156
    @covering:
    @environment: INT_ENV_MMI1, INT_ENV_MMI2, INT_ENV_VIRT
    @priority: mid
    @variants:

    This is the first test of the module.

    @steps
    1) > Read value A.
       > Value A is equal to 5.
    2) > Read value B.
       > Value B is less than 0.
    3) > Read value C.
       > Value C is greater than 1.
    @endsteps
    """
```

### Docstring Formatting

Because the docstrings are compiled as RST, you can use standard syntax like `**bold**` or `*italic*`.

If you need to set exact line breaks and formatting (e.g. for multi-line conditions or specific outputs), use [Line Blocks](https://docutils.sourceforge.io/0.4/docs/ref/rst/restructuredtext.html#line-blocks).

**Important rules for Line Blocks:**

- Each line of a line block must start with a vertical bar (`|`) and a space.
- If a line continues without a `|`, it must be indented to match the text of the line above it.
- Ensure vertical alignment of the `|` characters is strictly maintained.

```python
@steps
1) > | Read value from machine.
     | If the value is 0 or 1,
       LED should be activated.
     | Else: LED should not be activated.
   > Expected state is correctly set.
@endsteps
```

### Execution details in test steps

It is possible to add execution details into test steps. This can only be achieved programmatically directly in the test body. All you need is to append dictionary containing `number` (step number), `obtained`, `comment` and `result` keys into `self.steps`. Example is shown bellow.

These details will be shown in HTML Test Run Report.

```python
def test_example(self):
    """
    ...

    @steps
    1) >  Set ``user_permission`` to 3 (installer).
       > ``user_permission == 4``
    2) > Set ``tm_user_permission_user`` to 20.
       > ``tm_user_permission == 20``
    @endsteps
    """
    tested_class = User()

    tested_class.user_permission = 3
    self.steps.append({'number': 1,
                       'obtained':  f'tested_class.user_permission = {tested_class.user_permission}',
                       'comment': 'Some test execution comment',
                       'result': 'PASSED' if tested_class.user_permission == 4 else 'FAILED'})

    tested_class.tm_user_permission = 20
    self.steps.append({'number': 2})
    self.steps[1]['obtained'] = f'tested_class.tm_user_permission = {tested_class.tm_user_permission}'
    self.steps[1]['comment'] = 'Some test execution comment'
    self.steps[1]['result'] = 'PASSED' if tested_class.tm_user_permission == 20 else 'FAILED'

    self.assertEqual(tested_class.user_permission, 4)
    self.assertEqual(tested_class.tm_user_permission, 20)
```

## Test Loader

Once you have defined tests with extended docstring it is time to execute the tests. But first you need to load them.

The `brunhilda.BRunhildaTestLoader` class is used to create test suites from classes and modules. This is an extension of [`unittest.TestLoader`](https://docs.python.org/3/library/unittest.html#unittest.TestLoader).

In addition to the provides extended `discover` method

```python
brunhilda.BRunhildaTestLoader().discover(self, start_dir, pattern='test*.py', top_level_dir=None, tag_filter=None)
```

`discover` find and return all test modules from the specified start directory, recursing into subdirectories to find them and return all tests found within them. Only test files that match the pattern will be loaded. (Using shell style pattern matching.)

In addition to [`unittest.TestLoader.discover`](https://docs.python.org/3/library/unittest.html#unittest.TestLoader.discover):

- multiple patterns are supported `'test_A*.py, test_B*.py'` - test files that match one of comma separated list of
  patterns will be loaded,
- tag filtering based on tags in the test description.

### Tag-based Test Filtering

`tag_filter` parameter of the `discover` method can be used to limit the suite to the tests with the defined tag values.

Following syntax can be used for the tag_filter

- `tag1==A` *match* - test must be tagged by `tag1` and it must contain only the one value `A` (does not allow other
  values to be present),
- `tag1!=A` *mismatch* - test must be tagged by `tag1` and it must not contain the one value `A` (does not allow other
  values to be present),
- `tag1=~A` *contains* - test must be tagged by `tag1` and it must contain at least the one value `A` (allows other
  values to be present),
- `tag1!~A` *does not contain* - test must be tagged by `tag1` and it must not contain the value `A` (allows other
   values to be present),
- `@tag1` *is tagged* - test is tagged with `tag1`,
- `!tag1` *is not tagged* - test is not tagged `tag1`,
- `tag1>=A` *greater than or equal to* - test must be tagged by `tag1` its numeric value must not be lower than `A`,
- `tag1>A` *greater than* - test must be tagged by `tag1` its numeric value must be greater than `A`,
- `tag1<=A` *lower than or equal* - test must be tagged by `tag1` its numeric value must not be greater than `A`,
- `tag1<A` *lower than* - test must be tagged by `tag1` its numeric value must be lower than `A`.

Logical conjunction:

- `||` - OR (one of condition satisfied)
- `&&` - AND (all conditions satisfied)

when multiple conjunctions is used, the AND operator is treated with priority.

```
tag1==A && tag2==B || tag3==C
```

is equivalent to

```
(tag1==A && tag2==B) || tag3==C
```

#### Tag-based Test Filtering Examples

`tag1` contains `A` and `tag2` is present:

```
tag1=~A && @tag2
```

---

Given test case

```python
class Test_Environments(unittest.TestCase):
    def test_01(self):
        """
        @environment: ENV_TEST_1, ENV_TEST_2
        """
        ...

    def test_02(self):
        """
        @environment: ENV_TEST_2
        """
        ...

    def test_03(self):
        """
        @environment: ENV_TEST_1
        """
        ...
```

and the filter

```python
filter = 'environment=~ENV_TEST_1'
```

will result in loading only `test_01` and `test_03` in the test suite.

## Test Runner

Once you load the tests and create the test suite, it's time to execute it.

The core of the execution engine is the `brunhilda.BRunhilda` class. It extends [`unittest.TextTestRunner`](https://docs.python.org/3/library/unittest.html#unittest.TextTestRunner) and adds parameters for environment metadata and artifact management.

```python
class brunhilda.BRunhilda(stream=sys.stderr,
                          descriptions: bool = True,
                          verbosity: int =1,
                          failfast: bool = False,
                          buffer: bool = False,
                          warnings: Optional[str] = None,
                          name: str = "",
                          dut: str = "",
                          extra_data_output: str = "extra",
                          user_data: Optional[dict] = None)
```

- `stream` - Stream where the output text is written to. If stream is None, the default, sys.stderr is used as the output stream.
- `descriptions: bool`
- `verbosity: int` - Controls level of printed details (2 = more details, ...).
- `failfast: bool`  - Stop the test run on the first error or failure.
- `buffer: bool` - The standard output and standard error streams are buffered during the test run. Output during a passing test is discarded. Output is echoed normally on test fail or error and is added to the failure messages.
- `warnings: Optional[str]` - The `warnings` argument specifies the warning filter that should be used while running the tests. If it’s not specified, it will remain None if a -W option is passed to python (see Warning control), otherwise it will be set to `'default'`.
- `name: str` - Name of the test suite.
- `dut: str` - Name of the device under test.
- `extra_data_output: str` - Path were extra test artifacts are stored (e.g. images).
- `user_data: dict` - Dictionary with additional information rendered as an table in the output reports.

### Standard Execution

To perform a standard test run, use the `run()` method. This method executes the test logic within the provided suite and returns a detailed result object.

```python
loader = brunhilda.BRunhildaTestLoader()
suite = loader.discover('.', pattern='test*.py')
result = runner.run(suite)
```

### Test Evaluation Flow

#### Standard Tests

Fail-Fast per Method: A standard test method executes sequentially. The very first failed assertion (assertEqual, assertTrue, etc.) or uncaught exception immediately terminates that test method.

#### Tests with Subtests

Continuance on Failure: When using the with subTest context manager, a failure inside the block does not stop the execution of the test method.

The overall test outcome is determined by the highest severity status: $\text{ERROR} > \text{FAILED} > \text{PASSED}$, but you will get a detailed report for every single iteration.

#### Mixed Mode (Subtests + Regular Assertions)

If you combine both subtests and top-level (regular) assertions within a single test method, the behavior depends strictly on where the failure occurs:

- **Failure inside a SubTest**: The failure is logged, but execution continues. The runner will execute any subsequent sub-tests or regular assertions further down the method.
- **Failure in a Regular Assertion**: If a top-level assertion fails, the entire test method terminates immediately. Any sub-tests or code placed after this failed regular assertion will not be executed at all.

The final status of the entire test is depicted in the matrix below:

| Subtest(s) Status | Regular Assertion Status | Overall Test Outcome |
|------------------ | ------------------------ | -------------------- |
| All Passed        | Passed                   | `PASSED`             |
| 1+ Failed         | Passed                   | `FAILED`             |
| 1+ Errored        | Passed                   | `ERROR`              |
| 1+ Skipped        | Passed                   | `PASSED`             |
| 1+ Failed         | Errored                  | `ERROR`              |
| 1+ Errored        | Failed                   | `FAILED`             |
| All Passed        | Skipped                  | `SKIPPED`            |
| All Passed        | Failed                   | `FAILED`             |
| All Passed        | Errored                  | `ERROR`              |

> In short, subtest outcomes determine the final status only when all regular assertions pass. Otherwise, the status of the first unpassed regular assertion is used as the result for the entire test.

### Dry run

Test suite `dryrun` allows to generate artifacts without actually executing the tests. This is useful when you want
to create the reports and do not want to execute the entire test suite.

```python
loader = brunhilda.BRunhildaTestLoader()
suite = loader.discover('.', pattern='test*.py')
result = runner.dryrun(suite)
```

### Test Run Artifacts

In addition to the text execution log, BRunhilda support several additional artifacts.

```python
brunhilda.BRunhilda.save_issues(result, path: str) -> None
```

stores list of Failures and Errors from the `result` to the `path`. Format of the files is YAML or JSON based on the
suffix of the `path`.

```python
brunhilda.BRunhilda.save_tests(result, path: str) -> None
```

stores list of all tests from the `result` to the `path`. Format of the files is YAML or JSON based on the
suffix of the `path`.

```python
brunhilda.BRunhilda.save_junit_report(result, path: str) -> None
```

stores test execution report for given `result` in jUnit XML format.

```python
brunhilda.BRunhilda.save_html_report(result, path: str) -> None
```

stores test execution report for given `result` in HTML format.

## Test Execution Example

```python
import sys
import brunhilda

# create the test runner
runner = brunhilda.BRunhilda(user_data={'version': '1.0.0'},
                             verbosity=3,
                             stream=sys.stdout,
                             name='system',
                             dut='MMI2',
                             extra_data_output="dev/extra")

# create the test loader
loader = brunhilda.BRunhildaTestLoader()

# test discovery
suite = loader.discover('.', pattern='test*.py', top_level_dir=None, tag_filter=None)

# running the tests
result = runner.run(suite)

# save artifacts
runner.save_issues(result, path)
runner.save_tests(result, path)
runner.save_junit_report(result, path)
runner.save_html_report(result, path)
```

## Tests  Justification

File produced by `brunhilda.BRunhilda.save_issues` can hold information about *justified* test issue. Test issue
which is identified as a false-positive (e.g. failure of the testing system) is marked with `justified: 'yes'` and
`comment` explaining justification. One issue can be tracked with multiple Bug IDs, to split comment for each use `\n` for adding a new row.

Not justified issue record:

```yaml
- bug-id: ''
  comment: ''
  justified: ''
```

Justified issue record:

```yaml
- bug-id: '#123, #321'
  comment: 'Known issue \n Implementation issue (on a new line)'
  justified: 'yes'
```

The ticket number for tracking can also be entered during justification. Together with [bugtraq file](#bugtraq-file) load in reporter, you can achieve clickable Bug IDs (link to ticketing system).

## Reporting

BRunhilda Reporter supports the creation of advanced reports allowing to combine test runs into a single report file.

```python
class brunhilda.reporter.Reporter(user_data: Dict[str, str] = {},
                                  user_stories: List[Item] = [])
```

Reporter class `user_data` dictionary is rendered as a table at the top of produced reports. `user_stories` is a list of [doorstop](https://doorstop.readthedocs.io/en/latest/) item requirements.

### Methods

- `brunhilda.reporter.Reporter.load_tests` loads test execution artifact created by `brunhilda.BRunhilda.save_tests` method and store tests html report created by `brunhilda.BRunhilda.save_html_report`.
- `brunhilda.reporter.Reporter.load_issues` loads test execution artifact created by `brunhilda.BRunhilda.save_issues` method.
- `brunhilda.reporter.Reporter.load_requirements_list` loads requirements from list.
- `brunhilda.reporter.Reporter.load_out_of_scope_requirements_list` loads out of scope requirements from list.
- `brunhilda.reporter.Reporter.load_requirements` loads requirements from [file](#requirements-file).
- `brunhilda.reporter.Reporter.load_features` loads features linked to the individual tests.
- `brunhilda.reporter.Reporter.load_bugtraq` loads bugtraq configuration [file](#bugtraq-file).
- `brunhilda.reporter.Reporter.justify_tests` processes loaded tests and issues and applies the justifications.
- `brunhilda.reporter.Reporter.print_justified_record` regenerates HTML test record with updated tests results after justification.
- `brunhilda.reporter.Reporter.print_issue_list` creates a report with all issues and justifications.
- `brunhilda.reporter.Reporter.print_test_plan` creates a test plan report.
- `brunhilda.reporter.Reporter.print_requirements_summary` creates requirements summary report.
- `brunhilda.reporter.Reporter.print_user_stories_summary` creates user stories summary report.
- `brunhilda.reporter.Reporter.print_test_summary` creates a test summary report.
- `brunhilda.reporter.Reporter.print_feature_summary` creates a feature summary report.
- `brunhilda.reporter.Reporter.add_index_link` adds not generated file link to index page.
- `brunhilda.reporter.Reporter.print_index` creates an index file referencing all files yet created.

Reporter instance **doesn't allow** to create reports with just part of the tests (eg. load tests → justify → print reports → load tests → justify → print reports). Similar behaviour can be achieved using multiple reporter instances and using reporters method `add_index_link`.

> [!IMPORTANT]
> It is important to keep the order
>
> 1. load tests,
> 2. load issues, requirements, bugtraq,
> 3. load features,
> 4. justify,
> 5. print justified test record
> 6. print test plan report,
> 7. print issues report,
> 8. print rest of reports,
> 9. add links to index page,
> 10. print index.

```python
reporter = brunhilda.reporter.Reporter(user_data={'version': '1.1.2', 'reporter': 'Marry Poppins'},
                                       user_stories=[doorstop.Item])
reporter.load_tests('tests_run_1.yaml', 'test_run_1_report.html')
reporter.load_tests('tests_run_2.yaml', 'test_run_2_report.html')
reporter.load_issues('issues_run_1.yaml')
reporter.load_issues('issues_run_2.yaml')
reporter.load_requirements('requirements.json')
reporter.load_bugtraq('.bugtraq')
reporter.load_features('features.yaml')
reporter.justify_tests()
reporter.print_justified_record('tests_run_1.yaml', 'test_run_1_report_justified.html')
reporter.print_test_plan('plan.html', preamble='preamble.html')
reporter.print_issue_list('issues.html')
reporter.print_requirements_summary('requirements.html', preamble=['preamble1.html', 'preamble2.html'])
reporter.print_test_summary('tests.html')
reporter.print_feature_summary('features.html')
reporter.add_index_link('table.xlsx', 'Table')
reporter.print_index('index.html')
```

Dry run results can be combined with actually executed tests, this is usefull in a situation where the customer requests only a part of the suite. Keep in mind that the dry run and executed suite **must be disjoint**.

```python
executed_suite = loader.discover('dev', pattern='test*.py', tag_filter='priority!=high || !priority')
dryrun_suite = loader.discover('dev', pattern='test*.py', tag_filter='priority==high')
...
reporter.load_tests('dev/dry_run_tests.yaml', Path('dev/dry_run_report.html'))
reporter.load_tests('dev/executed_tests.yaml', Path('dev/report.html'))
```

### Requirements File

BRunhilda Reporter can load requirements from JSON/YAML file, where keys are requirements IDs.

Requirement is set as out of scope if contains `out-of-scope` key. Value of this key specifies reason why is out of scope (can be empty string).

In following example only the first requirement is in scope.

```json
{
    "INTF_001.3": {},
    "INTF_001.4": {
        "out-of-scope": ""
    },
    "INTF_001.5": {
        "out-of-scope": "This requirement can't be tested on our site"
    }
}
```

> Tests can be linked to requirements using the `@spec` tag.


### Features File

BRunhilda supports linking DUT features to individual test requirements. Each feature can contain a number of requirements. Features linked to a specific requirement are evaluated based on the tests covering that requirement. Features are described in YAML with the following structure:

```yaml
feature group 1:            # group of features
- feature A:                # feature A
    link:
      MMI_PGF_G04:          # name of the specification used in test @spec tag
        bc:                 # additional specification parameter name (sub-test parameter)
        - 9.E               # additional specification parameter value (sub-test parameter)
        - 9.*               # additional specification parameter value wildcard (sub-test parameter)
      MMI_PGF_L21_4: {}     # specification without additional parameter
    order: 8100             # numerical order
- feature B:
    ...
feature group 2:
- feature C:
    ...
```

### Bugtraq File

The `.bugtraq` file is used to automatically recognize bug IDs in reports and convert them into clickable HTML links. The file uses the standard INI configuration format with subsections. The concept is based on the original [bugtraq](https://github.com/mstrap/bugtraq), but some optional keys are omitted that would be redundant for BRunhilda's purpose.

#### File Structure

Each bug tracker is defined in a separate section with a unique name (each section must begin with the word bugtraq):

```ini
[bugtraq "tracker_name"]
key = value
```

#### Mandatory Fields

- `url` - The target URL of your bug tracker. It must contain the `%BUGID%` placeholder where the actual bug ID will be inserted.
- `logregex` - A regular expression used to find and isolate the bug ID itself. If it contains a capturing group `()`, only the content of the first group will be used as the `%BUGID%`.

#### Optional Fields

- `loglinkregex` - A regular expression for a broader pre-selection of text that should be completely wrapped in the HTML link (e.g., including a hash symbol `#`). If this parameter is missing, the link will wrap the text found directly by `logregex`.
- `projects` - A comma-separated list of project keys (commonly used for Jira). You can then use the `%PROJECT%` macro in logregex or loglinkregex, and the generator will automatically expand it into a list of these projects.

#### Examples

``` ini
# Two-step search
[bugtraq "redmine"]
url = https://redmine.company.com/issues/%BUGID%
loglinkregex = "#\d+"
logregex = \d+

# %PROJECT% macro
[bugtraq "jira"]
url = https://company.atlassian.net/browse/%BUGID%
projects = PROJA, PROJB
logregex = %PROJECT%-\d+

# Capturing Groups ()
[bugtraq "legacy-tracker"]
url = https://legacy.company.com/tickets?id=%BUGID%
logregex = BUG-(\d+)
```

### Evaluation Policy

BRunhilda supports multiple polices for feature and requirement evaluation.

| Policy            | Description                                                                                                                                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| STRICT (default)  | Evaluates results according to strict priority order: `ERRORED` > `UNEXPECTED-SUCCESS` > `FAILED` > `EXPECTED-FAILURE`* > `SKIPPED`* > `JUSTIFIED` > `PASSED`. The first one to match will determine the outcome. |
| ALL_PASS          | Feature / requirement is `PASSED` only if all results are `PASSED`, `SKIPPED` or `JUSTIFIED`, otherwise feature is `FAILED`.                                                                                                       |
| ONE_PASS          | Feature / requirement is `PASSED` if at least one result is `PASSED`, otherwise feature is `FAILED`.                                                                                                                            |
| LENIENT           | Feature / requirement is `PASSED` if at least one result is `PASSED` and there aren't any `FAILED` or `ERRORED` results.                                                                                                        |
| MAJORITY          | Feature / requirement is result as same as the most common result. In case of tie the priority order decides: `ERRORED` > `UNEXPECTED-SUCCESS` > `FAILED` > `EXPECTED-FAILURE` > `SKIPPED` > `JUSTIFIED` > `PASSED`             |
| THRESHOLD         | Feature / requirement is `PASSED` if share of `PASSED` result is equal or greater than 80 %. If all tests are `SKIPPED`, result is `SKIPPED`. Otherwise result is `FAILED`.                                     |

*\* = All results*

> [!NOTE]
> These two feature / requirement results cannot be affected by evaluation policy:
>
> - If feature / requirement doesn't have any test, the result is `NOT-COVERED`.
> - If feature / requirement have all tests not executed, the result is `NOT-EXECUTED`.

#### Custom Evaluation Policy

Custom policy can be used instead of defined ones. Conditions:

- Function must have one parameter `List[str]` (list of test results)
- Function must resturn string which corresponds to one of possible results (`PASSED`, `FAILED`, `ERRORED`, `SKIPPED`, `EXPECTED-FAILURE`, `UNEXPECTED-SUCCESS`, `JUSTIFIED`, `NOT-EXECUTED`, `NOT-COVERED`)

#### Evaluation Policy Example

``` Python
import brunhilda

def my_policy(results: List[str]) -> str:
    if 'FAILED' in results:
        return 'FAILED'
    return 'PASSED'

reporter = brunhilda.reporter.Reporter()
# load tests, load issues, etc.
reporter.print_feature_summary('dev/features_custom_policy.html', evaluation_policy=my_policy)
reporter.print_feature_summary('dev/features_threshold_policy.html', evaluation_policy=brunhilda.CoveragePolicy.THRESHOLD)
reporter.print_feature_summary('dev/features_default_policy.html')  # STRICT policy will be used
```

### Custom Colors

BRunhilda Reporter supports custom color pallete for pie charts. In generated html files are constants for each pie chart (`colorPaletteTestResult`, `colorPaletteTestExecution`, `colorPaletteTestLevels`) which defines colors for relevant pie chart.

```html
<script id="color_palette">
  const colorPaletteTestResult = {
      passed: 'green',
      failed: '#dc0000',
      errored: '#a700d1',
      justified: 'orange',
      skipped: '#74ad09',
      expectedFailure: '#4000f0',
      unexpectedSuccess: '#00c8c8',
      notExecuted: '#808080'
  };

  const colorPaletteTestExecution = {
      automatic: 'CornflowerBlue',
      manual: 'green',
      notspecified: 'red'
  };

  const colorPaletteTestLevels = {
      component: 'CornflowerBlue',
      module: 'Chocolate',
      system: 'Coral',
      visual: 'DarkKhaki'
  };
</script>
```

To change color palette, the constant need to be **updated** in report preamble. In case that any execution or level is missing in default color palette, the missing one can be added to the dict with lowercase key name without spaces.

```html
<!-- preamble.html -->
<script>
  colorPaletteTestResult.passed = 'black'
  colorPaletteTestExecution.notspecified = '#A9A9A9'
  colorPaletteTestLevels.undefinedlevel = 'yellow'
</script>
```

Setting the preamble:

```py
reporter.print_test_summary('tests.html', preamble="preamble.html")
```

### Doorstop Requirements

BRunhilda supports linking the doorstop requirements to the individual tests. Doorstop requirements are described
in YAML with the following structure:

```yaml
active: true
derived: false
enabled: true                 # indicates activity status of the requirement
header: |                     # gives the name of the requirement header
  header name
level: 1.0
links: []                     # gives the link to the children requirements / specs / test cases
normative: true
ref: ''
reviewed:
text: |
  As a User, I want a BRunhilda to support a doorstop requirements, so that I can nicely publish requirements links with individual tests.
```
