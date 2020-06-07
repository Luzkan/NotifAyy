from web.msnotifier.another_example import subtract


def test_subtract_correct():
    assert subtract(7, 5) == 2


def test_subtract_incorrect():
    assert subtract(15, 8) != 5
