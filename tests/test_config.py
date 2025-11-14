import pytest

from app.config import Settings, load_settings


@pytest.fixture
def mock_env(monkeypatch, tmp_path):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("GOOGLE_CLOUD_DATASET", "test_dataset")
    monkeypatch.setenv("GOOGLE_CLOUD_TABLE_RESIDENTS", "residents")
    monkeypatch.setenv("GOOGLE_CLOUD_TABLE_FACTURATIONS", "facturations")

    fake_instruction = tmp_path / "systeme_instrucyion.yml"
    fake_instruction.write_text("fake context")

    monkeypatch.setenv("SYSTEM_INSTRUCTION_PATH", str(fake_instruction))

    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)

    return {"instruction_path": fake_instruction}


def test_load_settings_success(mock_env):
    """Test that load_settings returns a proper Settings object when env is valid."""
    settings = load_settings(dotenv=False)

    assert isinstance(settings, Settings)

    assert settings.project_id == "test-project"
    assert settings.dataset == "test_dataset"
    assert settings.table_residents == "residents"
    assert settings.table_facturations == "facturations"
    assert settings.system_instruction_path.is_file()


def test_load_settings_missing_env(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)

    with pytest.raises(RuntimeError):
        load_settings(dotenv=False)
