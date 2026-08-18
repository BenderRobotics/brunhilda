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

    Parametrized over both datasets: the legacy `data/<version>` folder captured from the
    runner version that reported the bug, and `data/head` executed against the current code.

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

    legacy_folders = sorted(p for p in data_dir.iterdir() if p.is_dir() and p.name != 'head')
    if len(legacy_folders) != 1:
        pytest.fail(f'expected one legacy data folder in {data_dir}, found {[p.name for p in legacy_folders]}')
    legacy_folder = legacy_folders[0]

    head_folder = data_dir / 'head'

    features_yaml_path = legacy_folder / 'features.yaml'

    if data_source == 'actual_data':
        folder = tmp_path
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
