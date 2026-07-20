"""Step 09: CAZyme annotation using run_dbcan."""

from .models import Context, Sample
from .utils import cfg_path, ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["run_dbcan"])

    proteins = ctx.result_dir / "annotation" / sample.sample_id / "bakta" / f"{sample.sample_id}.faa"
    db = cfg_path(ctx, "databases", "dbcan")
    ensure_inputs([proteins, db])

    outdir = ctx.result_dir / "cazyme" / sample.sample_id
    overview = outdir / "overview.txt"
    threads = int(ctx.config["threads"]["cazyme"])

    command = f"""
set -euo pipefail
mkdir -p {q(outdir)}
run_dbcan {q(proteins)} protein --db_dir {q(db)} \
  --out_dir {q(outdir)} --dia_cpu {threads} --hmm_cpu {threads}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p09_cazyme.log",
                [overview])
