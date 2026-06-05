from main import mask, is_sensitive ,read_and_parse , write_env
import pytest

def test_mask_short():
    assert mask("abc") == "***"

def test_mask_long():
   assert  mask("abcde12345") == "abcd******"

def test_is_sensitive_true():
    assert is_sensitive("api")== True 


import pytest
from main import read_and_parse, is_sensitive


def test_is_sensitive_false():
    assert is_sensitive("DATABASE_URL") is False


@pytest.fixture
def env_data():
    data, comments = read_and_parse("sample.env")
    return data


def test_normal_value(env_data):
    assert env_data["DATABASE_URL"] == "postgres://localhost/db"


def test_empty_value(env_data):
    assert "missing value" in env_data["EMPTY"]


def test_double_equal(env_data):
    assert env_data["TOKEN"] == "abc=123=xyz"

def test_inline_comment(env_data):
    assert env_data["API_KEY"] == "secret123"


def test_hash_inside_quotes(env_data):
    assert env_data["NAME"] == "John # Smith"
    

def test_write_env(tmp_path):
    file = tmp_path / "test_output.env"
    data = {"PORT": 5432, "DEBUG": False}
    result = write_env(str(file), data)
    assert result == True


def test_data_inside(tmp_path):
    file = tmp_path / "test_output.env"
    data = {"PORT": 5432, "DEBUG": False}
    result = write_env(str(file), data)
    with open (tmp_path / "test_output.env" , "r") as f :
        test = f.read()
    assert "PORT=5432" in test

def test_write_env_no_overwrite(tmp_path):
    file = tmp_path / "test.env"

    write_env(str(file), {"A": 1})

    result = write_env(str(file), {"B": 2})

    assert result is None