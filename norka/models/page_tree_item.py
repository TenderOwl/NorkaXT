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

from gi.repository import GObject

from norka.models import PageNode


class PageTreeItem(GObject.Object):
    """
    Wrapper class for PageNode to work with Gtk.TreeListModel.
    This represents a single item in the tree structure.
    """

    def __init__(self, page_node: PageNode):
        super().__init__()
        self._page_node = page_node

    @GObject.Property
    def page_node(self) -> PageNode:
        return self._page_node

    @GObject.Property
    def title(self) -> str:
        return self._page_node.page.title

    @GObject.Property
    def icon(self) -> str:
        return self._page_node.page.icon or "📄"

    @GObject.Property
    def has_children(self) -> bool:
        return len(self._page_node.children) > 0

    @GObject.Property
    def children_count(self) -> int:
        return len(self._page_node.children)
