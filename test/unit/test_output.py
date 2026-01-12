import datetime
import os
import urllib.parse
from unittest.mock import MagicMock, mock_open, patch

import jinja2
import pytest

from brunhilda.outputs.output import Output, _quote_path

# --- Tests _quote_path ---


@pytest.mark.parametrize(
    'input_path, expected_output', [
        ('folder/file.html', 'folder/file.html'),
        ('folder\\subfolder\\file.html', 'folder/subfolder/file.html'),
        ('my folder/my file.html', 'my%20folder/my%20file.html'),
        ('folder/file_ščřž.html', 'folder/file_%C5%A1%C4%8D%C5%99%C5%BE.html'),
        ('folder\\subfolder/file.html', 'folder/subfolder/file.html'),
    ]
)
def test_quote_path(input_path, expected_output):
    assert _quote_path(input_path) == expected_output


# --- Tests Output class---


class TestOutput:

    @pytest.fixture
    def output_instance(self):
        return Output()

    @patch('builtins.open', new_callable=mock_open, read_data='Template Content {{ now() }}')
    @patch('jinja2.FileSystemLoader')
    def test_load_template_success(self, mock_loader, mock_file, output_instance):
        """
        Validate that load_template:
        1. Open correct file
        2. Creates Jinja2 Environment.
        3. Returns Template object.
        4. Inject globals.
        """
        template_name = 'test_template.jinja2'

        tmpl = output_instance.load_template(template_name)

        # 1. Verifying that the file has been opened
        args, kwargs = mock_file.call_args
        assert args[0].endswith(os.path.join('templates', template_name))
        assert kwargs.get('encoding') == 'utf-8'

        # 2. Verifying that the return value is a Jinja2 Template
        assert isinstance(tmpl, jinja2.Template)

        # 3. Verifying globals injection
        # load_template adds following to 'globals': now, rel_path, join_path, dir_path, quote
        assert 'now' in tmpl.globals
        assert tmpl.globals['now'] == datetime.datetime.now

        assert 'join_path' in tmpl.globals
        assert tmpl.globals['join_path'] == os.path.join

        assert 'dir_path' in tmpl.globals
        assert tmpl.globals['dir_path'] == os.path.dirname

        assert 'quote' in tmpl.globals
        # Here we verify that the 'quote' function in the template is our _quote_path
        assert tmpl.globals['quote'] == _quote_path

        assert 'rel_path' in tmpl.globals
        assert callable(tmpl.globals['rel_path'])

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_template_file_not_found(self, mock_file, output_instance):
        with pytest.raises(FileNotFoundError):
            output_instance.load_template('non_existent.jinja2')

    @patch('builtins.open', new_callable=mock_open, read_data='Bad Syntax {{ ')
    def test_load_template_syntax_error(self, mock_file, output_instance):
        with pytest.raises(jinja2.TemplateSyntaxError):
            output_instance.load_template('broken.jinja2')
