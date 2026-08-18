import json
from pathlib import Path

from bs4 import BeautifulSoup


def customize_issues(issues_file: Path) -> None:
    # Justify failed test
    with open(issues_file, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        data['failures'][0]['justified'] = 'yes'
        data['failures'][0]['bug-id'] = 'SDHW-052'
        data['failures'][0][
            'comment'
        ] = 'The possibility to connect to the SmartDevice device from external network is enabled on stag environment.'
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def test_issue_in_issues_list_is_justified(generated_reports: dict[str, BeautifulSoup]):
    """
    GIVEN generated HTML reports where a test failure has been justified.
    WHEN inspecting the issues list report ('issues.html').
    THEN the issue row should have the 'issue--justified' CSS class and display
         the expected bug ID, justification status, and comment.
    """
    soup = generated_reports['issues']
    justified_test_row = soup.tbody.tr

    assert 'issue--justified' in justified_test_row.get('class')

    justified_test_columns = [td.get_text(strip=True) for td in justified_test_row.find_all('td')]

    assert justified_test_columns[
        -1
    ] == 'The possibility to connect to the SmartDevice device from external network is enabled on stag environment.'
    assert justified_test_columns[-2] == 'yes'
    assert justified_test_columns[-3] == 'SDHW-052'


def test_test_summary_tables(generated_reports: dict[str, BeautifulSoup]):
    """
    GIVEN generated HTML reports where a test failure has been justified.
    WHEN inspecting the test summary report ('tests.html').
    THEN the run summary counters accurately reflect passed, failed, justified tests and subtests,
         and the main test row correctly displays 'JUSTIFIED' status with associated bug details.
    """
    soup = generated_reports['tests']

    # Validate Summary table
    summary_table_passed_subtests = soup.select_one('tr.run-summary--passed').find_all('td')
    summary_table_justified_subtests = soup.select_one('tr.run-summary--justified').find_all('td')
    summary_table_failed_subtests = soup.select_one('tr.run-summary--failed').find_all('td')

    assert summary_table_passed_subtests[0].get_text(strip=True) == '0'
    assert summary_table_passed_subtests[1].get_text(strip=True) == '3'

    assert summary_table_failed_subtests[0].get_text(strip=True) == '0'
    assert summary_table_failed_subtests[1].get_text(strip=True) == '0'

    assert summary_table_justified_subtests[0].get_text(strip=True) == '1'
    assert summary_table_justified_subtests[1].get_text(strip=True) == '1'

    # Validate Tests Summary table
    main_table_test_row = soup.select_one('table.summary.table--wide.resizable-table tbody').tr

    assert 'test--justified' in main_table_test_row.get('class')

    main_table_test_row_cols = main_table_test_row.find_all('td')

    assert main_table_test_row_cols[4].get_text(strip=True) == 'JUSTIFIED'
    assert main_table_test_row_cols[6].get_text(strip=True) == 'SDHW-052'
    assert main_table_test_row_cols[7].get_text(
        strip=True
    ) == 'The possibility to connect to the SmartDevice device from external network is enabled on stag environment.'


def test_test_case_justification_in_features_summary(generated_reports: dict[str, BeautifulSoup]):
    """
    GIVEN generated HTML reports where a test failure has been justified.
    WHEN inspecting the feature summary report ('features.html').
    THEN the summary table shows correct number of justified features,
         the feature row and test case cells carry the 'feature--justified' class,
         and individual subtest list items render appropriate status icons (passed vs. justified).
    """
    soup = generated_reports['features']

    # Validate Summary table
    summary_table_passed_features = soup.select_one('tr.run-summary--passed').find_all('td')
    summary_table_justified_features = soup.select_one('tr.run-summary--justified').find_all('td')
    summary_table_failed_features = soup.select_one('tr.run-summary--failed').find_all('td')

    assert summary_table_passed_features[0].get_text(strip=True) == '0'
    assert summary_table_failed_features[0].get_text(strip=True) == '0'
    assert summary_table_justified_features[0].get_text(strip=True) == '1'

    # Validate Features Summary table
    main_table_feature_row = soup.select_one('table.summary.table--wide tbody').tr
    feature_name_cell = main_table_feature_row.find('td')
    test_case_cell = main_table_feature_row.find_all('td')[-1]

    assert 'feature--justified' in feature_name_cell.get('class')
    assert 'feature--justified' in test_case_cell.get('class')

    test_cases = test_case_cell.select_one('div.collapsible__content').ul.find_all('li')

    assert 'fa-check' in test_cases[0].i.get('class')
    assert 'passed' == test_cases[0].i.get('title')

    assert 'fa-check' in test_cases[1].i.get('class')
    assert 'passed' == test_cases[1].i.get('title')

    assert 'fa-check' in test_cases[2].i.get('class')
    assert 'passed' == test_cases[2].i.get('title')

    assert 'fa-magnifying-glass' in test_cases[3].i.get('class')
    assert 'justified' == test_cases[3].i.get('title')
