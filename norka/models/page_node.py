from typing import List, Optional

from norka.models import Page

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


class PageNode:
    """
    Represents a page node in a tree structure.

    This helper class is used to build and represent the hierarchical
    structure of pages within a workspace.
    """

    def __init__(self, page: Page):
        self.page = page
        self.children: List[PageNode] = []
        self.parent: Optional[PageNode] = None

    def add_child(self, child_node: "PageNode"):
        """Add a child node to this page node."""
        child_node.parent = self
        self.children.append(child_node)
        # Sort children by sort_order and then by title
        self.children.sort(key=lambda x: (x.page.sort_order, x.page.title))

    def get_depth(self) -> int:
        """Get the depth of this node in the tree (root = 0)."""
        depth = 0
        current = self.parent
        while current:
            depth += 1
            current = current.parent
        return depth

    def to_dict(self, include_children: bool = True) -> dict:
        """Convert node to dictionary representation."""
        result = self.page.to_dict()
        result["depth"] = self.get_depth()

        if include_children:
            result["children"] = [child.to_dict() for child in self.children]
        else:
            result["has_children"] = len(self.children) > 0
            result["children_count"] = len(self.children)

        return result
