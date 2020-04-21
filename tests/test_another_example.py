from msnotifier.another_example import subtract


def test_add_correct():
    assert subtract(7, 5) == 2


def test_add_incorrect():
    assert subtract(15, 8) == 7
