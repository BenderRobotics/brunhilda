import json
from pathlib import Path

from bs4 import BeautifulSoup


def customize_issues(issues_file: Path) -> None:
    # Justify failed test
    with open(issues_file, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        data['failures'][4]['justified'] = 'yes'
        data['failures'][5]['justified'] = 'yes'
        data['failures'][6]['justified'] = 'yes'
        data['failures'][9]['justified'] = 'yes'
        data['failures'][10]['justified'] = 'yes'
        data['failures'][11]['justified'] = 'yes'
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def test_correct_tests_background_color_in_features_summary(generated_reports: dict[str, BeautifulSoup]):
    """
    GIVEN generated Features Summary report where are all possible test results.
    WHEN inspecting the feature summary report ('features.html').
    THEN tests background color should be correcponding to overall test result.
    """
    soup = generated_reports['features']

    feature_table = soup.find('table', class_='summary')

    expected_classes = [
        'feature-test--passed',
        'feature-test--failed',
        'feature-test--failed',
        'feature-test--errored',
        'feature-test--errored',
        'feature-test--errored',
        'feature-test--errored',
        'feature-test--errored',
        'feature-test--errored',
        'feature-test--failed',
        'feature-test--failed',
        'feature-test--justified',
        'feature-test--unexpected-success',
        'feature-test--expected-failure',
        'feature-test--skipped',
        'feature-test--passed',
    ]

    for row, expected_cls in zip(feature_table.find('tbody').find_all('tr'), expected_classes, strict=True):
        test_case = row.find_all('td')[-1]
        assert expected_cls in test_case.get('class')
