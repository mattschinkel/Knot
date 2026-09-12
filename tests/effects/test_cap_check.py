"""check_capabilities — needed ⊆ granted (Phase 3 T4)."""

from __future__ import annotations

from golem.effects import Capability, CapabilitySet, check_capabilities


def test_check_ok():
    needed = CapabilitySet([Capability.FS_READ])
    granted = CapabilitySet([Capability.FS_READ, Capability.NET_REQUEST])
    assert check_capabilities(needed, granted) is True


def test_check_missing():
    needed = CapabilitySet([Capability.NET_REQUEST])
    granted = CapabilitySet([Capability.FS_READ])
    assert check_capabilities(needed, granted) is False


def test_check_empty_needed():
    assert check_capabilities(CapabilitySet(), CapabilitySet([Capability.AI])) is True
