#!/usr/bin/env python3
"""
Test basic functionality
"""
import pytest

def test_simple_assertion():
    """Test basic assertion"""
    assert 1 + 1 == 2

def test_string_operations():
    """Test string operations"""
    test_string = "hello world"
    assert test_string.upper() == "HELLO WORLD"
    assert len(test_string) == 11

def test_list_operations():
    """Test list operations"""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert sum(test_list) == 15

def test_dictionary_operations():
    """Test dictionary operations"""
    test_dict = {"a": 1, "b": 2, "c": 3}
    assert len(test_dict) == 3
    assert test_dict["a"] == 1

def test_boolean_operations():
    """Test boolean operations"""
    assert True is True
    assert False is False
    assert not False