"""
DSA Lab 09 - PBL: Tree Data Structure
Application : File System Directory Navigation (N-ary Tree)

Each node = a folder or a file.
Every node (except the root) has exactly ONE parent; a folder can have
any number of children -> N-ary tree.

Features
  - Node-based tree (parent + children links)
  - Insert (by path), delete, move
  - Search: DFS (by name) and BFS (by name), find by extension
  - Traversals: pre-order (DFS), post-order, level-order (BFS)
  - Display hierarchy (tree-style print)
  - Enhancements: folder size calculation, path-from-root, depth/height,
    cycle prevention when moving folders
  - Unit tests (normal + boundary/unsuccessful cases)

Run demo : python filesystem_tree.py
Run tests: python filesystem_tree.py test
"""

from collections import deque
import sys
import unittest


# --------------------------------------------------------------------------
# Node
# --------------------------------------------------------------------------
class Node:
    """A single item in the file system (folder or file)."""

    def __init__(self, name, is_dir=True, size=0, parent=None):
        self.name = name
        self.is_dir = is_dir
        self.size = 0 if is_dir else size     # folders get size from children
        self.parent = parent                   # exactly one parent (None for root)
        self.children = {}                     # name -> Node (unique names per folder)

    def path(self):
        """Full path from root, e.g. /Documents/Work/report.pdf"""
        parts, cur = [], self
        while cur.parent is not None:
            parts.append(cur.name)
            cur = cur.parent
        return "/" + "/".join(reversed(parts))

    def __repr__(self):
        kind = "DIR" if self.is_dir else "FILE"
        return f"<{kind} {self.name}>"


# --------------------------------------------------------------------------
# Tree
# --------------------------------------------------------------------------
class FileSystemTree:
    def __init__(self, root_name="root"):
        self.root = Node(root_name, is_dir=True)
        self.count = 1

    # ---------- helpers ----------
    @staticmethod
    def _split(path):
        return [p for p in path.strip("/").split("/") if p]

    def get(self, path):
        """Return node at path (e.g. '/Documents/Work') or None."""
        node = self.root
        for part in self._split(path):
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node

    # ---------- insertion ----------
    def add(self, parent_path, name, is_dir=True, size=0):
        """Add a folder/file under parent_path. Returns the new node."""
        parent = self.get(parent_path)
        if parent is None:
            raise FileNotFoundError(f"Parent path not found: {parent_path}")
        if not parent.is_dir:
            raise NotADirectoryError(f"{parent_path} is a file, cannot contain items")
        if name in parent.children:
            raise FileExistsError(f"'{name}' already exists in {parent_path}")
        if not name or "/" in name:
            raise ValueError("Invalid name")
        if not is_dir and size < 0:
            raise ValueError("Size cannot be negative")
        node = Node(name, is_dir, size, parent)
        parent.children[name] = node
        self.count += 1
        return node

    # ---------- deletion ----------
    def delete(self, path):
        """Delete a node and its whole subtree."""
        node = self.get(path)
        if node is None:
            raise FileNotFoundError(path)
        if node is self.root:
            raise PermissionError("Cannot delete the root")
        removed = self._count(node)
        del node.parent.children[node.name]
        node.parent = None
        self.count -= removed
        return removed

    # ---------- move (enhancement) ----------
    def move(self, src_path, dest_folder_path):
        node, dest = self.get(src_path), self.get(dest_folder_path)
        if node is None or dest is None:
            raise FileNotFoundError("Source or destination not found")
        if node is self.root:
            raise PermissionError("Cannot move the root")
        if not dest.is_dir:
            raise NotADirectoryError(dest_folder_path)
        # prevent a folder being moved inside itself -> would create a cycle
        cur = dest
        while cur is not None:
            if cur is node:
                raise ValueError("Cannot move a folder into itself/its subtree")
            cur = cur.parent
        if node.name in dest.children:
            raise FileExistsError(f"'{node.name}' already exists in destination")
        del node.parent.children[node.name]
        node.parent = dest
        dest.children[node.name] = node

    # ---------- searching ----------
    def search_dfs(self, name):
        """DFS search; returns list of paths of all nodes with this name."""
        found, stack = [], [self.root]
        while stack:
            node = stack.pop()
            if node.name == name:
                found.append(node.path())
            stack.extend(reversed(list(node.children.values())))
        return found

    def search_bfs(self, name):
        """BFS search; returns the path of the SHALLOWEST match or None."""
        q = deque([self.root])
        while q:
            node = q.popleft()
            if node.name == name:
                return node.path()
            q.extend(node.children.values())
        return None

    def find_by_extension(self, ext):
        ext = ext.lower() if ext.startswith(".") else "." + ext.lower()
        return [n.path() for n in self.preorder()
                if not n.is_dir and n.name.lower().endswith(ext)]

    # ---------- traversals ----------
    def preorder(self, node=None):
        node = node or self.root
        yield node
        for child in node.children.values():
            yield from self.preorder(child)

    def postorder(self, node=None):
        node = node or self.root
        for child in node.children.values():
            yield from self.postorder(child)
        yield node

    def level_order(self):
        q = deque([self.root])
        while q:
            node = q.popleft()
            yield node
            q.extend(node.children.values())

    # ---------- metrics ----------
    def _count(self, node):
        return 1 + sum(self._count(c) for c in node.children.values())

    def total_size(self, path="/"):
        """Total size (KB) of a folder = sum of all files below it (post-order idea)."""
        node = self.get(path)
        if node is None:
            raise FileNotFoundError(path)
        return self._size(node)

    def _size(self, node):
        if not node.is_dir:
            return node.size
        return sum(self._size(c) for c in node.children.values())

    def height(self, node=None):
        node = node or self.root
        if not node.children:
            return 0
        return 1 + max(self.height(c) for c in node.children.values())

    def depth(self, path):
        node = self.get(path)
        if node is None:
            raise FileNotFoundError(path)
        d = 0
        while node.parent is not None:
            node, d = node.parent, d + 1
        return d

    # ---------- display ----------
    def display(self, node=None, prefix="", show_size=True):
        """Pretty tree print, like the Linux `tree` command."""
        lines = []
        node = node or self.root

        def rec(n, pre, last, is_root=False):
            label = n.name + ("/" if n.is_dir else "")
            if show_size:
                label += f"  [{self._size(n)} KB]"
            if is_root:
                lines.append(label)
                new_pre = ""
            else:
                lines.append(pre + ("└── " if last else "├── ") + label)
                new_pre = pre + ("    " if last else "│   ")
            kids = list(n.children.values())
            for i, c in enumerate(kids):
                rec(c, new_pre, i == len(kids) - 1)

        rec(node, "", True, is_root=True)
        return "\n".join(lines)


