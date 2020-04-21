from msnotifier.example import add


def test_add_correct():
    assert add(5, 7) == 12


def test_add_incorrect():
    assert add(15, 8) != 21
