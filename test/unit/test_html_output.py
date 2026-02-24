import os
from unittest.mock import mock_open, patch

import colorama
import pytest

from brunhilda.outputs.html_output import HtmlOutput


class TestHtmlOutput:

    # --- Tests for __init__ and preamble load ---

    def test_init_no_preamble(self):
        output = HtmlOutput()
        assert output._include_preamble == ''
        assert output.path == 'output.html'

    def test_init_single_preamble_file(self):
        fake_content = '<div>My Preamble</div>'
        with patch('builtins.open', mock_open(read_data=fake_content)) as mock_file:
            output = HtmlOutput(preamble='header.html')

            assert output._include_preamble == fake_content
            mock_file.assert_called_once_with('header.html', encoding='utf-8')

    def test_init_multiple_preamble_files(self):
        with patch('builtins.open', mock_open()) as mock_file:
            handlers = [
                mock_open(read_data='<p>Part 1</p>').return_value,
                mock_open(read_data='<p>Part 2</p>').return_value
            ]
            mock_file.side_effect = handlers

            output = HtmlOutput(preamble=['file1.html', 'file2.html'])

            assert output._include_preamble == '<p>Part 1</p><p>Part 2</p>'

    # --- Tests for _format_doc ---

    def test_format_doc_none_or_invalid(self):
        output = HtmlOutput()
        assert output._format_doc(None) == ''
        assert output._format_doc(123) == ''

    def test_format_doc_simple_rst(self):
        output = HtmlOutput()
        docstring = """
        Title
        =====
        Some *bold* text.
        """
        html = output._format_doc(docstring)

        assert 'Title' in html
        assert 'Some <em>bold</em> text' in html or 'Some <i>bold</i> text' in html  # záleží na verzi docutils

    def test_format_doc_indentation_fix(self):
        output = HtmlOutput()
        docstring = """
        Line 1
          Line 2 indented
        """
        html = output._format_doc(docstring)
        assert 'Line 1' in html
        assert 'Line 2 indented' in html

    @pytest.mark.parametrize(
        'docstring, expected_output', [
            (
                '        | Connect the P1P2 simulator device and add Hydro slave device, then start the initial communication\n'
                '          between the simulated Hydro and DUT and wait for the state NORMAL in DUT.\n'
                '        | Launch the debug GUI tool.',
                '<div class="line-block">\n<div class="line">Connect the P1P2 simulator device and add Hydro slave device, then start the initial communication\nbetween the simulated Hydro and DUT and wait for the state NORMAL in DUT.</div>\n<div class="line">Launch the debug GUI tool.</div>\n</div>'
            ),
            ('    Step one\n    Step two', '<p>Step one\nStep two</p>'),
            ('    Text with trailing space   \n    Second line  ', '<p>Text with trailing space\nSecond line</p>'),
            ('    Expected values are in range 5-10.', '<p>Expected values are in range 5-10.</p>'),
            ('    Link to parameter *.', '<p>Link to parameter *.</p>'),
            (
                '    Check if **DHW_reheatFG** is set to *True*.',
                '<p>Check if <strong>DHW_reheatFG</strong> is set to <em>True</em>.</p>'
            ),
            (123, ''),
        ]
    )
    def test_format_doc_test_steps(self, docstring, expected_output):
        output = HtmlOutput()
        html = output._format_doc(docstring)
        if expected_output == '':
            assert html == ''
        else:
            assert expected_output in html

    # --- Tests for _format_logging ---

    def test_format_logging(self):
        output = HtmlOutput()
        log_text = '2023-01-01 10:00:00 - root - INFO - Application started\n' \
                   '2023-01-01 10:00:01 - root - ERROR - Something went wrong'

        html = output._format_logging(log_text)
        print(html)
        expected_info = '<span class="log log--info">'
        expected_error = '<span class="log log--error">'

        assert expected_info in html
        assert expected_error in html
        assert 'Application started' in html

    # --- Tests for _format_terminal ---

    def test_format_terminal_simple_color(self):
        """Tests simple color transfer"""
        output = HtmlOutput()
        text = f'{colorama.Fore.RED}Error occurred{colorama.Fore.RESET}'

        html = output._format_terminal(text)

        assert '<span class="fore fore--red">' in html
        assert 'Error occurred' in html
        assert '</span>' in html

    def test_format_terminal_nested_colors(self):
        """Tests nested colors and their reset"""
        output = HtmlOutput()
        text = f'{colorama.Fore.RED}Red {colorama.Back.GREEN}GreenBG{colorama.Back.RESET} RedAgain{colorama.Fore.RESET}'

        html = output._format_terminal(text)

        assert '<span class="fore fore--red">' in html
        assert '<span class="back back--green">' in html

        assert html.count('<span class="fore fore--red">') >= 2

    def test_format_terminal_unknown_sequence(self):
        output = HtmlOutput()
        # Some fancy ANSI sequence
        text = 'Start \033[999mUnknown\033[0m End'

        html = output._format_terminal(text)

        assert 'Start' in html
        assert 'Unknown' in html
        assert 'End' in html
        assert '\033[' not in html

    def test_format_terminal_reset_all(self):
        output = HtmlOutput()
        text = f'{colorama.Fore.RED}{colorama.Back.BLUE}Text{colorama.Style.RESET_ALL}'

        html = output._format_terminal(text)

        assert html.count('<span') == 2
        assert html.count('</span>') == 2
