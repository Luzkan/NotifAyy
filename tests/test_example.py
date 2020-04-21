from source.example import add


def add_correct():
    assert add(5, 7) == 12


def add_incorrect():
    assert add(15, 8) != 21
