"""Tests for CardConversionService — the core conversion rules."""

import pytest

from domain.service.card_conversion import CardConversionService


class TestCardConversionService:
    def test_no_cards_returns_clean(self):
        svc = CardConversionService(yellow_to_red=4, red_to_black=4)
        result = svc.convert(total_yellow=0, total_red=0)

        assert result.yellow == 0
        assert result.red == 0
        assert result.black == 0
        assert result.is_clean

    def test_four_yellows_become_one_red(self):
        svc = CardConversionService(yellow_to_red=4, red_to_black=4)
        result = svc.convert(total_yellow=4)

        assert result.yellow == 0
        assert result.red == 1
        assert result.black == 0

    def test_sixteen_yellows_become_one_black(self):
        """0/4 attacks all 4 days = 16 yellows → 4 reds → 1 black."""
        svc = CardConversionService(yellow_to_red=4, red_to_black=4)
        result = svc.convert(total_yellow=16)

        assert result.yellow == 0
        assert result.red == 0
        assert result.black == 1
        assert result.is_critical

    def test_eight_yellows_become_two_reds(self):
        svc = CardConversionService(yellow_to_red=4, red_to_black=4)
        result = svc.convert(total_yellow=8)

        assert result.yellow == 0
        assert result.red == 2
        assert result.black == 0

    def test_three_yellows_remain_yellow(self):
        svc = CardConversionService(yellow_to_red=4, red_to_black=4)
        result = svc.convert(total_yellow=3)

        assert result.yellow == 3
        assert result.red == 0
        assert result.black == 0

    def test_yellows_plus_points_red(self):
        """12 yellows + 1 red from points = 4 reds → 1 black."""
        svc = CardConversionService(yellow_to_red=4, red_to_black=4)
        result = svc.convert(total_yellow=12, total_red=1)

        assert result.yellow == 0
        assert result.red == 0
        assert result.black == 1

    def test_custom_thresholds(self):
        svc = CardConversionService(yellow_to_red=2, red_to_black=3)
        result = svc.convert(total_yellow=6)  # 6 yellows ÷ 2 = 3 reds; 3 reds ÷ 3 = 1 black

        assert result.yellow == 0
        assert result.red == 0
        assert result.black == 1

    def test_invalid_threshold(self):
        with pytest.raises(ValueError, match="yellow_to_red must be >= 2"):
            CardConversionService(yellow_to_red=1)

    def test_five_yellows_leave_remainder(self):
        svc = CardConversionService(yellow_to_red=4, red_to_black=4)
        result = svc.convert(total_yellow=5)

        assert result.yellow == 1  # remainder
        assert result.red == 1
        assert result.black == 0
