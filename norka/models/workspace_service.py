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

from gi.repository import GObject, Gom

from norka.models import DatabaseManager, Workspace


class WorkspaceService(GObject.Object):
    __gtype_name__ = "WorkspaceService"

    def __init__(self, database: DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self._database = database

    def create_workspace(
        self, name: str, description: str = None, path: str = None
    ) -> Workspace:
        """
        Create a new workspace.

        Args:
            name: Workspace name
            description: Optional description
            path: Optional filesystem path

        Returns:
            Created workspace
        """
        workspace = Workspace.create(self._database.repository, name, description, path)
        self._session.add(workspace)
        self._session.commit()
        return workspace

    def get_workspace(self, workspace_id: int) -> Optional[Workspace]:
        """
        Get workspace by ID.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace or None if not found
        """
        return (
            self._session.query(Workspace).filter(Workspace.id == workspace_id).first()
        )

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
        group = self._database._repository.find_sorted_sync(Workspace, None, sorting)
        count = len(group)
        group.fetch_sync(0, count)
        return list(group)

    def delete_workspace(self, workspace: Workspace):
        """
        Delete a workspace.

        Args:
            workspace: Workspace to delete
        """
        self._session.delete(workspace)
        self._session.commit()

    def activate_workspace(self, workspace: Workspace):
        """
        Activate a workspace.

        Args:
            workspace: Workspace to activate
        """
        workspace.activate(self._session)
