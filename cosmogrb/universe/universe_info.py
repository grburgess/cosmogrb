import popsynth
import h5py
import numpy as np
import pandas as pd
from IPython.display import display
import collections

from cosmogrb.io.grb_save import GRBSave
from cosmogrb.io.detector_save import DetectorSave
from cosmogrb.grb.grb_detector import GRBDetector


class UniverseInfo(object):
    """Documentation for UniverseInfo

    """

    def __init__(self, grb_save_files, population_file, grb_detector_files=None):

        self._n_grbs = len(grb_save_files)
        self._grb_save_files = grb_save_files
        self._population_file = population_file
        self._population = popsynth.Population.from_file(self._population_file)
        self._grb_detector_files = grb_detector_files

        self._is_processed = False

        self._detected = np.zeros(len(grb_save_files), dtype=bool)

        if grb_detector_files is not None:

            self._is_processed = True

            assert len(grb_detector_files) == len(grb_save_files)

            for i, f in enumerate(grb_detector_files):

                tmp = DetectorSave.from_file(f)
                if tmp.is_detected:

                    self._detected[i] = True

    @property
    def population(self):
        return self._population

    @property
    def n_detected(self):
        return self._detected.sum()

    @property
    def n_grbs(self):
        return self._n_grbs

    def info(self):

        generic_info = collections.OrderedDict()

        generic_info["n_grbs"] = self._n_grbs
        generic_info["is_processed"] = self._is_processed
        if self._is_processed:

            generic_info["n_detected"] = self.n_detected

    def process(self, detector_type, client=None, serial=False, **kwargs):

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

                _submit([grb_file, GRBDetector, kwargs])

        

        
    @property
    def is_processed(self):

        return self._is_processed

    def write(self, file_name):

        dt = h5py.string_dtype(encoding='utf-8')
        
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
