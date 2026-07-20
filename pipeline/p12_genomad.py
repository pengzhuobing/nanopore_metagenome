"""Step 12: plasmid and virus detection using geNomad."""

from .models import Context, Sample
from .utils import cfg_path, ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["genomad"])

    assembly = ctx.result_dir / "assembly" / sample.sample_id / "assembly.fasta"
    db = cfg_path(ctx, "databases", "genomad")
    ensure_inputs([assembly, db])

    outdir = ctx.result_dir / "genomad" / sample.sample_id
    summary_dir = outdir / f"{sample.sample_id}_summary"
    virus_summary = summary_dir / f"{sample.sample_id}_virus_summary.tsv"
    threads = int(ctx.config["threads"]["genomad"])

    command = f"""
set -euo pipefail
mkdir -p {q(outdir)}
genomad end-to-end --threads {threads} {q(assembly)} {q(outdir)} {q(db)}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p12_genomad.log",
                [virus_summary])
