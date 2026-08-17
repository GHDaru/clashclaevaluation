"""Tests for derive_per_day_attacks — per-day attack reconstruction from snapshots."""

from datetime import date

from domain.model.aggregates import WarSnapshot, derive_per_day_attacks
from domain.model.value_objects import PlayerTag


def _snap(war_id, tag, snap_date, decks_used, decks_today, fame):
    return WarSnapshot(
        war_id=war_id,
        player_tag=tag,
        player_name="Player",
        snapshot_date=snap_date,
        decks_used_at_snapshot=decks_used,
        decks_used_today_at_snapshot=decks_today,
        fame_at_snapshot=fame,
    )


class TestDerivePerDayAttacks:
    WAR_START = date(2026, 8, 13)  # Thursday
    TAG = PlayerTag("#ABC")

    def test_full_war_4_days(self):
        """All 4 days captured — uses decksUsedToday as authoritative."""
        snaps = [
            _snap(1, self.TAG, date(2026, 8, 13), 4, 4, 1000),
            _snap(1, self.TAG, date(2026, 8, 14), 7, 3, 2000),
            _snap(1, self.TAG, date(2026, 8, 15), 11, 4, 3000),
            _snap(1, self.TAG, date(2026, 8, 16), 16, 5, 4000),
        ]
        result = derive_per_day_attacks(snaps, self.WAR_START)
        assert [a.value for a in result] == [4, 3, 4, 4]

    def test_missing_day_defaults_to_zero(self):
        """A day with no snapshot gets 0 attacks."""
        snaps = [
            _snap(1, self.TAG, date(2026, 8, 13), 4, 4, 1000),
            _snap(1, self.TAG, date(2026, 8, 15), 11, 4, 3000),
        ]
        result = derive_per_day_attacks(snaps, self.WAR_START)
        assert [a.value for a in result] == [4, 0, 4, 0]

    def test_player_joins_mid_war(self):
        """First snapshot on day 2 — prior is 0, full cumulative returned."""
        snaps = [
            _snap(1, self.TAG, date(2026, 8, 14), 3, 3, 500),
            _snap(1, self.TAG, date(2026, 8, 15), 7, 4, 1500),
        ]
        result = derive_per_day_attacks(snaps, self.WAR_START)
        assert [a.value for a in result] == [0, 3, 4, 0]

    def test_no_snapshots(self):
        """Empty snapshot list — all zeros."""
        result = derive_per_day_attacks([], self.WAR_START)
        assert [a.value for a in result] == [0, 0, 0, 0]

    def test_capped_at_four(self):
        """Attacks capped at 4 (physical max per war day)."""
        snaps = [
            _snap(1, self.TAG, date(2026, 8, 13), 5, 5, 1000),
        ]
        result = derive_per_day_attacks(snaps, self.WAR_START)
        assert result[0].value == 4

    def test_uses_diff_when_today_is_zero(self):
        """Falls back to cumulative diff when decksUsedToday is 0 but diff is positive."""
        snaps = [
            _snap(1, self.TAG, date(2026, 8, 13), 4, 4, 1000),
            _snap(1, self.TAG, date(2026, 8, 14), 7, 0, 2000),  # today=0 but diff=3
        ]
        result = derive_per_day_attacks(snaps, self.WAR_START)
        assert result[1].value == 3

    def test_returns_exactly_four_attack_counts(self):
        """Always returns exactly 4 values regardless of snapshot count."""
        snaps = [_snap(1, self.TAG, date(2026, 8, 13), 4, 4, 1000)]
        result = derive_per_day_attacks(snaps, self.WAR_START)
        assert len(result) == 4
