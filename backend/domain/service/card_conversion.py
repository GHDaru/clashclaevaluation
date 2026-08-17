"""CardConversionService — converts YellowCards → RedCards → BlackCards.

Pure domain service. No I/O. Testable with fixtures.
"""

from domain.model.value_objects import CardSummary


class CardConversionService:
    """Converts accumulated cards according to configurable thresholds.

    Ubiquitous Language:
    - yellow_to_red: how many YellowCards become 1 RedCard (default: 4)
    - red_to_black: how many RedCards become 1 BlackCard (default: 4)
    """

    def __init__(self, yellow_to_red: int = 4, red_to_black: int = 4):
        if yellow_to_red < 2:
            raise ValueError(f"yellow_to_red must be >= 2: {yellow_to_red}")
        if red_to_black < 2:
            raise ValueError(f"red_to_black must be >= 2: {red_to_black}")
        self.yellow_to_red = yellow_to_red
        self.red_to_black = red_to_black

    def convert(self, total_yellow: int, total_red: int = 0) -> CardSummary:
        """Convert raw card counts into final CardSummary.

        Args:
            total_yellow: Raw yellow cards (from attacks + points).
            total_red: Additional red cards (from point threshold).

        Returns:
            CardSummary with converted counts.
        """
        # Step 1: convert yellows to reds
        additional_reds = total_yellow // self.yellow_to_red
        remaining_yellow = total_yellow % self.yellow_to_red

        total_red += additional_reds

        # Step 2: convert reds to blacks
        blacks = total_red // self.red_to_black
        remaining_red = total_red % self.red_to_black

        return CardSummary(
            yellow=remaining_yellow,
            red=remaining_red,
            black=blacks,
        )
