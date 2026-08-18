# **BRunhilda** the test system

Brunhilda is the test runner with advanced reporting features.

## Documentation

- [How to run tests and create test reports.](doc/producer-guide.md)
- [How to read test reports.](doc/consumer-guide.md)

## Contributing

Here is a short guide to the environment setup to ease you up contributing to the
project. Start by installing and creating a virtual environment

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

After that you should see `(venv)` as a prefix to your command line cursor. You
have to repeat activation every time you close the terminal. To install the
package in development mode call:

```shell
pip install -e .
```

If you want to use Brunhilda for user stories defined by doorstop artifacts then install BRunhilda by calling a command below. Please note that BRunhilda with doorstop feature requires **Python >= 3.9**.

```shell
pip install -e .[doorstop-user-stories]
```

Now you can use `BRunhilda` package directly from the command line and all
changes to the source code are instantly applied.

### Testing

The project includes both unit tests and integration tests.

#### Integration Tests

Most reporting issues stem from backward-compatibility bugs—specifically when generating reports from datasets produced by older runner versions. To prevent regressions, integration tests are executed against **two datasets**:

1. **Original Dataset (`<runner_version>`):** Anonymized execution data captured from the specific runner version where the bug was reported.
2. **Current Dataset (`head`):** Fresh execution data generated dynamically by running sample tests on the current version.

##### Directory Structure

Integration tests are organized by bug tickets (`test/integration/<bug_ticket_number>/`):

```text
test/integration/14492/
├── test_14492_report_generation.py
└── data/
    ├── 2.8.1/    # Original data from the bug ticket
    └── head/      # Data generated from current execution
```

### Visual Studio Code tasks

To speed up the execution of useful operations for development, vscode tasks are implemented.

- `static-type-check` Static type checking using `mypy`
- `test-with-coverage` Running unit tests including measuring code coverage.

> Tasks can be run within vscode `Terminal -> Run Tasks...`
