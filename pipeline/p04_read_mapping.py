"""Step 04: map reads back to assembly."""

from .models import Context, Sample
from .utils import ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["minimap2", "samtools"])

    outdir = ctx.result_dir / "assembly" / sample.sample_id
    assembly = outdir / "assembly.fasta"
    nonhost = ctx.result_dir / "host_removed" / f"{sample.sample_id}.nonhost.fastq.gz"
    ensure_inputs([assembly, nonhost])

    bam = outdir / "reads_to_contigs.bam"
    bai = outdir / "reads_to_contigs.bam.bai"
    coverage = outdir / "contig_coverage.tsv"
    threads = int(ctx.config["threads"]["mapping"])

    command = f"""
set -euo pipefail
minimap2 -ax map-ont -t {threads} {q(assembly)} {q(nonhost)} |
  samtools sort -@ 4 -o {q(bam)}
samtools index {q(bam)}
samtools coverage {q(bam)} > {q(coverage)}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p04_read_mapping.log",
                [bam, bai, coverage])
