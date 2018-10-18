import pytest

from cirq.circuits._bucket_priority_queue import BucketPriorityQueue
import cirq


def test_init():
    q = BucketPriorityQueue()
    assert not q.drop_duplicate_entries
    assert list(q) == []
    assert len(q) == 0
    assert not bool(q)
    with pytest.raises(ValueError, match='empty'):
        _ = q.dequeue()

    q = BucketPriorityQueue(entries=[(5, 'a')])
    assert not q.drop_duplicate_entries
    assert list(q) == [(5, 'a')]
    assert len(q) == 1
    assert bool(q)

    q = BucketPriorityQueue(entries=[(5, 'a'), (6, 'b')],
                            drop_duplicate_entries=True)
    assert q.drop_duplicate_entries
    assert list(q) == [(5, 'a'), (6, 'b')]
    assert len(q) == 2
    assert bool(q)


def test_eq():
    eq = cirq.testing.EqualsTester()
    eq.add_equality_group(
        BucketPriorityQueue(),
        BucketPriorityQueue(drop_duplicate_entries=False),
        BucketPriorityQueue(entries=[]),
    )
    eq.add_equality_group(
        BucketPriorityQueue(drop_duplicate_entries=True),
        BucketPriorityQueue(entries=[], drop_duplicate_entries=True),
    )
    eq.add_equality_group(
        BucketPriorityQueue(entries=[(0, 'a')], drop_duplicate_entries=True),
        BucketPriorityQueue(entries=[(0, 'a'), (0, 'a')],
                            drop_duplicate_entries=True),
    )
    eq.add_equality_group(
        BucketPriorityQueue(entries=[(0, 'a')]),
    )
    eq.add_equality_group(
        BucketPriorityQueue(entries=[(0, 'a'), (0, 'a')]),
    )
    eq.add_equality_group(
        BucketPriorityQueue(entries=[(1, 'a')]),
    )
    eq.add_equality_group(
        BucketPriorityQueue(entries=[(0, 'b')]),
    )
    eq.add_equality_group(
        BucketPriorityQueue(entries=[(0, 'a'), (1, 'b')]),
        BucketPriorityQueue(entries=[(1, 'b'), (0, 'a')]),
    )
    eq.add_equality_group(
        BucketPriorityQueue(entries=[(0, 'a'), (1, 'b'), (0, 'a')]),
        BucketPriorityQueue(entries=[(1, 'b'), (0, 'a'), (0, 'a')]),
    )


def test_enqueue_dequeue():
    q = BucketPriorityQueue()
    q.enqueue(5, 'a')
    assert q == BucketPriorityQueue([(5, 'a')])
    q.enqueue(4, 'b')
    assert q == BucketPriorityQueue([(4, 'b'), (5, 'a')])
    assert q.dequeue() == (4, 'b')
    assert q == BucketPriorityQueue([(5, 'a')])
    assert q.dequeue() == (5, 'a')
    assert q == BucketPriorityQueue()
    with pytest.raises(ValueError, match='empty'):
        _ = q.dequeue()


def test_drop_duplicates_enqueue():
    q0 = BucketPriorityQueue()
    q1 = BucketPriorityQueue(drop_duplicate_entries=False)
    q2 = BucketPriorityQueue(drop_duplicate_entries=True)
    for q in [q0, q1, q2]:
        for _ in range(2):
            q.enqueue(0, 'a')

    assert q0 == q1 == BucketPriorityQueue([(0, 'a'), (0, 'a')])
    assert q2 == BucketPriorityQueue([(0, 'a')], drop_duplicate_entries=True)


def test_drop_duplicates_dequeue():
    q0 = BucketPriorityQueue()
    q1 = BucketPriorityQueue(drop_duplicate_entries=False)
    q2 = BucketPriorityQueue(drop_duplicate_entries=True)
    for q in [q0, q1, q2]:
        q.enqueue(0, 'a')
        q.enqueue(0, 'b')
        q.enqueue(0, 'a')
        q.dequeue()
        q.enqueue(0, 'b')
        q.enqueue(0, 'a')

    assert q0 == q1 == BucketPriorityQueue(
        [(0, 'b'), (0, 'a'), (0, 'b'), (0, 'a')])
    assert q2 == BucketPriorityQueue([(0, 'b'), (0, 'a')],
                                     drop_duplicate_entries=True)


def test_same_priority_fifo():
    a = (5, 'a')
    b = (5, 'b')
    for x, y in [(a, b), (b, a)]:
        q = BucketPriorityQueue()
        q.enqueue(*x)
        q.enqueue(*y)
        assert q
        assert q.dequeue() == x
        assert q
        assert q.dequeue() == y
        assert not q


def test_supports_arbitrary_offsets():
    m = 1 << 60

    q_neg = BucketPriorityQueue()
    q_neg.enqueue(-m + 0, 'b')
    q_neg.enqueue(-m - 4, 'a')
    q_neg.enqueue(-m + 4, 'c')
    assert list(q_neg) == [(-m-4, 'a'), (-m, 'b'), (-m+4, 'c')]

    q_pos = BucketPriorityQueue()
    q_pos.enqueue(m + 0, 'b')
    q_pos.enqueue(m + 4, 'c')
    q_pos.enqueue(m - 4, 'a')
    assert list(q_pos) == [(m-4, 'a'), (m, 'b'), (m+4, 'c')]


def test_repr():
    r = repr(BucketPriorityQueue(entries=[(1, 2), (3, 4)],
                                 drop_duplicate_entries=True))
    assert r.endswith('BucketPriorityQueue(entries=[(1, 2), (3, 4)], '
                      'drop_duplicate_entries=True)')

    cirq.testing.assert_equivalent_repr(BucketPriorityQueue())
    cirq.testing.assert_equivalent_repr(BucketPriorityQueue(
        entries=[(1, 'a')]))
    cirq.testing.assert_equivalent_repr(BucketPriorityQueue(
        entries=[(1, 2), (3, 4)],
        drop_duplicate_entries=True))


def test_str():
    s = str(BucketPriorityQueue(entries=[(1, 2), (3, 4)],
                                drop_duplicate_entries=True))
    assert s == """
BucketPriorityQueue {
    1: 2,
    3: 4,
}""".strip()
