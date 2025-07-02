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


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/edit_workspace_dialog.ui")
class EditWorkspaceDialog(Adw.Dialog):
    __gtype_name__ = "EditWorkspaceDialog"

    __gsignals__ = {"workspace-updated": (GObject.SIGNAL_RUN_FIRST, None, (Workspace,))}

    name_entry: Gtk.Entry = Gtk.Template.Child(name="name")
    cover_picture: Gtk.Picture = Gtk.Template.Child(name="cover")
    change_cover_btn: Gtk.Button = Gtk.Template.Child()
    emoji_btn: Gtk.Button = Gtk.Template.Child()
    overlay: Gtk.Overlay = Gtk.Template.Child()

    workspace: Workspace = GObject.Property(type=GObject.TYPE_PYOBJECT)

    def __init__(self, workspace: Workspace, **kwargs):
        super().__init__(**kwargs)

        self.workspace = workspace

        self.name_entry.set_text(self.workspace.name)
        self.emoji_btn.set_label(self.workspace.icon)
        self.cover_picture.set_resource(f"/com/tenderowl/norka/covers/{self.workspace.cover}")

        # self.change_cover_btn.connect('clicked', self._on_changecover_clicked)
        # self.name_entry.connect('activate', self._on_entry_activate)
        # self.emoji_btn.connect('clicked', self._on_choose_emoji_clicked)

    @Gtk.Template.Callback()
    def _on_cancel_clicked(self, _button: Gtk.Widget):
        self.close()

    @Gtk.Template.Callback()
    def _on_ok_clicked(self, _button: Gtk.Widget):
        name = self.name_entry.get_text().strip()
        if not name:
            return
        self.workspace.name = name
        self.emit("workspace-updated", self.workspace)
        self.close()

    @Gtk.Template.Callback()
    def _on_entry_activate(self, _entry: Gtk.Entry):
        if not _entry.get_text().strip():
            return

        self._on_ok_clicked(_entry)

    @Gtk.Template.Callback()
    def _on_change_cover_clicked(self, button: Gtk.Button):
        index = int(self.workspace.cover[-1])
        if index < 8:
            index += 1
        else:
            index = 1
        self.workspace.cover = f"cover-{index}"
        self.cover_picture.set_resource(f"/com/tenderowl/norka/covers/{self.workspace.cover}")

    @Gtk.Template.Callback()
    def _on_choose_emoji_clicked(self, button: Gtk.Button):
        emoji_chooser = Gtk.EmojiChooser()
        emoji_chooser.set_parent(button)
        emoji_chooser.connect("emoji-picked", self._on_emoji_picked)
        emoji_chooser.popup()

    def _on_emoji_picked(self, _emoji_chooser: Gtk.EmojiChooser, emoji: str):
        self.workspace.icon = emoji
