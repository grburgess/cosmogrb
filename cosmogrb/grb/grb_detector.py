import h5py
import abc
from cosmogrb import GRBSave
from cosmogrb.utils.hdf5_utils import recursively_save_dict_contents_to_group


class GRBDetector(object, metaclass=abc.ABCMeta):
    def __init__(self, grb_save_file_name):
        """

        A generic class for assessing if a GRB was detected or not

        :param grb_save_file_name: 
        :returns: 
        :rtype: 

        """

        self._grb_save = GRBSave.from_file(grb_save_file_name)
        self._is_detected = False
        self._name = self._grb_save.name

        file_name_head = ".".join(grb_save_file_name.split(".")[:-1])

        self._out_file_name = f"{file_name_head}_detection_info.h5"

        self._extra_info = {}

    @property
    def is_detected(self):
        return self._is_detected

    @abc.abstractmethod
    def process(self):

        # the method to process the detection
        
        pass
    
    def save(self):

        with h5py.File(self._out_file_name, "w") as f:

            f.attrs["is_detected"] = self._is_detected
            f.attrs["name"] = self._name

            # store any extra info if there is
            # some.

            if self._extra_info:

                recursively_save_dict_contents_to_group(
                    f, "extra_info", self._extra_info
                )
