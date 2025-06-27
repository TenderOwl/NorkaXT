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
from typing import List

from gi.repository import Gio, GObject, Gtk

from norka.models.workspace import Workspace
from norka.widgets.workspace_card import WorkspaceCard

EMPTY_STACK_PAGE = "empty-view"
CONTENT_STACK_PAGE = "content-view"


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/workspace_view.ui")
class WorkspaceView(Gtk.Box):
    __gtype_name__ = "WorkspaceView"

    _workspaces: List[Workspace]

    screens: Gtk.Stack = Gtk.Template.Child()
    grid_view: Gtk.GridView = Gtk.Template.Child(name="grid_view")
    selection_model: Gtk.NoSelection = Gtk.Template.Child()
    workspaces_store: Gio.ListStore = Gtk.Template.Child()

    def __init__(self, workspaces: List[Workspace] = None):
        super().__init__()
        self._workspaces = workspaces or []

        self.grid_view.remove_css_class("view")

    @GObject.Property
    def workspaces(self) -> List[Workspace]:
        return self._workspaces

    @workspaces.setter
    def workspaces(self, workspaces: List[Workspace]):
        self._workspaces = workspaces

        if not self._workspaces:
            self.screens.set_visible_child_name(EMPTY_STACK_PAGE)
        else:
            self.screens.set_visible_child_name(CONTENT_STACK_PAGE)

        self.workspaces_store.remove_all()
        for workspace in self._workspaces:
            self.workspaces_store.append(workspace)

    @Gtk.Template.Callback()
    def _on_item_setup(self, factory: Gtk.ListItemFactory, list_item: Gtk.ListItem):
        list_item.set_child(WorkspaceCard())

    @Gtk.Template.Callback()
    def _on_item_bind(self, factory: Gtk.ListItemFactory, list_item: Gtk.ListItem):
        item = list_item.get_item()
        workspace_card = list_item.get_child()
        workspace_card.workspace = item
