from .BTreeDB import BTreeDB

t = 1024


def init_db(truncate=False):
    if not truncate:
        try:
            return BTreeDB('db', t, truncate=False)
        except ValueError or FileNotFoundError:
            pass
    return BTreeDB('db', t, truncate=True)


def insert_or_update(data):
    btree = init_db(False)

    key, value = int(data['key']), data['value']

    with btree.open('w'):
        btree[key] = value


def delete(data):
    btree = init_db(False)

    key = int(data['key'])

    with btree.open('w'):
        btree.pop(key)


def read(data):
    btree = init_db(False)

    key = int(data['key'])

    with btree.open('r'):
        return btree[key]


def read_all():
    btree = init_db(False)

    with btree.open('r'):
        return btree.traverse()


def delete_all():
    init_db(True)
