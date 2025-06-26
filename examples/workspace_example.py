#!/usr/bin/env python3
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

"""
Example usage of the Workspace model with GOM library.

This example demonstrates how to:
- Create workspaces
- Manage workspace activation
- Handle workspace events
- Query workspaces
"""

import sys
from pathlib import Path

# Add the parent directory to sys.path to import norka modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from norka.models import close_database, get_database_manager


def on_workspace_activated(workspace):
    """Handle workspace activation event."""
    print(f"✓ Workspace '{workspace.name}' activated")


def on_workspace_changed(workspace, property_name):
    """Handle workspace property changes."""
    print(f"✓ Workspace '{workspace.name}' property '{property_name}' changed")


def demonstrate_workspace_usage():
    """Demonstrate various workspace operations."""
    print("Norka Workspace Model Example")
    print("=" * 40)

    # Get database manager
    db = get_database_manager()

    try:
        # Create some example workspaces
        print("\n1. Creating workspaces...")

        workspace1 = db.create_workspace(
            name="My Project",
            description="Main project workspace",
            path="/home/user/projects/my-project",
        )

        workspace2 = db.create_workspace(
            name="Notes", description="Personal notes and ideas"
        )

        workspace3 = db.create_workspace(
            name="Research",
            description="Research documents and papers",
            path="/home/user/documents/research",
        )

        print(f"✓ Created workspace: {workspace1}")
        print(f"✓ Created workspace: {workspace2}")
        print(f"✓ Created workspace: {workspace3}")

        # Connect to workspace signals
        print("\n2. Setting up event handlers...")
        workspace1.connect("workspace-activated", on_workspace_activated)
        workspace1.connect("workspace-changed", on_workspace_changed)

        # Activate a workspace
        print("\n3. Activating workspace...")
        db.activate_workspace(workspace1)

        # Make workspace2 a favorite
        print("\n4. Managing workspace properties...")
        workspace2.toggle_favorite()
        workspace2.set_window_state(1200, 800, maximized=False)
        db.commit()

        print(
            f"✓ Workspace '{workspace2.name}' is now favorite: {workspace2.is_favorite}"
        )

        # Query workspaces
        print("\n5. Querying workspaces...")

        # Get active workspace
        active = db.get_active_workspace()
        if active:
            print(f"✓ Active workspace: {active.name}")

        # Get all workspaces
        all_workspaces = db.get_all_workspaces()
        print(f"✓ Total workspaces: {len(all_workspaces)}")

        # Get recent workspaces
        recent = db.get_recent_workspaces(limit=5)
        print(f"✓ Recent workspaces: {[w.name for w in recent]}")

        # Get favorites
        favorites = db.get_favorite_workspaces()
        print(f"✓ Favorite workspaces: {[w.name for w in favorites]}")

        # Demonstrate workspace data export
        print("\n6. Exporting workspace data...")
        workspace_data = workspace1.to_dict()
        print(f"✓ Workspace data keys: {list(workspace_data.keys())}")

        # Update workspace access time
        print("\n7. Updating access times...")
        workspace3.update_access_time()
        db.commit()
        print(f"✓ Updated access time for '{workspace3.name}'")

        # Demonstrate path operations
        print("\n8. Working with workspace paths...")
        if workspace1.get_path():
            print(f"✓ Workspace path: {workspace1.get_path()}")

        # Set a new path
        new_path = Path("/tmp/example-workspace")
        workspace2.set_path(new_path)
        db.commit()
        print(f"✓ Set new path for '{workspace2.name}': {workspace2.get_path()}")

        print("\n" + "=" * 40)
        print("Example completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        close_database()


if __name__ == "__main__":
    demonstrate_workspace_usage()
