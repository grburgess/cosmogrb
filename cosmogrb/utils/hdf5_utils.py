import h5py
import numpy as np


def recursively_save_dict_contents_to_group(h5file, path, dic):
    """

    save a dictionary to an HDf5 file

    :param h5file:
    :param path:
    :param dic:
    :returns:
    :rtype:

    """

    for key, item in dic.items():
        if isinstance(
            item, (np.ndarray, np.int64, np.float64, str, bytes, float, int)
        ):
            h5file[path + "/" + key] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(
                h5file, path + "/" + key + "/", item
            )
        else:
            raise ValueError("Cannot save %s type" % type(item))


def recursively_load_dict_contents_from_group(h5file, path):
    """

    read a dictionary from and HDF5 file

    :param h5file:
    :param path:
    :returns:
    :rtype:

    """

    ans = {}

    for key, item in h5file[path].items():

        if isinstance(item, h5py._hl.dataset.Dataset):
            ans[key] = item[()]
        elif isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load_dict_contents_from_group(
                h5file, path + "/" + key + "/"
            )
    return ans
