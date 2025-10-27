from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    project_id: str
    location: str
    dataset: str
    table_residents: str
    table_facturations: str
    data_agent_id: str
    credentials_path: Optional[Path]
    system_instruction_path: Path


def load_settings(dotenv: bool = True) -> Settings:
    if dotenv:
        load_dotenv()

    project_id = _require_env("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    dataset = _require_env("GOOGLE_CLOUD_DATASET")
    table_residents = _require_env("GOOGLE_CLOUD_TABLE_RESIDENTS")
    table_facturations = _require_env("GOOGLE_CLOUD_TABLE_FACTURATIONS")
    data_agent_id = os.getenv("DATA_AGENT_ID", "senior_residence_analytics_agent")
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    system_instruction_path = Path(
        os.getenv("SYSTEM_INSTRUCTION_PATH", "system_instruction.yml")
    ).resolve()

    return Settings(
        project_id=project_id,
        location=location,
        dataset=dataset,
        table_residents=table_residents,
        table_facturations=table_facturations,
        data_agent_id=data_agent_id,
        credentials_path=Path(credentials).resolve()
        if credentials
        else None,
        system_instruction_path=system_instruction_path,
    )


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value
