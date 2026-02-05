"""Tests for pagination constants and clamp_limit helper."""

from app.core.constants import MAX_LIMIT, clamp_limit


def test_max_limit_value():
    assert MAX_LIMIT == 200


def test_clamp_limit_normal():
    assert clamp_limit(50) == 50
    assert clamp_limit(1) == 1
    assert clamp_limit(200) == 200


def test_clamp_limit_exceeds_max():
    assert clamp_limit(201) == 200
    assert clamp_limit(1000) == 200
    assert clamp_limit(999999) == 200


def test_clamp_limit_zero_or_negative():
    assert clamp_limit(0) == 50  # default
    assert clamp_limit(-1) == 50
    assert clamp_limit(-100) == 50


def test_clamp_limit_custom_default():
    assert clamp_limit(0, default=25) == 25
    assert clamp_limit(-1, default=10) == 10
