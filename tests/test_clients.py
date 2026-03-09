from llm_safety_eval.llm_clients.base import ClientRegistry
from llm_safety_eval.data_models import ModelConfig, ProviderConfig
from llm_safety_eval.cli import app as cli_app
import typer.testing


def test_mock_client_instantiation():
    models_cfg = [
        {"model_id": "mock_safe", "provider_id": "mock", "model_name": "mock-safety-eval", "generation_parameters": {}}
    ]
    providers_cfg = [
        {"provider_id": "mock", "api_type": "mock", "base_url": "http://localhost/mock"}
    ]
    registry = ClientRegistry.from_configs(models_cfg, providers_cfg)
    client = registry.get_client("mock_safe")
    assert client.model_name == "mock-safety-eval"
    result = client.generate("hello", {})
    assert "mock response" in result.text


def test_execute_flag_respects_env(monkeypatch):
    monkeypatch.delenv("LSE_ALLOW_NETWORK", raising=False)
    provider = ProviderConfig(provider_id="openai", api_type="openai_compatible", base_url="http://example.com")
    model = ModelConfig(model_id="m", provider_id="openai", model_name="gpt-4o")
    registry = ClientRegistry.from_configs([model.model_dump()], [provider.model_dump()])
    client = registry.get_client("m")
    result = client.generate("hi", {}, execute=True)
    # Since env is off, it should still stub
    assert "stub" in result.text or "openai-compatible" in result.text


def test_execute_flag_abort(monkeypatch):
    runner = typer.testing.CliRunner()
    result = runner.invoke(
        cli_app,
        [
            "run",
            "--execute",
            "--base-config",
            "configs/base.yaml",
            "--matrix",
            "configs/matrix.yaml",
            "--models",
            "configs/models.yaml",
            "--providers",
            "configs/providers.yaml",
        ],
        env={"LSE_ALLOW_NETWORK": "0"},
    )
    assert result.exit_code != 0
