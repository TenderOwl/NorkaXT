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

from gi.repository import Adw, GLib, GObject, Gtk
from loguru import logger

from norka.models import Page, Workspace
from norka.services import PageService, WorkspaceService
from norka.widgets.content_view import ContentView
from norka.widgets.sidebar import Sidebar


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/content_page.ui")
class ContentPage(Adw.BreakpointBin):
    __gtype_name__ = "ContentPage"

    _workspace: Workspace | None = None

    split_view: Adw.OverlaySplitView = Gtk.Template.Child()
    sidebar_container: Adw.NavigationPage = Gtk.Template.Child()
    sidebar: Sidebar = Gtk.Template.Child()
    content_view: ContentView = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._workspace_service = WorkspaceService.get_default()
        self._page_service = PageService.get_default()

        self.content_view.connect("save-page", self._on_save_page)

        self.split_view.bind_property(
            "show-sidebar",
            self.content_view.toggle_sidebar_btn,
            "visible",
            GObject.BindingFlags.INVERT_BOOLEAN,
        )

        self.install_action("win.toggle-sidebar", None, self._on_toggle_sidebar_action)
        self.install_action("win.create-page", None, self._on_create_page_action)
        self.install_action("win.open-page", "s", self._on_open_page_action)

        if self.split_view.get_show_sidebar():
            self.content_view.toggle_sidebar_btn.set_visible(False)

    @GObject.Property
    def workspace(self) -> Workspace | None:
        return self._workspace

    @workspace.setter
    def workspace(self, workspace: Workspace):
        self._workspace = workspace
        if not workspace:
            # Deactivate all actions and workers
            self.content_view.close_page()
            return

        self.sidebar_container.set_title(self._workspace.name_with_icon)
        self.sidebar.workspace = workspace

    def _on_toggle_sidebar_action(self, sender: Gtk.Widget, action: str, args=None):
        logger.debug("Toggle sidebar action activated")
        self.split_view.set_show_sidebar(True)

    def _on_create_page_action(self, sender: Gtk.Widget, action: str, args=None):
        logger.debug("New page action activated")

        if self._workspace and self._page_service:
            GLib.idle_add(self._create_page)

    def _on_open_page_action(
        self, _sender: Gtk.Widget, _action: str, page_id: GLib.Variant = None
    ):
        logger.debug("Open page action activated: {}", page_id.get_string())
        GLib.idle_add(self._open_page, page_id.get_string())

    def _create_page(self):
        self._page_service.create_page(self._workspace.id, _("Untitled"), "")
        return False

    def _open_page(self, page_id: str):
        if page := self._page_service.get_page(page_id):
            self.content_view.open_page(page)

        return False

    def _on_save_page(self, _sender, page: Page):
        logger.debug("Saving page: {}", page.text)
        GLib.idle_add(self._save_page_async, page)
        return False

    def _save_page_async(self, page: Page):
        self._page_service.update_page(
            page.id,
            page.title,
            page.text,
            page.content,
            page.icon,
            page.cover,
        )
        # Remove source from Loop
        return False
