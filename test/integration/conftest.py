import sys
import unittest
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from brunhilda import BRunhilda, BRunhildaTestLoader, Reporter


@pytest.fixture(
    scope='module',
    params=['original_data', 'actual_data'],
    ids=['exec_version < reporter_version', 'exec_version == reporter_version']
)
def generated_reports(request: pytest.FixtureRequest,
                      tmp_path_factory: pytest.TempPathFactory) -> dict[str, BeautifulSoup]:
    """
    Generate the three HTML reports for one dataset and parse them with BeautifulSoup.

    This fixture is parametrized to run over two datasets:
    1. 'original_data' - legacy data captured from an older runner version.
    2. 'actual_data' - data executed against the current code in the `data/head` directory.

    If no legacy data folder is found in the `data/` directory (ignoring `head`,
    `__pycache__`, etc.), the 'original_data' run is automatically skipped via `pytest.skip`,
    effectively adapting to a single-dataset test environment.

    The `features.yaml` file is resolved dynamically, searching in `data/`, `data/head/`,
    and the legacy folder, making it suitable for both legacy and single-dataset layouts.

    A test module may define a module-level `customize_issues(issues_file: Path) -> None`
    hook. When present it is called on the freshly generated `issues.json` before the
    reports are built, which is how a test injects its own justification.

    :param request: pytest request, supplies the dataset param and the calling test module
    :param tmp_path_factory: factory for the module-scoped output directory
    :return: mapping of `issues` / `tests` / `features` to the parsed report
    """
    data_source = request.param
    tmp_path = tmp_path_factory.mktemp('reports')
    test_dir = Path(request.module.__file__).resolve().parent
    data_dir = test_dir / 'data'

    legacy_folders = sorted(p for p in data_dir.iterdir() if p.is_dir() and p.name not in ('head', '__pycache__'))
    legacy_folder = legacy_folders[0] if legacy_folders else None
    print(legacy_folder)

    if data_source == 'original_data':
        if legacy_folder is None:
            pytest.skip('Test needs just actual dataset (legacy data are skipped).')

    head_folder = data_dir / 'head' if (data_dir / 'head').exists() else data_dir

    # features.yaml search
    candidate_paths = [
        data_dir / 'features.yaml',
        head_folder / 'features.yaml',
    ]
    if legacy_folder:
        candidate_paths.append(legacy_folder / 'features.yaml')

    features_yaml_path = next((path for path in candidate_paths if path.is_file()), None)

    if not features_yaml_path:
        pytest.fail(f'features.yaml was not find in any of those locations: {candidate_paths}')

    if data_source == 'actual_data':
        folder = tmp_path

        # Reset inner loader state
        if 'test' in sys.modules:
            del sys.modules['test']
        unittest.defaultTestLoader._top_level_dir = None

        # Create suite
        runner = BRunhilda()
        loader = BRunhildaTestLoader()
        suite = loader.discover(head_folder, pattern='test.py')

        # Execute suite
        result = runner.run(suite)
        runner.save_issues(result, folder / 'issues.json')
        runner.save_tests(result, folder / 'tests.json')

        # Look for issues customization callback and call it if found
        customize_callback = getattr(request.module, 'customize_issues', None)
        if callable(customize_callback):
            customize_callback(folder / 'issues.json')
    else:
        folder = legacy_folder

    reporter = Reporter()
    reporter.load_tests(folder / 'tests.json')
    reporter.load_issues(folder / 'issues.json')
    reporter.load_features(features_yaml_path)
    reporter.justify_tests()

    issues_path = tmp_path / 'issues.html'
    tests_path = tmp_path / 'tests.html'
    features_path = tmp_path / 'features.html'

    reporter.print_issue_list(issues_path)
    reporter.print_test_summary(tests_path)
    reporter.print_feature_summary(features_path)

    return {
        'issues': BeautifulSoup(issues_path.read_text(encoding='utf-8'), 'html.parser'),
        'tests': BeautifulSoup(tests_path.read_text(encoding='utf-8'), 'html.parser'),
        'features': BeautifulSoup(features_path.read_text(encoding='utf-8'), 'html.parser'),
    }
