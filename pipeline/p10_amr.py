"""Step 10: AMR gene screening using AMRFinderPlus."""

from .models import Context, Sample
from .utils import ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["amrfinder"])

    proteins = ctx.result_dir / "annotation" / sample.sample_id / "bakta" / f"{sample.sample_id}.faa"
    ensure_inputs([proteins])

    outdir = ctx.result_dir / "amr"
    output = outdir / f"{sample.sample_id}.amrfinder.tsv"
    threads = int(ctx.config["threads"]["amr"])

    command = f"""
set -euo pipefail
mkdir -p {q(outdir)}
amrfinder -p {q(proteins)} -o {q(output)} --threads {threads}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p10_amr.log",
                [output])
