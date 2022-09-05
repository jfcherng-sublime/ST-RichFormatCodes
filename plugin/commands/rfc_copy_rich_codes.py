import os
import string
import subprocess
import sys
import tempfile
import textwrap
from typing import IO

import sublime
import sublime_plugin

SYS_PLATFORM = sys.platform

if SYS_PLATFORM == "win32":
    from ..libs import winclip


def reformat(text: str) -> str:
    return textwrap.dedent(text).rstrip()


class RfcCopyRichCodesCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, open_html: bool = True) -> None:
        if not (html := self._get_html()):
            sublime.error_message(f"[{self.name()}]\nEmpty html output")
            return

        self._copy_rich_html(html, open_html)

    def _copy_rich_html(self, html: str, open_html: bool) -> None:
        if SYS_PLATFORM == "win32":
            winclip.Paste(html, type="html")
            return

        if SYS_PLATFORM == "darwin":
            file = self._write_temp_html_file(html)
            subprocess.call(f'cat "{file.name}" | pbcopy -Prefer html', shell=True)
            os.remove(file.name)
            return

        # cannot find a better way...
        sublime.set_clipboard(html)
        if open_html:
            file = self._write_temp_html_file(html)
            sublime.run_command("open_url", {"url": f"file:///{file.name}"})

    def _write_temp_html_file(self, html: str) -> IO:
        file = tempfile.NamedTemporaryFile("w", encoding="utf-8", prefix="st-", suffix=".html", delete=False)
        file.write(html)
        return file

    def _get_html(self) -> str:
        input_regions = (
            tuple(r for r in self.view.sel() if not r.empty())
            if self.view.has_non_empty_selection_region()
            else (sublime.Region(0, self.view.size()),)
        )
        html = self.view.export_to_html(regions=input_regions, minihtml=True, enclosing_tags=True)
        return self._fix_html(html)

    def _fix_html(self, html: str) -> str:
        # table can be copied to Word, PowerPoint while keeping the background color
        html = f"<table><tr><td>{html}</td></tr></table>"
        # fixes many pasting issues in Microsoft Word... don't ask me why it works ¯\_(ツ)_/¯
        html = f'<br style="line-height:0">{html}'

        style = f"<style>{self._css()}</style>"
        return f'<html><head><meta charset="utf-8">{style}</head><body>{html}</body></html>'

    def _css(self) -> str:
        css = reformat(
            """
            body {
                background-color: ${bgcolor};
                padding: 1rem;
                margin: 0;
            }
            table {
                background-color: ${bgcolor};
            }
            """
        )
        bgcolor = self.view.style().get("background", "inherit")
        return string.Template(css).substitute(bgcolor=bgcolor)
