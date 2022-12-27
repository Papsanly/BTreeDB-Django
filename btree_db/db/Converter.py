class Converter:

    @classmethod
    def to_bytes(cls, value: int | str) -> bytes:
        if isinstance(value, int):
            return value.to_bytes(4, 'little', signed=False)
        elif isinstance(value, str):
            return value.encode()
        else:
            raise TypeError('to_bytes method supports only str or int objects')

    @classmethod
    def byte_length(cls, value):
        return len(cls.to_bytes(value))

    @classmethod
    def to_int(cls, b: bytes) -> int:
        return int.from_bytes(b, 'little', signed=False)

    @classmethod
    def to_str(cls, b: bytes) -> str:
        return b.decode()
