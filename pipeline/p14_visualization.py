"""Step 14: basic study-level visualizations."""

from __future__ import annotations
import csv
from pathlib import Path

from .models import Context, Sample


def run(ctx: Context, sample: Sample) -> None:
    first = next(iter(ctx.samples))
    if sample.sample_id != first:
        return

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("matplotlib is required for visualization") from exc

    matrix = ctx.result_dir / "statistics" / "bracken_species_matrix.tsv"
    if not matrix.exists():
        raise FileNotFoundError(matrix)

    outdir = ctx.result_dir / "visualization"
    outdir.mkdir(parents=True, exist_ok=True)

    totals = {}
    with matrix.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        sample_ids = [x for x in reader.fieldnames if x != "taxon"]
        totals = {sid: 0.0 for sid in sample_ids}
        for row in reader:
            for sid in sample_ids:
                try:
                    totals[sid] += float(row[sid])
                except ValueError:
                    pass

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(list(totals), list(totals.values()))
    ax.set_ylabel("Summed abundance")
    ax.set_xlabel("Sample")
    ax.set_title("Taxonomic abundance summary")
    fig.tight_layout()
    fig.savefig(outdir / "taxonomic_abundance_summary.png", dpi=200)
    plt.close(fig)
