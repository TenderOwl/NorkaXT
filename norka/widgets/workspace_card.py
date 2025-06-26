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

from gi.repository import GObject, Gtk

from norka.models.workspace import Workspace


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/workspace_card.ui")
class WorkspaceCard(Gtk.Box):
    __gtype_name__ = "WorkspaceCard"

    _workspace: Workspace | None = None

    cover: Gtk.Image = Gtk.Template.Child()
    icon: Gtk.Label = Gtk.Template.Child()
    title: Gtk.Label = Gtk.Template.Child()
    updated_at: Gtk.Label = Gtk.Template.Child()

    def __init__(self, workspace: Workspace = None):
        super().__init__()
        self._workspace = workspace

        print("workspace:", workspace)
        if workspace:
            self._bind_workspace(workspace)

    @GObject.Property
    def workspace(self) -> Workspace | None:
        return self._workspace

    @workspace.setter
    def workspace(self, workspace: Workspace):
        self._workspace = workspace

    def _bind_workspace(self, workspace: Workspace):
        if workspace.icon:
            self.icon.set_label(workspace.icon)
        else:
            self.icon.set_visible(False)
        self.title.set_label(workspace.name)
        self.updated_at.set_label(f"{workspace.last_accessed}")
