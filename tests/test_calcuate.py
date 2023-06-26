from src.calculate import Calculate


def test_1():
    calc = Calculate()
    assert calc.add(1, 2) == 3
