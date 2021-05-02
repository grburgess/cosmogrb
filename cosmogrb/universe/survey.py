import collections
from typing import Any, Dict, List, Optional

import h5py
import numpy as np
import pandas as pd
import popsynth
from IPython.display import display
from natsort import natsorted

from cosmogrb.grb.grb_detector import GRBDetector
from cosmogrb.io.detector_save import DetectorSave
from cosmogrb.io.grb_save import GRBSave
from cosmogrb.utils.file_utils import file_existing_and_readable
from cosmogrb.utils.logging import setup_logger

logger = setup_logger(__name__)


class Observation(object):
    def __init__(
        self,
        grb_save_file: str,
        grb_detector_file: Optional[str] = None,
        population=None,
        idx=None,
    ):
        """
        A small container class to access observations

        :param grb_save_file:
        :param grb_detector_file:
        :param population:
        :param idx:
        :returns:
        :rtype:

        """

        self._grb = grb_save_file

        self._detector = grb_detector_file

    @property
    def grb(self):
        return GRBSave.from_file(self._grb)

    @property
    def detector_info(self):
        if self._detector is None:

            return None

        else:

            return DetectorSave.from_file(self._detector)


class Survey(collections.OrderedDict):
    def __init__(
        self, grb_save_files: List[str], population_file: str, grb_detector_files=None
    ) -> None:
        """
        A container for a survey of observed GRBs. Holds file locations
        for all the GRBs created in the Universe. It also allows you to process
        the observations with a GRBDetector class.

        :param grb_save_files: the file locations for the survey
        :param population_file: the population file used to generate the population
        :param grb_detector_files: the generated detector files
        :returns:
        :rtype:
        """

        super(Survey, self).__init__()

        self._n_grbs: int = len(grb_save_files)
        self._grb_save_files: List[str] = grb_save_files
        self._names: List[str] = []

        # build  a population from the file

        if file_existing_and_readable(population_file):

            self._population_file: Optional[str] = population_file
            self._population: Optional[
                popsynth.Population
            ] = popsynth.Population.from_file(self._population_file)

        else:

            self._population_file = None
            self._population = None

            logger.warnings(f"{population_file} does not exist. Perhaps you moved it?")

        for f in self._grb_save_files:

            with h5py.File(f, "r") as f:

                self._names.append(f.attrs["grb_name"])

        # we start off with not being processed unless
        # we find that there are some detector files

        self._is_processed: bool = False

        self._detected = np.zeros(len(grb_save_files), dtype=bool)

        self._grb_detector_files = None

        # lets see if we have detector files

        if grb_detector_files is not None:

            self._is_processed = True

            self._grb_detector_files = natsorted(grb_detector_files)

            assert len(grb_detector_files) == len(grb_save_files)

            # fill in the detected ones

            for i, f in enumerate(self._grb_detector_files):

                tmp = DetectorSave.from_file(f)
                if tmp.is_detected:

                    self._detected[i] = True

            # now fill the dict

            for name, grb_save_file, grb_detector_file in zip(
                self._names, self._grb_save_files, self._grb_detector_files
            ):

                self[name] = Observation(
                    grb_save_file=grb_save_file, grb_detector_file=grb_detector_file
                )

        else:

            for name, grb_save_file in zip(self._names, self._grb_save_files):

                self[name] = Observation(
                    grb_save_file=grb_save_file, grb_detector_file=None
                )

    @property
    def population(self) -> Optional[popsynth.Population]:
        return self._population

    @property
    def n_detected(self) -> int:
        return self._detected.sum()

    @property
    def n_grbs(self) -> int:
        return self._n_grbs

    def info(self) -> None:
        """
        display the information about the survey

        :returns:
        :rtype:

        """

        generic_info = collections.OrderedDict()

        generic_info["n_grbs"] = self._n_grbs
        generic_info["is_processed"] = self._is_processed
        if self._is_processed:

            generic_info["n_detected"] = self.n_detected

        df = pd.Series(data=generic_info, index=generic_info.keys())

        display(df.to_frame())

    def process(
        self, detector_type, client=None, serial: bool = False, **kwargs
    ) -> None:
        """
        Process the triggers or detectors in the survey. This runs the provided
        GRBDetector type on each of the GRBs and prepares the information

        :param detector_type: a **class** of GRBDetector type
        :param client: the dask client
        :param serial: True/False for if the survey is processed without dask
        :returns:
        :rtype:

        """

        assert issubclass(detector_type, GRBDetector), "Not a valid GRB detector"

        if not serial:

            assert (
                client is not None
            ), "One must provide a client to process in parallel"

            args = []
            for grb_file in self._grb_save_files:

                args.append([grb_file, detector_type, kwargs])

            futures = client.map(_submit, args)
            client.gather(futures)

        else:

            for grb_file in self._grb_save_files:

                _submit([grb_file, detector_type, kwargs])

        # the survey has now had its triggers run
        # so lets flip its status and make sure that when
        # when we save it, we record the new status

        self._is_processed = True

        self._grb_detector_files = []

        for file_name in self._grb_save_files:

            file_name_head = ".".join(file_name.split(".")[:-1])

            out_file_name = f"{file_name_head}_detection_info.h5"

            self._grb_detector_files.append(out_file_name)

            # now update the survey
            # fill in the detected ones

            for i, f in enumerate(self._grb_detector_files):

                tmp = DetectorSave.from_file(f)
                if tmp.is_detected:

                    self._detected[i] = True

            # now fill the dict

        for name, grb_save_file, grb_detector_file in zip(
            self._names, self._grb_save_files, self._grb_detector_files
        ):

            self[name] = Observation(
                grb_save_file=grb_save_file, grb_detector_file=grb_detector_file
            )

    @property
    def is_processed(self):

        return self._is_processed

    def write(self, file_name):
        """
        write the info to a file.
        if the universe has been processed, this information is also written

        :param file_name:
        :returns:
        :rtype:

        """

        dt = h5py.string_dtype(encoding="utf-8")

        with h5py.File(file_name, "w") as f:

            f.attrs["n_grbs"] = self._n_grbs
            f.attrs["is_processed"] = self._is_processed
            f.attrs["population_file"] = self._population_file

            grbs = f.create_dataset(
                "grb_saves", data=np.array(self._grb_save_files, dtype=dt)
            )

            if self._is_processed:

                grb_dets = f.create_dataset(
                    "grb_dets", data=np.array(self._grb_detector_files, dtype=dt)
                )

    @classmethod
    def from_file(cls, file_name):
        """
        create a universe

        :param cls:
        :param file_name:
        :returns:
        :rtype:

        """

        with h5py.File(file_name, "r") as f:

            n_grbs = f.attrs["n_grbs"]
            is_processed = f.attrs["is_processed"]
            population_file = f.attrs["population_file"]

            grb_files = f["grb_saves"][()].astype(str)

            grb_dets = None

            if is_processed:

                grb_dets = f["grb_dets"][()].astype(str)

        return cls(grb_files, population_file, grb_dets)


def _submit(args):

    grb_file, detector_type, kwargs = args

    processor = detector_type(grb_save_file_name=grb_file, **kwargs)
    processor.process()
    processor.save()