# --------------------------------------------------------------------------
# Demonstration dataset
# --------------------------------------------------------------------------
def build_sample():
    t = FileSystemTree("C:")
    t.add("/", "Documents")
    t.add("/", "Pictures")
    t.add("/", "Programs")
    t.add("/Documents", "Work")
    t.add("/Documents", "University")
    t.add("/Documents/Work", "report.pdf", False, 250)
    t.add("/Documents/Work", "budget.xlsx", False, 120)
    t.add("/Documents/University", "DSA")
    t.add("/Documents/University/DSA", "lab09.py", False, 8)
    t.add("/Documents/University/DSA", "lab09_report.pdf", False, 540)
    t.add("/Documents/University", "Circuits")
    t.add("/Documents/University/Circuits", "notes.docx", False, 90)
    t.add("/Pictures", "Trip")
    t.add("/Pictures/Trip", "beach.jpg", False, 2048)
    t.add("/Pictures/Trip", "city.jpg", False, 1800)
    t.add("/Pictures", "profile.png", False, 300)
    t.add("/Programs", "Python")
    t.add("/Programs/Python", "python.exe", False, 5000)
    return t


def demo():
    t = build_sample()
    print("=== Directory hierarchy ===")
    print(t.display())

    print("\n=== Pre-order (DFS) ===")
    print(" -> ".join(n.name for n in t.preorder()))
    print("\n=== Post-order ===")
    print(" -> ".join(n.name for n in t.postorder()))
    print("\n=== Level-order (BFS) ===")
    print(" -> ".join(n.name for n in t.level_order()))

    print("\n=== Search ===")
    print("DFS 'lab09.py'      :", t.search_dfs("lab09.py"))
    print("BFS 'Trip'          :", t.search_bfs("Trip"))
    print("Find *.pdf          :", t.find_by_extension("pdf"))
    print("Search 'ghost.txt'  :", t.search_dfs("ghost.txt"))

    print("\n=== Metrics ===")
    print("Total files+folders :", t.count)
    print("Tree height         :", t.height())
    print("Depth of lab09.py   :", t.depth("/Documents/University/DSA/lab09.py"))
    print("Size of /Pictures   :", t.total_size("/Pictures"), "KB")

    print("\n=== Move /Pictures/Trip -> /Documents ===")
    t.move("/Pictures/Trip", "/Documents")
    print(t.display())

    print("\n=== Delete /Programs ===")
    print("Nodes removed:", t.delete("/Programs"))
    print(t.display())


