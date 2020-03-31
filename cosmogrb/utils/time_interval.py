# from 3ML

import matplotlib.pyplot as plt
import copy
from operator import itemgetter, attrgetter
import numpy as np

from cosmogrb.utils.plotting import step_plot


class IntervalsDoNotOverlap(RuntimeError):
    pass


class IntervalsNotContiguous(RuntimeError):
    pass


class TimeInterval(object):
    def __init__(self, start, stop, counts=None, dead_time=0, swap_if_inverted=False):

        self._start = float(start)
        self._stop = float(stop)

        self._counts = counts
        self._dead_time = dead_time

        self._exposure = (self._stop - self._start) - dead_time

        # Note that this allows to have intervals of zero duration

        if self._stop < self._start:

            if swap_if_inverted:

                self._start = stop
                self._stop = start

            else:

                raise RuntimeError(
                    "Invalid time interval! TSTART must be before TSTOP and TSTOP-TSTART >0. "
                    "Got tstart = %s and tstop = %s" % (start, stop)
                )

    def __add__(self, number):
        """
        Return a new time interval equal to the original time interval shifted to the right by number

        :param number: a float
        :return: a new TimeInterval instance
        """

        return TimeInterval(self._start + number, self._stop + number)

    def __sub__(self, number):
        """
        Return a new time interval equal to the original time interval shifted to the left by number

        :param number: a float
        :return: a new TimeInterval instance
        """

        return TimeInterval(self._start - number, self._stop - number)

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def counts(self):
        return self._counts

    @property
    def dead_time(self):
        return self._dead_time

    @property
    def rate(self):
        if self._counts is not None:
            return self._counts / self._exposure

    @property
    def width(self):

        return self._stop - self._start

    @property
    def exposure(self):
        return self._exposure

    @property
    def mid_point(self):

        return (self._start + self._stop) / 2.0

    def __repr__(self):

        return " interval %s - %s (width: %s)" % (self.start, self.stop, self.width,)

    def intersect(self, interval):
        """
        Returns a new time interval corresponding to the intersection between this interval and the provided one.

        :param interval: a TimeInterval instance
        :type interval: Interval
        :return: new interval covering the intersection
        :raise IntervalsDoNotOverlap : if the intervals do not overlap
        """

        if not self.overlaps_with(interval):
            raise IntervalsDoNotOverlap(
                "Current interval does not overlap with provided interval"
            )

        new_start = max(self._start, interval.start)
        new_stop = min(self._stop, interval.stop)

        return TimeInterval(new_start, new_stop)

    def merge(self, interval):
        """
        Returns a new interval corresponding to the merge of the current and the provided time interval. The intervals
        must overlap.

        :param interval: a TimeInterval instance
         :type interval : Interval
        :return: a new TimeInterval instance
        """

        if self.overlaps_with(interval):

            new_start = min(self._start, interval.start)
            new_stop = max(self._stop, interval.stop)

            if (self._counts is not None) and (interval.counts is not None):

                new_counts = self._counts + interval.counts

            else:

                new_counts = None

            new_dead_time = self._dead_time + interval.dead_time

            return TimeInterval(new_start, new_stop, new_counts, new_dead_time)

        else:

            raise IntervalsDoNotOverlap("Could not merge non-overlapping intervals!")

    def overlaps_with(self, interval):
        """
        Returns whether the current time interval and the provided one overlap or not

        :param interval: a TimeInterval instance
        :type interval: Interval
        :return: True or False
        """

        if interval.start == self._start or interval.stop == self._stop:

            return True

        elif interval.start > self._start and interval.start < self._stop:

            return True

        elif interval.stop > self._start and interval.stop < self._stop:

            return True

        elif interval.start < self._start and interval.stop > self._stop:

            return True

        else:

            return False

    def to_string(self):
        """
        returns a string representation of the time interval that is like the
        argument of many interval reading funcitons

        :return:
        """

        return "%f-%f" % (self.start, self.stop)

    def __eq__(self, other):

        if not isinstance(other, TimeInterval):

            # This is needed for things like comparisons to None or other objects.
            # Of course if the other object is not even a TimeInterval, the two things
            # cannot be equal

            return False

        else:

            return self.start == other.start and self.stop == other.stop


