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


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/add_workspace_dialog.ui")
class AddWorkspaceDialog(Adw.Dialog):
    __gtype_name__ = "AddWorkspaceDialog"

    __gsignals__ = {"workspace-created": (GObject.SIGNAL_RUN_FIRST, None, (str, str, str))}

    name: Gtk.Entry = Gtk.Template.Child()
    emoji_btn: Gtk.Button = Gtk.Template.Child()
    overlay: Gtk.Overlay = Gtk.Template.Child()
    cover: Gtk.Picture = Gtk.Template.Child()

    _cover: str = "cover-1"
    _name: str = None
    emoji: str = GObject.Property(type=str, default="🚀")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind_property(
            "emoji", self.emoji_btn, "label", GObject.BindingFlags.DEFAULT
        )
        self.cover.set_resource(f"/com/tenderowl/norka/covers/{self._cover}")

    @Gtk.Template.Callback()
    def _on_cancel_clicked(self, _button: Gtk.Widget):
        self.close()

    @Gtk.Template.Callback()
    def _on_ok_clicked(self, _button: Gtk.Widget):
        name = self.name.get_text().strip()
        if not name:
            return
        self.emit("workspace-created", name, self.emoji, self._cover)
        self.close()

    @Gtk.Template.Callback()
    def _on_entry_activate(self, _entry: Gtk.Entry):
        if not _entry.get_text().strip():
            return

        self._on_ok_clicked(_entry)

    @Gtk.Template.Callback()
    def _on_change_cover_clicked(self, button: Gtk.Button):
        index = int(self._cover[-1])
        if index < 8:
            index += 1
        else:
            index = 1
        self._cover = f"cover-{index}"
        self.cover.set_resource(f"/com/tenderowl/norka/covers/{self._cover}")

    @Gtk.Template.Callback()
    def _on_choose_emoji_clicked(self, button: Gtk.Button):
        emoji_chooser = Gtk.EmojiChooser()
        emoji_chooser.set_parent(button)
        emoji_chooser.connect("emoji-picked", self._on_emoji_picked)
        emoji_chooser.popup()

    def _on_emoji_picked(self, _emoji_chooser: Gtk.EmojiChooser, emoji: str):
        self.emoji = emoji
