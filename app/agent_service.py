from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, cast

from google.api_core import exceptions
from google.cloud import geminidataanalytics
from google.protobuf import field_mask_pb2

from .config import Settings

logger = logging.getLogger(__name__)


def _load_system_instruction(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"System instruction file not found: {path}") from exc


def build_datasource_references(settings: Settings) -> geminidataanalytics.DatasourceReferences:
    residents_ref = geminidataanalytics.BigQueryTableReference(
        project_id=settings.project_id,
        dataset_id=settings.dataset,
        table_id=settings.table_residents,
    )
    facturations_ref = geminidataanalytics.BigQueryTableReference(
        project_id=settings.project_id,
        dataset_id=settings.dataset,
        table_id=settings.table_facturations,
    )
    return geminidataanalytics.DatasourceReferences(
        bq=geminidataanalytics.BigQueryTableReferences(
            table_references=[residents_ref, facturations_ref]
        )
    )


def _build_context(settings: Settings) -> geminidataanalytics.Context:
    system_instruction = _load_system_instruction(settings.system_instruction_path)
    return geminidataanalytics.Context(
        system_instruction=system_instruction,
        datasource_references=build_datasource_references(settings),
        options=geminidataanalytics.ConversationOptions(
            analysis=geminidataanalytics.AnalysisOptions(
                python=geminidataanalytics.AnalysisOptions.Python(enabled=False)
            )
        ),
    )


def _build_data_agent(settings: Settings) -> geminidataanalytics.DataAgent:
    return geminidataanalytics.DataAgent(
        data_analytics_agent=geminidataanalytics.DataAnalyticsAgent(
            published_context=_build_context(settings)
        )
    )


def _maybe_await_operation(response: Any) -> Any:
    """Unwrap long running operations returned by the API."""
    if hasattr(response, "result"):
        return response.result()
    return response


def create_agent(settings: Settings) -> geminidataanalytics.DataAgent:
    """Create the data agent. Raises AlreadyExists if the agent is present."""
    client = geminidataanalytics.DataAgentServiceClient()
    parent = client.common_location_path(settings.project_id, settings.location)
    request = geminidataanalytics.CreateDataAgentRequest(
        parent=parent,
        data_agent_id=settings.data_agent_id,
        data_agent=_build_data_agent(settings),
    )
    response = client.create_data_agent(request=request)
    agent = cast(geminidataanalytics.DataAgent, _maybe_await_operation(response))
    logger.info("Data agent created: %s", agent.name)
    return agent


def update_agent(settings: Settings) -> geminidataanalytics.DataAgent:
    """Update the existing data agent definition."""
    client = geminidataanalytics.DataAgentServiceClient()
    name = client.data_agent_path(
        settings.project_id, settings.location, settings.data_agent_id
    )
    data_agent = _build_data_agent(settings)
    data_agent.name = name
    update_mask = field_mask_pb2.FieldMask(paths=["data_analytics_agent.published_context"])
    response = client.update_data_agent(
        request=geminidataanalytics.UpdateDataAgentRequest(
            data_agent=data_agent,
            update_mask=update_mask,
        )
    )
    agent = cast(geminidataanalytics.DataAgent, _maybe_await_operation(response))
    logger.info("Data agent updated: %s", agent.name)
    return agent


def create_or_update_agent(
    settings: Settings,
    *,
    allow_update: bool = True,
) -> geminidataanalytics.DataAgent:
    """Create the data agent. Optionally update it if it already exists."""
    try:
        return create_agent(settings)
    except exceptions.AlreadyExists:
        if not allow_update:
            raise
        logger.info(
            "Agent %s already exists; attempting update.",
            settings.data_agent_id,
        )
        return update_agent(settings)


def get_agent(settings: Settings) -> geminidataanalytics.DataAgent | None:
    client = geminidataanalytics.DataAgentServiceClient()
    name = client.data_agent_path(
        settings.project_id, settings.location, settings.data_agent_id
    )
    try:
        return client.get_data_agent(request=geminidataanalytics.GetDataAgentRequest(name=name))
    except exceptions.NotFound:
        return None


def list_agents(settings: Settings) -> list[geminidataanalytics.DataAgent]:
    client = geminidataanalytics.DataAgentServiceClient()
    parent = client.common_location_path(settings.project_id, settings.location)
    return list(client.list_data_agents(request=geminidataanalytics.ListDataAgentsRequest(parent=parent)))


def delete_agent(settings: Settings, agent_id: str | None = None, *, force: bool = False) -> bool:
    client = geminidataanalytics.DataAgentServiceClient()
    agent_identifier = agent_id or settings.data_agent_id
    name = client.data_agent_path(settings.project_id, settings.location, agent_identifier)
    try:
        response = client.delete_data_agent(
            request=geminidataanalytics.DeleteDataAgentRequest(name=name)
        )
        _maybe_await_operation(response)
        logger.info("Agent deletion requested: %s", name)
        return True
    except exceptions.NotFound:
        logger.warning("Agent %s not found. Nothing to delete.", name)
        return False
    except exceptions.FailedPrecondition as exc:
        if not force:
            raise
        logger.warning("Deletion failed due to state=%s; ignoring because force=True", exc)
        return False
