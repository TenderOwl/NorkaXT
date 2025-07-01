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
from pathlib import Path
from typing import List, Optional

import nanoid
from gi.repository import GObject, Gom
from gi.types import GObjectMeta


class WorkspaceResourceMeta(GObjectMeta):
    def __init__(self, name, bases, dct):
        super().__init__(name, bases, dct)
        self.set_table("workspaces")
        self.set_primary_key("id")
        self.set_notnull("name")


class Workspace(Gom.Resource, metaclass=WorkspaceResourceMeta):
    """
    Workspace model representing a collection of documents and settings.

    A workspace contains multiple documents, workspace-specific settings,
    and metadata about the working environment.
    """

    # GOM resource primary key
    id: str = GObject.Property(type=str)
    name: str = GObject.Property(type=str)
    description: str | None = GObject.Property(type=str)
    path: str | None = GObject.Property(type=str)

    icon: str | None = GObject.Property(type=str)
    cover: str | None = GObject.Property(type=str)

    created_at: int = GObject.Property(type=int)
    updated_at: int = GObject.Property(type=int)
    last_accessed: int = GObject.Property(type=int)

    is_active: bool = GObject.Property(type=bool, default=True)
    is_favorite: bool = GObject.Property(type=bool, default=False)

    def __init__(self, **kwargs):
        """Initialize a new workspace."""
        super().__init__(repository=kwargs.get("repository", None))

        self.id = kwargs.get("id", nanoid.generate())
        # Initialize properties with defaults
        self.name = kwargs.get("name", "")
        self.description = kwargs.get("description", None)
        self.path = kwargs.get("path", None)

        # Optional fields
        self.icon = kwargs.get("icon", None)
        self.cover = kwargs.get("cover", None)

        # Timestamps
        now = int(datetime.now().timestamp())
        self.created_at = kwargs.get("created_at", now)
        self.updated_at = kwargs.get("updated_at", now)
        self.last_accessed = kwargs.get("last_accessed", now)

        # Workspace settings
        self.is_active = kwargs.get("is_active", False)
        self.is_favorite = kwargs.get("is_favorite", False)

        self._signal_handlers = {}
        self._setup_signals()

    def _setup_signals(self):
        """Setup GObject signals for the workspace."""
        # Connect to property change signals
        self.connect("notify::name", self._on_property_changed)
        self.connect("notify::is-active", self._on_active_changed)
        self.connect("notify::last-accessed", self._on_accessed)

    def _on_property_changed(self, obj, pspec):
        """Handle property changes."""
        self.updated_at = int(datetime.now().timestamp())
        self.emit("workspace-changed", pspec.name)

    def _on_active_changed(self, obj, pspec):
        """Handle workspace activation/deactivation."""
        if self.is_active:
            self.last_accessed = int(datetime.now().timestamp())
            self.emit("workspace-activated")
        else:
            self.emit("workspace-deactivated")

    def _on_accessed(self, obj, pspec):
        """Handle workspace access updates."""
        self.emit("workspace-accessed")

    @property
    def last_accessed_dt(self) -> datetime:
        return datetime.fromtimestamp(self.last_accessed)

    @classmethod
    def create(
        cls,
        name: str,
        description: str = None,
        cover: str = None,
        icon: str = None,
        repository=None,
    ) -> "Workspace":
        """
        Create a new workspace.

        Args:
            name: The workspace name
            description: Optional description
            path: Optional filesystem path
            icon: Optional workspace icon
            repository: Optional repository

        Returns:
            New Workspace instance
        """
        workspace = cls(
            name=name,
            description=description,
            cover=cover,
            icon=icon,
            repository=repository,
        )
        workspace.created_at = int(datetime.now().timestamp())
        workspace.updated_at = workspace.created_at
        return workspace

    @classmethod
    def get_active(cls, session) -> Optional["Workspace"]:
        """
        Get the currently active workspace.

        Args:
            session: Database session

        Returns:
            Active workspace or None
        """
        return session.query(cls).filter(cls.is_active == True).first()

    @classmethod
    def get_recent(cls, session, limit: int = 10) -> List["Workspace"]:
        """
        Get recently accessed workspaces.

        Args:
            session: Database session
            limit: Maximum number of workspaces to return

        Returns:
            List of recent workspaces
        """
        return session.query(cls).order_by(cls.last_accessed.desc()).limit(limit).all()

    @classmethod
    def get_favorites(cls, session) -> List["Workspace"]:
        """
        Get favorite workspaces.

        Args:
            session: Database session

        Returns:
            List of favorite workspaces
        """
        return (
            session.query(cls).filter(cls.is_favorite == True).order_by(cls.name).all()
        )

    def activate(self, session):
        """
        Activate this workspace and deactivate others.

        Args:
            session: Database session
        """
        # Deactivate all workspaces
        session.query(Workspace).update({"is_active": False})

        # Activate this workspace
        self.is_active = True
        self.last_accessed = datetime.now()
        session.commit()

    def deactivate(self):
        """Deactivate this workspace."""
        self.is_active = False

    def toggle_favorite(self):
        """Toggle the favorite status of this workspace."""
        self.is_favorite = not self.is_favorite

    def update_access_time(self):
        """Update the last accessed time."""
        self.last_accessed = datetime.now()

    def get_path(self) -> Optional[Path]:
        """
        Get the workspace path as a Path object.

        Returns:
            Path object or None if no path is set
        """
        if self.path:
            return Path(self.path)
        return None

    def set_path(self, path: Path):
        """
        Set the workspace filesystem path.

        Args:
            path: Path object
        """
        self.path = str(path.resolve())

    def to_dict(self) -> dict:
        """
        Convert workspace to dictionary representation.

        Returns:
            Dictionary with workspace data
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_accessed": self.last_accessed.isoformat()
            if self.last_accessed
            else None,
            "is_active": self.is_active,
            "is_favorite": self.is_favorite,
            "icon": self.icon,
            "cover": self.cover,
        }

    def __str__(self) -> str:
        """String representation of the workspace."""
        return f"Workspace(id={self.id}, name='{self.name}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"Workspace(id={self.id}, name='{self.name}', "
            f"path='{self.path}', active={self.is_active})"
        )


# Register GObject signals
GObject.signal_new(
    "workspace-changed", Workspace, GObject.SignalFlags.DETAILED, None, (str,)
)
GObject.signal_new(
    "workspace-activated", Workspace, GObject.SignalFlags.RUN_FIRST, None, ()
)
GObject.signal_new(
    "workspace-deactivated", Workspace, GObject.SignalFlags.RUN_FIRST, None, ()
)
GObject.signal_new(
    "workspace-accessed", Workspace, GObject.SignalFlags.RUN_FIRST, None, ()
)
