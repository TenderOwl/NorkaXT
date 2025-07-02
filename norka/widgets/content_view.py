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

from gi.repository import Adw, GObject, Gtk

from norka.models import Workspace


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/content_view.ui")
class ContentView(Adw.Bin):
    __gtype_name__ = "ContentView"

    _workspaces: List[Workspace] = []

    flow_box: Gtk.FlowBox = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @GObject.Property
    def workspaces(self) -> List[Workspace]:
        return self._workspaces

    @workspaces.setter
    def workspaces(self, value: List[Workspace] | None):
        self._workspaces = value or []

        for workspace in self._workspaces:
            self.flow_box.append(self._new_flow_box_item(workspace))

    def _new_flow_box_item(self, workspace: Workspace):
        flow_box_item = Gtk.FlowBoxChild()
        flow_box_item.set_child(Gtk.Label(label=workspace.name))
        return flow_box_item
