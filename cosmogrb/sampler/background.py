import h5py
import numba as nb
import numpy as np

from cosmogrb.utils.logging import setup_logger
from cosmogrb.utils.numba_array import VectorFloat64

from .sampler import Sampler

logger = setup_logger(__name__)


@nb.njit(fastmath=True)
def background_poisson_generator(tstart, tstop, rate):
    """

    :param tstart:
    :param tstop:
    :param rate:
    :returns:
    :rtype:

    """

    fmax = rate

    time = tstart

    arrival_times = VectorFloat64(0)
    arrival_times.append(time)

    while True:

        time = time - (1.0 / fmax) * np.log(np.random.rand())
        if time > tstop:
            break
        test = np.random.rand()

        p_test = rate / fmax

        if test <= p_test:
            arrival_times.append(time)

    return arrival_times.arr


class BackgroundSpectrumTemplate(object):
    def __init__(self, counts, start_at_one=False):
        """
        A background template stores and samples
        from a predefined background distribution

        :param counts:
        :returns:
        :rtype:

        """

        self._counts = counts

        j = 0
        if start_at_one:
            j = 1

        self._channels = [i + j for i in range(len(counts))]

        self._normalize_counts()

    def _normalize_counts(self):
        """
        get weights by normalizing the counts

        :returns:
        :rtype:

        """

        self._weights = self._counts / self._counts.sum()

    def sample_channel(self, size=None):
        """
        Sample from the background template

        :param size:
        :returns:
        :rtype:

        """

        np.random.seed()

        # sample a channel from the background
        return np.random.choice(self._channels, size=size, p=self._weights)

    @classmethod
    def from_file(cls, file_name, start_at_one=False):
        """
        Read the counts from a HDF5 file that has
        a dataset in its top directory called counts

        :param cls:
        :param file_name:
        :returns:
        :rtype:

        """

        with h5py.File(file_name, "r") as f:

            counts = f["counts"][()]

        return cls(counts, start_at_one)


class Background(Sampler):
    def __init__(
        self,
        tstart,
        tstop,
        average_rate=1000,
        background_spectrum_template=None,
    ):

        # TODO: change this as it is currently stupid
        self._background_rate = np.random.normal(average_rate, 10)

        self._background_spectrum_template = background_spectrum_template

        logger.debug(f"background rate is {self._background_rate}")

        super(Background, self).__init__(
            tstart=tstart,
            tstop=tstop,
        )

    def sample_times(self):
        """
        sample the background times

        :returns:
        :rtype:

        """

        np.random.seed()

        background_times = background_poisson_generator(
            self._tstart, self._tstop, self._background_rate
        )

        logger.debug(f"created {len(background_times)} background counts")

        return background_times

    def sample_channel(self, size=None):
        """
        Sample the background template. Other options
        do not exist yet

        :param size:
        :returns:
        :rtype:

        """

        np.random.seed()

        if self._background_spectrum_template is not None:

            return self._background_spectrum_template.sample_channel(size=size)

        else:

            raise NotImplementedError()
