from typing import Literal
from .Converter import Converter


class BTreeIO:

    def __init__(self, file_name: str, truncate: bool = False):
        self.file_name = file_name + '.btree'
        with open(self.file_name, 'ab') as f:
            self._file = f
            if truncate:
                self._file.truncate(0)

    def seek(self, position: int, whence: int = 0):
        self._file.seek(position, whence)

    def to_eof(self):
        self.seek(0, 2)

    def tell(self):
        return self._file.tell()

    def open(self, mode: Literal['r', 'w']):
        if mode == 'r':
            self._file = open(self.file_name, 'rb')
        elif mode == 'w':
            self._file = open(self.file_name, 'ab')
        else:
            raise ValueError("Mode can only be 'r' or 'w'")

    def close(self):
        self._file.close()

    def _read_int(self) -> int:
        return Converter.to_int(self._file.read(4))

    def read(self, pointer: int = None) -> str:
        current_position = self._file.tell()
        if pointer is not None:
            self._file.seek(pointer)
        size = self._read_int()
        result = Converter.to_str(self._file.read(size))
        if pointer is not None:
            self._file.seek(current_position)
        return result

    @property
    def eof(self) -> bool:
        current_position = self.tell()
        self.to_eof()
        eof_position = self.tell()
        self.seek(current_position)
        return current_position == eof_position

    def write(self, value: int | str | bytes):
        if isinstance(value, bytes):
            self._file.write(value)
        elif isinstance(value, str):
            self._file.write(Converter.to_bytes(Converter.byte_length(value)))
            self._file.write(Converter.to_bytes(value))
        elif isinstance(value, int):
            self._file.write(Converter.to_bytes(value))
