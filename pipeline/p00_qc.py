"""Step 00: read quality control."""

from .models import Context, Sample
from .utils import ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["NanoPlot", "chopper", "seqkit"])
    ensure_inputs([sample.fastq])

    outdir = ctx.result_dir / "qc" / sample.sample_id
    filtered = outdir / "filtered.fastq.gz"
    stats = outdir / "seqkit_stats.tsv"
    done = outdir / "nanoplot.done"

    threads = int(ctx.config["threads"]["qc"])
    min_length = int(ctx.config["qc"]["min_length"])
    min_quality = float(ctx.config["qc"]["min_quality"])

    command = "\n".join(
        [
            "set -euo pipefail",
            f"mkdir -p {q(outdir / 'nanoplot')}",
            (
                f"NanoPlot --fastq {q(sample.fastq)} "
                f"--threads {threads} "
                f"--outdir {q(outdir / 'nanoplot')}"
            ),
            f"touch {q(done)}",
            (
                f"gzip -cd {q(sample.fastq)} "
                f"| chopper --minlength {min_length} --quality {min_quality} "
                f"| gzip -c > {q(filtered)}"
            ),
            (
                f"seqkit stats -T {q(sample.fastq)} {q(filtered)} "
                f"> {q(stats)}"
            ),
        ]
    )

    run_command(
        ctx,
        command,
        ctx.log_dir / sample.sample_id / "p00_qc.log",
        [filtered, stats, done],
    )
