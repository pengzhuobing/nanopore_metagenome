"""Step 11: MAG taxonomy using GTDB-Tk."""

from .models import Context, Sample
from .utils import ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["gtdbtk"])

    bins = ctx.result_dir / "binning" / sample.sample_id / "bins_combined"
    ensure_inputs([bins])

    outdir = ctx.result_dir / "gtdbtk" / sample.sample_id
    summary = outdir / "gtdbtk.bac120.summary.tsv"
    threads = int(ctx.config["threads"]["gtdbtk"])

    command = f"""
set -euo pipefail
mkdir -p {q(outdir)}
gtdbtk classify_wf --genome_dir {q(bins)} --out_dir {q(outdir)} \
  --extension fa --cpus {threads}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p11_gtdbtk.log",
                [summary])
