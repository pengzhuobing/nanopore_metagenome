"""Step 03: long-read metagenome assembly."""

from .models import Context, Sample
from .utils import ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["flye"])

    nonhost = ctx.result_dir / "host_removed" / f"{sample.sample_id}.nonhost.fastq.gz"
    ensure_inputs([nonhost])

    outdir = ctx.result_dir / "assembly" / sample.sample_id
    assembly = outdir / "assembly.fasta"
    info = outdir / "assembly_info.txt"
    threads = int(ctx.config["threads"]["assembly"])

    command = f"""
set -euo pipefail
flye --nano-hq {q(nonhost)} --meta --threads {threads} --out-dir {q(outdir)}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p03_assembly.log",
                [assembly, info])
