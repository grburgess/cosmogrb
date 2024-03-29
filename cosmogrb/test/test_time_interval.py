from __future__ import print_function

from builtins import zip

import pytest

from cosmogrb.utils.time_interval import (
    IntervalsDoNotOverlap,
    IntervalsNotContiguous,
    TimeInterval,
    TimeIntervalSet,
)


def test_time_interval_constructor():

    t = TimeInterval(-10.0, 10.0)

    assert t.start == -10.0
    assert t.stop == 10.0
    assert t.width == 20.0
    assert t.mid_point == 0.0
    assert t.dead_time == 0.0
    assert t.exposure == 20.0

    with pytest.raises(RuntimeError):

        _ = TimeInterval(10.0, -10.0, swap_if_inverted=False)

    _ = TimeInterval(-10.0, 10.0, swap_if_inverted=True)

    t2 = TimeInterval(-10.0, 10.0, counts=20)

    assert t2.start == -10.0
    assert t2.stop == 10.0
    assert t2.width == 20.0
    assert t2.mid_point == 0.0
    assert t2.rate == 1.0

    t2 = TimeInterval(-10.0, 10.0, counts=20, dead_time=10.0)

    assert t2.start == -10.0
    assert t2.stop == 10.0
    assert t2.width == 20.0
    assert t2.mid_point == 0.0
    assert t2.rate == 2.0
    assert t2.exposure == 10.0


def test_time_interval_repr():

    t = TimeInterval(-10.0, 10.0)

    print(t)


def test_time_interval_overlaps_with():

    t1 = TimeInterval(-10.0, 10.0)
    t2 = TimeInterval(0.0, 30.0)
    t3 = TimeInterval(-100, 100.0)
    t4 = TimeInterval(-100, -10)
    t5 = TimeInterval(100.0, 200.0)

    assert t1.overlaps_with(t2)
    assert t1.overlaps_with(t3)
    assert not t1.overlaps_with(t4)
    assert not t1.overlaps_with(t5)


def test_time_interval_intersect():

    t1 = TimeInterval(-10.0, 10.0)
    t2 = TimeInterval(0.0, 30.0)

    t = t1.intersect(t2)

    assert t.start == 0.0
    assert t.stop == 10.0

    with pytest.raises(IntervalsDoNotOverlap):

        t1 = TimeInterval(-10.0, 10.0)
        t2 = TimeInterval(20.0, 30.0)

        _ = t1.intersect(t2)


def test_time_interval_merge():
    t1 = TimeInterval(-10.0, 10.0)
    t2 = TimeInterval(0.0, 30.0)

    t = t1.merge(t2)

    assert t.start == -10.0
    assert t.stop == 30.0

    with pytest.raises(IntervalsDoNotOverlap):

        t1 = TimeInterval(-10.0, 10.0)
        t2 = TimeInterval(20.0, 30.0)

        _ = t1.merge(t2)

    t1 = TimeInterval(-10.0, 1.0, counts=10.0)
    t2 = TimeInterval(0.0, 10.0, counts=10.0)

    t3 = t1.merge(t2)

    # i think this is incorrect
    assert t3.counts == 20.0


def test_time_interval_add():

    t = TimeInterval(-10.0, 10.0)

    new_t = t + 10.0  # type: TimeInterval

    assert new_t.start == 0
    assert new_t.stop == 20.0


def test_time_interval_sub():

    t = TimeInterval(-10.0, 10.0)

    new_t = t - 10.0  # type: TimeInterval

    assert new_t.start == -20.0
    assert new_t.stop == 0.0


def test_time_interval_constructor_set():

    t1 = TimeInterval(-10.0, 20.0)
    t2 = TimeInterval(10.0, 30.0)

    ts = TimeIntervalSet([t1, t2])

    assert ts[0] == t1
    assert ts[1] == t2

    t1 = TimeInterval(-10.0, 20.0, counts=1)
    t2 = TimeInterval(10.0, 30.0, counts=1)

    ts = TimeIntervalSet([t1, t2])

    ts.plot_intervals()

    ts.counts

    ts.rates

    # Use start and stops
    ts5 = TimeIntervalSet.from_starts_and_stops([-2, -1, 0, 1], [-1, 0, 1, 2])

    assert ts5[0].start == -2
    assert ts5[0].stop == -1
    assert ts5[-1].start == 1
    assert ts5[-1].stop == 2
    assert ts5[1].start == -1
    assert ts5[1].stop == 0
    assert ts5[2].start == 0
    assert ts5[2].stop == 1

    with pytest.raises(AssertionError):

        ts6 = TimeIntervalSet.from_starts_and_stops([-2, -1, 0, 1], [-1, 0, 1])

    # test display


#    ts5.display()


