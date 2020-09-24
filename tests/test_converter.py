""" Pytest unit tests for the Data class of converter.py"""

import os
import sys

import numpy as np
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
import converter


# path to mesc testfile
loadpath = os.path.join(os.path.dirname(__file__), "../tests/testfile.mesc")


def test_load_h5keys():
    """Can the h5keys be loaded from the testfile?"""
    data = converter.Data(loadpath=loadpath)
    data.load_h5keys()
    assert True


@pytest.fixture
def fixture_load_h5keys():
    """Load the testfile"""
    data = converter.Data(loadpath=loadpath)
    data.load_h5keys()
    return data


def test_h5keys_are_in_list(fixture_load_h5keys):
    """Are the loaded h5keys stored in a list?"""
    data = fixture_load_h5keys
    assert isinstance(data.h5keys, list)


def test_h5keys_are_strings(fixture_load_h5keys):
    """Are the loaded h5keys strings?"""
    data = fixture_load_h5keys
    for h5key in data.h5keys:
        assert isinstance(h5key, str)


def test_select_h5key(fixture_load_h5keys):
    """Is the first h5key of the testfile loaded correctly?"""
    data = fixture_load_h5keys
    data.h5key = data.h5keys[0]
    assert data.h5key == "MSession_0/MUnit_3/Channel_0"


@pytest.fixture
def fixture_select_h5key(fixture_load_h5keys):
    """Select the first h5key of the loaded testfile"""
    data = fixture_load_h5keys
    data.h5key = data.h5keys[0]
    return data


def test_load_dataset(fixture_select_h5key):
    """Can the dataset be loaded?"""
    data = fixture_select_h5key
    data.load_dataset()
    assert True


@pytest.fixture
def fixture_load_dataset(fixture_select_h5key):
    """Load the dataset"""
    data = fixture_select_h5key
    data.load_dataset()
    return data


def test_dataset_is_array(fixture_load_dataset):
    """Is the dataset a numpy ndarray?"""
    data = fixture_load_dataset
    assert isinstance(data.dataset, np.ndarray)


def test_dataset_correct_value(fixture_load_dataset):
    """Does the first pixel of the first frame of the dataset have the correct value?"""
    data = fixture_load_dataset
    assert data.dataset[0, 0, 0] == 64512


def test_get_linear_offset(fixture_load_dataset):
    """Can the linear offset be extracted?"""
    data = fixture_load_dataset
    data.get_linear_offset()
    assert True


def test_linear_offset_correct_value(fixture_load_dataset):
    """Does the linear offset in the testfile have the correct value?"""
    data = fixture_load_dataset
    data.get_linear_offset()
    assert data.linear_offset == 64621.0


def test_get_linear_scale(fixture_load_dataset):
    """Can the linear scaling factor be extracted?"""
    data = fixture_load_dataset
    data.get_linear_scale()
    assert True


def test_linear_scale_correct_value(fixture_load_dataset):
    """Does the linear scaling factor in the testfile have the correct value?"""
    data = fixture_load_dataset
    data.get_linear_scale()
    assert data.linear_scale == -1.0


def test_linear_correction(fixture_load_dataset):
    """Can the linear correction be applied?"""
    data = fixture_load_dataset
    data.linear_correction()
    assert True


@pytest.fixture
def fixture_linear_correction(fixture_load_dataset):
    """Apply the linear correction"""
    data = fixture_load_dataset
    data.linear_correction()
    return data


def test_linear_correction_correct_value(fixture_linear_correction):
    """Does the linear correction yield the correct result?"""
    data = fixture_linear_correction
    assert data.dataset_corr[0, 0, 0] == 109.0


def test_save_dataset(fixture_load_dataset):
    """Can the dataset be saved?"""
    data = fixture_load_dataset
    data.savepath = "tests/unittest-" + data.h5key.replace("/", "-") + ".h5"
    data.save_dataset(data.dataset)
    assert True


def test_save_corrected_dataset(fixture_linear_correction):
    """Can the corrected dataset be saved?"""
    data = fixture_linear_correction
    data.savepath = "tests/unittest-" + data.h5key.replace("/", "-") + "-corr.h5"
    data.save_dataset(data.dataset_corr)
    assert True
