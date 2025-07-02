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

from norka.models import Workspace
from norka.models.workspace_service import WorkspaceService
from norka.widgets.content_view import ContentView
from norka.widgets.sidebar import Sidebar


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/content_page.ui")
class ContentPage(Adw.BreakpointBin):
    __gtype_name__ = "ContentPage"

    _workspace: Workspace | None = None

    sidebar_container: Adw.NavigationPage = Gtk.Template.Child()
    sidebar: Sidebar = Gtk.Template.Child()
    content_view: ContentView = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._workspace_service = WorkspaceService.get_default()

    @GObject.Property
    def workspace(self) -> Workspace | None:
        return self._workspace

    @workspace.setter
    def workspace(self, workspace: Workspace):
        self._workspace = workspace
        if workspace:
            self.sidebar_container.set_title(self._workspace.name_with_icon)
