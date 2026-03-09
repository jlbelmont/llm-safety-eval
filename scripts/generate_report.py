from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    return yaml.safe_load(config_path.read_text()) or {}


def load_sections(base_dir: Path, sections: List[str]) -> Dict[str, str]:
    loaded: Dict[str, str] = {}
    for name in sections:
        section_path = base_dir / f"{name}.tex"
        if not section_path.exists():
            raise FileNotFoundError(f"Section file missing: {section_path}")
        loaded[name] = section_path.read_text()
    return loaded


def render(template_dir: Path, template_name: str, context: dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_name)
    return template.render(**context)


def write_output(content: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def maybe_build_pdf(tex_path: Path, output_dir: Path) -> None:
    # Use latexmk if available; otherwise fail gracefully.
    try:
        subprocess.run(
            ["latexmk", "-pdf", "-output-directory", str(output_dir), str(tex_path)],
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError("latexmk not found. Install TeX Live or MacTeX to build PDF.")


def read_as_latex(path: Path) -> str:
    """
    Return file content as LaTeX. If the source is Markdown, attempt to use pandoc
    for a clean conversion; otherwise wrap the raw text in verbatim as a fallback.
    """
    if not path.exists():
        raise FileNotFoundError(f"Extra content not found: {path}")

    if path.suffix.lower() == ".md":
        try:
            result = subprocess.run(
                ["pandoc", "-f", "markdown", "-t", "latex", str(path)],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout
        except FileNotFoundError:
            # Safe fallback: keep content visible without rendering errors.
            content = path.read_text()
            return "\\begin{verbatim}\n" + content + "\n\\end{verbatim}\n"
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"pandoc failed on {path}: {exc}") from exc

    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
        return frame.to_latex(index=False, escape=True)

    # Assume already-LaTeX content
    return path.read_text()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LaTeX report from config.")
    parser.add_argument("--config", type=Path, required=True, help="Path to report_config.yaml")
    parser.add_argument("--output", type=Path, required=True, help="Path to write rendered .tex")
    parser.add_argument("--build-pdf", action="store_true", help="Invoke latexmk to build PDF")
    args = parser.parse_args()

    cfg = load_config(args.config)

    template_dir = Path(cfg.get("template_dir", "reports/templates"))
    template_name = cfg.get("template_name", "research_report.tex.jinja")
    sections_dir = Path(cfg.get("sections_dir", "reports/sections"))
    sections_list: List[str] = cfg.get("section_order", [])
    bibliography = cfg.get("bibliography", "")

    sections = load_sections(sections_dir, sections_list)

    # Optional: pull in a run summary (e.g., runs/<id>/summary.md) into the report.
    run_summary_cfg = cfg.get("run_summary")
    run_summary: dict[str, str] | None = None
    if run_summary_cfg:
        summary_path = Path(run_summary_cfg.get("path", ""))
        if summary_path:
            run_summary = {
                "title": run_summary_cfg.get("title", "Run Summary"),
                "content": read_as_latex(summary_path),
            }

    analysis_artifacts: list[dict[str, str]] = []
    for artifact_cfg in cfg.get("analysis_artifacts", []):
        artifact_path = Path(artifact_cfg.get("path", ""))
        if artifact_path:
            analysis_artifacts.append(
                {
                    "title": artifact_cfg.get("title", artifact_path.name),
                    "content": read_as_latex(artifact_path),
                }
            )

    context = {
        "meta": cfg.get("meta", {}),
        "sections": sections,
        "bibliography": bibliography,
        "run_summary": run_summary,
        "analysis_artifacts": analysis_artifacts,
    }

    rendered = render(template_dir, template_name, context)
    write_output(rendered, args.output)

    if args.build_pdf:
        maybe_build_pdf(args.output, args.output.parent)

    print(f"Wrote LaTeX to {args.output}")
    if args.build_pdf:
        print(f"PDF build attempted in {args.output.parent}")


if __name__ == "__main__":
    main()