class TimeIntervalSet(object):
    """
    A set of intervals

    """

    def __init__(self, list_of_intervals=()):

        self._intervals = list(list_of_intervals)

    @classmethod
    def from_starts_and_stops(cls, starts, stops, counts=None, dead_time=None):
        """
        Builds a TimeIntervalSet from a list of start and stop times:

        start = [-1,0]  ->   [-1,0], [0,1]
        stop =  [0,1]

        :param starts:
        :param stops:
        :return:
        """

        assert len(starts) == len(stops), (
            "starts length: %d and stops length: %d must have same length"
            % (len(starts), len(stops))
        )

        if counts is not None:

            assert len(starts) == len(counts), (
                "starts length: %d and counts length: %d must have same length"
                % (len(starts), len(counts))
            )

        else:

            counts = [None] * len(starts)

        if dead_time is not None:

            assert len(starts) == len(dead_time), (
                "starts length: %d and dead_time length: %d must have same length"
                % (len(starts), len(dead_time))
            )

        else:

            dead_time = [0] * len(starts)

        list_of_intervals = []

        for imin, imax, ic, idt in zip(starts, stops, counts, dead_time):
            list_of_intervals.append(TimeInterval(imin, imax, ic, idt))

        return cls(list_of_intervals)

    @classmethod
    def from_list_of_edges(cls, edges):
        """
        Builds a IntervalSet from a list of time edges:

        edges = [-1,0,1] -> [-1,0], [0,1]


        :param edges:
        :return:
        """

        raise NotImplementedError()

        # # sort the time edges

        # edges.sort()

        # list_of_intervals = []

        # for imin, imax in zip(edges[:-1], edges[1:]):
        #     list_of_intervals.append(cls.new_interval(imin, imax))

        # return cls(list_of_intervals)

    def merge_intersecting_intervals(self, in_place=False):
        """

        merges intersecting intervals into a contiguous intervals


        :return:
        """

        # get a copy of the sorted intervals

        sorted_intervals = self.sort()

        new_intervals = []

        while len(sorted_intervals) > 1:

            # pop the first interval off the stack

            this_interval = sorted_intervals.pop(0)

            # see if that interval overlaps with the the next one

            if this_interval.overlaps_with(sorted_intervals[0]):

                # if so, pop the next one

                next_interval = sorted_intervals.pop(0)

                # and merge the two, appending them to the new intervals

                new_intervals.append(this_interval.merge(next_interval))

            else:

                # otherwise just append this interval

                new_intervals.append(this_interval)

                # now if there is only one interval left
                # it should not overlap with any other interval
                # and the loop will stop
                # otherwise, we continue

        # if there was only one interval
        # or a leftover from the merge
        # we append it
        if sorted_intervals:

            assert (
                len(sorted_intervals) == 1
            ), "there should only be one interval left over, this is a bug"  # pragma: no cover

            # we want to make sure that the last new interval did not
            # overlap with the final interval
            if new_intervals:

                if new_intervals[-1].overlaps_with(sorted_intervals[0]):

                    new_intervals[-1] = new_intervals[-1].merge(sorted_intervals[0])

                else:

                    new_intervals.append(sorted_intervals[0])

            else:

                new_intervals.append(sorted_intervals[0])

        if in_place:

            self.__init__(new_intervals)

        else:

            return TimeIntervalSet(new_intervals)

    def extend(self, list_of_intervals):

        self._intervals.extend(list_of_intervals)

    def __len__(self):

        return len(self._intervals)

    def __iter__(self):

        for interval in self._intervals:
            yield interval

    def __getitem__(self, item):

        return self._intervals[item]

    def __eq__(self, other):

        for interval_this, interval_other in zip(self.argsort(), other.argsort()):

            if not self[interval_this] == other[interval_other]:
                return False

        return True

    def pop(self, index):

        return self._intervals.pop(index)

    def sort(self):
        """
        Returns a sorted copy of the set (sorted according to the tstart of the time intervals)

        :return:
        """

        if self.is_sorted:

            return copy.deepcopy(self)

        else:

            return TimeIntervalSet(
                np.atleast_1d(itemgetter(*self.argsort())(self._intervals))
            )

    def argsort(self):
        """
        Returns the indices which order the set

        :return:
        """

        # Gather all tstarts
        tstarts = [x.start for x in self._intervals]

        return [x[0] for x in sorted(enumerate(tstarts), key=itemgetter(1))]

    def is_contiguous(self, relative_tolerance=1e-5):
        """
        Check whether the time intervals are all contiguous, i.e., the stop time of one interval is the start
        time of the next

        :return: True or False
        """

        starts = [attrgetter("start")(x) for x in self._intervals]
        stops = [attrgetter("stop")(x) for x in self._intervals]

        return np.allclose(starts[1:], stops[:-1], rtol=relative_tolerance)

    @property
    def is_sorted(self):
        """
        Check whether the time intervals are sorted
        :return: True or False
        """

        return np.all(self.argsort() == np.arange(len(self)))

    def containing_bin(self, value):
        """
        finds the index of the interval containing
        :param value:
        :return:
        """

        # Get the index of the first ebounds upper bound larger than energy
        # (but never go below zero or above the last channel)
        idx = min(max(0, np.searchsorted(self.edges, value) - 1), len(self))

        return idx

    def containing_interval(self, start, stop, inner=True, as_mask=False):
        """

        returns either a mask of the intervals contained in the selection
        or a new set of intervals within the selection. NOTE: no sort is performed

        :param start: start of interval
        :param stop: stop of interval
        :param inner: if True, returns only intervals strictly contained within bounds, if False, returns outer bounds as well
        :param as_mask: if you want a mask or the intervals
        :return:
        """

        # loop only once because every call unpacks the array
        # we need to round for the comparison because we may have read from
        # strings which are rounded to six decimals

        starts = np.round(self.starts, decimals=6)
        stops = np.round(self.stops, decimals=6)

        start = np.round(start, decimals=6)
        stop = np.round(stop, decimals=6)

        condition = (starts >= start) & (stop >= stops)

        if not inner:

            # now we get the end caps
            lower_condition = (starts <= start) & (start <= stops)

            upper_condition = (starts <= stop) & (stop <= stops)

            condition = condition | lower_condition | upper_condition

        # if we just want the mask

        if as_mask:

            return condition

        else:

            return TimeIntervalSet(np.asarray(self._intervals)[condition])

    @property
    def starts(self):
        """
        Return the starts fo the set

        :return: list of start times
        """

        return np.array([interval.start for interval in self._intervals])

    @property
    def stops(self):
        """
        Return the stops of the set

        :return:
        """

        return np.array([interval.stop for interval in self._intervals])

    @property
    def counts(self):

        return np.array([interval.counts for interval in self._intervals])

    @property
    def rates(self):

        return np.array([interval.rate for interval in self._intervals])

    @property
    def exposures(self):

        return np.array([interval.exposure for interval in self._intervals])

    @property
    def mid_points(self):

        return np.array([interval.mid_point for interval in self._intervals])

    @property
    def widths(self):

        return np.array([interval._get_width() for interval in self._intervals])

    @property
    def absolute_start(self):
        """
        the minimum of the start times
        :return:
        """

        return min(self.starts)

    @property
    def absolute_stop(self):
        """
        the maximum of the stop times
        :return:
        """

        return max(self.stops)

    @property
    def edges(self):
        """
        return an array of time edges if contiguous
        :return:
        """

        if self.is_contiguous() and self.is_sorted:

            edges = [
                interval.start
                for interval in itemgetter(*self.argsort())(self._intervals)
            ]
            edges.append(
                [
                    interval.stop
                    for interval in itemgetter(*self.argsort())(self._intervals)
                ][-1]
            )

        else:

            raise IntervalsNotContiguous(
                "Cannot return edges for non-contiguous intervals"
            )

        return edges

    def to_string(self):
        """


        returns a set of string representaitons of the intervals
        :return:
        """

        return ",".join([interval.to_string() for interval in self._intervals])

    @property
    def bin_stack(self):
        """

        get a stacked view of the bins [[start_1,stop_1 ],
                                        [start_2,stop_2 ]]

        :return:
        """

        return np.vstack((self.starts, self.stops)).T

    def __add__(self, number):
        """
        Shift all time intervals to the right by number

        :param number: a float
        :return: new TimeIntervalSet instance
        """

        new_set = TimeIntervalSet()
        new_set.extend([time_interval + number for time_interval in self._intervals])

        return new_set

    def __sub__(self, number):
        """
        Shift all time intervals to the left by number (in place)

        :param number: a float
        :return: new TimeIntervalSet instance
        """

        new_set = TimeIntervalSet(
            [time_interval - number for time_interval in self._intervals]
        )

        return new_set

    def plot_intervals(self, as_rates=True, ax=None, **kwargs):
        """
        plot the intervals as rates or counts

        :param as_rates: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        xbins = self.bin_stack

        if as_rates:

            y = self.rates
            y_label = "rate (cnts/s)"

        else:

            y = self.counts
            y_label = "cnts"

        step_plot(xbins, y, ax=ax, **kwargs)

        ax.set_xlabel("time")
        ax.set_ylabel(y_label)

        return fig
