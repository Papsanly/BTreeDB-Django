import os
from os import mkdir, listdir
from shutil import rmtree
from typing import Literal

from .BTreeNode import BTreeNode


class Index:

    def __init__(self, db_name: str, t: int, truncate: bool, max_nodes_in_memory: int = 2048):
        self.db_name = db_name
        self.dir_name = f'{db_name}_index/'
        self.max_nodes_in_memory = max_nodes_in_memory
        self.t = t

        if truncate:
            try:
                rmtree(self.dir_name)
            except FileNotFoundError:
                pass
            mkdir(self.dir_name)
            self.root_pointer = 0
            self.max_pointer = 0
            self._root = BTreeNode(db_name, 0, t)
        else:
            self.root_pointer = self._get_root_pointer()
            self.max_pointer = self._get_max_pointer()
            self._root = BTreeNode.load(db_name, self.root_pointer)
        self._unsaved_nodes = {self.root_pointer: self._root}

    @property
    def nodes(self) -> list[BTreeNode]:
        nodes = []
        for file_name in self._node_file_names:
            nodes.append(BTreeNode.load(self.db_name, file_name))
        return nodes

    @property
    def _node_file_names(self) -> list[str]:
        return [self.dir_name + name for name in listdir(self.dir_name)]

    def _get_root_pointer(self) -> int:
        for node in self.nodes:
            if node.parent is None:
                return node.pointer

    def _get_max_pointer(self) -> int:
        return max(node.pointer for node in self.nodes)

    def read(self, pointer: int, modify: bool = True) -> BTreeNode:
        if len(self._unsaved_nodes) > self.max_nodes_in_memory:
            self.save(2)
        if pointer in self._unsaved_nodes.keys():
            node = self._unsaved_nodes[pointer]
        else:
            node = BTreeNode.load(self.db_name, pointer)
            if modify:
                self._unsaved_nodes[pointer] = node
        return node

    def _create_node(self):
        if len(self._unsaved_nodes) > self.max_nodes_in_memory:
            self.save(2)
        self.max_pointer += 1
        new_node = BTreeNode(self.db_name, self.max_pointer, self.t)
        self._unsaved_nodes[self.max_pointer] = new_node
        return new_node

    def split_node(self, node: BTreeNode):
        new_node = self._create_node()
        mid_key, mid_pointer, new_node.children, new_node.keys, new_node.pointers = node.split()
        for child_pointer in new_node.children:
            child = self.read(child_pointer)
            child.parent = new_node.pointer
        if node.parent:
            parent = self.read(node.parent)
            new_node.parent = parent.pointer
            _, index = parent.search(mid_key)
            parent.children.insert(index + 1, new_node.pointer)
            self.insert(node.parent, index, mid_key, mid_pointer)
        else:
            parent = self._create_node()
            self.root_pointer = node.parent = parent.pointer
            new_node.parent = parent.pointer
            parent.keys.append(mid_key)
            parent.pointers.append(mid_pointer)
            parent.children = [node.pointer, new_node.pointer]

    def insert(self, node_pointer: int, index: int, key: int, db_pointer: int):
        node = self.read(node_pointer)
        node.insert(index, key, db_pointer)
        if node.is_full:
            self.split_node(node)

    def update(self, node_pointer: int, index: int, db_pointer: int):
        node = self.read(node_pointer)
        node.pointers[index] = db_pointer

    def search(self, key: int) -> tuple[int, int, int]:
        return self._search_recursive(self.root_pointer, key)

    def _search_recursive(self, pointer: int, key: int):
        node = self.read(pointer, modify=False)
        db_pointer, index = node.search(key)

        if db_pointer is not None or node.is_leaf:
            return db_pointer, pointer, index
        child = node.children[index]
        return self._search_recursive(child, key)

    def _get_sibling(self, which: Literal['l', 'r'], node: BTreeNode, parent: BTreeNode) -> BTreeNode | None:
        _, index = parent.search(node.keys[0])
        if which == 'l':
            sibling_idx = index - 1
        elif which == 'r':
            sibling_idx = index + 1
        else:
            raise ValueError("Which can only be 'l' or 'r'")

        if not 0 <= sibling_idx < len(parent.children):
            return

        sibling_pointer = parent.children[sibling_idx]
        return self.read(sibling_pointer)

    def _clear_node(self, node: BTreeNode):
        try:
            os.remove(node.file_name)
        except FileNotFoundError:
            pass
        self._unsaved_nodes.pop(node.pointer)

    def _merge(self, left_node: BTreeNode, right_node: BTreeNode, parent: BTreeNode):
        parent.merge(left_node, right_node)
        for child_pointer in right_node.children:
            child = self.read(child_pointer)
            child.parent = left_node.pointer
        self._clear_node(right_node)
        if parent.is_empty:
            self.root_pointer = left_node.pointer
            left_node.parent = None

    def _handle_min_node_deletion(self, node: BTreeNode):
        if node.parent is None:
            return

        parent = self.read(node.parent)

        left_sibling = self._get_sibling('l', node, parent)
        if left_sibling is not None and not left_sibling.size == self.t - 1:
            parent.redistribute_keys_left(left_sibling, node)
            if not node.is_leaf:
                child = self.read(node.children[0])
                child.parent = node.pointer
            return

        right_sibling = self._get_sibling('r', node, parent)
        if right_sibling is not None and not right_sibling.size == self.t - 1:
            parent.redistribute_keys_right(node, right_sibling)
            if not node.is_leaf:
                child = self.read(node.children[-1])
                child.parent = node.pointer
            return

        if left_sibling is not None:
            self._merge(left_sibling, node, parent)
        elif right_sibling is not None:
            self._merge(node, right_sibling, parent)

        if parent.is_empty:
            self._clear_node(parent)
            return

        if parent.is_min:
            self._handle_min_node_deletion(parent)

    def _handle_non_leaf_node_deletion(self, node: BTreeNode, index: int):
        predecessor_node = self._get_predecessor_node(node, index)
        if not predecessor_node.size == self.t - 1:
            element = predecessor_node.remove(-1)
            node.insert(index, *element)
            return

        successor_node = self._get_successor_node(node, index)
        if not successor_node.size == self.t - 1:
            element = successor_node.remove(0)
            node.insert(index, *element)
            return

        node.insert(index, *predecessor_node[-1])
        self.delete(predecessor_node.pointer, -1)

    def _get_successor_node(self, node: BTreeNode, index: int) -> BTreeNode:
        child = self.read(node.children[index + 1])
        while not child.is_leaf:
            child = self.read(child.children[0])
        return child

    def _get_predecessor_node(self, node: BTreeNode, index: int) -> BTreeNode:
        child = self.read(node.children[index])
        while not child.is_leaf:
            child = self.read(child.children[-1])
        return child

    def delete(self, node_pointer: int, index: int):
        node = self.read(node_pointer)
        node.remove(index)
        if node.is_leaf:
            if node.is_min:
                self._handle_min_node_deletion(node)
        else:
            self._handle_non_leaf_node_deletion(node, index)

    def save(self, count: int = None):
        if count is None:
            count = len(self._unsaved_nodes)
        for key in list(self._unsaved_nodes.keys())[:count]:
            self._unsaved_nodes[key].save()
            self._unsaved_nodes.pop(key)
