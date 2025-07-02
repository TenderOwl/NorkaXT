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
import asyncio
import sys
from gettext import gettext as _

from gi.events import GLibEventLoopPolicy
from gi.repository import Adw, Gio, GLib
from loguru import logger

from norka.services import WorkspaceService
from norka.window import NorkaWindow


class NorkaApplication(Adw.Application):
    """The main application singleton class."""

    _workspace_service: WorkspaceService | None = None
    _profile: str = ''

    def __init__(self, version: str, profile: str):
        super().__init__(
            application_id="com.tenderowl.norka",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
            resource_base_path="/com/tenderowl/norka",
        )

        self._profile = profile

        logger.debug("Started with profile: {}", profile)

        self.create_action("quit", lambda *_: self.quit(), ["<primary>q"])
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)
        self.create_action(
            "delete-workspace",
            self.on_delete_workspace_action,
            parameter_type=GLib.VariantType.new("s"),
        )

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win: NorkaWindow | None = self.props.active_window
        if not win:
            win = NorkaWindow(application=self)
            if self._profile == "Devel":
                win.add_css_class("devel")
        win.present()

    def do_startup(self):
        Adw.Application.do_startup(self)
        self._workspace_service = WorkspaceService.get_default()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(
            application_name="Norka",
            application_icon="com.tenderowl.norka",
            developer_name="Tender Owl",
            version=self.get_version(),
            developers=["Andrey Maksimov"],
            copyright="© 2025 Tender Owl",
        )
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_("translator-credits"))
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        logger.debug("app.preferences action activated")

    def on_delete_workspace_action(self, action, param: GLib.Variant):
        workspace_id = param.get_string()
        logger.debug("delete workspace {}", workspace_id)
        GLib.idle_add(self._workspace_service.delete_workspace, workspace_id)

    def create_action(self, name, callback, shortcuts=None, parameter_type=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
            parameter_type: an optional action's parameter type
        """
        action = Gio.SimpleAction.new(name, parameter_type)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version: str, profile: str):
    """The application's entry point."""
    asyncio.set_event_loop_policy(GLibEventLoopPolicy())
    app = NorkaApplication(version, profile)
    return app.run(sys.argv)
