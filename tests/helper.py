import os
import shutil
import zipfile

global samples_directory
global input_samples_directory
global expected_samples_directory

samples_directory = "./samples"
input_samples_directory = f"{samples_directory}/input"
expected_samples_directory = f"{samples_directory}/expected"


def create_samples(samples_directory):
    if os.path.exists(samples_directory):
        shutil.rmtree(samples_directory)

    with zipfile.ZipFile("samples.zip", "r") as zip_ref:
        zip_ref.extractall(".")
