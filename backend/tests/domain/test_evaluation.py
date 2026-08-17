"""Tests for EvaluationService — the core evaluation logic."""

from domain.model.aggregates import PlayerWar, War, WarStatus
from domain.model.value_objects import (
    AttackCount,
    PlayerTag,
)
from domain.service.evaluation import EvaluationConfig, EvaluationService


def make_player_war(
    tag: str = "#PLAYER1",
    name: str = "TestPlayer",
    attacks: list[int] | None = None,
    points: int = 3200,
) -> PlayerWar:
    if attacks is None:
        attacks = [4, 4, 4, 4]
    return PlayerWar(
        player_tag=PlayerTag(tag),
        player_name=name,
        attacks=[AttackCount(a) for a in attacks],
        total_points=points,
    )


def make_war(
    status: WarStatus = WarStatus.FINISHED_1ST,
    relaxed_days: list[int] | None = None,
) -> War:
    from datetime import date
    return War(
        id=1,
        clan_tag="#CLAN1",
        start_date=date(2026, 8, 13),
        end_date=date(2026, 8, 16),
        status=status,
        total_fame=50000,
        relaxed_days=relaxed_days or [],
    )


class TestEvaluationService:
    def test_perfect_player_no_cards(self):
        war = make_war()
        war.add_player_war(make_player_war(attacks=[4, 4, 4, 4], points=3200))

        svc = EvaluationService(EvaluationConfig())
        results = svc.evaluate(war)

        assert len(results) == 1
        r = results[0]
        assert r.final_yellow == 0
        assert r.final_red == 0
        assert r.final_black == 0

    def test_zero_attacks_all_days_is_black(self):
        """0/4 for 4 days = 16 yellows → 4 reds → 1 black."""
        war = make_war()
        war.add_player_war(make_player_war(attacks=[0, 0, 0, 0], points=0))

        svc = EvaluationService(EvaluationConfig())
        results = svc.evaluate(war)

        r = results[0]
        assert r.raw_yellows == 16  # 4 missing × 4 days
        assert r.points_yellow == 1  # < 1600
        assert r.points_red == 0  # min_points_critical=0 (disabled)
        assert r.final_black == 1  # 16+1=17 yellows → 4 reds (1 remainder) → 1 black
        # 17 ÷ 4 = 4 reds + 1 yellow remainder → 4 reds ÷ 4 = 1 black

    def test_below_warning_points(self):
        war = make_war()
        war.add_player_war(make_player_war(attacks=[4, 4, 4, 4], points=1500))

        svc = EvaluationService(EvaluationConfig(min_points_warning=1600))
        results = svc.evaluate(war)

        r = results[0]
        assert r.raw_yellows == 0
        assert r.points_yellow == 1  # < 1600
        assert r.final_yellow == 1

    def test_below_critical_points(self):
        war = make_war()
        war.add_player_war(make_player_war(attacks=[4, 4, 4, 4], points=800))

        svc = EvaluationService(
            EvaluationConfig(min_points_warning=1600, min_points_critical=1000)
        )
        results = svc.evaluate(war)

        r = results[0]
        assert r.points_yellow == 1
        assert r.points_red == 1  # < critical
        assert r.final_red == 1

    def test_relaxed_day_no_cards(self):
        """Sunday relaxed → 0 attacks on Sunday generates no cards."""
        war = make_war(relaxed_days=[3])  # Sunday is relaxed
        war.add_player_war(make_player_war(attacks=[4, 4, 4, 0], points=2400))

        svc = EvaluationService(EvaluationConfig(relax_on_first_place=True))
        results = svc.evaluate(war)

        r = results[0]
        assert r.raw_yellows == 0  # Sunday is relaxed, no cards

    def test_mixed_scenario(self):
        """3/4 Thu, 2/4 Fri, 4/4 Sat, 4/4 Sun, 2000 points."""
        war = make_war()
        war.add_player_war(make_player_war(attacks=[3, 2, 4, 4], points=2000))

        svc = EvaluationService(EvaluationConfig())
        results = svc.evaluate(war)

        r = results[0]
        assert r.raw_yellows == 3  # 1 missing Thu + 2 missing Fri
        assert r.points_yellow == 0  # 2000 >= 1600
        assert r.final_yellow == 3
        assert r.final_red == 0
