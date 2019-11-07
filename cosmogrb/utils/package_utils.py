import pkg_resources
import os
from shutil import copyfile


def get_path_of_data_file(data_file):
    file_path = pkg_resources.resource_filename("cosmogrb", "data/%s" % data_file)

    return file_path


def get_path_of_data_dir():
    file_path = pkg_resources.resource_filename("cosmogrb", "data")

    return file_path
