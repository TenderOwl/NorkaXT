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

from gi.repository import Gio, GObject, Gtk

from norka.models import PageTreeItem


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/pages_tree_row.ui")
class PagesTreeRow(Gtk.Box):
    __gtype_name__ = "PagesTreeRow"

    # content_box: Gtk.Box = Gtk.Template.Child()
    expander: Gtk.TreeExpander = Gtk.Template.Child()
    icon_label: Gtk.Label = Gtk.Template.Child()
    title_label: Gtk.Label = Gtk.Template.Child()

    item: PageTreeItem = GObject.Property(type=GObject.TYPE_PYOBJECT)

    popover: Gtk.PopoverMenu
    _edit_menu: Gio.Menu | None
    _menu_subpages: Gio.MenuItem
    _menu_rename: Gio.MenuItem
    _menu_duplicate: Gio.MenuItem
    _menu_move: Gio.MenuItem
    _menu_delete: Gio.MenuItem

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.popover = Gtk.PopoverMenu(position=Gtk.PositionType.RIGHT)
        self.popover.set_parent(self)

    def build_menu(self):
        self._edit_menu = Gio.Menu.new()
        self._edit_menu.append_item(
            Gio.MenuItem.new(
                _("New Subpage"),
                detailed_action=f"page.add-page('{self.item.page_node.page.id}')",
            )
        )
        self._edit_menu.append_item(
            Gio.MenuItem.new(
                _("Rename"),
                detailed_action=f"page.rename('{self.item.page_node.page.id}')",
            )
        )
        self._edit_menu.append_item(
            Gio.MenuItem.new(
                _("Duplicate"),
                detailed_action=f"page.duplicate('{self.item.page_node.page.id}')",
            )
        )

        self._edit_menu.append_item(
            Gio.MenuItem.new(
                _("Move to Workspace"),
                detailed_action=f"page.change-workspace('{self.item.page_node.page.id}')",
            )
        )
        self._menu_delete = Gio.MenuItem.new(
            _("Delete"),
            detailed_action=f"page.delete('{self.item.page_node.page.id}')",
        )

        delete_section = Gio.Menu()
        delete_section.append_item(self._menu_delete)
        self._edit_menu.append_section(None, delete_section)
        self.popover.set_menu_model(self._edit_menu)

    @Gtk.Template.Callback()
    def _on_context_menu(self, controller, button, x, y):
        if self.item:
            self.build_menu()
        self.popover.popup()
