import os

import pytest

from brunhilda.rel_path import rel_path


@pytest.mark.parametrize(
    'base_path, target_path, expected_path', [
        ('index.html', 'style.css', os.path.join('.', 'style.css')),
        ('index.html', os.path.join('css', 'style.css'), os.path.join('css', 'style.css')),
        (os.path.join('output', 'report.html'), 'logo.png', os.path.join('..', 'logo.png')),
        (
            os.path.join('output', 'html', 'report.html'), os.path.join('assets', 'images', 'logo.png'),
            os.path.join('..', '..', 'assets', 'images', 'logo.png')
        ),
    ]
)
def test_rel_path(base_path, target_path, expected_path):
    result = rel_path(base_path, target_path)

    assert result == expected_path
