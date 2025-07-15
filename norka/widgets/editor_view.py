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
import json
from typing import Dict, List, Tuple

from gi.overrides.Gtk import TextIter
from gi.repository import Adw, Gdk, GLib, GObject, Gtk, GtkSource, Pango
from loguru import logger

from norka.models import Page
from norka.widgets.editor_actions_popover import EditorActionsPopover

PAGE_MIME_TYPE = "application/octet-stream"


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/editor_view.ui")
class EditorView(Gtk.Box):
    __gtype_name__ = "EditorView"

    __gsignals__ = {
        "save-page": (GObject.SIGNAL_RUN_FIRST, None, (Page,)),
    }

    text_view: GtkSource.View = Gtk.Template.Child()
    _buffer: GtkSource.Buffer = Gtk.Template.Child(name="buffer")
    # completion: GtkSource.Completion = Gtk.Template.Child()
    action_popover: EditorActionsPopover
    gesture_click: Gtk.GestureClick = Gtk.Template.Child()

    _page: Page | None
    _save_timer: int | None = None
    _is_action_popover_open: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        language_manager = GtkSource.LanguageManager.get_default()
        language = language_manager.get_language("markdown")

        self._buffer.set_language(language)
        self.gesture_click.connect("released", self._on_mouse_button_released)
        self.gesture_click.connect(
            "unpaired-release", self._on_mouse_button_unpaired_released
        )

        # Basic formatting tags
        self.tag_bold = self._buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tag_italic = self._buffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.tag_underline = self._buffer.create_tag(
            "underline", underline=Pango.Underline.SINGLE
        )
        self.tag_found = self._buffer.create_tag("found", background="yellow")

        # Heading tags
        self.tag_heading1 = self._buffer.create_tag(
            "heading1", weight=Pango.Weight.BOLD, size_points=24, pixels_inside_wrap=24/1.5,
            pixels_below_lines=16
        )
        self.tag_heading2 = self._buffer.create_tag(
            "heading2", weight=Pango.Weight.BOLD, size_points=20, pixels_inside_wrap=20/1.5,
            pixels_below_lines=12
        )
        self.tag_heading3 = self._buffer.create_tag(
            "heading3", weight=Pango.Weight.BOLD, size_points=16, pixels_inside_wrap=16/1.5,
            pixels_below_lines=8
        )

        # List tags
        self.tag_bullet = self._buffer.create_tag(
            "bullet", pixels_above_lines=6, pixels_below_lines=6
        )
        self.tag_numbered = self._buffer.create_tag(
            "numbered", pixels_above_lines=6, pixels_below_lines=6
        )

        # Color tags
        self.tag_red = self._buffer.create_tag("red", foreground="red")
        self.tag_green = self._buffer.create_tag("green", foreground="green")
        self.tag_blue = self._buffer.create_tag("blue", foreground="blue")
        self.tag_yellow = self._buffer.create_tag("yellow", foreground="#FFD700")

        # Special formatting
        self.tag_hr = self._buffer.create_tag(
            "hr", pixels_above_lines=12, pixels_below_lines=12
        )
        self.tag_link = self._buffer.create_tag(
            "link", foreground="blue", underline=Pango.Underline.SINGLE
        )
        self.tag_image = self._buffer.create_tag("image", foreground="#888888")

        # Add actions for new formatting options
        self.install_action("editor.format", "s", self._on_format_action)
        self.install_action(
            "editor.heading1", None, lambda *args: self.apply_tag("heading1")
        )
        self.install_action(
            "editor.heading2", None, lambda *args: self.apply_tag("heading2")
        )
        self.install_action(
            "editor.heading3", None, lambda *args: self.apply_tag("heading3")
        )
        self.install_action(
            "editor.bullet", None, lambda *args: self.apply_tag("bullet")
        )
        self.install_action(
            "editor.numbered", None, lambda *args: self.apply_tag("numbered")
        )
        self.install_action("editor.hr", None, lambda *args: self.apply_tag("hr"))
        self.install_action("editor.link", None, lambda *args: self.apply_tag("link"))
        self.install_action("editor.image", None, lambda *args: self.apply_tag("image"))
        self.install_action("editor.red", None, lambda *args: self.apply_tag("red"))
        self.install_action("editor.green", None, lambda *args: self.apply_tag("green"))
        self.install_action("editor.blue", None, lambda *args: self.apply_tag("blue"))
        self.install_action(
            "editor.yellow", None, lambda *args: self.apply_tag("yellow")
        )

        self.action_popover = EditorActionsPopover()
        self.action_popover.set_parent(self.text_view)

    @GObject.Property
    def page(self) -> Page | None:
        return self._page

    @page.setter
    def page(self, page: Page | None):
        self._page = page

        # Stop the save timer
        if self._save_timer:
            GLib.source_remove(self._save_timer)
            self._save_timer = None

        if not page:
            return

        # Set the page content
        self._buffer.set_text(page.text or "")
        self._apply_tags(json.loads(page.tag_table or "{}"))
        logger.debug("Loaded page tag table: {}", json.loads(page.tag_table))
        # And start the save timer for automatic saving
        # self._save_timer = GLib.timeout_add_seconds(5, self._save_page)
        logger.info("Autosaving disabled")

        self._apply_styling()

    def _apply_styling(self) -> None:
        style_manager = Adw.StyleManager.get_default()
        style_scheme_manager = GtkSource.StyleSchemeManager.get_default()

        scheme_id = "norka"
        if style_manager.get_dark():
            scheme_id = f"{scheme_id}-dark"

        scheme = style_scheme_manager.get_scheme(scheme_id)
        self._buffer.set_style_scheme(scheme)

    def _apply_tags(self, tag_table: Dict[str, List[Tuple[int, int]]]) -> None:
        """
        Applies tags to the editor view buffer from a tag table.

        :param tag_table: A dictionary of tag names to lists of tag ranges.
            Each tag range is a tuple of two integers representing the start
            and end offsets of the tag in the buffer.
        """
        tag_table = tag_table
        for tag_name in tag_table:
            for tag_range in tag_table[tag_name]:
                start_iter = self._buffer.get_iter_at_offset(tag_range[0])
                end_iter = self._buffer.get_iter_at_offset(tag_range[1])
                self._buffer.apply_tag_by_name(tag_name, start_iter, end_iter)

    @Gtk.Template.Callback
    def _on_key_pressed(
        self,
        controller: Gtk.EventControllerKey,
        keyval: int,
        keycode: int,
        state: Gdk.ModifierType,
    ) -> bool:
        return Gdk.EVENT_PROPAGATE

    def do_hide(self):
        logger.debug("Editor hidden")
        super().do_hide()

    def _get_text(self):
        return self._buffer.get_text(
            self._buffer.get_start_iter(), self._buffer.get_end_iter(), True
        ).strip()

    def _save_page(self):
        logger.debug("Saving page: {}", self._page)
        self._page.text = self._get_text()
        self.emit("save-page", self._page)
        return True

    def do_grab_focus(self):
        self.text_view.grab_focus()
        return True

    def _on_format_action(self, sender, action, tag_name: GLib.Variant):
        logger.debug("{}: {}", action, tag_name.get_string())
        self.apply_tag(tag_name.get_string())

    def apply_tag(self, tag_name: str):
        bounds: tuple[Gtk.TextIter, Gtk.TextIter] = self._buffer.get_selection_bounds()
        if len(bounds) == 0:
            # If no text is selected, create a placeholder
            start_iter = self._buffer.get_iter_at_mark(self._buffer.get_insert())
            if tag_name == "hr":
                self._buffer.insert(start_iter, "\n---\n")
            elif tag_name == "link":
                self._buffer.insert(start_iter, "[Link](https://)")
            elif tag_name == "image":
                self._buffer.insert(start_iter, "![Image](https://)")
            elif tag_name in ["bullet", "numbered"]:
                self._buffer.insert(start_iter, "\n* ")
            return

        start, end = bounds
        if tag_name.startswith('heading'):
            start.backward_line()
            end.forward_line()
        self._buffer.apply_tag_by_name(tag_name, start, end)

    @Gtk.Template.Callback()
    def _on_button_save_clicked(self, button):
        bounds = self._buffer.get_bounds()
        if len(bounds) == 0:
            return

        logger.info("Begin saving page")

        text_iter = self._buffer.get_start_iter()
        # Tag table contains all tags applied to the text and their start and end positions
        tag_table: Dict[str, Tuple[int, int]]() = {}
        while text_iter.forward_to_tag_toggle():
            # Get all tags toggled on the current position
            # If the tag is not in the tag table, add it and set the start position
            tags = text_iter.get_toggled_tags(toggled_on=True)
            for tag in tags:
                tag_name = tag.props.name
                if tag_name not in tag_table:
                    tag_table[tag_name] = []

                tag_table[tag_name].append([text_iter.get_offset(), 0])

            # Get all tags toggled off the current position
            # If the tag is in the tag table, set the end position
            tags = text_iter.get_toggled_tags(toggled_on=False)
            for tag in tags:
                tag_name = tag.props.name
                if tag_name in tag_table:
                    if tag_ranges := tag_table[tag_name]:
                        tag_ranges[-1][1] = text_iter.get_offset()
                        tag_table[tag_name] = tag_ranges

        logger.info("Tag table: {}", tag_table)

        self._page.tag_table = json.dumps(tag_table)
        self._page.text = self._get_text()
        self.emit("save-page", self._page)

    def on_text_changed(self, text_buffer):
        selection = text_buffer.get_selection_bounds()
        if selection and selection[0] != selection[1]:
            start, end = selection
            # Selection exists
            # selected_text = text_buffer.get_text(start, end, include_hidden_chars=False)
            # print(f"Selection changed: {selected_text}")
            strong_cursor_pos, weak_cursos_pos = self.text_view.get_cursor_locations(
                start
            )
            strong_cursor_pos.x, strong_cursor_pos.y = (
                self.text_view.buffer_to_window_coords(
                    Gtk.TextWindowType.TEXT, strong_cursor_pos.x, strong_cursor_pos.y
                )
            )

            self.action_popover.set_pointing_to(strong_cursor_pos)
            GLib.idle_add(self.action_popover.popup)
        else:
            # No selection
            print("No text selected")

        # return False

    def on_mark_set(self, text_buffer, location, mark):
        logger.debug("Insert mark: {}", mark.get_name())
        if mark.get_name() in ("insert", "selection_bound"):
            GLib.timeout_add(1500, self.on_text_changed, text_buffer)

    def _toggle_editor_popover(self):
        if self._is_action_popover_open:
            logger.debug("Toggle editor popover down")
            GLib.idle_add(self.action_popover.popdown)
            self._is_action_popover_open = False
            return

        selection = self._buffer.get_selection_bounds()
        if selection and selection[0] != selection[1]:
            start, end = selection
            # Selection exists
            # selected_text = text_buffer.get_text(start, end, include_hidden_chars=False)
            # print(f"Selection changed: {selected_text}")
            strong_cursor_pos, weak_cursos_pos = self.text_view.get_cursor_locations(
                start
            )
            strong_cursor_pos.x, strong_cursor_pos.y = (
                self.text_view.buffer_to_window_coords(
                    Gtk.TextWindowType.TEXT, strong_cursor_pos.x, strong_cursor_pos.y
                )
            )

            self.action_popover.set_pointing_to(strong_cursor_pos)
            GLib.idle_add(self.action_popover.popup)
            self._is_action_popover_open = True

    @Gtk.Template.Callback()
    def _on_mouse_button_released(
        self, controller: Gtk.GestureClick, n_clicks: int, x: float, y: float
    ):
        logger.debug("Mouse button released: {}", controller.get_button())
        self._toggle_editor_popover()

    def _on_mouse_button_unpaired_released(
        self,
        controller: Gtk.GestureClick,
        x: float,
        y: float,
        button: int,
        sequence: Gdk.EventSequence,
    ):
        logger.debug("Mouse button unpaired-released: {}", button)
        self._toggle_editor_popover()
