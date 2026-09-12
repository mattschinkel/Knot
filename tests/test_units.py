from __future__ import annotations

from golem.units import Dimension, DIMENSIONLESS, m, s, kg


def test_dimensionless():
    assert DIMENSIONLESS.is_dimensionless
    assert DIMENSIONLESS.to_string() == "1"
    assert DIMENSIONLESS.items == ()

def test_mul_adds_exponents():
    area = m.mul(m)
    assert area == Dimension.from_map({"m": 2})
    assert area.to_string() == "m^2"

def test_mul_drops_zeros():
    # m * m^-1 -> dimensionless
    inv = Dimension.from_map({"m": -1})
    assert m.mul(inv) == DIMENSIONLESS

def test_div_subtracts_exponents():
    velocity = m.div(s)
    assert velocity == Dimension.from_map({"m": 1, "s": -1})
    assert velocity.to_string() == "m·s^-1"

def test_compatible_requires_equal_maps():
    assert m.compatible(m)
    assert not m.compatible(s)
    assert not m.compatible(m.mul(m))

def test_commutative_mul():
    assert m.mul(s) == s.mul(m)

def test_to_string_single_power():
    assert m.to_string() == "m"

def test_canonical_form_sorted():
    # order of construction must not affect equality
    a = Dimension.from_map({"s": 1, "m": 1})
    b = Dimension.from_map({"m": 1, "s": 1})
    assert a == b
    assert hash(a) == hash(b)

def test_user_defined_dimension():
    money = Dimension.from_map({"money": 1})
    assert money.compatible(money)
    assert not money.compatible(m)
    # money * money -> money^2
    assert money.mul(money).to_string() == "money^2"

def test_pow_positive():
    # pow(2) of meters == m^2
    assert m.pow(2) == Dimension.from_map({"m": 2})


def test_pow_zero():
    # pow(0) == dimensionless
    assert m.pow(0) == DIMENSIONLESS


def test_pow_positive_three():
    # pow(3) of m·s^-1 == m^3·s^-3
    velocity = m.div(s)
    assert velocity.pow(3) == Dimension.from_map({"m": 3, "s": -3})


def test_pow_negative_one():
    # pow(-1) of meters == m^-1 (inverts)
    assert m.pow(-1) == Dimension.from_map({"m": -1})


def test_pow_negative_two():
    # pow(-2) of meters == m^-2
    assert m.pow(-2) == Dimension.from_map({"m": -2})
