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
from gi.repository import Gdk, GObject, Gtk, GtkSource

from norka.models import Page


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/editor_view.ui")
class EditorView(Gtk.Box):
    __gtype_name__ = "EditorView"

    text_view: GtkSource.View = Gtk.Template.Child()
    _buffer: GtkSource.Buffer
    # completion: GtkSource.Completion = Gtk.Template.Child()

    _page: Page | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        language_manager = GtkSource.LanguageManager.get_default()
        language = language_manager.get_language("markdown")

        self._buffer = GtkSource.Buffer()
        self._buffer.set_language(language)
        self.text_view.set_buffer(self._buffer)

    @GObject.Property
    def page(self) -> Page | None:
        return self._page

    @page.setter
    def page(self, page: Page | None):
        self._page = page

        self._buffer.set_text(page.text)

    @Gtk.Template.Callback
    def _on_key_pressed(
        self,
        controller: Gtk.EventControllerKey,
        keyval: int,
        keycode: int,
        state: Gdk.ModifierType,
    ) -> bool:
        return Gdk.EVENT_PROPAGATE
