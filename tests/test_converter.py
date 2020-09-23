import os
import sys

import numpy as np
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
import converter


# path to mesc testfile
loadpath = os.path.join(os.path.dirname(__file__), "../tests/testfile.mesc")


def test_load_h5keys():
    data = converter.Data(loadpath=loadpath)
    data.load_h5keys()
    assert True


@pytest.fixture
def fixture_load_h5keys():
    data = converter.Data(loadpath=loadpath)
    data.load_h5keys()
    return data


def test_h5keys_are_in_list(fixture_load_h5keys):
    data = fixture_load_h5keys
    assert isinstance(data.h5keys, list)


def test_h5keys_are_strings(fixture_load_h5keys):
    data = fixture_load_h5keys
    for h5key in data.h5keys:
        assert isinstance(h5key, str)


def test_select_h5key(fixture_load_h5keys):
    data = fixture_load_h5keys
    data.h5key = data.h5keys[0]
    assert data.h5key == "MSession_0/MUnit_3/Channel_0"


@pytest.fixture
def fixture_select_h5key(fixture_load_h5keys):
    data = fixture_load_h5keys
    data.h5key = data.h5keys[2]
    return data


# load dataset
def test_load_dataset(fixture_select_h5key):
    data = fixture_select_h5key
    data.load_dataset()
    assert True


@pytest.fixture
def fixture_load_dataset(fixture_select_h5key):
    data = fixture_select_h5key
    data.load_dataset()
    return data


def test_dataset_is_array(fixture_load_dataset):
    data = fixture_load_dataset
    assert isinstance(data.dataset, np.ndarray)


def test_dataset_correct_value(fixture_load_dataset):
    data = fixture_load_dataset
    assert data.dataset[0, 0, 0] == np.uint16(64512)


# get and remove offset and linear conversion
def test_get_linear_offset(fixture_load_dataset):
    data = fixture_load_dataset
    data.get_linear_offset()
    assert True


def test_linear_offset_correct_value(fixture_load_dataset):
    data = fixture_load_dataset
    data.get_linear_offset()
    assert data.linear_offset == np.float64(-786.0)


def test_get_linear_scale(fixture_load_dataset):
    data = fixture_load_dataset
    data.get_linear_scale()
    assert True


def test_linear_scale_correct_value(fixture_load_dataset):
    data = fixture_load_dataset
    data.get_linear_scale()
    assert data.linear_scale == np.float64(1.0)


def test_linear_conversion(fixture_load_dataset):
    data = fixture_load_dataset
    data.linear_conversion()
    assert True


@pytest.fixture
def fixture_linear_conversion(fixture_load_dataset):
    data = fixture_load_dataset
    data.linear_conversion()
    return data


def test_linear_conversion_correct_value(fixture_linear_conversion):
    data = fixture_linear_conversion
    assert data.dataset[0, 0, 0] == np.int16(110)


# save to h5
def test_save_dataset(fixture_linear_conversion):
    data = fixture_linear_conversion
    data.savepath = "tests/test-" + data.h5key.replace("/", "-") + ".h5"
    data.save_dataset()
    assert True
