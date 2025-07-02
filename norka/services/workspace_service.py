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
import datetime
from typing import Optional, Self

from gi.repository import GLib, GObject, Gom
from loguru import logger

from norka.models import DatabaseManager, Workspace, get_database_manager

# Global database manager instance
_db_manager: DatabaseManager | None = None


class WorkspaceService(GObject.Object):
    __gtype_name__ = "WorkspaceService"

    _service: Self | None = None

    __gsignals__ = {
        "workspace-created": (GObject.SIGNAL_RUN_FIRST, None, (Workspace,)),
        "workspace-updated": (GObject.SIGNAL_RUN_FIRST, None, (Workspace,)),
        "workspace-deleted": (GObject.SIGNAL_RUN_FIRST, None, (Workspace, bool)),
        "workspace-activated": (GObject.SIGNAL_RUN_FIRST, None, (Workspace,)),
    }

    def __init__(self, database: DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self._database = database
        logger.debug(
            "WorkspaceService initialized with database at {}", database.database_path
        )

    @classmethod
    def get_default(cls) -> Self:
        if cls._service is None:
            cls._service = cls(database=get_database_manager())
        return cls._service

    def create_workspace(
        self, name: str, description: str = None, cover: str = None, icon: str = None
    ) -> Workspace:
        """
        Create a new workspace.

        Args:
            name: Workspace name
            description: Optional description
            cover: Optional filesystem path
            icon: Optional workspace icon

        Returns:
            Created workspace
        """
        workspace = Workspace.create(
            name, description, cover, icon, repository=self._database.repository
        )
        workspace.save_sync()
        self.emit("workspace-created", workspace)
        return workspace

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """
        Get workspace by ID.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace or None if not found
        """
        _filter = Gom.Filter.new_eq(Workspace, "id", workspace_id)
        return self._database.repository.find_one_sync(Workspace, _filter)

    def get_workspace_by_name(self, name: str) -> Optional[Workspace]:
        """
        Get workspace by name.

        Args:
            name: Workspace name

        Returns:
            Workspace or None if not found
        """
        return self._session.query(Workspace).filter(Workspace.name == name).first()

    def get_active_workspace(self) -> Optional[Workspace]:
        """
        Get the currently active workspace.

        Returns:
            Active workspace or None
        """
        return Workspace.get_active(self._session)

    def get_recent_workspaces(self, limit: int = 10):
        """
        Get recently accessed workspaces.

        Args:
            limit: Maximum number of workspaces

        Returns:
            List of recent workspaces
        """
        return Workspace.get_recent(self._session, limit)

    def get_favorite_workspaces(self):
        """
        Get favorite workspaces.

        Returns:
            List of favorite workspaces
        """
        return Workspace.get_favorites(self._session)

    def get_all_workspaces(self):
        """
        Get all workspaces.

        Returns:
            List of all workspaces
        """
        sorting = Gom.Sorting(Workspace, "name", Gom.SortingMode.DESCENDING)
        group = self._database.repository.find_sorted_sync(Workspace, None, sorting)
        count = len(group)
        group.fetch_sync(0, count)
        return list(group)

    def update_workspace(self, workspace: Workspace) -> bool:
        """
        Update a workspace.

        Args:
            workspace: Workspace to update
        """
        try:
            workspace.updated_at = int(datetime.datetime.now().timestamp())
            workspace.update_access_time()
            workspace.save_sync()
            self.emit("workspace-updated", workspace)

        except GLib.Error as e:
            logger.error("Error: ", e.domain)
            logger.error(e)

        return False

    def delete_workspace(self, workspace_id: str) -> bool:
        """
        Delete a workspace.

        Args:
            workspace_id: Workspace ID to delete
        """
        logger.debug("delete_workspace({})", workspace_id)
        try:
            workspace = self.get_workspace(workspace_id)
        except GLib.Error as e:
            logger.error("Error: ", e.domain)
            logger.error(e)
            return False

        if workspace:
            logger.debug("Found workspace to delete: {}", workspace)
            result = workspace.delete_sync()
            self.emit("workspace-deleted", workspace, result)
            return result

        return False

    def activate_workspace(self, workspace_id: str):
        """
        Activate a workspace.

        Args:
            workspace_id: Workspace ID to activate
        """
        try:
            workspace = self.get_workspace(workspace_id)
        except GLib.Error as e:
            logger.error("Error: ", e.domain)
            logger.error(e)
            return False

        workspace.update_access_time()
        workspace.save_sync()
        self.emit("workspace-activated", workspace)

        return None
