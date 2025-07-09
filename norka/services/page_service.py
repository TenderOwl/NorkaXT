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

from typing import Dict, List, Optional, Self

from gi.repository import GLib, GObject, Gom
from loguru import logger

from norka.models import DatabaseManager, Page, PageNode, get_database_manager


class PageService(GObject.Object):
    __gtype_name__ = "PageService"

    _service: Self | None = None

    __gsignals__ = {
        "page-created": (GObject.SIGNAL_RUN_FIRST, None, (Page,)),
        "page-updated": (GObject.SIGNAL_RUN_FIRST, None, (Page,)),
        "page-deleted": (GObject.SIGNAL_RUN_FIRST, None, (Page, bool)),
        "page-moved": (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (Page, str, str),
        ),  # page, old_parent_id, new_parent_id
        "page-tree-changed": (GObject.SIGNAL_RUN_FIRST, None, (str,)),  # workspace_id
    }

    def __init__(self, database: DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self._database = database
        logger.debug(
            "PageService initialized with database at {}", database.database_path
        )

    @classmethod
    def get_default(cls) -> Self:
        if cls._service is None:
            cls._service = cls(database=get_database_manager())
        return cls._service

    # CRUD Operations

    def create_page(
        self,
        workspace_id: str,
        title: str,
        text: str = "",
        parent_page_id: str = None,
        icon: str = None,
        cover: str = None,
    ) -> Page:
        """
        Create a new page.

        Args:
            workspace_id: ID of the workspace this page belongs to
            title: Page title
            text: Page content
            parent_page_id: Optional parent page ID for tree structure
            icon: Optional page icon
            cover: Optional page cover

        Returns:
            Created page
        """
        page = Page.create(
            workspace_id=workspace_id,
            title=title,
            text=text,
            parent_page_id=parent_page_id,
            icon=icon,
            cover=cover,
            repository=self._database.repository,
        )
        page.save_sync()
        self.emit("page-created", page)
        self.emit("page-tree-changed", workspace_id)
        return page

    def get_page(self, page_id: str) -> Optional[Page]:
        """
        Get page by ID.

        Args:
            page_id: Page ID

        Returns:
            Page or None if not found
        """
        _filter = Gom.Filter.new_eq(Page, "id", page_id)
        return self._database.repository.find_one_sync(Page, _filter)

    def get_page_by_title(self, workspace_id: str, title: str) -> Optional[Page]:
        """
        Get page by title within a workspace.

        Args:
            workspace_id: Workspace ID
            title: Page title

        Returns:
            Page or None if not found
        """
        title_filter = Gom.Filter.new_eq(Page, "title", title)
        workspace_filter = Gom.Filter.new_eq(Page, "workspace_id", workspace_id)
        combined_filter = Gom.Filter.new_and(title_filter, workspace_filter)
        return self._database.repository.find_one_sync(Page, combined_filter)

    def update_page(
        self,
        page_id: str,
        title: str = None,
        text: str = None,
        content: bytes = None,
        icon: str = None,
        cover: str = None,
    ) -> Optional[Page]:
        """
        Update page content.

        Args:
            page_id: Page ID
            title: New title (optional)
            text: New text content (optional)
            icon: New icon (optional)
            cover: New cover (optional)

        Returns:
            Updated page or None if not found
        """
        page = self.get_page(page_id)
        if not page:
            return None

        if title is not None:
            page.title = title
        if text is not None:
            page.text = text
        if icon is not None:
            page.icon = icon
        if cover is not None:
            page.cover = cover
        if content is not None:
            page.content = content

        page.update_content(title, text)
        page.save_sync()
        self.emit("page-updated", page)
        return page

    def delete_page(self, page_id: str) -> bool:
        """
        Delete a page and all its children.

        Args:
            page_id: Page ID to delete

        Returns:
            True if successful, False otherwise
        """
        logger.debug("delete_page({})", page_id)
        try:
            page = self.get_page(page_id)
        except GLib.Error as e:
            logger.error("Error: ", e.domain)
            logger.error(e)
            return False

        if page:
            workspace_id = page.workspace_id

            # First delete all child pages recursively
            children = self.get_child_pages(page_id)
            for child in children:
                self.delete_page(child.id)

            logger.debug("Found page to delete: {}", page)
            result = page.delete_sync()
            self.emit("page-deleted", page, result)
            self.emit("page-tree-changed", workspace_id)
            return result

        return False

    # Tree Structure Operations

    def get_workspace_pages(self, workspace_id: str) -> List[Page]:
        """
        Get all pages in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of all pages in the workspace
        """
        workspace_filter = Gom.Filter.new_eq(Page, "workspace_id", workspace_id)
        sorting = Gom.Sorting(Page, "sort_order", Gom.SortingMode.ASCENDING)
        group = self._database.repository.find_sorted_sync(
            Page, workspace_filter, sorting
        )
        count = len(group)
        group.fetch_sync(0, count)
        return list(group)

    def get_root_pages(self, workspace_id: str) -> List[Page]:
        """
        Get root pages (pages without parent) in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of root pages
        """
        workspace_filter = Gom.Filter.new_eq(Page, "workspace_id", workspace_id)
        parent_filter = Gom.Filter.new_is_null(Page, "parent_page_id")
        combined_filter = Gom.Filter.new_and(workspace_filter, parent_filter)
        sorting = Gom.Sorting(Page, "sort_order", Gom.SortingMode.ASCENDING)

        group = self._database.repository.find_sorted_sync(
            Page, combined_filter, sorting
        )
        count = len(group)
        group.fetch_sync(0, count)
        return list(group)

    def get_child_pages(self, parent_page_id: str) -> List[Page]:
        """
        Get direct child pages of a parent page.

        Args:
            parent_page_id: Parent page ID

        Returns:
            List of child pages
        """
        parent_filter = Gom.Filter.new_eq(Page, "parent_page_id", parent_page_id)
        sorting = Gom.Sorting(Page, "sort_order", Gom.SortingMode.ASCENDING)

        group = self._database.repository.find_sorted_sync(Page, parent_filter, sorting)
        count = len(group)
        group.fetch_sync(0, count)
        return list(group)

    def get_page_tree(self, workspace_id: str) -> List[PageNode]:
        """
        Get the complete page tree for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of root PageNode objects with children populated
        """
        # Get all pages in the workspace
        all_pages = self.get_workspace_pages(workspace_id)

        # Create a map of page_id -> PageNode
        node_map: Dict[str, PageNode] = {}
        for page in all_pages:
            node_map[page.id] = PageNode(page)

        # Build the tree structure
        root_nodes = []
        for page in all_pages:
            node = node_map[page.id]

            if page.parent_page_id and page.parent_page_id in node_map:
                # This page has a parent, add it as a child
                parent_node = node_map[page.parent_page_id]
                parent_node.add_child(node)
            else:
                # This is a root page
                root_nodes.append(node)

        # Sort root nodes by sort_order and title
        root_nodes.sort(key=lambda x: (x.page.sort_order, x.page.title))

        return root_nodes

    def get_page_ancestors(self, page_id: str) -> List[Page]:
        """
        Get all ancestor pages (breadcrumb path) for a page.

        Args:
            page_id: Page ID

        Returns:
            List of ancestor pages from root to immediate parent
        """
        page = self.get_page(page_id)
        if not page:
            return []

        ancestors = []
        current_page = page

        # Get parent chain
        while current_page and current_page.parent_page_id:
            parent = self.get_page(current_page.parent_page_id)
            if parent:
                ancestors.insert(0, parent)  # Insert at beginning for correct order
                current_page = parent
            else:
                break

        return ancestors

    def move_page(self, page_id: str, new_parent_id: Optional[str]) -> bool:
        """
        Move a page to a new parent (or make it a root page).

        Args:
            page_id: Page ID to move
            new_parent_id: New parent page ID, or None to make it a root page

        Returns:
            True if successful, False otherwise
        """
        page = self.get_page(page_id)
        if not page:
            return False

        # Prevent moving a page to be a child of itself or its descendants
        if new_parent_id and self._is_descendant(new_parent_id, page_id):
            logger.warning(
                "Cannot move page {} to its descendant {}", page_id, new_parent_id
            )
            return False

        old_parent_id = page.parent_page_id
        page.parent_page_id = new_parent_id
        page.update_access_time()
        page.save_sync()

        self.emit("page-moved", page, old_parent_id or "", new_parent_id or "")
        self.emit("page-tree-changed", page.workspace_id)
        return True

    def _is_descendant(self, potential_ancestor_id: str, page_id: str) -> bool:
        """
        Check if a page is a descendant of another page.

        Args:
            potential_ancestor_id: ID of the potential ancestor page
            page_id: ID of the page to check

        Returns:
            True if page_id is a descendant of potential_ancestor_id
        """
        descendants = self._get_all_descendants(potential_ancestor_id)
        return page_id in descendants

    def _get_all_descendants(self, page_id: str) -> set:
        """
        Get all descendant page IDs for a given page.

        Args:
            page_id: Page ID

        Returns:
            Set of descendant page IDs
        """
        descendants = set()
        children = self.get_child_pages(page_id)

        for child in children:
            descendants.add(child.id)
            # Recursively get descendants
            descendants.update(self._get_all_descendants(child.id))

        return descendants

    # Utility Methods

    def get_favorite_pages(self, workspace_id: str) -> List[Page]:
        """
        Get favorite pages in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of favorite pages
        """
        workspace_filter = Gom.Filter.new_eq(Page, "workspace_id", workspace_id)
        favorite_filter = Gom.Filter.new_eq(Page, "is_favorite", True)
        combined_filter = Gom.Filter.new_and(workspace_filter, favorite_filter)
        sorting = Gom.Sorting(Page, "updated_at", Gom.SortingMode.DESCENDING)

        group = self._database.repository.find_sorted_sync(
            Page, combined_filter, sorting
        )
        count = len(group)
        group.fetch_sync(0, count)
        return list(group)

    def get_recent_pages(self, workspace_id: str, limit: int = 10) -> List[Page]:
        """
        Get recently accessed pages in a workspace.

        Args:
            workspace_id: Workspace ID
            limit: Maximum number of pages to return

        Returns:
            List of recent pages
        """
        workspace_filter = Gom.Filter.new_eq(Page, "workspace_id", workspace_id)
        archived_filter = Gom.Filter.new_eq(Page, "is_archived", False)
        combined_filter = Gom.Filter.new_and(workspace_filter, archived_filter)
        sorting = Gom.Sorting(Page, "last_accessed", Gom.SortingMode.DESCENDING)

        group = self._database.repository.find_sorted_sync(
            Page, combined_filter, sorting
        )
        count = min(len(group), limit)
        group.fetch_sync(0, count)
        return list(group)[:limit]

    def search_pages(self, workspace_id: str, query: str) -> List[Page]:
        """
        Search pages by title and content in a workspace.

        Args:
            workspace_id: Workspace ID
            query: Search query

        Returns:
            List of matching pages
        """
        # This is a simple implementation. For better search,
        # you might want to use full-text search capabilities
        all_pages = self.get_workspace_pages(workspace_id)
        query_lower = query.lower()

        matching_pages = []
        for page in all_pages:
            if query_lower in page.title.lower() or (
                page.text and query_lower in page.text.lower()
            ):
                matching_pages.append(page)

        return matching_pages

    def toggle_page_favorite(self, page_id: str) -> Optional[Page]:
        """
        Toggle the favorite status of a page.

        Args:
            page_id: Page ID

        Returns:
            Updated page or None if not found
        """
        page = self.get_page(page_id)
        if page:
            page.toggle_favorite()
            page.save_sync()
            self.emit("page-updated", page)
            return page
        return None

    def archive_page(self, page_id: str) -> Optional[Page]:
        """
        Archive a page.

        Args:
            page_id: Page ID

        Returns:
            Updated page or None if not found
        """
        page = self.get_page(page_id)
        if page:
            page.archive()
            page.save_sync()
            self.emit("page-updated", page)
            return page
        return None

    def unarchive_page(self, page_id: str) -> Optional[Page]:
        """
        Unarchive a page.

        Args:
            page_id: Page ID

        Returns:
            Updated page or None if not found
        """
        page = self.get_page(page_id)
        if page:
            page.unarchive()
            page.save_sync()
            self.emit("page-updated", page)
            return page
        return None
