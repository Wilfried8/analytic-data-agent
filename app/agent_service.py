from __future__ import annotations

import logging
from pathlib import Path

from google.api_core import exceptions
from google.cloud import geminidataanalytics

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


def create_or_update_agent(
    settings: Settings,
    *,
    allow_update: bool = True,
) -> geminidataanalytics.DataAgent:
    """Create the data agent. Optionally fetch it if it already exists."""
    client = geminidataanalytics.DataAgentServiceClient()
    parent = client.common_location_path(settings.project_id, settings.location)
    system_instruction = _load_system_instruction(settings.system_instruction_path)

    context = geminidataanalytics.Context(
        system_instruction=system_instruction,
        datasource_references=build_datasource_references(settings),
        options=geminidataanalytics.ConversationOptions(
            analysis=geminidataanalytics.AnalysisOptions(
                python=geminidataanalytics.AnalysisOptions.Python(enabled=False)
            )
        ),
    )
    data_agent = geminidataanalytics.DataAgent(
        data_analytics_agent=geminidataanalytics.DataAnalyticsAgent(
            published_context=context
        )
    )
    request = geminidataanalytics.CreateDataAgentRequest(
        parent=parent,
        data_agent_id=settings.data_agent_id,
        data_agent=data_agent,
    )
    try:
        response = client.create_data_agent(request=request)
        logger.info("Data agent created: %s", response.name)
        return response
    except exceptions.AlreadyExists:
        if not allow_update:
            raise
        logger.info(
            "Agent %s already exists; fetching current definition.",
            settings.data_agent_id,
        )
        name = client.data_agent_path(
            settings.project_id, settings.location, settings.data_agent_id
        )
        return client.get_data_agent(request=geminidataanalytics.GetDataAgentRequest(name=name))


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


def delete_agent(settings: Settings, *, force: bool = False) -> None:
    client = geminidataanalytics.DataAgentServiceClient()
    name = client.data_agent_path(
        settings.project_id, settings.location, settings.data_agent_id
    )
    try:
        client.delete_data_agent(request=geminidataanalytics.DeleteDataAgentRequest(name=name))
        logger.info("Agent deletion requested: %s", name)
    except exceptions.NotFound:
        logger.warning("Agent %s not found. Nothing to delete.", name)
    except exceptions.FailedPrecondition as exc:
        if not force:
            raise
        logger.warning("Deletion failed due to state=%s; ignoring because force=True", exc)
