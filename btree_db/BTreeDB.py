from typing import Literal, Self
from .BTreeIO import BTreeIO
from .Index import Index


class BTreeDB:

    def __init__(
            self,
            name: str,
            t: int,
            truncate: bool = True
    ):
        if t < 2:
            raise ValueError('t can only be 2 or greater')
        self._mode = None
        self.name = name
        self._io = BTreeIO(name, truncate)
        self._index = Index(name, t, truncate)

    @property
    def closed(self):
        return self._mode is None

    def open(self, mode: Literal['r', 'w']) -> Self:
        self._mode = mode
        self._io.open(mode)
        return self

    def close(self):
        self._index.save()
        self._io.close()
        self._mode = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def read_db_all(self) -> list[str]:
        self._io.seek(0)
        content = []
        while not self._io.eof:
            value = self._io.read()
            content.append(value)
        return content

    def __getitem__(self, key: int) -> str:
        db_pointer, _, _ = self._index.search(key, logging=True)
        if db_pointer is None:
            raise KeyError
        return self._io.read(db_pointer)

    def __setitem__(self, key: int, value: str):
        db_pointer, node_pointer, index = self._index.search(key)
        new_pointer = self._io.tell()
        self._io.write(value)
        if db_pointer is not None:
            self._index.update(node_pointer, index, new_pointer)
        else:
            self._index.insert(node_pointer, index, key, new_pointer)

    def pop(self, key: int):
        db_pointer, node_pointer, index = self._index.search(key)
        if db_pointer is None:
            raise KeyError
        self._index.delete(node_pointer, index)

    def _traverse_recursive(self, node_pointer: int, content: list[tuple[int, str]]):
        node = self._index.read(node_pointer)
        if node.is_leaf:
            for key, pointer in zip(node.keys, node.pointers):
                content.append((key, self._io.read(pointer)))
            return
        for child, key, pointer in node:
            self._traverse_recursive(child, content)
            content.append((key, self._io.read(pointer)))
        self._traverse_recursive(node.children[-1], content)

    def traverse(self) -> list[tuple[int, str]]:
        content = []
        self._traverse_recursive(self._index.root_pointer, content)
        return content
