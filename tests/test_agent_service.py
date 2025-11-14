import pytest
from pathlib import Path
from app.agent_service import _load_system_instruction, build_datasource_references
from app.config import Settings


def test_load_system_instruction_success(tmp_path):
    file_path = tmp_path / "systeme_instruction.yml"
    file_content = "fake context"
    file_path.write_text(file_content, encoding="utf-8")

    file_result = _load_system_instruction(file_path)

    assert file_content == file_result


def test_load_system_instruction_file_not_found():
    no_path = Path("no_path_file.txt")

    with pytest.raises(RuntimeError):
        _load_system_instruction(no_path)


def test_build_datasource_references():
    settings = Settings(
        project_id="test_project_id",
        dataset="test_dataset_id",
        table_residents="test_table_residents",
        table_facturations="test_table_facturations",
        location="",
        data_agent_id="",
        system_instruction_path="",
        credentials_path="",
    )

    datasource_references = build_datasource_references(settings=settings)
    bq_refs = datasource_references.bq.table_references

    assert len(bq_refs) == 2

    assert bq_refs[0].table_id == "test_table_residents"
    assert bq_refs[0].dataset_id == "test_dataset_id"
    assert bq_refs[0].project_id == "test_project_id"

    assert bq_refs[1].table_id == "test_table_facturations"
    assert bq_refs[1].dataset_id == "test_dataset_id"
    assert bq_refs[1].project_id == "test_project_id"
