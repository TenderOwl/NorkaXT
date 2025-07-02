# MIT License
#
# Copyright (c) 2025 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, pagesmerge, publish, distribute, sublicense, and/or sell
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

from gi.repository import Adw, GLib, GObject, Gtk
from loguru import logger

from norka.models import Page, Workspace
from norka.services import PageService
from norka.widgets.pages_tree import PagesTree


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/sidebar.ui")
class Sidebar(Adw.Bin):
    __gtype_name__ = "Sidebar"

    pages_tree: PagesTree = Gtk.Template.Child()

    _workspace: Workspace | None

    __gsignals__ = {
        "page-selected": (GObject.SIGNAL_RUN_FIRST, None, (Page,)),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._page_service = PageService.get_default()
        self._page_service.connect("page-created", self._on_page_created)
        
        # Connect to pages tree signals
        self.pages_tree.connect("page-selected", self._on_page_selected)

    @GObject.Property
    def workspace(self):
        return self._workspace

    @workspace.setter
    def workspace(self, workspace: Workspace):
        self._workspace = workspace

        if not workspace:
            return

        GLib.idle_add(self._get_page_tree)

    def _get_page_tree(self):
        page_nodes = self._page_service.get_page_tree(self._workspace.id)
        
        logger.debug("Pages Tree: {}", page_nodes)
        
        # Populate the tree widget with the page nodes
        self.pages_tree.populate_tree(page_nodes)

    def _on_page_created(self, sender, page: Page):
        logger.debug("Page created: {}", page)
        # Refresh the tree when a new page is created
        if self._workspace:
            GLib.idle_add(self._get_page_tree)
    
    def _on_page_selected(self, sender, page: Page):
        logger.debug("Page selected: {}", page)
        # Emit the signal to parent widgets
        self.emit("page-selected", page)
