"""RelaxationService — determines which WarDays are relaxed.

EarlyVictory: if the clan finished 1st before Sunday, remaining days
do not generate cards.
"""

from domain.model.aggregates import War, WarStatus


class RelaxationService:
    """Determines relaxed WarDays for a War.

    Ubiquitous Language:
    - EarlyVictory: clan crossed finish line in 1st place
    - Relaxation: suspension of card issuance on remaining WarDays
    """

    def compute_relaxed_days(self, war: War) -> list[int]:
        """Compute which WarDay indices (0-3) should be relaxed.

        A day is relaxed if:
        - EarlyVictory is detected (clan finished 1st AND not the last day)
        - The day is AFTER the victory was achieved

        For simplicity in v1: if war.status is FINISHED_1ST and the last
        completed periodIndex < 3, remaining days are relaxed.
        """
        if war.status != WarStatus.FINISHED_1ST:
            return []

        # If the war ended with 1st place and the API reported the
        # finish before Sunday, the relaxed_days come from the API data.
        # In v1: if there are relaxed_days already set, use them.
        if war.relaxed_days:
            return war.relaxed_days

        # Fallback: no relaxation computed
        return []
