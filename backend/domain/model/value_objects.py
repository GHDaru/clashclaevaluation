"""Value Objects — immutable, defined by their attributes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerTag:
    """Player identifier in Clash Royale (e.g. #ABC123). Immutable in CR."""

    value: str

    def __post_init__(self):
        if not self.value.startswith("#"):
            raise ValueError(f"PlayerTag must start with '#': {self.value}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ClanTag:
    """Clan identifier in Clash Royale (e.g. #XYZ789). Immutable in CR."""

    value: str

    def __post_init__(self):
        if not self.value.startswith("#"):
            raise ValueError(f"ClanTag must start with '#': {self.value}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AttackCount:
    """Number of attacks performed in a WarDay (0-4)."""

    value: int

    def __post_init__(self):
        if not (0 <= self.value <= 4):
            raise ValueError(f"AttackCount must be 0-4: {self.value}")

    @property
    def missing(self) -> int:
        """Attacks missing from the expected 4."""
        return 4 - self.value


@dataclass(frozen=True)
class YellowCard:
    """Penalty for 1 missing Attack in a WarDay."""

    count: int = 1

    def __post_init__(self):
        if self.count < 0:
            raise ValueError(f"YellowCard count cannot be negative: {self.count}")


@dataclass(frozen=True)
class RedCard:
    """Penalty from conversion of YellowCards (default: 4 YellowCards → 1 RedCard)."""

    count: int = 1

    def __post_init__(self):
        if self.count < 0:
            raise ValueError(f"RedCard count cannot be negative: {self.count}")


@dataclass(frozen=True)
class BlackCard:
    """Maximum penalty — conversion of RedCards (default: 4 RedCards → 1 BlackCard).
    Player is candidato a expulsão (expulsion candidate)."""

    count: int = 1

    def __post_init__(self):
        if self.count < 0:
            raise ValueError(f"BlackCard count cannot be negative: {self.count}")


@dataclass(frozen=True)
class CardSummary:
    """Summary of all cards for a player."""

    yellow: int
    red: int
    black: int

    @property
    def is_clean(self) -> bool:
        return self.yellow == 0 and self.red == 0 and self.black == 0

    @property
    def is_critical(self) -> bool:
        return self.black > 0


@dataclass(frozen=True)
class WarDay:
    """One of the 4 days of War: Thursday, Friday, Saturday, Sunday."""

    index: int  # 0=Thursday, 1=Friday, 2=Saturday, 3=Sunday
    label: str  # "Quinta", "Sexta", "Sábado", "Domingo"

    DAYS = [
        ("Quinta", "Thu"),
        ("Sexta", "Fri"),
        ("Sábado", "Sat"),
        ("Domingo", "Sun"),
    ]

    @classmethod
    def from_index(cls, index: int) -> "WarDay":
        if not (0 <= index <= 3):
            raise ValueError(f"WarDay index must be 0-3: {index}")
        label, _ = cls.DAYS[index]
        return cls(index=index, label=label)

    @classmethod
    def all_days(cls) -> list["WarDay"]:
        return [cls.from_index(i) for i in range(4)]


@dataclass(frozen=True)
class PeriodPoints:
    """Points accumulated by a player during a War period."""

    total: int
    war_days: list[int]  # [day1_points, day2_points, day3_points, day4_points]

    def __post_init__(self):
        if len(self.war_days) != 4:
            raise ValueError(f"PeriodPoints must have 4 war days: {len(self.war_days)}")
