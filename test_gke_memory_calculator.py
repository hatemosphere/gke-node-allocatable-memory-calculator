import pytest
from gke_memory_calculator import (
    calculate_reserved_memory,
    gb_to_gib,
    MEMORY_TIERS_GKE,
    MEMORY_TIERS_STREAMING,
    EVICTION_MEMORY_GIB,
)


class TestGbToGib:
    def test_1_gb(self):
        assert gb_to_gib(1) == pytest.approx(1000**3 / 1024**3)

    def test_round_trip(self):
        # 1 GiB in GB is 1.073741824
        assert gb_to_gib(1.073741824) == pytest.approx(1.0)


class TestGkeMemoryReservation:
    """Validate standard GKE memory reservations against official docs:
    - 255 MiB for < 1 GiB
    - 25% of first 4 GiB
    - 20% of next 4 GiB (4-8)
    - 10% of next 8 GiB (8-16)
    - 6% of next 112 GiB (16-128)
    - 2% above 128 GiB
    """

    def _reserved(self, total_gib):
        return calculate_reserved_memory(total_gib, MEMORY_TIERS_GKE)

    def test_below_1gib(self):
        # 0.5 GiB: 255/1024 * 0.5
        expected = (255 / 1024) * 0.5
        assert self._reserved(0.5) == pytest.approx(expected)

    def test_at_1gib_boundary(self):
        # Exactly 1 GiB: 255/1024 * 1
        expected = 255 / 1024
        assert self._reserved(1.0) == pytest.approx(expected)

    def test_in_4gib_tier(self):
        # 2 GiB: 255/1024 * 1 + 0.25 * 1
        expected = (255 / 1024) * 1 + 0.25 * 1
        assert self._reserved(2.0) == pytest.approx(expected)

    def test_at_4gib_boundary(self):
        # 4 GiB: 255/1024 * 1 + 0.25 * 3
        expected = (255 / 1024) * 1 + 0.25 * 3
        assert self._reserved(4.0) == pytest.approx(expected)

    def test_in_8gib_tier(self):
        # 6 GiB: first 4 GiB reserved + 0.20 * 2
        first_4 = (255 / 1024) * 1 + 0.25 * 3
        expected = first_4 + 0.20 * 2
        assert self._reserved(6.0) == pytest.approx(expected)

    def test_at_8gib_boundary(self):
        # 8 GiB: first 4 GiB reserved + 0.20 * 4
        first_4 = (255 / 1024) * 1 + 0.25 * 3
        expected = first_4 + 0.20 * 4
        assert self._reserved(8.0) == pytest.approx(expected)

    def test_at_16gib_boundary(self):
        # 16 GiB: first 8 GiB reserved + 0.10 * 8
        first_8 = (255 / 1024) * 1 + 0.25 * 3 + 0.20 * 4
        expected = first_8 + 0.10 * 8
        assert self._reserved(16.0) == pytest.approx(expected)

    def test_in_128gib_tier(self):
        # 64 GiB: first 16 GiB reserved + 0.06 * 48
        first_16 = (255 / 1024) * 1 + 0.25 * 3 + 0.20 * 4 + 0.10 * 8
        expected = first_16 + 0.06 * 48
        assert self._reserved(64.0) == pytest.approx(expected)

    def test_at_128gib_boundary(self):
        # 128 GiB: first 16 GiB reserved + 0.06 * 112
        first_16 = (255 / 1024) * 1 + 0.25 * 3 + 0.20 * 4 + 0.10 * 8
        expected = first_16 + 0.06 * 112
        assert self._reserved(128.0) == pytest.approx(expected)

    def test_above_128gib(self):
        # 256 GiB: first 128 GiB reserved + 0.02 * 128
        first_128 = (255 / 1024) * 1 + 0.25 * 3 + 0.20 * 4 + 0.10 * 8 + 0.06 * 112
        expected = first_128 + 0.02 * 128
        assert self._reserved(256.0) == pytest.approx(expected)


class TestStreamingMemoryReservation:
    """Validate image streaming reservations against official docs:
    - 0 for < 1 GiB
    - 1% of first 4 GiB
    - 0.8% of next 4 GiB (4-8)
    - 0.4% of next 8 GiB (8-16)
    - 0.24% of next 112 GiB (16-128)
    - 0.08% above 128 GiB
    """

    def _reserved(self, total_gib):
        return calculate_reserved_memory(total_gib, MEMORY_TIERS_STREAMING)

    def test_below_1gib(self):
        assert self._reserved(0.5) == pytest.approx(0.0)

    def test_in_4gib_tier(self):
        # 2 GiB: 0 * 1 + 0.01 * 1
        expected = 0.01 * 1
        assert self._reserved(2.0) == pytest.approx(expected)

    def test_at_4gib_boundary(self):
        # 4 GiB: 0 * 1 + 0.01 * 3
        expected = 0.01 * 3
        assert self._reserved(4.0) == pytest.approx(expected)

    def test_at_8gib_boundary(self):
        # 8 GiB: first 4 + 0.008 * 4
        first_4 = 0.01 * 3
        expected = first_4 + 0.008 * 4
        assert self._reserved(8.0) == pytest.approx(expected)

    def test_at_16gib_boundary(self):
        # 16 GiB: first 8 + 0.004 * 8
        first_8 = 0.01 * 3 + 0.008 * 4
        expected = first_8 + 0.004 * 8
        assert self._reserved(16.0) == pytest.approx(expected)

    def test_at_128gib_boundary(self):
        # 128 GiB: first 16 + 0.0024 * 112
        first_16 = 0.01 * 3 + 0.008 * 4 + 0.004 * 8
        expected = first_16 + 0.0024 * 112
        assert self._reserved(128.0) == pytest.approx(expected)

    def test_above_128gib(self):
        # 256 GiB: first 128 + 0.0008 * 128
        first_128 = 0.01 * 3 + 0.008 * 4 + 0.004 * 8 + 0.0024 * 112
        expected = first_128 + 0.0008 * 128
        assert self._reserved(256.0) == pytest.approx(expected)


class TestEvictionThreshold:
    def test_eviction_is_100mib(self):
        assert EVICTION_MEMORY_GIB == pytest.approx(100 / 1024)