def test_time_interval_iterator_set():

    t1 = TimeInterval(-10.0, 20.0)
    t2 = TimeInterval(10.0, 30.0)

    ts = TimeIntervalSet([t1, t2])

    for i, tt in enumerate(ts):

        if i == 0:

            assert tt == t1

        else:

            assert tt == t2


def test_time_interval_extend_set():

    t1 = TimeInterval(-10.0, 20.0)
    t2 = TimeInterval(10.0, 30.0)

    ts = TimeIntervalSet([t1, t2])

    t3 = TimeInterval(30.0, 40.0)
    t4 = TimeInterval(40.0, 50.0)

    ts.extend([t3, t4])

    assert len(ts) == 4

    ts.extend(TimeIntervalSet([t3, t4]))

    assert len(ts) == 6


def test_time_interval_add_sub_set():

    t1 = TimeInterval(-10.0, 20.0)
    t2 = TimeInterval(10.0, 30.0)

    ts = TimeIntervalSet([t1, t2])

    ts2 = ts + 10.0  # type: TimeIntervalSet

    assert ts2[0].start == 0.0
    assert ts2[1].stop == 40.0

    ts3 = ts - 10.0  # type: TimeIntervalSet

    assert ts3[0].start == -20.0
    assert ts3[1].stop == 20.0


def test_time_interval_argsort_set():

    t1 = TimeInterval(-10.0, 20.0)
    t2 = TimeInterval(10.0, 30.0)
    t3 = TimeInterval(-30.0, 50.0)

    ts = TimeIntervalSet([t1, t2, t3])

    idx = ts.argsort()

    assert idx == [2, 0, 1]


def test_time_interval_sort_set():

    t1 = TimeInterval(-10.0, 20.0)
    t2 = TimeInterval(10.0, 30.0)
    t3 = TimeInterval(-30.0, 50.0)

    ts = TimeIntervalSet([t1, t2, t3])

    ts2 = ts.sort()

    assert ts2[0] == t3
    assert ts2[1] == t1
    assert ts2[2] == t2


def test_time_interval_equivalence():

    t1 = TimeInterval(10.523, 20.32)

    assert t1 == TimeInterval(10.523, 20.32)

    assert t1 is not None


def test_time_interval_set_pop():

    t1 = TimeInterval(-10.0, 20.0)
    t2 = TimeInterval(10.0, 30.0)
    t3 = TimeInterval(-30.0, 50.0)

    ts = TimeIntervalSet([t1, t2, t3])

    popped = ts.pop(1)

    assert popped == t2


def test_time_interval_set_is_contiguous():

    t1 = TimeInterval(-10.0, 20.0)
    t2 = TimeInterval(10.0, 30.0)
    t3 = TimeInterval(-30.0, 50.0)

    ts = TimeIntervalSet([t1, t2, t3])

    assert not ts.is_contiguous()

    t1 = TimeInterval(0.0, 1.0)
    t2 = TimeInterval(1.0, 2.0)
    t3 = TimeInterval(2.0, 3.0)

    ts = TimeIntervalSet([t1, t2, t3])

    assert ts.is_contiguous()

    t1 = TimeInterval(0.0, 1.0)
    t2 = TimeInterval(1.1, 2.0)
    t3 = TimeInterval(2.0, 3.0)

    ts = TimeIntervalSet([t1, t2, t3])

    assert not ts.is_contiguous()

    t1 = TimeInterval(0.0, 1.0)
    t2 = TimeInterval(2.0, 3.0)
    t3 = TimeInterval(1.0, 2.0)

    ts = TimeIntervalSet([t1, t2, t3])

    assert not ts.is_contiguous()

    new_ts = ts.sort()

    assert new_ts.is_contiguous()


