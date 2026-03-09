from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import typer.testing


def _load_prompt_lint_app():
    module_path = Path("scripts/lint_prompt_suite.py")
    spec = spec_from_file_location("lint_prompt_suite", module_path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


def test_prompt_lint_ok(tmp_path: Path):
    runner = typer.testing.CliRunner()
    app = _load_prompt_lint_app()
    result = runner.invoke(app, [str(Path("prompts/prompt_suites.yaml"))])
    assert result.exit_code == 0
