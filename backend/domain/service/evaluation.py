"""EvaluationService — the core evaluation of a War.

Applies all rules from M2: attacks, points, relaxation, conversion.
Pure domain service. No I/O.
"""

from dataclasses import dataclass

from domain.model.aggregates import PlayerWar, War
from domain.model.value_objects import (
    AttackCount,
    PlayerTag,
)
from domain.service.card_conversion import CardConversionService


@dataclass
class EvaluationConfig:
    """Configuration snapshot for one Evaluation (from M4)."""

    attacks_per_day: int = 4
    yellow_to_red: int = 4
    red_to_black: int = 4
    min_points_warning: int = 1600
    min_points_critical: int = 0  # 0 = disabled
    relax_on_first_place: bool = True


@dataclass
class PlayerEvaluationResult:
    """Result of evaluating one player in one War."""

    player_tag: PlayerTag
    player_name: str
    attacks: list[AttackCount]
    raw_yellows: int
    points_yellow: int
    points_red: int
    final_yellow: int
    final_red: int
    final_black: int


class EvaluationService:
    """Evaluates a War: assigns YellowCards, RedCards, BlackCards to each participant.

    Rules applied (in order):
    1. Count missing attacks → YellowCards
    2. Check point thresholds → additional YellowCards/RedCards
    3. Apply relaxation if EarlyVictory
    4. Convert cards via CardConversionService
    """

    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.converter = CardConversionService(
            yellow_to_red=config.yellow_to_red,
            red_to_black=config.red_to_black,
        )

    def evaluate(self, war: War) -> list[PlayerEvaluationResult]:
        results: list[PlayerEvaluationResult] = []

        for pw in war.player_wars:
            result = self._evaluate_player(pw, war)
            results.append(result)

        return results

    def _evaluate_player(self, pw: PlayerWar, war: War) -> PlayerEvaluationResult:
        # Step 1: count missing attacks → YellowCards
        raw_yellows = 0
        for day_idx, attack_count in enumerate(pw.attacks):
            if war.is_day_relaxed(day_idx):
                continue  # Relaxation: no cards for this day
            missing = self.config.attacks_per_day - attack_count.value
            if missing > 0:
                raw_yellows += missing  # 1 YellowCard per missing Attack

        # Step 2: point thresholds
        points_yellow = 0
        points_red = 0

        if pw.total_points < self.config.min_points_warning:
            points_yellow = 1
        if (
            self.config.min_points_critical > 0
            and pw.total_points < self.config.min_points_critical
        ):
            points_red = 1

        total_yellows = raw_yellows + points_yellow
        total_reds = points_red

        # Step 3: convert
        summary = self.converter.convert(total_yellows, total_reds)

        return PlayerEvaluationResult(
            player_tag=pw.player_tag,
            player_name=pw.player_name,
            attacks=pw.attacks,
            raw_yellows=raw_yellows,
            points_yellow=points_yellow,
            points_red=points_red,
            final_yellow=summary.yellow,
            final_red=summary.red,
            final_black=summary.black,
        )
