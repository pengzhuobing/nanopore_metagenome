from __future__ import annotations

import csv
import logging
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import yaml

from .models import Context, Sample


def setup_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
        force=True,
    )


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Configuration must be a YAML mapping: {path}")
    return data


def load_samples(path: Path) -> dict[str, Sample]:
    required = {
        "sample_id", "subject_id", "diet", "age_months",
        "timepoint", "batch", "fastq",
    }
    samples: dict[str, Sample] = {}

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"Missing header in {path}")

        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing sample columns: {sorted(missing)}")

        for row in reader:
            sample_id = row["sample_id"].strip()
            if not sample_id:
                raise ValueError("Empty sample_id")
            if sample_id in samples:
                raise ValueError(f"Duplicate sample_id: {sample_id}")

            samples[sample_id] = Sample(
                sample_id=sample_id,
                subject_id=row["subject_id"].strip(),
                diet=row["diet"].strip(),
                age_months=row["age_months"].strip(),
                timepoint=row["timepoint"].strip(),
                batch=row["batch"].strip(),
                fastq=Path(row["fastq"]).expanduser(),
            )
    return samples


def require_tools(tools: Iterable[str]) -> None:
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        raise RuntimeError("Missing executables in PATH: " + ", ".join(sorted(missing)))


def ensure_inputs(paths: Iterable[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing input files:\n" + "\n".join(missing))


def outputs_ready(outputs: Iterable[Path]) -> bool:
    files = list(outputs)
    return bool(files) and all(p.exists() and p.stat().st_size > 0 for p in files)


def q(value: str | Path) -> str:
    return shlex.quote(str(value))


def cfg_path(ctx: Context, *keys: str) -> Path:
    value = ctx.config
    for key in keys:
        value = value[key]
    return Path(str(value)).expanduser()


def run_command(ctx: Context, command: str, log_path: Path, outputs: Iterable[Path]) -> None:
    outputs = list(outputs)
    if not ctx.force and outputs_ready(outputs):
        logging.info("Skip completed: %s", ", ".join(map(str, outputs)))
        return

    for output in outputs:
        output.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.info("Command: %s", " ".join(command.split()))
    if ctx.dry_run:
        return

    with log_path.open("w", encoding="utf-8") as log_handle:
        process = subprocess.run(
            ["bash", "-o", "pipefail", "-c", command],
            cwd=ctx.root,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    if process.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {process.returncode}. See: {log_path}"
        )

    missing = [str(p) for p in outputs if not p.exists()]
    if missing:
        raise RuntimeError("Expected outputs are missing:\n" + "\n".join(missing))
