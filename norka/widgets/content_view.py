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

from gi.repository import Adw, GObject, Gtk

from norka.models import Page
from norka.widgets.editor_view import EditorView

EMPTY_STACK_PAGE = "empty-view"
EDITOR_STACK_PAGE = "editor-view"


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/content_view.ui")
class ContentView(Adw.Bin):
    __gtype_name__ = "ContentView"

    __gsignals__ = {
        "save-page": (GObject.SIGNAL_RUN_FIRST, None, (Page,)),
    }

    toggle_sidebar_btn: Gtk.Button = Gtk.Template.Child()
    view_stack: Adw.ViewStack = Gtk.Template.Child()
    editor_view: EditorView = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.editor_view.connect("save-page", self._save_page)

    def open_page(self, page: Page):
        if not page:
            return

        self.view_stack.set_visible_child_name(EDITOR_STACK_PAGE)
        self.editor_view.page = page

    def close_page(self):
        self.view_stack.set_visible_child_name(EMPTY_STACK_PAGE)
        self.editor_view.page = None

    def _save_page(self, sender, page: Page):
        self.emit("save-page", page)
