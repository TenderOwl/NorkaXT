# MIT License
#
# Copyright (c) 2025 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# SPDX-License-Identifier: MIT
from gi.repository import Adw, Gdk, GLib, GObject, Gtk, GtkSource, Pango
from loguru import logger

from norka.models import Page


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/editor_view.ui")
class EditorView(Gtk.Box):
    __gtype_name__ = "EditorView"

    __gsignals__ = {
        "save-page": (GObject.SIGNAL_RUN_FIRST, None, (Page,)),
    }

    text_view: GtkSource.View = Gtk.Template.Child()
    _buffer: GtkSource.Buffer
    # completion: GtkSource.Completion = Gtk.Template.Child()

    _page: Page | None
    _save_timer: int | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        language_manager = GtkSource.LanguageManager.get_default()
        language = language_manager.get_language("markdown")

        self._buffer = GtkSource.Buffer()
        self._buffer.set_language(language)
        self.text_view.set_buffer(self._buffer)

        self.tag_bold = self._buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tag_italic = self._buffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.tag_underline = self._buffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        self.tag_found = self._buffer.create_tag("found", background="yellow")

        self.install_action("editor.format", "s", self._on_format_action)

    @GObject.Property
    def page(self) -> Page | None:
        return self._page

    @page.setter
    def page(self, page: Page | None):
        self._page = page

        # Stop the save timer
        if self._save_timer:
            GLib.source_remove(self._save_timer)
            self._save_timer = None

        if not page:
            return

        # Set the page content
        self._buffer.set_text(page.text or "")
        # And start the save timer for automatic saving
        self._save_timer = GLib.timeout_add_seconds(5, self._save_page)

        self._apply_styling()

    def _apply_styling(self) -> None:
        style_manager = Adw.StyleManager.get_default()
        style_scheme_manager = GtkSource.StyleSchemeManager.get_default()

        scheme_id = "norka"
        if style_manager.get_dark():
            scheme_id = f"{scheme_id}-dark"

        scheme = style_scheme_manager.get_scheme(scheme_id)
        self._buffer.set_style_scheme(scheme)

    @Gtk.Template.Callback
    def _on_key_pressed(
        self,
        controller: Gtk.EventControllerKey,
        keyval: int,
        keycode: int,
        state: Gdk.ModifierType,
    ) -> bool:
        return Gdk.EVENT_PROPAGATE

    def do_hide(self):
        logger.debug("Editor hidden")
        super().do_hide()

    def _get_text(self):
        return self._buffer.get_text(
            self._buffer.get_start_iter(), self._buffer.get_end_iter(), True
        ).strip()

    def _save_page(self):
        logger.debug("Saving page: {}", self._page)
        self._page.text = self._get_text()
        self.emit("save-page", self._page)
        return True

    def do_grab_focus(self):
        self.text_view.grab_focus()
        return True

    def _on_format_action(self, sender, action, tag_name: GLib.Variant):
        logger.debug("{}: {}", action, tag_name.get_string())
        self.apply_tag(tag_name.get_string())

    def apply_tag(self, tag_name: str):
        bounds = self._buffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self._buffer.apply_tag_by_name(tag_name, start, end)