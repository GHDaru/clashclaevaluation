"""Tests for Value Objects."""

import pytest

from domain.model.value_objects import (
    AttackCount,
    BlackCard,
    CardSummary,
    ClanTag,
    PlayerTag,
    RedCard,
    WarDay,
    YellowCard,
)


class TestPlayerTag:
    def test_valid_tag(self):
        tag = PlayerTag("#ABC123")
        assert str(tag) == "#ABC123"

    def test_tag_must_start_with_hash(self):
        with pytest.raises(ValueError):
            PlayerTag("ABC123")


class TestClanTag:
    def test_valid_tag(self):
        tag = ClanTag("#XYZ789")
        assert str(tag) == "#XYZ789"

    def test_tag_must_start_with_hash(self):
        with pytest.raises(ValueError):
            ClanTag("XYZ789")


class TestAttackCount:
    def test_valid(self):
        a = AttackCount(3)
        assert a.value == 3
        assert a.missing == 1

    def test_max(self):
        a = AttackCount(4)
        assert a.missing == 0

    def test_min(self):
        a = AttackCount(0)
        assert a.missing == 4

    def test_out_of_range(self):
        with pytest.raises(ValueError):
            AttackCount(5)
        with pytest.raises(ValueError):
            AttackCount(-1)


class TestCards:
    def test_yellow_card(self):
        c = YellowCard(3)
        assert c.count == 3

    def test_red_card(self):
        c = RedCard(2)
        assert c.count == 2

    def test_black_card(self):
        c = BlackCard(1)
        assert c.count == 1

    def test_negative_card(self):
        with pytest.raises(ValueError):
            YellowCard(-1)


class TestCardSummary:
    def test_clean(self):
        s = CardSummary(yellow=0, red=0, black=0)
        assert s.is_clean
        assert not s.is_critical

    def test_critical(self):
        s = CardSummary(yellow=0, red=0, black=1)
        assert not s.is_clean
        assert s.is_critical


class TestWarDay:
    def test_from_index(self):
        assert WarDay.from_index(0).label == "Quinta"
        assert WarDay.from_index(1).label == "Sexta"
        assert WarDay.from_index(2).label == "Sábado"
        assert WarDay.from_index(3).label == "Domingo"

    def test_invalid_index(self):
        with pytest.raises(ValueError):
            WarDay.from_index(4)
        with pytest.raises(ValueError):
            WarDay.from_index(-1)

    def test_all_days(self):
        days = WarDay.all_days()
        assert len(days) == 4
        assert [d.label for d in days] == ["Quinta", "Sexta", "Sábado", "Domingo"]
