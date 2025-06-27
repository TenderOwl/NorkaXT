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

from pathlib import Path
from typing import Optional

from gi.repository import GLib, GObject, Gom

from .workspace import Workspace


class DatabaseManager:
    """
    Database manager for GOM-based models.

    Handles database initialization, session management, and provides
    convenience methods for workspace operations.
    """

    _repository: Gom.Repository | None = None
    _adapter: Gom.Adapter | None = None

    _database_path: str

    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize the database manager.

        Args:
            database_path: Optional custom database path
        """

        if database_path is None:
            # Use XDG data directory for database storage
            data_dir = Path(GLib.get_user_data_dir())
            data_dir.mkdir(parents=True, exist_ok=True)
            database_path = str(data_dir / "norka.db")

        self._database_path = database_path
        self._setup_database()

    def _setup_database(self):
        """Setup the database connection and create tables."""
        # Connect to the database
        self._adapter = Gom.Adapter()
        self._adapter.open_sync(self._database_path)

        # Create the table
        self._repository = Gom.Repository(adapter=self._adapter)
        self._repository.automatic_migrate_sync(1, [Workspace])

    @property
    def database_path(self):
        return self._database_path

    def close(self):
        """Close the database connection."""
        self._adapter.close_sync()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # Workspace convenience methods
    def commit(self):
        """Commit pending changes."""
        self._repository.commit()

    def rollback(self):
        """Rollback pending changes."""
        self._repository.rollback()

    @GObject.Property()
    def repository(self):
        return self._repository


# Global database manager instance
_db_manager: DatabaseManager | None = None


def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def close_database():
    """Close the global database connection."""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None
