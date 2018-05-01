from cirq.testing import EqualsTester
from cirq import LineQubit


def test_init():
    q = LineQubit(1)
    assert q.x == 1


def test_eq():
    eq = EqualsTester()
    eq.make_equality_pair(lambda: LineQubit(1))
    eq.add_equality_group(LineQubit(2))
    eq.add_equality_group(LineQubit(0))


def test_str():
    assert str(LineQubit(5)) == '5'


def test_repr():
    assert repr(LineQubit(5)) == 'LineQubit(5)'


def test_is_adjacent():
    assert LineQubit(1).is_adjacent(LineQubit(2))
    assert LineQubit(1).is_adjacent(LineQubit(0))
    assert LineQubit(2).is_adjacent(LineQubit(3))
    assert not LineQubit(1).is_adjacent(LineQubit(3))
    assert not LineQubit(2).is_adjacent(LineQubit(0))


def test_range():
    assert LineQubit.range(0) == []
    assert LineQubit.range(1) == [LineQubit(0)]
    assert LineQubit.range(2) == [LineQubit(0), LineQubit(1)]
    assert LineQubit.range(5) == [
        LineQubit(0),
        LineQubit(1),
        LineQubit(2),
        LineQubit(3),
        LineQubit(4),
    ]

    assert LineQubit.range(0, 0) == []
    assert LineQubit.range(0, 1) == [LineQubit(0)]
    assert LineQubit.range(1, 4) == [LineQubit(1), LineQubit(2), LineQubit(3)]

    assert LineQubit.range(3, 1, -1) == [LineQubit(3), LineQubit(2)]
    assert LineQubit.range(3, 5, -1) == []
    assert LineQubit.range(1, 5, 2) == [LineQubit(1), LineQubit(3)]
