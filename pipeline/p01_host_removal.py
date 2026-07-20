"""Step 01: remove host reads."""

from .models import Context, Sample
from .utils import cfg_path, ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["minimap2", "samtools"])

    filtered = ctx.result_dir / "qc" / sample.sample_id / "filtered.fastq.gz"
    human = cfg_path(ctx, "references", "human")
    ensure_inputs([filtered, human])

    outdir = ctx.result_dir / "host_removed"
    bam = outdir / f"{sample.sample_id}.host.bam"
    nonhost = outdir / f"{sample.sample_id}.nonhost.fastq.gz"
    stats = outdir / f"{sample.sample_id}.host_stats.tsv"
    threads = int(ctx.config["threads"]["host"])

    command = f"""
set -euo pipefail
minimap2 -ax map-ont -t {threads} {q(human)} {q(filtered)} |
  samtools sort -@ 4 -o {q(bam)}
samtools fastq -@ 4 -f 4 {q(bam)} | gzip -c > {q(nonhost)}
printf 'sample\\ttotal_alignments\\tunmapped_alignments\\n' > {q(stats)}
printf '{sample.sample_id}\\t%s\\t%s\\n' \
  "$(samtools view -c {q(bam)})" \
  "$(samtools view -c -f 4 {q(bam)})" >> {q(stats)}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p01_host_removal.log",
                [nonhost, stats])
