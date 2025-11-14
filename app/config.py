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

    project_id = _require_env(
        "GOOGLE_CLOUD_PROJECT",
        "Example: GOOGLE_CLOUD_PROJECT=my-gcp-project",
    )
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    dataset = _require_env(
        "GOOGLE_CLOUD_DATASET",
        "Example: GOOGLE_CLOUD_DATASET=test_demo",
    )
    table_residents = _require_env(
        "GOOGLE_CLOUD_TABLE_RESIDENTS",
        "Example: GOOGLE_CLOUD_TABLE_RESIDENTS=residents",
    )
    table_facturations = _require_env(
        "GOOGLE_CLOUD_TABLE_FACTURATIONS",
        "Example: GOOGLE_CLOUD_TABLE_FACTURATIONS=facturations",
    )
    data_agent_id = os.getenv("DATA_AGENT_ID", "senior_residence_analytics_agent")

    credentials_raw = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    credentials_path: Optional[Path] = None
    if credentials_raw:
        candidate = Path(credentials_raw).expanduser().resolve()
        if not candidate.is_file():
            raise RuntimeError(
                f"Credential file not found at {candidate}. "
                "Update GOOGLE_APPLICATION_CREDENTIALS or unset it to rely on Application Default Credentials."
            )
        credentials_path = candidate

    system_instruction_path = (
        Path(os.getenv("SYSTEM_INSTRUCTION_PATH", "system_instruction.yml"))
        .expanduser()
        .resolve()
    )
    if not system_instruction_path.is_file():
        raise RuntimeError(
            f"System instruction file not found at {system_instruction_path}. "
            "Set SYSTEM_INSTRUCTION_PATH or ensure the file exists."
        )

    return Settings(
        project_id=project_id,
        location=location,
        dataset=dataset,
        table_residents=table_residents,
        table_facturations=table_facturations,
        data_agent_id=data_agent_id,
        credentials_path=credentials_path,
        system_instruction_path=system_instruction_path,
    )


def _require_env(key: str, hint: Optional[str] = None) -> str:
    value = os.getenv(key)
    if not value:
        message = (
            f"Missing required environment variable: {key}. "
            "Define it in the shell, Terraform env vars, or .env file."
        )
        if hint:
            message += f" {hint}"
        raise RuntimeError(message)
    return value
