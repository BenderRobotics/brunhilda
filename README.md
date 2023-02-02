**BRunhilda** the test system
=============================

Usage
-----

Brunhilda is the test runner with advanced reporting features.

### Test Runner

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
A test runner implementation that outputs results to a stream as an extension of [`unittest.TextTestRunner`](https://docs.python.org/3/library/unittest.html#unittest.TextTestRunner).

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

#### Dry run

Test suite `dryrun` allows to generate artifacts without actually executing the tests. This is useful when you want
to create the reports and do not want to execute the entire test suite.

```python
    loader = brunhilda.BRunhildaTestLoader()
    suite = loader.discover('.', pattern='test*.py')
    result = runner.dryrun(suite)
    runner.save_issues(result, 'issues.yaml')
    runner.save_tests(result, 'tests.yaml')
    runner.save_junit_report(result, 'report.junit')
    runner.save_html_report(result, 'report.html')
```

### Extended Test Docstring format

BRunhilda introduces extended format of the test method docstring to hold the detailed information about the test in the
machine readable form.

```python
def test_01(self):
    """
    {tags}

    {description}

    {steps}
    """
```

`{tags}` field holds tagging information. Each tag consists of pair

```
@name: value
```

Multiple values are expressed as a comma separated list.

```
@name: value1, value2, value3
```

`name` can be any text starting with `@` and can not contain `:` character.

Tags representing the time may contain units. Following keywords are supported:

- `s`, `sec`, `second`, `seconds`
- `m`, `min`, `minute`, `minutes`
- `h`, `hour`, `hours`
- `d`, `day`, `days`

Examples

- `1h 1m 1s` -> 3661
- `2 hours 2 minutes 2 seconds` -> 7322

Example:

```
@execution: automatic
@exec-time: 46
@covering:
@environment: INT_ENV_MMI1, INT_ENV_MMI2, INT_ENV_VIRT
@priority: mid
```

`{description}` field holds general description of the test.

`{steps}` field holds detailed description of the test sequence. This field starts with the
`@steps` and ends with `@endsteps`. Each step in the sequence starts with the number `X)` (`1)`,
`2)`, ...). First `>` character is followed by the step action description (what is done),
second `>` character is followed by the step expectation description (what is checked).

Example:

```
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

Example:

```python
def test_01(self):
    """
    @test-id:
    @name: First test
    @maintainer: Pavel Kumpan
    @execution: automatic
    @exec-time: 46
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

### Test Loader

The TestLoader class is used to create test suites from classes and modules. This is an extension of [`unittest.TestLoader`](https://docs.python.org/3/library/unittest.html#unittest.TestLoader).

In addition to the provides extended `discover` method

```python
discover(self, start_dir, pattern='test*.py', top_level_dir=None, tag_filter=None)
```

`discover` find and return all test modules from the specified start directory, recursing into subdirectories to find
them and return all tests found within them. Only test files that match the pattern will be loaded.
(Using shell style pattern matching.)

In addition to [`unittest.TestLoader.discover`](https://docs.python.org/3/library/unittest.html#unittest.TestLoader.discover):

- multiple patterns are supported `'test_A*.py, test_B*.py'` - test files that match one of comma separated list of
  patterns will be loaded,
- tag filtering based on tags in the test description.

#### Tag-based Test Filtering

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

#### Examples

`tag1` contains `A` and `tag2` is present:

```
tag1=~A && @tag2
```

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

#### Test Failures/Errors Justification

File produced by `brunhilda.BRunhilda.save_issues` can hold information about *justified* test issue. Test issue
which is identified as a false-positive (e.g. failure of the testing system) is marked with `justified: 'yes'` and
`comment` explaining justification.

Not justified issue record:

```yaml
- bug-id: ''
  comment: ''
  justified: ''
```

Justified issue record:

```yaml
- bug-id: ''
  comment: 'Not a bug'
  justified: 'yes'
```

### Example

```python
import sys
import brunhilda

# create the test runner
runner = brunhilda.BRunhilda(user_data={'version': '1.0.0'},    # this is
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

### Reporting

BRunhilda Reporter supports creating of advanced reports allowing to combine multiple test runs into single report file.

```python
class brunhilda.reporter.Reporter(requirements: List[str] = [],
                                  user_data: Dict[str, str] = {},
                                  user_stories: List[Item] = [])
```

Reporter class. `requirements` is list of requirements ID's, `user_data` dictionary in rendered as a table in the top of
produced reports. `user_stories` is a list of [doorstop](https://doorstop.readthedocs.io/en/latest/) Item requirements.

- `brunhilda.reporter.Reporter.load_tests` loads test execution artefact created by `brunhilda.BRunhilda.save_tests` method.
- `brunhilda.reporter.Reporter.load_issues` loads test execution artefact created by `brunhilda.BRunhilda.save_issues` method.
- `brunhilda.reporter.Reporter.load_features` loads features linked to the individual tests.
- `brunhilda.reporter.Reporter.justify_tests` processes loaded tests and issues and applies the justifications.
- `brunhilda.reporter.Reporter.print_issue_list` creates report with all issues and justifications.
- `brunhilda.reporter.Reporter.print_test_plan` creates test plan report.
- `brunhilda.reporter.Reporter.print_requirements_summary` creates requirements summary report.
- `brunhilda.reporter.Reporter.print_user_stories_summary` creates user stories summary report.
- `brunhilda.reporter.Reporter.print_test_summary` creates test summary report.
- `brunhilda.reporter.Reporter.print_feature_summary` creates feature summary report.
- `brunhilda.reporter.Reporter.print_index` creates index file referencing all files yet created.

It is important to keep the order>

1. load issues, tests, features,
2. justify,
3. print reports,
4. print index.

```python
reporter = brunhilda.reporter.Reporter(requirements=['REQ_01', 'REQ_02'],
                                       user_data={'version': '1.1.2', 'reporter': 'Marry Poppins'},
                                       user_stories=[doorstop.Item])
reporter.load_tests('tests_run_1.yaml')
reporter.load_issues('issues_run_1.yaml')
reporter.load_tests('tests_run_2.yaml')
reporter.load_issues('issues_run_2.yaml')
reporter.load_features('features.yaml')
reporter.justify_tests()
reporter.print_issue_list('issues.html')
reporter.print_test_plan('plan.html', preamble='preamble.html')
reporter.print_requirements_summary('requirements.html')
reporter.print_test_summary('tests.html')
reporter.print_feature_summary('features.html')
reporter.print_index('index.html')
```

### Features

BRunhilda supports linking of the DUT features to the individual tests. Features are described in YAML with the
following structure:

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

### Doorstop requirements

BRunhilda supports linking of the doorstop requirements to the individual tests. Doorstop requirements are described
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

Contributing
------------

Here is a short guide to environment setup to ease you up contributing to the
project. Start by installing and creating virtual environment

```shell
pip install virtualenv
virtualenv venv
```

Now you should see `venv` folder in the project structure. Activate virtual
environment

```shell
source venv/bin/activate    # Linux
venv\Scripts\activate.bat   # Windows
```

After that you should see `(venv)` as prefix to your command line cursor. You
have to to repeat activation every time you close the terminal. To install
package in development mode call:

```shell
pip install -e .
```

Now you can use `BRunhilda` package directly from command line and all changes
to source code are instantly applied.
