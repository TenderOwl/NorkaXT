# Norka Models

This directory contains the data models for the Norka application, built using the GOM (GObject Manager) library from
the GNOME project.

## Workspace Model

The `Workspace` model represents a collection of documents and settings within the Norka application. Each workspace can
contain multiple documents and maintains its own configuration and state.

### Features

- **GObject Integration**: Built on GObject with signal support for property changes
- **Database Persistence**: Uses GOM with SQLite backend for data storage
- **Rich Metadata**: Tracks creation, modification, and access times
- **Workspace States**: Support for active/inactive and favorite workspaces
- **Filesystem Integration**: Optional filesystem path association

### Key Properties

- `name`: Workspace display name
- `description`: Optional workspace description
- `path`: Optional filesystem path
- `is_active`: Whether this is the currently active workspace
- `is_favorite`: Whether this workspace is marked as favorite
- `created_at`, `updated_at`, `last_accessed`: Timestamp tracking

### Signals

The Workspace model emits the following GObject signals:

- `workspace-changed`: Emitted when any workspace property changes
- `workspace-activated`: Emitted when workspace becomes active
- `workspace-deactivated`: Emitted when workspace becomes inactive
- `workspace-accessed`: Emitted when workspace access time is updated

### Usage Example

```python
from norka.models import get_database_manager

# Get database manager
db = get_database_manager()

# Create a new workspace
workspace = db.create_workspace(
    name="My Project",
    description="Main project workspace",
    path="/home/user/projects/my-project"
)

# Connect to signals
workspace.connect('workspace-activated', lambda w: print(f"Activated: {w.name}"))

# Activate the workspace
db.activate_workspace(workspace)

# Make it a favorite
workspace.toggle_favorite()
db.commit()

# Query workspaces
active = db.get_active_workspace()
recent = db.get_recent_workspaces(limit=5)
favorites = db.get_favorite_workspaces()
```

### Database Manager

The `DatabaseManager` class provides a high-level interface for workspace operations:

- `create_workspace()`: Create new workspaces
- `get_workspace()`, `get_workspace_by_name()`: Retrieve workspaces
- `get_active_workspace()`: Get currently active workspace
- `get_recent_workspaces()`: Get recently accessed workspaces
- `get_favorite_workspaces()`: Get favorite workspaces
- `activate_workspace()`: Activate a workspace
- `delete_workspace()`: Delete a workspace

### Installation Requirements

The GOM library and its dependencies need to be installed:

```bash
# Install GOM library (if available through package manager)
sudo dnf install python3-gom  # Fedora
# or
sudo apt install python3-gom  # Ubuntu/Debian

# Or install via pip if available
pip install gom
```

### Database Storage

Workspaces are stored in an SQLite database located at:

- `~/.local/share/norka/norka.db` (follows XDG specification)

The database is automatically created and initialized on first use.

### Integration

To integrate workspace functionality into your Norka application:

1. Import the models: `from norka.models import get_database_manager`
2. Initialize the database manager in your application startup
3. Use workspace signals to respond to state changes
4. Save workspace state during application shutdown
5. Restore active workspace on application startup

See `examples/workspace_example.py` for a complete usage demonstration.
