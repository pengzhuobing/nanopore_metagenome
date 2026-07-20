"""Step 02: read-level taxonomy."""

from .models import Context, Sample
from .utils import cfg_path, ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["kraken2", "bracken"])

    nonhost = ctx.result_dir / "host_removed" / f"{sample.sample_id}.nonhost.fastq.gz"
    db = cfg_path(ctx, "databases", "kraken2")
    ensure_inputs([nonhost, db])

    outdir = ctx.result_dir / "taxonomy"
    report = outdir / f"{sample.sample_id}.kraken.report"
    raw = outdir / f"{sample.sample_id}.kraken.out"
    bracken = outdir / f"{sample.sample_id}.bracken.S.tsv"
    threads = int(ctx.config["threads"]["taxonomy"])
    read_len = int(ctx.config["taxonomy"]["bracken_read_length"])

    command = f"""
set -euo pipefail
kraken2 --db {q(db)} --threads {threads} --gzip-compressed \
  --report {q(report)} --output {q(raw)} {q(nonhost)}
bracken -d {q(db)} -i {q(report)} -o {q(bracken)} -r {read_len} -l S
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p02_taxonomy.log",
                [report, bracken])
