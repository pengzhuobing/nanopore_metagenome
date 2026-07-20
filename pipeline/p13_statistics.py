"""Step 13: combine per-sample outputs into study-level matrices."""

from __future__ import annotations
import csv
from collections import defaultdict

from .models import Context, Sample


def run(ctx: Context, sample: Sample) -> None:
    # This step is study-level. It runs once when the first selected sample is reached.
    first = next(iter(ctx.samples))
    if sample.sample_id != first:
        return

    outdir = ctx.result_dir / "statistics"
    outdir.mkdir(parents=True, exist_ok=True)

    abundance_out = outdir / "bracken_species_matrix.tsv"
    rows = defaultdict(dict)
    sample_ids = list(ctx.samples)

    for sample_id in sample_ids:
        path = ctx.result_dir / "taxonomy" / f"{sample_id}.bracken.S.tsv"
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                name = row.get("name") or row.get("taxonomy_name") or row.get("Name")
                value = (
                    row.get("fraction_total_reads")
                    or row.get("new_est_reads")
                    or row.get("abundance")
                    or "0"
                )
                if name:
                    rows[name][sample_id] = value

    with abundance_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["taxon", *sample_ids])
        for taxon in sorted(rows):
            writer.writerow([taxon, *[rows[taxon].get(sid, "0") for sid in sample_ids]])
