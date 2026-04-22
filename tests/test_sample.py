# 함수 이름이 반드시 'test_'로 시작해야 합니다!
import pytest

def test_func1():
    assert 1 == 1

def test_func2():
    assert 2 == 2

def test_func3(app_data):
    assert app_data == 3