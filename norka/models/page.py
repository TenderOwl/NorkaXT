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

from datetime import datetime
from typing import List, Optional

import nanoid
from gi.repository import GObject, Gom
from gi.types import GObjectMeta


class PageResourceMeta(GObjectMeta):
    def __init__(self, name, bases, dct):
        super().__init__(name, bases, dct)
        self.set_table("pages")
        self.set_primary_key("id")
        self.set_notnull("workspace_id")
        self.set_notnull("title")


class Page(Gom.Resource, metaclass=PageResourceMeta):
    """
    Page model representing a document within a workspace.

    A page contains content (text), metadata, and can be organized in a tree
    structure by linking to parent pages. This enables building hierarchical
    document structures similar to Notion, Craft, or Microsoft Loop.
    """

    # GOM resource primary key
    id: str = GObject.Property(type=str)

    # Workspace relationship
    workspace_id: str = GObject.Property(type=str)

    # Page content
    title: str = GObject.Property(type=str)
    text: str | None = GObject.Property(type=str)

    # Visual properties
    icon: str | None = GObject.Property(type=str)
    cover: str | None = GObject.Property(type=str)

    # Tree structure - parent page relationship
    parent_page_id: str | None = GObject.Property(type=str)

    # Metadata
    created_at: int = GObject.Property(type=int)
    updated_at: int = GObject.Property(type=int)
    last_accessed: int = GObject.Property(type=int)

    # Page settings
    is_favorite: bool = GObject.Property(type=bool, default=False)
    is_archived: bool = GObject.Property(type=bool, default=False)
    is_published: bool = GObject.Property(type=bool, default=False)

    # Display order for sorting within parent
    sort_order: int = GObject.Property(type=int, default=0)

    def __init__(self, **kwargs):
        """Initialize a new page."""
        super().__init__(repository=kwargs.get("repository", None))

        self.id = kwargs.get("id", nanoid.generate())

        # Required fields
        self.workspace_id = kwargs.get("workspace_id", "")
        self.title = kwargs.get("title", "Untitled")

        # Content
        self.text = kwargs.get("text", "")

        # Optional visual fields
        self.icon = kwargs.get("icon", None)
        self.cover = kwargs.get("cover", None)

        # Tree structure
        self.parent_page_id = kwargs.get("parent_page_id", None)

        # Timestamps
        now = int(datetime.now().timestamp())
        self.created_at = kwargs.get("created_at", now)
        self.updated_at = kwargs.get("updated_at", now)
        self.last_accessed = kwargs.get("last_accessed", now)

        # Page settings
        self.is_favorite = kwargs.get("is_favorite", False)
        self.is_archived = kwargs.get("is_archived", False)
        self.is_published = kwargs.get("is_published", False)
        self.sort_order = kwargs.get("sort_order", 0)

        self._signal_handlers = {}
        self._setup_signals()

    def _setup_signals(self):
        """Setup GObject signals for the page."""
        # Connect to property change signals
        self.connect("notify::title", self._on_property_changed)
        self.connect("notify::text", self._on_property_changed)
        self.connect("notify::is-favorite", self._on_favorite_changed)
        self.connect("notify::last-accessed", self._on_accessed)

    def _on_property_changed(self, obj, pspec):
        """Handle property changes."""
        self.updated_at = int(datetime.now().timestamp())
        self.emit("page-changed", pspec.name)

    def _on_favorite_changed(self, obj, pspec):
        """Handle favorite status change."""
        self.emit("page-favorite-changed", self.is_favorite)

    def _on_accessed(self, obj, pspec):
        """Handle page access updates."""
        self.emit("page-accessed")

    @property
    def last_accessed_dt(self) -> datetime:
        return datetime.fromtimestamp(self.last_accessed)

    @property
    def created_at_dt(self) -> datetime:
        return datetime.fromtimestamp(self.created_at)

    @property
    def updated_at_dt(self) -> datetime:
        return datetime.fromtimestamp(self.updated_at)

    @property
    def title_with_icon(self):
        return f"{self.icon if self.icon else ''} {self.title}"

    @property
    def is_root_page(self) -> bool:
        """Check if this page is a root page (has no parent)."""
        return self.parent_page_id is None

    @classmethod
    def create(
        cls,
        workspace_id: str,
        title: str,
        text: str = "",
        parent_page_id: str = None,
        icon: str = None,
        cover: str = None,
        repository=None,
    ) -> "Page":
        """
        Create a new page.

        Args:
            workspace_id: ID of the workspace this page belongs to
            title: The page title
            text: Page content text
            parent_page_id: Optional parent page ID for tree structure
            icon: Optional page icon
            cover: Optional page cover
            repository: Optional repository

        Returns:
            New Page instance
        """
        page = cls(
            workspace_id=workspace_id,
            title=title,
            text=text,
            parent_page_id=parent_page_id,
            icon=icon,
            cover=cover,
            repository=repository,
        )
        page.created_at = int(datetime.now().timestamp())
        page.updated_at = page.created_at
        return page

    @classmethod
    def get_by_workspace(cls, session, workspace_id: str) -> List["Page"]:
        """
        Get all pages in a workspace.

        Args:
            session: Database session
            workspace_id: Workspace ID

        Returns:
            List of pages in the workspace
        """
        return session.query(cls).filter(cls.workspace_id == workspace_id).all()

    @classmethod
    def get_root_pages(cls, session, workspace_id: str) -> List["Page"]:
        """
        Get root pages (pages without parent) in a workspace.

        Args:
            session: Database session
            workspace_id: Workspace ID

        Returns:
            List of root pages
        """
        return (
            session.query(cls)
            .filter(cls.workspace_id == workspace_id)
            .filter(cls.parent_page_id.is_(None))
            .order_by(cls.sort_order, cls.title)
            .all()
        )

    @classmethod
    def get_child_pages(cls, session, parent_page_id: str) -> List["Page"]:
        """
        Get child pages of a parent page.

        Args:
            session: Database session
            parent_page_id: Parent page ID

        Returns:
            List of child pages
        """
        return (
            session.query(cls)
            .filter(cls.parent_page_id == parent_page_id)
            .order_by(cls.sort_order, cls.title)
            .all()
        )

    @classmethod
    def get_favorites(cls, session, workspace_id: str) -> List["Page"]:
        """
        Get favorite pages in a workspace.

        Args:
            session: Database session
            workspace_id: Workspace ID

        Returns:
            List of favorite pages
        """
        return (
            session.query(cls)
            .filter(cls.workspace_id == workspace_id)
            .filter(cls.is_favorite == True)
            .order_by(cls.updated_at.desc())
            .all()
        )

    @classmethod
    def get_recent(cls, session, workspace_id: str, limit: int = 10) -> List["Page"]:
        """
        Get recently accessed pages in a workspace.

        Args:
            session: Database session
            workspace_id: Workspace ID
            limit: Maximum number of pages to return

        Returns:
            List of recent pages
        """
        return (
            session.query(cls)
            .filter(cls.workspace_id == workspace_id)
            .filter(cls.is_archived == False)
            .order_by(cls.last_accessed.desc())
            .limit(limit)
            .all()
        )

    def get_children(self, session) -> List["Page"]:
        """
        Get direct child pages of this page.

        Args:
            session: Database session

        Returns:
            List of child pages
        """
        return self.get_child_pages(session, self.id)

    def get_parent(self, session) -> Optional["Page"]:
        """
        Get the parent page of this page.

        Args:
            session: Database session

        Returns:
            Parent page or None if this is a root page
        """
        if self.parent_page_id:
            return session.query(Page).filter(Page.id == self.parent_page_id).first()
        return None

    def get_ancestors(self, session) -> List["Page"]:
        """
        Get all ancestor pages (breadcrumb path).

        Args:
            session: Database session

        Returns:
            List of ancestor pages from root to immediate parent
        """
        ancestors = []
        current_page = self.get_parent(session)

        while current_page:
            ancestors.insert(0, current_page)  # Insert at beginning for correct order
            current_page = current_page.get_parent(session)

        return ancestors

    def move_to_parent(self, session, new_parent_id: Optional[str]):
        """
        Move this page to a new parent.

        Args:
            session: Database session
            new_parent_id: New parent page ID, or None to make it a root page
        """
        self.parent_page_id = new_parent_id
        self.updated_at = int(datetime.now().timestamp())
        session.commit()

    def archive(self):
        """Archive this page."""
        self.is_archived = True
        self.updated_at = int(datetime.now().timestamp())

    def unarchive(self):
        """Unarchive this page."""
        self.is_archived = False
        self.updated_at = int(datetime.now().timestamp())

    def toggle_favorite(self):
        """Toggle the favorite status of this page."""
        self.is_favorite = not self.is_favorite
        self.updated_at = int(datetime.now().timestamp())

    def update_access_time(self):
        """Update the last accessed time."""
        self.last_accessed = int(datetime.now().timestamp())

    def update_content(self, title: str = None, text: str = None):
        """
        Update page content.

        Args:
            title: New title (optional)
            text: New text content (optional)
        """
        if title is not None:
            self.title = title
        if text is not None:
            self.text = text
        self.updated_at = int(datetime.now().timestamp())

    def to_dict(self) -> dict:
        """
        Convert page to dictionary representation.

        Returns:
            Dictionary with page data
        """
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "title": self.title,
            "text": self.text,
            "icon": self.icon,
            "cover": self.cover,
            "parent_page_id": self.parent_page_id,
            "created_at": self.created_at_dt.isoformat() if self.created_at else None,
            "updated_at": self.updated_at_dt.isoformat() if self.updated_at else None,
            "last_accessed": self.last_accessed_dt.isoformat() if self.last_accessed else None,
            "is_favorite": self.is_favorite,
            "is_archived": self.is_archived,
            "is_published": self.is_published,
            "sort_order": self.sort_order,
        }

    def __str__(self) -> str:
        """String representation of the page."""
        return f"Page(id={self.id}, title='{self.title}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"Page(id={self.id}, title='{self.title}', "
            f"workspace_id='{self.workspace_id}', parent_id='{self.parent_page_id}')"
        )


# Register GObject signals
GObject.signal_new(
    "page-changed", Page, GObject.SignalFlags.DETAILED, None, (str,)
)
GObject.signal_new(
    "page-favorite-changed", Page, GObject.SignalFlags.RUN_FIRST, None, (bool,)
)
GObject.signal_new(
    "page-accessed", Page, GObject.SignalFlags.RUN_FIRST, None, ()
)