def test_merging_set_intervals():

    # test that non overlapping intervals
    # do not result in a merge

    t1 = TimeInterval(-10.0, 0.0)
    t2 = TimeInterval(5.0, 10.0)
    t3 = TimeInterval(15.0, 20.0)

    ts1 = TimeIntervalSet([t1, t2, t3])

    ts2 = ts1.merge_intersecting_intervals(in_place=False)

    assert len(ts2) == 3
    assert t1 == ts2[0]
    assert t2 == ts2[1]
    assert t3 == ts2[2]

    # end merge works

    t1 = TimeInterval(-10.0, 0.0)
    t2 = TimeInterval(5.0, 10.0)
    t3 = TimeInterval(7.0, 20.0)

    ts1 = TimeIntervalSet([t1, t2, t3])

    ts2 = ts1.merge_intersecting_intervals(in_place=False)

    assert len(ts2) == 2
    assert t1 == ts2[0]
    assert TimeInterval(5.0, 20.0) == ts2[1]

    # begin merge works

    t1 = TimeInterval(-10.0, 0.0)
    t2 = TimeInterval(-5.0, 10.0)
    t3 = TimeInterval(15, 20.0)

    ts1 = TimeIntervalSet([t1, t2, t3])

    ts2 = ts1.merge_intersecting_intervals(in_place=False)

    assert len(ts2) == 2
    assert TimeInterval(-10.0, 10.0) == ts2[0]
    assert TimeInterval(15.0, 20.0) == ts2[1]

    # middle merge works

    t1 = TimeInterval(-10.0, 0.0)
    t2 = TimeInterval(5.0, 10.0)
    t3 = TimeInterval(7.0, 20.0)
    t4 = TimeInterval(35.0, 40.0)

    ts1 = TimeIntervalSet([t1, t2, t3, t4])

    ts2 = ts1.merge_intersecting_intervals(in_place=False)

    assert len(ts2) == 3
    assert t1 == ts2[0]
    assert TimeInterval(5.0, 20.0) == ts2[1]
    assert t4 == ts2[2]

    # both end merge works

    t1 = TimeInterval(-10.0, 0.0)
    t2 = TimeInterval(-5.0, 10.0)
    t3 = TimeInterval(15.0, 20.0)
    t4 = TimeInterval(35.0, 45.0)
    t5 = TimeInterval(40.0, 50.0)

    ts1 = TimeIntervalSet([t1, t2, t3, t4, t5])

    ts2 = ts1.merge_intersecting_intervals(in_place=False)

    assert len(ts2) == 3
    assert TimeInterval(-10.0, 10.0) == ts2[0]
    assert t3 == ts2[1]
    assert TimeInterval(35.0, 50.0) == ts2[2]

    # multi merge works

    t1 = TimeInterval(-10.0, 0.0)
    t2 = TimeInterval(-5.0, 10.0)
    t3 = TimeInterval(7, 20.0)

    ts1 = TimeIntervalSet([t1, t2, t3])

    ts2 = ts1.merge_intersecting_intervals(in_place=False)

    assert len(ts2) == 1
    assert TimeInterval(-10.0, 20.0) == ts2[0]

    # complete overlap merge works

    t1 = TimeInterval(-10.0, 25.0)
    t2 = TimeInterval(-5.0, 10.0)
    t3 = TimeInterval(7, 20.0)

    ts1 = TimeIntervalSet([t1, t2, t3])

    ts2 = ts1.merge_intersecting_intervals(in_place=False)

    assert len(ts2) == 1
    assert TimeInterval(-10.0, 25.0) == ts2[0]

    # tests the inplace operation

    t1 = TimeInterval(-10.0, 25.0)
    t2 = TimeInterval(-5.0, 10.0)
    t3 = TimeInterval(7, 20.0)

    ts1 = TimeIntervalSet([t1, t2, t3])

    ts1.merge_intersecting_intervals(in_place=True)

    assert len(ts1) == 1
    assert TimeInterval(-10.0, 25.0) == ts1[0]


# def test_interval_set_to_string():

#     # also tests the time interval to string

#     t1 = TimeInterval(-10.0, 0.0)
#     t2 = TimeInterval(5.0, 10.0)
#     t3 = TimeInterval(15.0, 20.0)

#     ts1 = TimeIntervalSet([t1, t2, t3])

#     strings = ts1.to_string()

#     strings_split = strings.split(",")

#     assert t1.to_string() == strings_split[0]
#     assert t2.to_string() == strings_split[1]
#     assert t3.to_string() == strings_split[2]

#     ts2 = TimeIntervalSet.from_strings(t1.to_string())

#     assert ts2[0] == t1


def test_time_interval_sets_starts_stops():

    t1 = TimeInterval(-10.0, 0.0)
    t2 = TimeInterval(5.0, 10.0)
    t3 = TimeInterval(15.0, 20.0)

    ts1 = TimeIntervalSet([t1, t2, t3])

    for start, stop, interval in zip(ts1.starts, ts1.stops, [t1, t2, t3]):

        assert interval.start == start
        assert interval.stop == stop


# def test_time_edges():

#     t1 = TimeInterval(-10.0, 0.0)
#     t2 = TimeInterval(0.0, 10.0)
#     t3 = TimeInterval(10.0, 20.0)

#     ts1 = TimeIntervalSet([t1, t2, t3])

#     assert ts1.time_edges[0] == -10.0
#     assert ts1.time_edges[1] == 0.0
#     assert ts1.time_edges[2] == 10.0
#     assert ts1.time_edges[3] == 20.0

#     with pytest.raises(IntervalsNotContiguous):
#         t1 = TimeInterval(-10.0, -5.0)
#         t2 = TimeInterval(0.0, 10.0)
#         t3 = TimeInterval(10.0, 20.0)

#         ts1 = TimeIntervalSet([t1, t2, t3])

#         _ = ts1.time_edges
