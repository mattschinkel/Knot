"""Capability and CapabilitySet (Phase 3 T2)."""

from __future__ import annotations

from knot.effects import Capability, CapabilitySet


def test_capability_values():
    assert Capability.NET_REQUEST.value == "net.request"
    assert Capability.FS_READ.value == "fs.read"


def test_capabilityset_membership():
    cs = CapabilitySet([Capability.FS_READ, Capability.NET_REQUEST])
    assert Capability.FS_READ in cs
    assert Capability.AI not in cs
    assert len(cs) == 2


def test_capabilityset_union():
    a = CapabilitySet([Capability.FS_READ])
    b = CapabilitySet([Capability.NET_REQUEST])
    u = a.union(b)
    assert Capability.FS_READ in u and Capability.NET_REQUEST in u


def test_capabilityset_issubset():
    small = CapabilitySet([Capability.FS_READ])
    big = CapabilitySet([Capability.FS_READ, Capability.NET_REQUEST])
    assert small.issubset(big)
    assert not big.issubset(small)
