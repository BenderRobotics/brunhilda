import colorama
from typing import Union, Sequence
from docutils.core import publish_parts

from .output import Output

class HtmlOutput(Output):
    def __init__(self, preamble: Union[Sequence[str], str, None] = None, path='output.html'):
        """
        :param preamble: path or multiple paths to file(s) to include as a preamble
        :param path: output path where to create the HTML output
        """
        self._include_preamble = ''
        self.path = path

        if preamble:
            if not isinstance(preamble, (list, tuple, set)):
                preamble = [preamble]

            for p in preamble:
                with open(p, encoding='utf-8') as f:
                    self._include_preamble += f.read()

    def _format_doc(self, description):
        """
        This method formats python docstring to HTML.
        :param str description: python docstring of the method or class
        :return: HTML string representation.
        """
        if not isinstance(description, str):
            return ""
        else:
            description = description.strip('\n')               # description without first and last new line
            lines = description.split('\n')
            indent = len(lines[0]) - len(lines[0].lstrip())     # number of spaces from the left
            lines = [line.rstrip() for line in lines]           # cut out trailing spaces
            lines = [line[indent:] for line in lines]           # cut out leading spaces
            description = '\n'.join(lines)                      # join to string again
            description = description.replace("–", "-")         # TODO - use &ndash to be correct
            description = description.replace(" *.", " \*.")
            return publish_parts(description, writer_name='html')['html_body']  # convert from RST to HTML

    def _format_logging(self, text):
        """
        Wraps output of the python logging into HTML spans with the severity classes.
        """
        formatting = {
            "DEBUG":    '<span class="log log--debug">',
            "INFO":     '<span class="log log--info">',
            "WARNING":  '<span class="log log--warning">',
            "ERROR":    '<span class="log log--error">',
            "CRITICAL": '<span class="log log--critical">',
        }

        lines = text.split('\n')
        for i in range(len(lines)):
            for f in formatting:
                # Currently only by te occurrence of the keyword in the string, is there a better way?
                if f in lines[i]:
                    lines[i] = f'{formatting[f]}{lines[i]}</span>'
        return '\n'.join(lines)

    def _format_terminal(self, text):
        """
        Converts colorama terminal output into HTML string with the classes.
        """
        formatting = {
            colorama.Fore.BLACK:   '<span class="fore fore--black">',
            colorama.Fore.RED:     '<span class="fore fore--red">',
            colorama.Fore.GREEN:   '<span class="fore fore--green">',
            colorama.Fore.YELLOW:  '<span class="fore fore--yellow">',
            colorama.Fore.BLUE:    '<span class="fore fore--blue">',
            colorama.Fore.MAGENTA: '<span class="fore fore--magenta">',
            colorama.Fore.CYAN:    '<span class="fore fore--cyan">',
            colorama.Fore.WHITE:   '<span class="fore fore--white">',
            colorama.Back.BLACK:   '<span class="back back--black">',
            colorama.Back.RED:     '<span class="back back--red">',
            colorama.Back.GREEN:   '<span class="back back--green">',
            colorama.Back.YELLOW:  '<span class="back back--yellow">',
            colorama.Back.BLUE:    '<span class="back back--blue">',
            colorama.Back.MAGENTA: '<span class="back back--magenta">',
            colorama.Back.CYAN:    '<span class="back back--cyan">',
            colorama.Back.WHITE:   '<span class="back back--white">',
            colorama.Style.DIM:    '<span class="style style--dim">',
            colorama.Style.BRIGHT: '<span class="style style--bright">',
            colorama.Style.NORMAL: '<span class="style style--normal">',
        }

        CSI = '\033['   # this is start of the ASCII escape sequences
        start = 0
        opened = []     # list of opened tags

        while start >= 0:
            pos = text.find(CSI, start)     # nex loc of the CSI
            end = text.find('m', pos) + 1   # CSI ends with 'm'
            esc = text[pos:end]             # whole escape sequence, e.g. '\033[30m' for BACK

            if esc in formatting:
                opened.append(formatting[esc])
                text = text.replace(esc, formatting[esc])
            elif esc in (colorama.Style.RESET_ALL, colorama.Fore.RESET, colorama.Back.RESET):
                n = len(opened)             # number of currently opened spans

                # check which spans will be reopened because they are not reset
                if esc == colorama.Style.RESET_ALL:
                    opened = []
                elif esc == colorama.Fore.RESET:
                    opened = [op for op in opened if "fore" not in op]
                elif esc == colorama.Back.RESET:
                    opened = [op for op in opened if "back" not in op]

                # close all open spans and reopen not reset spans
                text = text.replace(esc, ''.join(['</span>'] * n + opened))
            else:
                # remove unknown formating
                text = text.replace(esc, '')

            start = pos
        return text
