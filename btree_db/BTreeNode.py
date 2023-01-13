import pickle
from os import path
from typing import Self


class BTreeNode:

    def __init__(self, db_name: str, pointer: int, t: int):
        self.db_name = db_name
        self.pointer = pointer
        self.file_name = self.file_name_from_pointer(db_name, pointer)
        self.t = t
        self.children = []
        self.keys = []
        self.pointers = []
        self.parent = None

    @classmethod
    def file_name_from_pointer(cls, db_name: str, pointer: int):
        return f'{db_name}_index/{pointer}.bnode'

    @classmethod
    def pointer_from_file_name(cls, file_name: str) -> int:
        return int(path.splitext(path.split(file_name)[1])[0])

    @classmethod
    def load(cls, db_name: str, pointer: int | str) -> Self:
        if isinstance(pointer, int):
            file_name = cls.file_name_from_pointer(db_name, pointer)
        else:
            file_name = pointer
        with open(file_name, 'rb') as f:
            return pickle.load(f)

    @property
    def is_full(self) -> bool:
        return self.size > 2 * self.t - 1

    @property
    def is_min(self) -> bool:
        return self.size < self.t - 1

    @property
    def level(self) -> int:
        if self.parent is None:
            return 0
        parent_node = self.load(self.db_name, self.parent)
        return parent_node.level + 1

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def size(self) -> int:
        return len(self.keys)

    @property
    def is_empty(self) -> bool:
        return len(self.keys) == 0

    def save(self):
        with open(self.file_name, 'wb') as f:
            pickle.dump(self, f)

    def split_list(self, lst: list) -> tuple[list[int], int, list[int]]:
        return lst[:self.size // 2], lst[self.size // 2], lst[self.size // 2 + 1:]

    def insert(self, index: int, key: int, pointer: int):
        self.keys.insert(index, key)
        self.pointers.insert(index, pointer)

    def append(self, key: int, pointer: int):
        self.keys.append(key)
        self.pointers.append(pointer)

    def remove(self, index: int) -> tuple[int, int]:
        key = self.keys.pop(index)
        pointer = self.pointers.pop(index)
        return key, pointer

    def extend(self, node: Self):
        self.keys.extend(node.keys)
        self.pointers.extend(node.pointers)
        if not self.is_leaf:
            self.children += node.children

    def split(self) -> tuple[int, int, list[int], list[int], list[int]]:
        keys1, mid_key, keys2 = self.split_list(self.keys)
        pointers1, mid_pointer, pointers2 = self.split_list(self.pointers)
        if self.children:
            children1, mid_children, children2 = self.split_list(self.children)
            self.children = children1 + [mid_children]
        else:
            children2 = []
        self.keys = keys1
        self.pointers = pointers1
        return mid_key, mid_pointer, children2, keys2, pointers2

    def search(self, key: int) -> tuple[int | None, int, int]:
        comparisons = 0
        if self.size == 0:
            return None, 0, comparisons
        low = 0
        high = self.size - 1
        while low <= high:
            comparisons += 1
            mid = (low + high) // 2
            if self.keys[mid] == key:
                return self.pointers[mid], mid, comparisons
            elif self.keys[mid] < key:
                low = mid + 1
            else:
                high = mid - 1
        return None, low, comparisons

    def redistribute_keys_left(self, left_node: Self, right_node: Self):
        left_node_last_element = left_node.remove(-1)
        index = self.get_child_index(right_node)
        parent_element = self[index]

        self[index] = left_node_last_element
        right_node.insert(0, *parent_element)

        if not left_node.is_leaf:
            child_pointer = left_node.children.pop(-1)
            right_node.children.insert(0, child_pointer)

    def redistribute_keys_right(self, left_node: Self, right_node: Self):
        right_node_first_element = right_node.remove(0)
        index = self.get_child_index(right_node)
        parent_element = self[index]

        self[index] = right_node_first_element
        left_node.append(*parent_element)

        if not right_node.is_leaf:
            child = right_node.children.pop(0)
            left_node.children.append(child)

    def get_child_index(self, right_child) -> int:
        return self.search(right_child.keys[0])[1] - 1

    def merge(self, left_child: Self, right_child: Self):
        index = self.get_child_index(right_child)
        parent_element = self.remove(index)
        self.children.pop(index + 1)

        left_child.append(*parent_element)
        left_child.extend(right_child)

    def __getitem__(self, index: int) -> tuple[int, int]:
        return self.keys[index], self.pointers[index]

    def __setitem__(self, index: int, value: tuple[int, int]):
        self.keys[index] = value[0]
        self.pointers[index] = value[1]

    def __iter__(self):
        return zip(self.children, self.keys, self.pointers)
