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

from typing import Optional

from gi.repository import Gio, GObject, Gtk, Gdk
from loguru import logger

from norka.models import Page, PageNode, PageTreeItem
from norka.widgets.pages_tree_row import PagesTreeRow


@Gtk.Template(resource_path="/com/tenderowl/norka/ui/pages_tree.ui")
class PagesTree(Gtk.Box):
    __gtype_name__ = "PagesTree"

    selection: Gtk.SingleSelection = Gtk.Template.Child()
    list_view: Gtk.ListView = Gtk.Template.Child()
    factory: Gtk.SignalListItemFactory = Gtk.Template.Child()

    __gsignals__ = {
        "page-selected": (GObject.SIGNAL_RUN_FIRST, None, (Page,)),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tree_model: Optional[Gtk.TreeListModel] = None
        self._root_model: Optional[Gio.ListStore] = None

        # Setup the factory callbacks for TreeExpander items
        self.factory.connect("setup", self._on_item_setup)
        self.factory.connect("bind", self._on_item_bind)
        self.factory.connect("unbind", self._on_item_unbind)

        self.list_view.add_css_class("navigation-sidebar")

    def populate_tree(self, page_nodes: list[PageNode]):
        """
        Populate the tree with PageNode objects from PageService.get_page_tree().

        Args:
            page_nodes: List of root PageNode objects from PageService.get_page_tree()
        """
        logger.debug("Populating tree with {} root nodes", len(page_nodes))

        # Create the root model with PageTreeItem objects
        self._root_model = Gio.ListStore.new(PageTreeItem)

        # Add all root nodes to the model
        for node in page_nodes:
            tree_item = PageTreeItem(node)
            self._root_model.append(tree_item)

        # Create TreeListModel with a function to create child models
        self._tree_model = Gtk.TreeListModel.new(
            root=self._root_model,
            passthrough=False,
            autoexpand=False,
            create_func=self._create_child_model,
        )

        # Set the model on the selection
        self.selection.set_model(self._tree_model)

        logger.debug(
            "Tree populated with {} total items", self._tree_model.get_n_items()
        )

    def _create_child_model(self, item: PageTreeItem) -> Optional[Gio.ListStore]:
        """
        Create a child model for a tree item.
        This is called by TreeListModel when a node is expanded.

        Args:
            item: The PageTreeItem to create children for

        Returns:
            Gio.ListStore containing child PageTreeItem objects, or None if no children
        """
        page_node = item.page_node

        if not page_node.children:
            return None

        # Create a ListStore for the children
        child_model = Gio.ListStore.new(PageTreeItem)

        # Add all child nodes
        for child_node in page_node.children:
            child_item = PageTreeItem(child_node)
            child_model.append(child_item)

        logger.debug(
            "Created child model with {} items for '{}'",
            len(page_node.children),
            page_node.page.title,
        )

        return child_model

    def _on_item_setup(
            self, _factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ):
        """
        Setup callback for list items. Creates the UI structure.
        """
        child = PagesTreeRow()
        ev_drag = Gtk.DragSource(actions=Gdk.DragAction.COPY)
        ev_drag.connect('prepare', self._on_item_drag_prepare)
        child.add_controller(ev_drag)
        list_item.set_child(child)

    def _on_item_bind(
            self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ):
        """
        Bind callback for list items. Connects data to the UI.
        """
        # Get the tree list row (contains position info and item)
        tree_list_row: Gtk.TreeListRow = list_item.get_item()
        if not tree_list_row:
            return

        # Get the actual PageTreeItem
        page_tree_item: PageTreeItem = tree_list_row.get_item()
        if not page_tree_item:
            return

        # Get the expander widget
        child: PagesTreeRow = list_item.get_child()
        if not child:
            return

        # Set the tree list row on the expander (for expand/collapse functionality)
        child.set_list_row(tree_list_row)

        # Bind the data to the UI elements
        child.icon_label.set_text(page_tree_item.icon)
        child.title_label.set_text(page_tree_item.title)
        child.item = page_tree_item

        # Add CSS classes for styling
        if page_tree_item.has_children:
            child.content_box.add_css_class("tree-item-expandable")
        else:
            child.content_box.add_css_class("tree-item-leaf")

    def _on_item_unbind(
            self, _factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ):
        """
        Unbind callback for list items. Clean up when items are recycled.
        """
        child: PagesTreeRow = list_item.get_child()
        if child:
            # Clear the list row reference
            child.set_list_row(None)

            # Remove CSS classes
            if content_box := child.get_child():
                content_box.remove_css_class("tree-item-expandable")
                content_box.remove_css_class("tree-item-leaf")

    def _on_item_drag_prepare(self, ev_drag: Gtk.DragSource, x: int, y: int):
        """
        Handle drag prepare event.
        """
        try:
            widget = ev_drag.get_widget()
            item: PageTreeItem = widget.item
            page = item.page_node.page
            logger.debug("Dragging page: {}", page)
            return Gdk.ContentProvider.new_for_value(page.id)

        except Exception as e:
            logger.error("Failed to set drag cursor: {}", e)

        return None

    @Gtk.Template.Callback
    def _on_selection_changed(
            self, selection: Gtk.SingleSelection, position: int, n_items: int
    ):
        """
        Handle selection changes in the tree.
        """
        selected_item = selection.get_selected_item()
        if not selected_item:
            return

        # Get the PageTreeItem from the tree list row
        page_tree_item: PageTreeItem = selected_item.get_item()
        if not page_tree_item:
            return

        # Get the actual Page object
        page = page_tree_item.page_node.page

        logger.debug("Selected page: {} (ID: {})", page.title, page.id)

        # Emit signal with the selected page
        self.emit("page-selected", page)

    @Gtk.Template.Callback
    def _on_mouse_enter(
            self, controller: Gtk.EventControllerMotion, x: float, y: float
    ):
        """Handle mouse enter events."""
        pass

    @Gtk.Template.Callback
    def _on_mouse_leave(self, controller: Gtk.EventControllerMotion):
        """Handle mouse leave events."""
        pass

    @Gtk.Template.Callback
    def _on_item_setup_template(
            self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ):
        """
        Template callback for item setup.
        """
        self._on_item_setup(factory, list_item)

    @Gtk.Template.Callback
    def _on_item_bind_template(
            self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ):
        """
        Template callback for item binding.
        """
        self._on_item_bind(factory, list_item)

    def get_selected_page(self) -> Optional[Page]:
        """
        Get the currently selected page.

        Returns:
            Selected Page object or None if nothing is selected
        """
        selected_item = self.selection.get_selected_item()
        if not selected_item:
            return None

        page_tree_item: PageTreeItem = selected_item.get_item()
        if not page_tree_item:
            return None

        return page_tree_item.page_node.page

    def select_page(self, page_id: str) -> bool:
        """
        Select a page by its ID.

        Args:
            page_id: ID of the page to select

        Returns:
            True if page was found and selected, False otherwise
        """
        if not self._tree_model:
            return False

        # Search through all items in the tree model
        for i in range(self._tree_model.get_n_items()):
            tree_list_row = self._tree_model.get_item(i)
            if not tree_list_row:
                continue

            page_tree_item = tree_list_row.get_item()
            if not page_tree_item:
                continue

            if page_tree_item.page_node.page.id == page_id:
                self.selection.set_selected(i)
                return True

        return False

    def expand_all(self):
        """
        Expand all expandable nodes in the tree.
        """
        if not self._tree_model:
            return

        # Iterate through all items and expand them
        for i in range(self._tree_model.get_n_items()):
            tree_list_row = self._tree_model.get_item(i)
            if tree_list_row and tree_list_row.get_expandable():
                tree_list_row.set_expanded(True)

    def collapse_all(self):
        """
        Collapse all expanded nodes in the tree.
        """
        if not self._tree_model:
            return

        # Iterate through all items and collapse them
        for i in range(self._tree_model.get_n_items()):
            tree_list_row = self._tree_model.get_item(i)
            if tree_list_row and tree_list_row.get_expanded():
                tree_list_row.set_expanded(False)

    @Gtk.Template.Callback
    def _on_dragsource_prepare(self, _drag_source: Gtk.DragSource, x: int, y: int):
        """
        Handle drag source prepare event.
        """
        self.dragged_item = self.selection.get_selected_item()
        logger.debug("DnD Prepare with: {}", self.dragged_item)
        if not self.dragged_item:
            return False
        return

    @Gtk.Template.Callback
    def _on_droptarget_enter(self, *args):
        logger.debug("DropTarget enter: {}", args)

    @Gtk.Template.Callback
    def _on_droptarget_leave(self, *args):
        logger.debug("DropTarget leave: {}", args)

    @Gtk.Template.Callback
    def _on_droptarget_async_drop(self, *args):
        logger.debug("DropTarget async drop: {}", args)