# --------------------------------------------------------------------------
# Test cases
# --------------------------------------------------------------------------
class TestFileSystemTree(unittest.TestCase):
    def setUp(self):
        self.t = build_sample()

    # insertion
    def test_add_success(self):
        n = self.t.add("/Documents", "new.txt", False, 5)
        self.assertEqual(n.path(), "/Documents/new.txt")
        self.assertEqual(self.t.count, 20)

    def test_add_duplicate(self):
        with self.assertRaises(FileExistsError):
            self.t.add("/Documents", "Work")

    def test_add_invalid_parent(self):
        with self.assertRaises(FileNotFoundError):
            self.t.add("/Nope", "x")

    def test_add_under_file(self):
        with self.assertRaises(NotADirectoryError):
            self.t.add("/Documents/Work/report.pdf", "x")

    # search
    def test_search_found(self):
        self.assertEqual(self.t.search_dfs("city.jpg"), ["/Pictures/Trip/city.jpg"])
        self.assertEqual(self.t.search_bfs("Work"), "/Documents/Work")

    def test_search_not_found(self):
        self.assertEqual(self.t.search_dfs("zzz"), [])
        self.assertIsNone(self.t.search_bfs("zzz"))

    def test_search_duplicates_in_different_folders(self):
        self.t.add("/Pictures", "Work")
        self.assertEqual(len(self.t.search_dfs("Work")), 2)

    def test_extension(self):
        self.assertEqual(len(self.t.find_by_extension(".pdf")), 2)
        self.assertEqual(self.t.find_by_extension("mp3"), [])

    # traversals
    def test_preorder_starts_at_root_and_visits_all(self):
        names = [n.name for n in self.t.preorder()]
        self.assertEqual(names[0], "C:")
        self.assertEqual(len(names), self.t.count)

    def test_postorder_root_last(self):
        self.assertEqual([n.name for n in self.t.postorder()][-1], "C:")

    def test_level_order_top_level(self):
        names = [n.name for n in self.t.level_order()]
        self.assertEqual(names[:4], ["C:", "Documents", "Pictures", "Programs"])

    # metrics
    def test_sizes(self):
        self.assertEqual(self.t.total_size("/Documents/Work"), 370)
        self.assertEqual(self.t.total_size("/Pictures"), 4148)

    def test_height_depth(self):
        self.assertEqual(self.t.height(), 4)
        self.assertEqual(self.t.depth("/"), 0)
        self.assertEqual(self.t.depth("/Documents/University/DSA/lab09.py"), 4)

    # delete
    def test_delete_subtree(self):
        removed = self.t.delete("/Pictures")
        self.assertEqual(removed, 5)
        self.assertIsNone(self.t.get("/Pictures/Trip/beach.jpg"))
        self.assertEqual(self.t.count, 14)

    def test_delete_root_not_allowed(self):
        with self.assertRaises(PermissionError):
            self.t.delete("/")

    def test_delete_missing(self):
        with self.assertRaises(FileNotFoundError):
            self.t.delete("/ghost")

    # move
    def test_move_ok(self):
        self.t.move("/Pictures/Trip", "/Documents")
        self.assertIsNotNone(self.t.get("/Documents/Trip/beach.jpg"))
        self.assertIsNone(self.t.get("/Pictures/Trip"))

    def test_move_into_own_subtree(self):
        with self.assertRaises(ValueError):
            self.t.move("/Documents", "/Documents/Work")

    # boundary: tree with only root
    def test_empty_tree(self):
        e = FileSystemTree("root")
        self.assertEqual(e.height(), 0)
        self.assertEqual(e.count, 1)
        self.assertEqual([n.name for n in e.preorder()], ["root"])
        self.assertEqual(e.total_size(), 0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main(argv=["x"], verbosity=2)
    else:
        demo()
