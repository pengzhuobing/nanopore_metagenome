from __future__ import annotations

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .models import Context
from .registry import DEFAULT_ORDER, STEPS
from .utils import cfg_path, ensure_inputs, load_samples, load_yaml, setup_logging


def parse_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [x.strip() for x in value.split(",") if x.strip()]


def validate(ctx: Context) -> None:
    for sample in ctx.samples.values():
        ensure_inputs([sample.fastq])

    required = [
        cfg_path(ctx, "references", "human"),
        cfg_path(ctx, "references", "probiotic_competitive"),
        cfg_path(ctx, "references", "urate_proteins"),
        cfg_path(ctx, "databases", "kraken2"),
        cfg_path(ctx, "databases", "checkm2"),
        cfg_path(ctx, "databases", "bakta"),
        cfg_path(ctx, "databases", "dbcan"),
        cfg_path(ctx, "databases", "genomad"),
    ]
    ensure_inputs(required)
    logging.info("Configuration is valid")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Nanopore long-read metagenome pipeline v1.0"
    )
    parser.add_argument("--config", default="config/config.yaml")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate")
    run = sub.add_parser("run")
    run.add_argument("--steps", help="Comma-separated step names")
    run.add_argument("--samples", help="Comma-separated sample IDs")
    run.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Number of samples to process in parallel (default: 1)",
    )
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--force", action="store_true")
    sub.add_parser("list-steps")
    return parser


def run_sample(ctx: Context, sample_id: str, selected_steps: list[str]) -> None:
    sample = ctx.samples[sample_id]
    logging.info("=== %s ===", sample_id)

    for step in selected_steps:
        logging.info("[%s] --- %s ---", sample_id, step)
        STEPS[step](ctx, sample)

    logging.info("[%s] completed", sample_id)


def main() -> int:
    args = build_parser().parse_args()
    root = Path.cwd()
    config = load_yaml((root / args.config).resolve())

    samples_path = Path(config["samples"])
    if not samples_path.is_absolute():
        samples_path = root / samples_path

    ctx = Context(
        root=root,
        config=config,
        samples=load_samples(samples_path),
        dry_run=getattr(args, "dry_run", False),
        force=getattr(args, "force", False),
    )
    setup_logging(ctx.log_dir / "pipeline.log")

    if args.command == "list-steps":
        for idx, step in enumerate(DEFAULT_ORDER):
            print(f"{idx:02d}\t{step}")
        return 0

    if args.command == "validate":
        validate(ctx)
        return 0

    selected_steps = parse_csv(args.steps, DEFAULT_ORDER)
    unknown = [x for x in selected_steps if x not in STEPS]
    if unknown:
        raise ValueError(f"Unknown steps: {unknown}")

    selected_samples = parse_csv(args.samples, list(ctx.samples))
    unknown_samples = [x for x in selected_samples if x not in ctx.samples]
    if unknown_samples:
        raise ValueError(f"Unknown samples: {unknown_samples}")

    if args.jobs < 1:
        raise ValueError("--jobs must be at least 1")

    jobs = min(args.jobs, len(selected_samples))
    logging.info(
        "Running %d sample(s) with %d parallel job(s)",
        len(selected_samples),
        jobs,
    )

    if jobs == 1:
        for sample_id in selected_samples:
            run_sample(ctx, sample_id, selected_steps)
    else:
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = {
                executor.submit(run_sample, ctx, sample_id, selected_steps): sample_id
                for sample_id in selected_samples
            }

            for future in as_completed(futures):
                sample_id = futures[future]
                try:
                    future.result()
                except Exception:
                    logging.exception("[%s] failed", sample_id)
                    raise

    logging.info("Pipeline completed")
    return 0
