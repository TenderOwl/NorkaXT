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

from gettext import gettext as _

from loguru import logger
import humanize
from gi.repository import Gio, GObject, Gtk

from norka.models.workspace import Workspace


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/workspace_card.ui")
class WorkspaceCard(Gtk.Box):
    __gtype_name__ = "WorkspaceCard"

    __gsignals__ = {
        "edit-workspace": (GObject.SIGNAL_RUN_FIRST, None, (Workspace,)),
        "delete-workspace": (GObject.SIGNAL_RUN_FIRST, None, (Workspace,)),
        "favorite-workspace": (GObject.SIGNAL_RUN_FIRST, None, (Workspace, bool)),
    }

    _workspace: Workspace | None = None
    _edit_menu: Gio.Menu | None
    favorite_item: Gio.MenuItem
    edit_item: Gio.MenuItem
    delete_item: Gio.MenuItem
    workspace_id: str | None = GObject.Property(type=str)

    cover: Gtk.Picture = Gtk.Template.Child()
    # icon: Gtk.Label = Gtk.Template.Child()
    title: Gtk.Label = Gtk.Template.Child()
    updated_at: Gtk.Label = Gtk.Template.Child()

    def __init__(self, workspace: Workspace = None):
        super().__init__()
        self._workspace = workspace

        self.popover = Gtk.PopoverMenu(position=Gtk.PositionType.RIGHT)
        self.popover.set_parent(self)
        self.popover.add_child(Gtk.Label(label="Edit Workspace"), "edit-workspace")

        if workspace:
            self._bind_workspace(workspace)

    def build_menu(self):
        """ """
        self._edit_menu = Gio.Menu.new()

        self.favorite_item = Gio.MenuItem.new(
            _("Favorite"), detailed_action=f"favorite-workspace('{self._workspace.id}')"
        )
        self._edit_menu.append_item(self.favorite_item)

        self.edit_item = Gio.MenuItem.new(
            _("Rename and Style"), detailed_action=f"edit-workspace('{self._workspace.id}')"
        )
        self._edit_menu.append_item(self.edit_item)

        self.delete_item = Gio.MenuItem.new(
            _("Delete"), detailed_action=f"delete-workspace('{self._workspace.id}')"
        )

        delete_section = Gio.Menu()
        delete_section.append_item(self.delete_item)
        self._edit_menu.append_section(None, delete_section)

    @GObject.Property
    def workspace(self) -> Workspace | None:
        return self._workspace

    @workspace.setter
    def workspace(self, workspace: Workspace):
        self._workspace = workspace
        self._bind_workspace(workspace)

    def _bind_workspace(self, workspace: Workspace):
        logger.debug("Bind workspace: {}", workspace)

        self.build_menu()
        self.popover.set_menu_model(self._edit_menu)

        workspace.cover = workspace.cover or "cover-1"
        self.cover.set_resource(f"/com/tenderowl/norka/covers/{workspace.cover}")

        # if workspace.icon:
        #     self.icon.set_label(workspace.icon)
        # else:
        #     self.icon.set_visible(False)
        self.title.set_label(workspace.name_with_icon)
        self.updated_at.set_label(humanize.naturaldate(workspace.last_accessed_dt))
        self.updated_at.set_tooltip_text(workspace.last_accessed_dt.strftime("%Y-%m-%d %H:%M:%S"))

    @Gtk.Template.Callback()
    def _on_context_menu(self, controller, button, x, y):
        self.popover.popup()
