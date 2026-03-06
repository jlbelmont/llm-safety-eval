from pathlib import Path
from scripts.lint_prompt_suite import app
import typer.testing


def test_prompt_lint_ok(tmp_path: Path):
    runner = typer.testing.CliRunner()
    result = runner.invoke(app, [str(Path("prompts/prompt_suites.yaml"))])
    assert result.exit_code == 0
