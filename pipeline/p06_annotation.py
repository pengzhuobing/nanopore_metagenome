"""Step 06: contig annotation with Bakta."""

from .models import Context, Sample
from .utils import cfg_path, ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["bakta"])

    assembly = ctx.result_dir / "assembly" / sample.sample_id / "assembly.fasta"
    db = cfg_path(ctx, "databases", "bakta")
    ensure_inputs([assembly, db])

    outdir = ctx.result_dir / "annotation" / sample.sample_id / "bakta"
    faa = outdir / f"{sample.sample_id}.faa"
    gff = outdir / f"{sample.sample_id}.gff3"
    threads = int(ctx.config["threads"]["annotation"])

    command = f"""
set -euo pipefail
mkdir -p {q(outdir)}
bakta --db {q(db)} --threads {threads} --output {q(outdir)} \
  --prefix {q(sample.sample_id)} {q(assembly)}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p06_annotation.log",
                [faa, gff])
