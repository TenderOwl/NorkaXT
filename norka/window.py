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

from gi.repository import Adw, GLib, Gtk

from norka.models.workspace_service import WorkspaceService
from norka.widgets.add_workspace_dialog import AddWorkspaceDialog
from norka.widgets.main_view import MainView
from norka.widgets.sidebar import Sidebar
from norka.widgets.workspace_view import WorkspaceView

WORKSPACES_STACK_PAGE = "workspaces-view"
CONTENT_STACK_PAGE = "content-view"


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/window.ui")
class NorkaWindow(Adw.ApplicationWindow):
    __gtype_name__ = "NorkaWindow"

    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    screens: Gtk.Stack = Gtk.Template.Child()
    workspace_view: WorkspaceView = Gtk.Template.Child()
    sidebar: Sidebar = Gtk.Template.Child()
    main_view: MainView = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.workspace_service = WorkspaceService.get_default()
        self.workspace_service.connect("workspace-created", lambda _, workspace: GLib.idle_add(self._get_workspaces))
        self.workspace_service.connect("workspace-updated", lambda _, workspace: GLib.idle_add(self._get_workspaces))
        self.workspace_service.connect("workspace-deleted", lambda _, workspace, deleted: GLib.idle_add(self._get_workspaces))

        GLib.idle_add(self._get_workspaces)

    def add_toast(self, toast: Adw.Toast):
        self.toast_overlay.add_toast(toast)

    def _get_workspaces(self):
        workspaces = self.workspace_service.get_all_workspaces()
        self.workspace_view.workspaces = workspaces

    @Gtk.Template.Callback()
    def _on_add_workspace_clicked(self, button: Gtk.Button):
        dialog = AddWorkspaceDialog()
        dialog.connect("workspace-created", self._on_workspace_created)
        dialog.present(self)

    def _on_workspace_created(self, sender, workspace_name, emoji, cover):
        print(workspace_name, emoji)
        self.workspace_service.create_workspace(workspace_name,icon=emoji, cover=cover)
