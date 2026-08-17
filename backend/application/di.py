"""Dependency Injection — wires ports to adapters and builds use cases.

This is the composition root: the only place that knows about concrete implementations.
"""

from functools import lru_cache

from application.port.primary.use_cases import (
    EvaluateClanUseCase,
    GetClanStatusUseCase,
    GetPlayerHistoryUseCase,
)
from application.port.secondary.cr_api_client import CRApiClient
from application.port.secondary.repositories import (
    PlayerRepository,
    PlayerWarRepository,
    WarRepository,
)
from domain.service.evaluation import EvaluationConfig, EvaluationService
from domain.service.relaxation import RelaxationService
from infrastructure.adapter.secondary.cr_http_client import HttpCRApiClient
from infrastructure.config import Settings, settings


@lru_cache
def get_settings() -> Settings:
    return settings


@lru_cache
def get_cr_api_client() -> CRApiClient:
    return HttpCRApiClient()


@lru_cache
def get_evaluation_config() -> EvaluationConfig:
    s = get_settings()
    return EvaluationConfig(
        attacks_per_day=s.attacks_per_day,
        yellow_to_red=s.yellow_to_red,
        red_to_black=s.red_to_black,
        min_points_warning=s.min_points_warning,
        min_points_critical=s.min_points_critical,
        relax_on_first_place=s.relax_on_first_place,
    )


@lru_cache
def get_evaluation_service() -> EvaluationService:
    return EvaluationService(get_evaluation_config())


@lru_cache
def get_relaxation_service() -> RelaxationService:
    return RelaxationService()


def get_war_repo() -> WarRepository:
    from infrastructure.adapter.secondary.sql_repositories import SqlWarRepository
    from infrastructure.orm.database import async_session
    return SqlWarRepository(async_session())


def get_player_repo() -> PlayerRepository:
    from infrastructure.adapter.secondary.sql_repositories import SqlPlayerRepository
    from infrastructure.orm.database import async_session
    return SqlPlayerRepository(async_session())


def get_player_war_repo() -> PlayerWarRepository:
    from infrastructure.adapter.secondary.sql_repositories import SqlPlayerWarRepository
    from infrastructure.orm.database import async_session
    return SqlPlayerWarRepository(async_session())


def get_clan_status_use_case() -> GetClanStatusUseCase:
    return GetClanStatusUseCase(
        war_repo=get_war_repo(),
        player_war_repo=get_player_war_repo(),
        cr_api=get_cr_api_client(),
        config=get_evaluation_config(),
    )


def get_evaluate_use_case() -> EvaluateClanUseCase:
    return EvaluateClanUseCase(
        war_repo=get_war_repo(),
        player_war_repo=get_player_war_repo(),
        cr_api=get_cr_api_client(),
        evaluation_service=get_evaluation_service(),
        relaxation_service=get_relaxation_service(),
    )


def get_player_history_use_case() -> GetPlayerHistoryUseCase:
    return GetPlayerHistoryUseCase(
        player_repo=get_player_repo(),
        player_war_repo=get_player_war_repo(),
        cr_api=get_cr_api_client(),
        clan_tag=get_settings().cr_clan_tag,
        config=get_evaluation_config(),
    )
