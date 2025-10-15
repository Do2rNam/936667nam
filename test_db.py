from db import FruitDB


def test_lookup():
    db = FruitDB(':memory:')
    info = db.get_info('banana')
    assert info is not None
    assert info['name'] == 'banana'
    print('DB test passed')
    db.close()


if __name__ == '__main__':
    test_lookup()
from db import FruitDB


def test_lookup():
    db = FruitDB(':memory:')
    info = db.get_info('banana')
    assert info is not None
    assert info['name'] == 'banana'
    print('DB test passed')
    db.close()


if __name__ == '__main__':
    test_lookup()
