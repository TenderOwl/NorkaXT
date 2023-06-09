# MIT License
#
# Copyright (c) 2023 Andrey Maksimov
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

from gi.repository import Adw
from gi.repository import Gtk, Gdk

from norkaxt.widgets.note_view_column import NoteViewColumn
from norkaxt.widgets.notes_list_column import NotesListColumn
from norkaxt.widgets.sidebar_column import SidebarColumn


@Gtk.Template(resource_path='/com/tenderowl/norka/ui/content_page.ui')
class ContentPage(Gtk.Box):
    __gtype_name__ = 'ContentPage'

    flap: Adw.Flap = Gtk.Template.Child()
    note_view_column: NoteViewColumn = Gtk.Template.Child()
    notes_list_column: NotesListColumn = Gtk.Template.Child()
    sidebar_column: SidebarColumn = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.notes_list_column.props.sidebar_toggled = self.flap.get_reveal_flap()
