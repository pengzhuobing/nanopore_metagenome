"""Step 08: competitive probiotic detection."""

from .models import Context, Sample
from .utils import cfg_path, ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["minimap2", "samtools"])

    nonhost = ctx.result_dir / "host_removed" / f"{sample.sample_id}.nonhost.fastq.gz"
    ref = cfg_path(ctx, "references", "probiotic_competitive")
    ensure_inputs([nonhost, ref])

    outdir = ctx.result_dir / "probiotic"
    bam = outdir / f"{sample.sample_id}.bam"
    bai = outdir / f"{sample.sample_id}.bam.bai"
    coverage = outdir / f"{sample.sample_id}.coverage.tsv"
    idxstats = outdir / f"{sample.sample_id}.idxstats.tsv"
    threads = int(ctx.config["threads"]["probiotic"])

    command = f"""
set -euo pipefail
mkdir -p {q(outdir)}
minimap2 -ax map-ont -t {threads} {q(ref)} {q(nonhost)} |
  samtools sort -@ 4 -o {q(bam)}
samtools index {q(bam)}
samtools coverage {q(bam)} > {q(coverage)}
samtools idxstats {q(bam)} > {q(idxstats)}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p08_probiotic.log",
                [bam, bai, coverage, idxstats])
