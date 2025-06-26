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

from gi.repository import GObject, Gtk

from norka.models.workspace import Workspace
from norka.widgets.workspace_card import WorkspaceCard


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/workspace_view.ui")
class WorkspaceView(Gtk.Box):
    __gtype_name__ = "WorkspaceView"

    _workspaces: List[Workspace]

    flow_box: Gtk.FlowBox = Gtk.Template.Child(name="flowbox")

    def __init__(self, workspaces: List[Workspace] = None):
        super().__init__()
        self._workspaces = workspaces or []

    @GObject.Property
    def workspaces(self) -> List[Workspace]:
        return self._workspaces

    @workspaces.setter
    def workspaces(self, workspaces: List[Workspace]):
        self._workspaces = workspaces

        self.flow_box.remove_all()
        for workspace in self._workspaces:
            self.flow_box.append(self._new_item(workspace))

    def _new_item(self, workspace: Workspace) -> Gtk.FlowBoxChild:
        child = WorkspaceCard(workspace=workspace)
        return Gtk.FlowBoxChild(child=child)

    @Gtk.Template.Callback
    def _on_flowbox_child_activated(self, flow_box: Gtk.FlowBox, child: Gtk.FlowBoxChild):
        workspace = child.get_child().workspace
        print("workspace selected:", workspace)
        self.emit("workspace-selected", workspace)